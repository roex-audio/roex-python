"""
Unit tests for utility functions
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from roex_python.utils import get_content_type, upload_file
from roex_python.models import UploadUrlResponse


@pytest.mark.unit
class TestGetContentType:
    """Test content type detection"""
    
    def test_wav_file(self):
        """Test .wav file returns correct content type"""
        assert get_content_type("track.wav") == "audio/wav"
        assert get_content_type("path/to/track.wav") == "audio/wav"
    
    def test_mp3_file(self):
        """Test .mp3 file returns correct content type"""
        assert get_content_type("track.mp3") == "audio/mpeg"
        assert get_content_type("path/to/track.mp3") == "audio/mpeg"
    
    def test_flac_file(self):
        """Test .flac file returns correct content type"""
        assert get_content_type("track.flac") == "audio/flac"
        assert get_content_type("path/to/track.flac") == "audio/flac"
    
    def test_case_insensitive(self):
        """Test that extension matching is case insensitive"""
        assert get_content_type("track.WAV") == "audio/wav"
        assert get_content_type("track.Mp3") == "audio/mpeg"
        assert get_content_type("track.FLAC") == "audio/flac"
    
    def test_unsupported_extension_raises_error(self):
        """Test that unsupported file types raise ValueError"""
        with pytest.raises(ValueError, match="Unsupported file type"):
            get_content_type("track.txt")
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            get_content_type("track.pdf")
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            get_content_type("track.aac")
    
    def test_no_extension(self):
        """Test file with no extension raises error"""
        with pytest.raises(ValueError, match="Unsupported file type"):
            get_content_type("trackwithoutextension")


@pytest.mark.unit
class TestUploadFile:
    """Test file upload functionality"""
    
    @patch('roex_python.utils.requests.put')
    @patch('builtins.open', new_callable=mock_open, read_data=b'audio data')
    def test_successful_upload(self, mock_file, mock_put):
        """Test successful file upload"""
        # Setup
        mock_client = Mock()
        mock_upload_controller = Mock()
        mock_client.upload = mock_upload_controller
        
        upload_response = UploadUrlResponse(
            signed_url="https://signed.example.com/upload",
            readable_url="https://example.com/track.wav",
            error=False,
            message="Success"
        )
        mock_upload_controller.get_upload_url.return_value = upload_response
        
        mock_put_response = Mock()
        mock_put_response.raise_for_status = Mock()
        mock_put.return_value = mock_put_response
        
        # Execute
        result = upload_file(mock_client, "test_track.wav")
        
        # Assert
        assert result == "https://example.com/track.wav"
        mock_upload_controller.get_upload_url.assert_called_once()
        mock_put.assert_called_once()
        mock_file.assert_called_once_with("test_track.wav", 'rb')
    
    @patch('roex_python.utils.requests.put')
    def test_upload_with_error_response(self, mock_put):
        """Test upload when get_upload_url returns error"""
        # Setup
        mock_client = Mock()
        mock_upload_controller = Mock()
        mock_client.upload = mock_upload_controller
        
        upload_response = UploadUrlResponse(
            signed_url=None,
            readable_url=None,
            error=True,
            message="Failed to generate upload URL"
        )
        mock_upload_controller.get_upload_url.return_value = upload_response
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Failed to get valid upload URL"):
            upload_file(mock_client, "test_track.wav")
    
    @patch('roex_python.utils.requests.put')
    @patch('builtins.open', new_callable=mock_open, read_data=b'audio data')
    def test_upload_http_error(self, mock_file, mock_put):
        """Test upload when HTTP request fails"""
        # Setup
        mock_client = Mock()
        mock_upload_controller = Mock()
        mock_client.upload = mock_upload_controller
        
        upload_response = UploadUrlResponse(
            signed_url="https://signed.example.com/upload",
            readable_url="https://example.com/track.wav",
            error=False,
            message="Success"
        )
        mock_upload_controller.get_upload_url.return_value = upload_response
        
        import requests
        mock_put.side_effect = requests.exceptions.RequestException("Upload failed")
        
        # Execute & Assert
        with pytest.raises(requests.exceptions.RequestException):
            upload_file(mock_client, "test_track.wav")
    
    @patch('roex_python.utils.requests.put')
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_upload_file_not_found(self, mock_file, mock_put):
        """Test upload when file doesn't exist"""
        # Setup
        mock_client = Mock()
        mock_upload_controller = Mock()
        mock_client.upload = mock_upload_controller
        
        upload_response = UploadUrlResponse(
            signed_url="https://signed.example.com/upload",
            readable_url="https://example.com/track.wav",
            error=False,
            message="Success"
        )
        mock_upload_controller.get_upload_url.return_value = upload_response
        
        # Execute & Assert
        with pytest.raises(FileNotFoundError):
            upload_file(mock_client, "nonexistent.wav")
    
    @patch('roex_python.utils.requests.put')
    @patch('builtins.open', new_callable=mock_open, read_data=b'audio data')
    def test_correct_content_type_sent(self, mock_file, mock_put):
        """Test that correct content type header is sent"""
        # Setup
        mock_client = Mock()
        mock_upload_controller = Mock()
        mock_client.upload = mock_upload_controller
        
        upload_response = UploadUrlResponse(
            signed_url="https://signed.example.com/upload",
            readable_url="https://example.com/track.mp3",
            error=False,
            message="Success"
        )
        mock_upload_controller.get_upload_url.return_value = upload_response
        
        mock_put_response = Mock()
        mock_put_response.raise_for_status = Mock()
        mock_put.return_value = mock_put_response
        
        # Execute
        upload_file(mock_client, "test_track.mp3")
        
        # Assert - check that PUT was called with correct content type
        call_args = mock_put.call_args
        assert call_args[1]['headers']['Content-Type'] == 'audio/mpeg'
