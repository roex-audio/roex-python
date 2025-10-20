"""
Unit tests for EnhanceController
"""

import pytest
from unittest.mock import Mock, patch
import requests
from roex_python.controllers.enhance_controller import EnhanceController
from roex_python.models import (
    MixEnhanceRequest, MixEnhanceResponse, MusicalStyle, LoudnessPreference
)


@pytest.mark.unit
class TestEnhanceControllerInit:
    """Test EnhanceController initialization"""
    
    def test_init(self, mock_api_provider):
        """Test controller initialization"""
        controller = EnhanceController(mock_api_provider)
        assert controller.api_provider == mock_api_provider


@pytest.mark.unit
class TestCreateMixEnhancePreview:
    """Test create_mix_enhance_preview method"""
    
    def test_successful_creation(self, mock_api_provider):
        """Test successful enhance preview creation"""
        # Setup
        mock_api_provider.post.return_value = {
            "mixrevive_task_id": "enhance_task_123",
            "error": False,
            "message": "Success"
        }
        
        controller = EnhanceController(mock_api_provider)
        
        request = MixEnhanceRequest(
            audio_file_location="https://example.com/mix.wav",
            musical_style=MusicalStyle.POP
        )
        
        # Execute
        result = controller.create_mix_enhance_preview(request)
        
        # Assert
        assert isinstance(result, MixEnhanceResponse)
        assert result.mixrevive_task_id == "enhance_task_123"
        assert result.error is False
        
        # Verify correct endpoint
        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/mixenhancepreview"
    
    def test_with_custom_settings(self, mock_api_provider):
        """Test enhance preview with custom settings"""
        # Setup
        mock_api_provider.post.return_value = {
            "mixrevive_task_id": "enhance_task_456",
            "error": False,
            "message": "Success"
        }
        
        controller = EnhanceController(mock_api_provider)
        
        request = MixEnhanceRequest(
            audio_file_location="https://example.com/mix.wav",
            musical_style=MusicalStyle.ROCK_INDIE,
            is_master=True,
            fix_clipping_issues=True,
            fix_drc_issues=False,
            fix_stereo_width_issues=True,
            fix_tonal_profile_issues=True,
            fix_loudness_issues=False,
            apply_mastering=True,
            loudness_preference=LoudnessPreference.CD_LOUDNESS,
            stem_processing=True,
            webhook_url="https://example.com/webhook"
        )
        
        # Execute
        result = controller.create_mix_enhance_preview(request)
        
        # Assert
        assert result.mixrevive_task_id == "enhance_task_456"
        
        # Verify payload
        payload = mock_api_provider.post.call_args[0][1]
        mix_data = payload["mixReviveData"]
        assert mix_data["isMaster"] is True
        assert mix_data["fixClippingIssues"] is True
        assert mix_data["fixDRCIssues"] is False
        assert mix_data["applyMastering"] is True
        assert mix_data["stemProcessing"] is True
    
    def test_http_error_handling(self, mock_api_provider):
        """Test error handling when API returns HTTP error"""
        # Setup
        mock_api_provider.post.side_effect = requests.HTTPError("API Error")
        
        controller = EnhanceController(mock_api_provider)
        
        request = MixEnhanceRequest(
            audio_file_location="https://example.com/mix.wav",
            musical_style=MusicalStyle.POP
        )
        
        # Execute & Assert
        with pytest.raises(Exception, match="Failed to create mix enhance preview"):
            controller.create_mix_enhance_preview(request)


@pytest.mark.unit
class TestCreateMixEnhance:
    """Test create_mix_enhance method"""
    
    def test_successful_creation(self, mock_api_provider):
        """Test successful full enhance creation"""
        # Setup
        mock_api_provider.post.return_value = {
            "mixrevive_task_id": "enhance_full_123",
            "error": False,
            "message": "Success"
        }
        
        controller = EnhanceController(mock_api_provider)
        
        request = MixEnhanceRequest(
            audio_file_location="https://example.com/mix.wav",
            musical_style=MusicalStyle.ELECTRONIC
        )
        
        # Execute
        result = controller.create_mix_enhance(request)
        
        # Assert
        assert isinstance(result, MixEnhanceResponse)
        assert result.mixrevive_task_id == "enhance_full_123"
        
        # Verify correct endpoint
        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/mixenhance"
    
    def test_http_error_handling(self, mock_api_provider):
        """Test error handling"""
        # Setup
        mock_api_provider.post.side_effect = requests.HTTPError("API Error")
        
        controller = EnhanceController(mock_api_provider)
        
        request = MixEnhanceRequest(
            audio_file_location="https://example.com/mix.wav",
            musical_style=MusicalStyle.POP
        )
        
        # Execute & Assert
        with pytest.raises(Exception, match="Failed to create mix enhance"):
            controller.create_mix_enhance(request)


@pytest.mark.unit
class TestRetrieveEnhancedTrack:
    """Test retrieve_enhanced_track method"""
    
    @patch('roex_python.controllers.enhance_controller.time.sleep')
    def test_successful_retrieval(self, mock_sleep, mock_api_provider):
        """Test successful enhanced track retrieval"""
        # Setup
        mock_api_provider.post.return_value = {
            "error": False,
            "revived_track_tasks_results": {
                "download_url_revived": "https://example.com/enhanced.wav"
            }
        }
        
        controller = EnhanceController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_enhanced_track("enhance_task_123")
        
        # Assert
        assert result["download_url_revived"] == "https://example.com/enhanced.wav"
    
    @patch('roex_python.controllers.enhance_controller.time.sleep')
    def test_polling_until_ready(self, mock_sleep, mock_api_provider):
        """Test polling until enhanced track is ready"""
        # Setup - first calls return error, last returns result
        mock_api_provider.post.side_effect = [
            {"error": True},
            {"error": True},
            {
                "error": False,
                "revived_track_tasks_results": {
                    "download_url_revived": "https://example.com/enhanced.wav"
                }
            }
        ]
        
        controller = EnhanceController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_enhanced_track("enhance_task_123", poll_interval=1)
        
        # Assert
        assert result["download_url_revived"] == "https://example.com/enhanced.wav"
        assert mock_api_provider.post.call_count == 3
    
    @patch('roex_python.controllers.enhance_controller.time.sleep')
    def test_alternate_response_format(self, mock_sleep, mock_api_provider):
        """Test handling of alternate response format"""
        # Setup - response in different format
        mock_api_provider.post.return_value = {
            "error": False,
            "track_results": {
                "download_url_preview_revived": "https://example.com/preview_enhanced.wav"
            }
        }
        
        controller = EnhanceController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_enhanced_track("enhance_task_123")
        
        # Assert - should find the download URL in nested structure
        assert "download_url_preview_revived" in result
    
    @patch('roex_python.controllers.enhance_controller.time.sleep')
    def test_polling_timeout(self, mock_sleep, mock_api_provider):
        """Test polling timeout after max attempts"""
        # Setup - always return error
        mock_api_provider.post.return_value = {"error": True}
        
        controller = EnhanceController(mock_api_provider)
        
        # Execute & Assert
        with pytest.raises(Exception, match="Enhanced track was not available after polling"):
            controller.retrieve_enhanced_track("enhance_task_123", max_attempts=3, poll_interval=0.1)
        
        assert mock_api_provider.post.call_count == 3
    
    @patch('roex_python.controllers.enhance_controller.time.sleep')
    def test_http_error_continues_polling(self, mock_sleep, mock_api_provider):
        """Test that HTTP errors don't stop polling"""
        # Setup - first call errors, second succeeds
        mock_api_provider.post.side_effect = [
            requests.HTTPError("Temporary error"),
            {
                "error": False,
                "revived_track_tasks_results": {
                    "download_url_revived": "https://example.com/enhanced.wav"
                }
            }
        ]
        
        controller = EnhanceController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_enhanced_track("enhance_task_123", max_attempts=5, poll_interval=0.1)
        
        # Assert - should eventually succeed despite initial error
        assert result["download_url_revived"] == "https://example.com/enhanced.wav"


@pytest.mark.unit
class TestPayloadPreparation:
    """Test _prepare_mix_enhance_payload method"""
    
    def test_payload_structure_with_defaults(self, mock_api_provider):
        """Test payload structure with default values"""
        controller = EnhanceController(mock_api_provider)
        
        request = MixEnhanceRequest(
            audio_file_location="https://example.com/mix.wav",
            musical_style=MusicalStyle.POP
        )
        
        payload = controller._prepare_mix_enhance_payload(request)
        
        # Assert structure
        assert "mixReviveData" in payload
        data = payload["mixReviveData"]
        assert data["audioFileLocation"] == "https://example.com/mix.wav"
        assert data["musicalStyle"] == "POP"
        assert data["isMaster"] is False
        assert data["fixClippingIssues"] is True
        assert data["loudnessPreference"] == "STREAMING_LOUDNESS"
    
    def test_payload_structure_with_custom_values(self, mock_api_provider):
        """Test payload structure with custom values"""
        controller = EnhanceController(mock_api_provider)
        
        request = MixEnhanceRequest(
            audio_file_location="https://example.com/master.wav",
            musical_style=MusicalStyle.ROCK_INDIE,
            is_master=True,
            fix_clipping_issues=False,
            fix_drc_issues=True,
            fix_stereo_width_issues=False,
            fix_tonal_profile_issues=True,
            fix_loudness_issues=False,
            apply_mastering=True,
            webhook_url="https://example.com/webhook",
            loudness_preference=LoudnessPreference.CD_LOUDNESS,
            stem_processing=True
        )
        
        payload = controller._prepare_mix_enhance_payload(request)
        
        # Assert all custom values
        data = payload["mixReviveData"]
        assert data["isMaster"] is True
        assert data["fixClippingIssues"] is False
        assert data["fixDRCIssues"] is True
        assert data["fixStereoWidthIssues"] is False
        assert data["fixTonalProfileIssues"] is True
        assert data["fixLoudnessIssues"] is False
        assert data["applyMastering"] is True
        assert data["webhookURL"] == "https://example.com/webhook"
        assert data["loudnessPreference"] == "CD_LOUDNESS"
        assert data["stemProcessing"] is True
