"""
Unit tests for UploadController
"""

import pytest
from unittest.mock import Mock
from roex_python.controllers.upload_controller import UploadController
from roex_python.models import UploadUrlRequest, UploadUrlResponse


@pytest.mark.unit
class TestUploadControllerInit:
    """Test UploadController initialization"""
    
    def test_init(self, mock_api_provider):
        """Test controller initialization"""
        controller = UploadController(mock_api_provider)
        assert controller.api_provider == mock_api_provider


@pytest.mark.unit
class TestGetUploadUrl:
    """Test get_upload_url method"""
    
    def test_successful_request(self, mock_api_provider):
        """Test successful upload URL request"""
        # Setup
        mock_api_provider.post.return_value = {
            "signed_url": "https://storage.example.com/upload?signature=xyz",
            "readable_url": "https://storage.example.com/track.wav",
            "error": False,
            "message": "Success",
            "info": "URLs generated"
        }
        
        controller = UploadController(mock_api_provider)
        
        request = UploadUrlRequest(
            filename="track.wav",
            content_type="audio/wav"
        )
        
        # Execute
        result = controller.get_upload_url(request)
        
        # Assert
        assert isinstance(result, UploadUrlResponse)
        assert result.signed_url == "https://storage.example.com/upload?signature=xyz"
        assert result.readable_url == "https://storage.example.com/track.wav"
        assert result.error is False
        assert result.message == "Success"
        
        # Verify correct endpoint and payload
        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/upload"
        payload = call_args[0][1]
        assert payload["filename"] == "track.wav"
        assert payload["contentType"] == "audio/wav"
    
    def test_different_file_types(self, mock_api_provider):
        """Test with different audio file types"""
        # Setup
        mock_api_provider.post.return_value = {
            "signed_url": "https://storage.example.com/upload",
            "readable_url": "https://storage.example.com/file",
            "error": False,
            "message": "Success"
        }
        
        controller = UploadController(mock_api_provider)
        
        # Test different file types
        test_cases = [
            ("track.wav", "audio/wav"),
            ("song.mp3", "audio/mpeg"),
            ("audio.flac", "audio/flac")
        ]
        
        for filename, content_type in test_cases:
            request = UploadUrlRequest(
                filename=filename,
                content_type=content_type
            )
            
            result = controller.get_upload_url(request)
            
            # Verify content type in payload
            payload = mock_api_provider.post.call_args[0][1]
            assert payload["contentType"] == content_type
            assert result.error is False
    
    def test_error_response(self, mock_api_provider):
        """Test handling of error response"""
        # Setup
        mock_api_provider.post.return_value = {
            "signed_url": None,
            "readable_url": None,
            "error": True,
            "message": "Invalid filename",
            "info": "Filename must not contain special characters"
        }
        
        controller = UploadController(mock_api_provider)
        
        request = UploadUrlRequest(
            filename="track@#$.wav",
            content_type="audio/wav"
        )
        
        # Execute
        result = controller.get_upload_url(request)
        
        # Assert
        assert isinstance(result, UploadUrlResponse)
        assert result.error is True
        assert result.message == "Invalid filename"
        assert result.signed_url is None
        assert result.readable_url is None
    
    def test_exception_handling(self, mock_api_provider):
        """Test exception handling"""
        # Setup
        mock_api_provider.post.side_effect = Exception("Network error")
        
        controller = UploadController(mock_api_provider)
        
        request = UploadUrlRequest(
            filename="track.wav",
            content_type="audio/wav"
        )
        
        # Execute & Assert
        with pytest.raises(Exception, match="Network error"):
            controller.get_upload_url(request)
    
    def test_missing_optional_fields(self, mock_api_provider):
        """Test response with missing optional fields"""
        # Setup
        mock_api_provider.post.return_value = {
            "signed_url": "https://storage.example.com/upload",
            "readable_url": "https://storage.example.com/track.wav"
            # Missing error, message, info fields
        }
        
        controller = UploadController(mock_api_provider)
        
        request = UploadUrlRequest(
            filename="track.wav",
            content_type="audio/wav"
        )
        
        # Execute
        result = controller.get_upload_url(request)
        
        # Assert - optional fields should have defaults
        assert result.signed_url == "https://storage.example.com/upload"
        assert result.readable_url == "https://storage.example.com/track.wav"
        assert result.error is False  # Default value
        assert result.message == ""  # Default value
    
    def test_special_characters_in_filename(self, mock_api_provider):
        """Test handling of filenames with spaces and unicode"""
        # Setup
        mock_api_provider.post.return_value = {
            "signed_url": "https://storage.example.com/upload",
            "readable_url": "https://storage.example.com/my%20track.wav",
            "error": False,
            "message": "Success"
        }
        
        controller = UploadController(mock_api_provider)
        
        request = UploadUrlRequest(
            filename="my track.wav",
            content_type="audio/wav"
        )
        
        # Execute
        result = controller.get_upload_url(request)
        
        # Assert
        assert result.error is False
        payload = mock_api_provider.post.call_args[0][1]
        assert payload["filename"] == "my track.wav"
    
    def test_large_filename(self, mock_api_provider):
        """Test handling of very long filenames"""
        # Setup
        mock_api_provider.post.return_value = {
            "signed_url": "https://storage.example.com/upload",
            "readable_url": "https://storage.example.com/long_filename.wav",
            "error": False,
            "message": "Success"
        }
        
        controller = UploadController(mock_api_provider)
        
        long_filename = "a" * 200 + ".wav"
        request = UploadUrlRequest(
            filename=long_filename,
            content_type="audio/wav"
        )
        
        # Execute
        result = controller.get_upload_url(request)
        
        # Assert - should handle without crashing
        assert isinstance(result, UploadUrlResponse)
        payload = mock_api_provider.post.call_args[0][1]
        assert payload["filename"] == long_filename
