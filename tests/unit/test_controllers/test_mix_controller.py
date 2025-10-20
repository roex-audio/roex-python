"""
Unit tests for MixController
"""

import pytest
from unittest.mock import Mock, patch
import requests
from roex_python.controllers.mix_controller import MixController
from roex_python.models import (
    MultitrackMixRequest, TrackData, InstrumentGroup,
    PresenceSetting, PanPreference, ReverbPreference,
    MusicalStyle, FinalMixRequest, TrackGainData,
    MultitrackTaskResponse
)


@pytest.mark.unit
class TestMixControllerInit:
    """Test MixController initialization"""
    
    def test_init(self, mock_api_provider):
        """Test controller initialization"""
        controller = MixController(mock_api_provider)
        assert controller.api_provider == mock_api_provider


@pytest.mark.unit
class TestCreateMixPreview:
    """Test create_mix_preview method"""
    
    def test_successful_creation(self, mock_api_provider):
        """Test successful mix preview creation"""
        # Setup
        mock_api_provider.post.return_value = {
            "multitrack_task_id": "mix_task_123"
        }
        
        controller = MixController(mock_api_provider)
        
        tracks = [
            TrackData(
                track_url="https://example.com/bass.wav",
                instrument_group=InstrumentGroup.BASS_GROUP,
                presence_setting=PresenceSetting.NORMAL,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.NONE
            )
        ]
        
        request = MultitrackMixRequest(
            track_data=tracks,
            musical_style=MusicalStyle.POP
        )
        
        # Execute
        result = controller.create_mix_preview(request)
        
        # Assert
        assert isinstance(result, MultitrackTaskResponse)
        assert result.multitrack_task_id == "mix_task_123"
        
        # Verify payload
        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/mixpreview"
        payload = call_args[0][1]
        assert payload["multitrackData"]["musicalStyle"] == "POP"
        assert len(payload["multitrackData"]["trackData"]) == 1
    
    def test_with_multiple_tracks(self, mock_api_provider):
        """Test mix preview with multiple tracks"""
        # Setup
        mock_api_provider.post.return_value = {
            "multitrack_task_id": "mix_task_456"
        }
        
        controller = MixController(mock_api_provider)
        
        tracks = [
            TrackData(
                track_url="https://example.com/bass.wav",
                instrument_group=InstrumentGroup.BASS_GROUP,
                presence_setting=PresenceSetting.NORMAL,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.NONE
            ),
            TrackData(
                track_url="https://example.com/vocals.wav",
                instrument_group=InstrumentGroup.VOCAL_GROUP,
                presence_setting=PresenceSetting.LEAD,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.LOW
            ),
            TrackData(
                track_url="https://example.com/drums.wav",
                instrument_group=InstrumentGroup.DRUMS_GROUP,
                presence_setting=PresenceSetting.NORMAL,
                pan_preference=PanPreference.NO_PREFERENCE,
                reverb_preference=ReverbPreference.MEDIUM
            )
        ]
        
        request = MultitrackMixRequest(
            track_data=tracks,
            musical_style=MusicalStyle.ROCK_INDIE,
            return_stems=True
        )
        
        # Execute
        result = controller.create_mix_preview(request)
        
        # Assert
        payload = mock_api_provider.post.call_args[0][1]
        assert len(payload["multitrackData"]["trackData"]) == 3
        assert payload["multitrackData"]["returnStems"] is True
    
    def test_http_error_handling(self, mock_api_provider):
        """Test error handling when API returns HTTP error"""
        # Setup
        mock_api_provider.post.side_effect = requests.HTTPError("API Error")
        
        controller = MixController(mock_api_provider)
        tracks = [
            TrackData(
                track_url="https://example.com/track.wav",
                instrument_group=InstrumentGroup.BASS_GROUP,
                presence_setting=PresenceSetting.NORMAL,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.NONE
            )
        ]
        
        request = MultitrackMixRequest(
            track_data=tracks,
            musical_style=MusicalStyle.POP
        )
        
        # Execute & Assert
        with pytest.raises(Exception, match="Failed to create mix preview"):
            controller.create_mix_preview(request)


@pytest.mark.unit
class TestRetrievePreviewMix:
    """Test retrieve_preview_mix method"""
    
    def test_immediate_success(self, mock_api_provider):
        """Test when preview is immediately available"""
        # Setup
        mock_api_provider.post.return_value = {
            "previewMixTaskResults": {
                "download_url_preview_mix": "https://example.com/preview.wav",
                "status": "MIX_TASK_PREVIEW_COMPLETED"
            },
            "status": "MIX_TASK_PREVIEW_COMPLETED"
        }
        
        controller = MixController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_preview_mix("mix_task_123")
        
        # Assert
        assert result["download_url_preview_mix"] == "https://example.com/preview.wav"
        assert result["status"] == "MIX_TASK_PREVIEW_COMPLETED"
    
    @patch('roex_python.controllers.mix_controller.time.sleep')
    def test_polling_until_ready(self, mock_sleep, mock_api_provider):
        """Test polling until preview is ready"""
        # Setup - first calls return pending, last returns result
        mock_api_provider.post.side_effect = [
            requests.HTTPError("Not ready"),
            {"status": "PROCESSING"},
            {
                "previewMixTaskResults": {
                    "download_url_preview_mix": "https://example.com/preview.wav",
                    "status": "MIX_TASK_PREVIEW_COMPLETED"
                }
            }
        ]
        
        controller = MixController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_preview_mix("mix_task_123", poll_interval=1)
        
        # Assert
        assert result["download_url_preview_mix"] == "https://example.com/preview.wav"
        assert mock_api_provider.post.call_count == 3
    
    @patch('roex_python.controllers.mix_controller.time.sleep')
    def test_polling_timeout(self, mock_sleep, mock_api_provider):
        """Test polling timeout after max attempts"""
        # Setup - first call raises error (tries initial), then returns pending for polling attempts
        mock_api_provider.post.side_effect = [
            requests.HTTPError("Not ready"),
            {"status": "PROCESSING"},
            {"status": "PROCESSING"},
            {"status": "PROCESSING"}
        ]
        
        controller = MixController(mock_api_provider)
        
        # Execute & Assert
        with pytest.raises(Exception, match="Preview mix was not available after polling"):
            controller.retrieve_preview_mix("mix_task_123", max_attempts=3, poll_interval=0.1)
        
        # Should have tried: 1 initial (fails) + 3 polling attempts = 4 total
        assert mock_api_provider.post.call_count == 4
    
    def test_with_fx_settings(self, mock_api_provider):
        """Test retrieving preview with FX settings"""
        # Setup
        mock_api_provider.post.return_value = {
            "previewMixTaskResults": {
                "download_url_preview_mix": "https://example.com/preview.wav",
                "fx_settings": {"compression": "moderate"},
                "status": "MIX_TASK_PREVIEW_COMPLETED"
            },
            "status": "MIX_TASK_PREVIEW_COMPLETED"
        }
        
        controller = MixController(mock_api_provider)
        
        # Execute
        result = controller.retrieve_preview_mix("mix_task_123", retrieve_fx_settings=True)
        
        # Assert
        assert "fx_settings" in result
        
        # Verify retrieveFXSettings was passed
        payload = mock_api_provider.post.call_args[0][1]
        assert payload["multitrackData"]["retrieveFXSettings"] is True


@pytest.mark.unit
class TestRetrieveFinalMix:
    """Test retrieve_final_mix method"""
    
    def test_successful_retrieval(self, mock_api_provider):
        """Test successful final mix retrieval"""
        # Setup
        mock_api_provider.post.return_value = {
            "applyAudioEffectsResults": {
                "download_url_final_mix": "https://example.com/final.wav"
            }
        }
        
        controller = MixController(mock_api_provider)
        
        track_data = [
            TrackGainData(
                track_url="https://example.com/track1.wav",
                gain_db=2.5
            )
        ]
        
        request = FinalMixRequest(
            multitrack_task_id="mix_task_123",
            track_data=track_data
        )
        
        # Execute
        result = controller.retrieve_final_mix(request)
        
        # Assert
        assert result["download_url_final_mix"] == "https://example.com/final.wav"
    
    def test_with_multiple_tracks_and_gains(self, mock_api_provider):
        """Test final mix with multiple tracks and gain adjustments"""
        # Setup
        mock_api_provider.post.return_value = {
            "applyAudioEffectsResults": {
                "download_url_final_mix": "https://example.com/final.wav"
            }
        }
        
        controller = MixController(mock_api_provider)
        
        track_data = [
            TrackGainData(track_url="https://example.com/track1.wav", gain_db=2.5),
            TrackGainData(track_url="https://example.com/track2.wav", gain_db=-1.0),
            TrackGainData(track_url="https://example.com/track3.wav", gain_db=0.0)
        ]
        
        request = FinalMixRequest(
            multitrack_task_id="mix_task_123",
            track_data=track_data,
            return_stems=True
        )
        
        # Execute
        result = controller.retrieve_final_mix(request)
        
        # Assert
        payload = mock_api_provider.post.call_args[0][1]
        assert len(payload["applyAudioEffectsData"]["trackData"]) == 3
        assert payload["applyAudioEffectsData"]["returnStems"] is True
    
    def test_http_error(self, mock_api_provider):
        """Test error handling"""
        # Setup
        mock_api_provider.post.side_effect = requests.HTTPError("API Error")
        
        controller = MixController(mock_api_provider)
        
        request = FinalMixRequest(
            multitrack_task_id="mix_task_123",
            track_data=[TrackGainData(track_url="https://example.com/track.wav", gain_db=0)]
        )
        
        # Execute & Assert
        with pytest.raises(Exception, match="Failed to retrieve final mix"):
            controller.retrieve_final_mix(request)


@pytest.mark.unit
class TestPayloadPreparation:
    """Test payload preparation methods"""
    
    def test_mix_preview_payload_structure(self, mock_api_provider):
        """Test that mix preview payload is correctly structured"""
        controller = MixController(mock_api_provider)
        
        tracks = [
            TrackData(
                track_url="https://example.com/test.wav",
                instrument_group=InstrumentGroup.VOCAL_GROUP,
                presence_setting=PresenceSetting.LEAD,
                pan_preference=PanPreference.LEFT,
                reverb_preference=ReverbPreference.HIGH
            )
        ]
        
        request = MultitrackMixRequest(
            track_data=tracks,
            musical_style=MusicalStyle.ELECTRONIC,
            return_stems=True,
            sample_rate="48000",
            webhook_url="https://example.com/webhook"
        )
        
        payload = controller._prepare_mix_preview_payload(request)
        
        # Assert structure
        assert "multitrackData" in payload
        md = payload["multitrackData"]
        assert "trackData" in md
        assert "musicalStyle" in md
        assert "returnStems" in md
        assert "sampleRate" in md
        assert "webhookURL" in md
        
        # Assert values
        assert md["musicalStyle"] == "ELECTRONIC"
        assert md["returnStems"] is True
        assert md["sampleRate"] == "48000"
        assert len(md["trackData"]) == 1
        
        # Assert track data
        track = md["trackData"][0]
        assert track["trackURL"] == "https://example.com/test.wav"
        assert track["instrumentGroup"] == "VOCAL_GROUP"
        assert track["presenceSetting"] == "LEAD"
        assert track["panPreference"] == "LEFT"
        assert track["reverbPreference"] == "HIGH"
    
    def test_final_mix_payload_structure(self, mock_api_provider):
        """Test that final mix payload is correctly structured"""
        controller = MixController(mock_api_provider)
        
        track_data = [
            TrackGainData(track_url="https://example.com/track1.wav", gain_db=3.0),
            TrackGainData(track_url="https://example.com/track2.wav", gain_db=-2.5)
        ]
        
        request = FinalMixRequest(
            multitrack_task_id="mix_task_789",
            track_data=track_data,
            return_stems=False,
            sample_rate="44100"
        )
        
        payload = controller._prepare_final_mix_payload(request)
        
        # Assert structure
        assert "applyAudioEffectsData" in payload
        aed = payload["applyAudioEffectsData"]
        assert "multitrackTaskId" in aed
        assert "trackData" in aed
        assert "returnStems" in aed
        assert "sampleRate" in aed
        
        # Assert values
        assert aed["multitrackTaskId"] == "mix_task_789"
        assert aed["returnStems"] is False
        assert aed["sampleRate"] == "44100"
        assert len(aed["trackData"]) == 2
        
        # Assert track data
        assert aed["trackData"][0]["trackURL"] == "https://example.com/track1.wav"
        assert aed["trackData"][0]["gainDb"] == 3.0
        assert aed["trackData"][1]["trackURL"] == "https://example.com/track2.wav"
        assert aed["trackData"][1]["gainDb"] == -2.5
