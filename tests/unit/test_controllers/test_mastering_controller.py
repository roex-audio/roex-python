"""
Unit tests for MasteringController
"""

import pytest
from unittest.mock import Mock, patch
import requests
import time
from roex_python.controllers.mastering_controller import MasteringController
from roex_python.models import (
    MasteringRequest, MusicalStyle, DesiredLoudness,
    MasteringTaskResponse
)


@pytest.mark.unit
class TestMasteringControllerInit:
    """Test MasteringController initialization"""
    
    def test_init(self, mock_api_provider):
        """Test controller initialization"""
        controller = MasteringController(mock_api_provider)
        assert controller.api_provider == mock_api_provider


@pytest.mark.unit
class TestCreateMasteringPreview:
    """Test create_mastering_preview method"""
    
    def test_successful_creation(self, mock_api_provider):
        """Test successful mastering preview creation"""
        # Setup
        mock_api_provider.post.return_value = {
            "mastering_task_id": "task_123"
        }
        
        controller = MasteringController(mock_api_provider)
        request = MasteringRequest(
            track_url="https://example.com/track.wav",
            musical_style=MusicalStyle.POP,
            desired_loudness=DesiredLoudness.MEDIUM
        )
        
        # Execute
        result = controller.create_mastering_preview(request)
        
        # Assert
        assert isinstance(result, MasteringTaskResponse)
        assert result.mastering_task_id == "task_123"
        
        # Verify correct payload was sent
        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/masteringpreview"
        payload = call_args[0][1]
        assert payload["masteringData"]["trackData"][0]["trackURL"] == "https://example.com/track.wav"
        assert payload["masteringData"]["musicalStyle"] == "POP"
        assert payload["masteringData"]["desiredLoudness"] == "MEDIUM"
    
    def test_with_webhook_url(self, mock_api_provider):
        """Test mastering preview with webhook URL"""
        # Setup
        mock_api_provider.post.return_value = {
            "mastering_task_id": "task_456"
        }
        
        controller = MasteringController(mock_api_provider)
        request = MasteringRequest(
            track_url="https://example.com/track.wav",
            musical_style=MusicalStyle.ROCK_INDIE,
            desired_loudness=DesiredLoudness.HIGH,
            webhook_url="https://example.com/webhook"
        )
        
        # Execute
        result = controller.create_mastering_preview(request)
        
        # Assert
        call_args = mock_api_provider.post.call_args
        payload = call_args[0][1]
        assert payload["masteringData"]["webhookURL"] == "https://example.com/webhook"
    
    def test_http_error_handling(self, mock_api_provider):
        """Test error handling when API returns HTTP error"""
        # Setup
        mock_api_provider.post.side_effect = requests.HTTPError("API Error")
        
        controller = MasteringController(mock_api_provider)
        request = MasteringRequest(
            track_url="https://example.com/track.wav",
            musical_style=MusicalStyle.POP,
            desired_loudness=DesiredLoudness.MEDIUM
        )
        
        # Execute & Assert
        with pytest.raises(Exception, match="Failed to create mastering preview"):
            controller.create_mastering_preview(request)


@pytest.mark.unit
class TestRetrievePreviewMaster:
    """Test retrieve_preview_master method"""
    
    def test_immediate_success(self, mock_api_provider):
        """Test when preview is immediately available"""
        # Setup
        mock_api_provider.post.return_value = {
            "previewMasterTaskResults": {
                "download_url_mastered_preview": "https://example.com/preview.wav",
                "status": "completed"
            }
        }
        
        controller = MasteringController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_preview_master("task_123")
        
        # Assert
        assert result["download_url_mastered_preview"] == "https://example.com/preview.wav"
        assert result["status"] == "completed"
    
    @patch('roex_python.controllers.mastering_controller.time.sleep')
    def test_polling_until_ready(self, mock_sleep, mock_api_provider):
        """Test polling until preview is ready"""
        # Setup - first call returns pending, second returns result
        mock_api_provider.post.side_effect = [
            requests.HTTPError("Not ready"),
            {"status": 202},
            {
                "previewMasterTaskResults": {
                    "download_url_mastered_preview": "https://example.com/preview.wav"
                }
            }
        ]
        
        controller = MasteringController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_preview_master("task_123", poll_interval=1)
        
        # Assert
        assert result["download_url_mastered_preview"] == "https://example.com/preview.wav"
        assert mock_api_provider.post.call_count == 3
    
    @patch('roex_python.controllers.mastering_controller.time.sleep')
    def test_polling_timeout(self, mock_sleep, mock_api_provider):
        """Test polling timeout after max attempts"""
        # Setup - first call raises error, then returns pending status
        mock_api_provider.post.side_effect = [
            requests.HTTPError("Not ready"),  # Initial attempt fails
            {"status": 202},
            {"status": 202},
            {"status": 202}
        ]
        
        controller = MasteringController(mock_api_provider)
        
        # Execute & Assert
        with pytest.raises(Exception, match="Preview master was not available after polling"):
            controller.retrieve_preview_master("task_123", max_attempts=3, poll_interval=0.1)
        
        # Should have tried: 1 initial + 3 polling attempts = 4 total
        assert mock_api_provider.post.call_count == 4


@pytest.mark.unit
class TestRetrieveFinalMaster:
    """Test retrieve_final_master method"""
    
    def test_structured_response(self, mock_api_provider):
        """Test with structured response format"""
        # Setup
        mock_api_provider.post.return_value = {
            "finalMasterTaskResults": {
                "download_url_mastered": "https://example.com/final.wav"
            }
        }
        
        controller = MasteringController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_final_master("task_123")
        
        # Assert
        assert result["download_url_mastered"] == "https://example.com/final.wav"
    
    def test_direct_url_response(self, mock_api_provider):
        """Test when response is direct URL"""
        # Setup
        mock_api_provider.post.return_value = "https://example.com/final.wav"
        
        controller = MasteringController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_final_master("task_123")
        
        # Assert
        assert result == "https://example.com/final.wav"
    
    def test_http_error(self, mock_api_provider):
        """Test error handling"""
        # Setup
        mock_api_provider.post.side_effect = requests.HTTPError("API Error")
        
        controller = MasteringController(mock_api_provider)
        
        # Execute & Assert
        with pytest.raises(Exception, match="Failed to retrieve final master"):
            controller.retrieve_final_master("task_123")


@pytest.mark.unit
class TestProcessAlbum:
    """Test process_album method"""
    
    @patch('roex_python.controllers.mastering_controller.os.makedirs')
    def test_album_processing(self, mock_makedirs, mock_api_provider):
        """Test processing multiple tracks as album"""
        # Setup
        mock_api_provider.post.side_effect = [
            # First track - preview creation
            {"mastering_task_id": "task_1"},
            # First track - preview retrieval
            {"previewMasterTaskResults": {"status": "ready"}},
            # First track - final master
            {"finalMasterTaskResults": {"download_url_mastered": "https://example.com/track1.wav"}},
            # Second track - preview creation
            {"mastering_task_id": "task_2"},
            # Second track - preview retrieval
            {"previewMasterTaskResults": {"status": "ready"}},
            # Second track - final master
            {"finalMasterTaskResults": {"download_url_mastered": "https://example.com/track2.wav"}}
        ]
        
        mock_api_provider.download_file.return_value = True
        
        controller = MasteringController(mock_api_provider)
        
        tracks = [
            MasteringRequest(
                track_url="https://example.com/input1.wav",
                musical_style=MusicalStyle.POP,
                desired_loudness=DesiredLoudness.MEDIUM
            ),
            MasteringRequest(
                track_url="https://example.com/input2.wav",
                musical_style=MusicalStyle.POP,
                desired_loudness=DesiredLoudness.MEDIUM
            )
        ]
        
        from roex_python.models import AlbumMasteringRequest
        album_request = AlbumMasteringRequest(tracks=tracks)
        
        # Execute
        result = controller.process_album(album_request)
        
        # Assert
        assert len(result) == 2
        assert result[1] == "https://example.com/track1.wav"
        assert result[2] == "https://example.com/track2.wav"
