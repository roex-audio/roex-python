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
    MultitrackTaskResponse, FinalMixRequestAdvanced,
    TrackEffectsData, EQSettings, EQBandSettings,
    CompressionSettings, PanningSettings, DesiredLoudness
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
            ),
            TrackData(
                track_url="https://example.com/vocals.wav",
                instrument_group=InstrumentGroup.VOCAL_GROUP,
                presence_setting=PresenceSetting.LEAD,
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
        assert len(payload["multitrackData"]["trackData"]) == 2
    
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
            ),
            TrackData(
                track_url="https://example.com/track2.wav",
                instrument_group=InstrumentGroup.VOCAL_GROUP,
                presence_setting=PresenceSetting.LEAD,
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
        with pytest.raises(Exception, match="did not complete after polling"):
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
            ),
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
        assert len(md["trackData"]) == 2
        
        # Assert first track data
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


@pytest.mark.unit
class TestTrackCountValidation:
    """Test track count validation in request models"""
    
    def test_multitrack_mix_request_too_few_tracks(self):
        """Test validation fails with fewer than 2 tracks"""
        with pytest.raises(ValueError, match="must contain between 2 and 32 tracks"):
            MultitrackMixRequest(
                track_data=[
                    TrackData(
                        track_url="https://example.com/track.wav",
                        instrument_group=InstrumentGroup.BASS_GROUP,
                        presence_setting=PresenceSetting.NORMAL,
                        pan_preference=PanPreference.CENTRE,
                        reverb_preference=ReverbPreference.NONE
                    )
                ],  # Only 1 track - should fail
                musical_style=MusicalStyle.POP
            )
    
    def test_multitrack_mix_request_too_many_tracks(self):
        """Test validation fails with more than 32 tracks"""
        # Create 33 tracks
        tracks = [
            TrackData(
                track_url=f"https://example.com/track{i}.wav",
                instrument_group=InstrumentGroup.OTHER_GROUP1,
                presence_setting=PresenceSetting.NORMAL,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.NONE
            ) for i in range(33)
        ]
        
        with pytest.raises(ValueError, match="must contain between 2 and 32 tracks"):
            MultitrackMixRequest(
                track_data=tracks,
                musical_style=MusicalStyle.POP
            )
    
    def test_multitrack_mix_request_valid_track_count(self):
        """Test validation passes with 2-32 tracks"""
        # Test minimum (2 tracks)
        tracks_min = [
            TrackData(
                track_url=f"https://example.com/track{i}.wav",
                instrument_group=InstrumentGroup.BASS_GROUP,
                presence_setting=PresenceSetting.NORMAL,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.NONE
            ) for i in range(2)
        ]
        request_min = MultitrackMixRequest(track_data=tracks_min, musical_style=MusicalStyle.POP)
        assert len(request_min.track_data) == 2
        
        # Test maximum (32 tracks)
        tracks_max = [
            TrackData(
                track_url=f"https://example.com/track{i}.wav",
                instrument_group=InstrumentGroup.OTHER_GROUP1,
                presence_setting=PresenceSetting.NORMAL,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.NONE
            ) for i in range(32)
        ]
        request_max = MultitrackMixRequest(track_data=tracks_max, musical_style=MusicalStyle.POP)
        assert len(request_max.track_data) == 32
    
    def test_final_mix_request_advanced_no_validation(self):
        """Test FinalMixRequestAdvanced accepts any track count (validated during preview)"""
        # Single track is ok for final mix (track count was validated during preview creation)
        request = FinalMixRequestAdvanced(
            multitrack_task_id="task_123",
            track_data=[
                TrackEffectsData(track_url="https://example.com/track.wav", gain_db=0.0)
            ]
        )
        assert len(request.track_data) == 1
        
        # Multiple tracks also ok
        request2 = FinalMixRequestAdvanced(
            multitrack_task_id="task_456",
            track_data=[
                TrackEffectsData(track_url="https://example.com/track1.wav", gain_db=0.0),
                TrackEffectsData(track_url="https://example.com/track2.wav", gain_db=0.0)
            ]
        )
        assert len(request2.track_data) == 2


@pytest.mark.unit
class TestAdvancedAudioEffects:
    """Test advanced audio effects functionality"""
    
    def test_eq_band_settings_validation(self):
        """Test EQ band settings parameter validation"""
        # Valid settings should work
        eq_band = EQBandSettings(gain=5.0, q=2.0, centre_freq=1000.0)
        assert eq_band.gain == 5.0
        
        # Invalid gain (out of range)
        with pytest.raises(ValueError, match="EQ gain must be between"):
            EQBandSettings(gain=25.0, q=1.0, centre_freq=1000.0)
        
        # Invalid Q factor
        with pytest.raises(ValueError, match="EQ Q factor must be between"):
            EQBandSettings(gain=0.0, q=15.0, centre_freq=1000.0)
        
        # Invalid frequency
        with pytest.raises(ValueError, match="EQ centre frequency must be between"):
            EQBandSettings(gain=0.0, q=1.0, centre_freq=25000.0)
    
    def test_compression_settings_validation(self):
        """Test compression settings parameter validation"""
        # Valid settings should work
        comp = CompressionSettings(threshold=-20.0, ratio=4.0, attack_ms=5.0, release_ms=50.0)
        assert comp.threshold == -20.0
        
        # Invalid threshold
        with pytest.raises(ValueError, match="Compression threshold must be between"):
            CompressionSettings(threshold=-70.0, ratio=4.0, attack_ms=5.0, release_ms=50.0)
        
        # Invalid ratio
        with pytest.raises(ValueError, match="Compression ratio must be between"):
            CompressionSettings(threshold=-20.0, ratio=25.0, attack_ms=5.0, release_ms=50.0)
        
        # Invalid attack
        with pytest.raises(ValueError, match="Compression attack must be between"):
            CompressionSettings(threshold=-20.0, ratio=4.0, attack_ms=150.0, release_ms=50.0)
        
        # Invalid release
        with pytest.raises(ValueError, match="Compression release must be between"):
            CompressionSettings(threshold=-20.0, ratio=4.0, attack_ms=5.0, release_ms=1500.0)
    
    def test_panning_settings_validation(self):
        """Test panning settings parameter validation"""
        # Valid settings should work
        pan = PanningSettings(panning_angle=30.0)
        assert pan.panning_angle == 30.0
        
        # Invalid panning angle
        with pytest.raises(ValueError, match="Panning angle must be between"):
            PanningSettings(panning_angle=75.0)
    
    def test_eq_presets(self):
        """Test EQ preset functions"""
        # Test bass boost preset
        bass_boost = EQSettings.preset_bass_boost()
        assert bass_boost.band_1 is not None
        assert bass_boost.band_1.gain > 0
        
        # Test vocal clarity preset
        vocal = EQSettings.preset_vocal_clarity()
        assert vocal.band_4 is not None
        assert vocal.band_4.gain > 0
        
        # Test kick punch preset
        kick = EQSettings.preset_kick_punch()
        assert kick.band_1 is not None
        
        # Test snare crack preset
        snare = EQSettings.preset_snare_crack()
        assert snare.band_5 is not None
        
        # Test high pass preset
        high_pass = EQSettings.preset_high_pass()
        assert high_pass.band_1 is not None
        assert high_pass.band_1.gain < 0
        
        # Test brightness preset
        bright = EQSettings.preset_brightness()
        assert bright.band_5 is not None
        assert bright.band_5.gain > 0
    
    def test_compression_presets(self):
        """Test compression preset functions"""
        # Test vocal preset
        vocal = CompressionSettings.preset_vocal()
        assert vocal.threshold == -18.0
        assert vocal.ratio == 4.0
        
        # Test drum bus preset
        drum_bus = CompressionSettings.preset_drum_bus()
        assert drum_bus.threshold == -15.0
        
        # Test bass preset
        bass = CompressionSettings.preset_bass()
        assert bass.ratio == 5.0
        
        # Test gentle preset
        gentle = CompressionSettings.preset_gentle()
        assert gentle.ratio < 3.0
        
        # Test aggressive preset
        aggressive = CompressionSettings.preset_aggressive()
        assert aggressive.ratio >= 8.0
    
    def test_panning_presets(self):
        """Test panning preset functions"""
        assert PanningSettings.center().panning_angle == 0.0
        assert PanningSettings.hard_left().panning_angle == -60.0
        assert PanningSettings.hard_right().panning_angle == 60.0
        assert PanningSettings.slight_left().panning_angle == -20.0
        assert PanningSettings.slight_right().panning_angle == 20.0


@pytest.mark.unit
class TestRetrieveFinalMixAdvanced:
    """Test retrieve_final_mix_advanced method"""
    
    def test_successful_advanced_final_mix(self, mock_api_provider):
        """Test successful advanced final mix with all effects"""
        # Setup
        mock_api_provider.post.return_value = {
            "applyAudioEffectsResults": {
                "download_url_mixed": "https://example.com/final_advanced.wav",
                "status": "FINAL_MIX_COMPLETE"
            }
        }
        
        controller = MixController(mock_api_provider)
        
        # Create track with all effects
        track_effects = TrackEffectsData(
            track_url="https://example.com/track.wav",
            gain_db=2.5,
            eq_settings=EQSettings(
                band_1=EQBandSettings(gain=3.0, q=1.0, centre_freq=80.0),
                band_4=EQBandSettings(gain=-2.0, q=1.5, centre_freq=2000.0)
            ),
            compression_settings=CompressionSettings(
                threshold=-18.0,
                ratio=4.0,
                attack_ms=5.0,
                release_ms=40.0
            ),
            panning_settings=PanningSettings(panning_angle=-30.0)
        )
        
        request = FinalMixRequestAdvanced(
            multitrack_task_id="task_123",
            track_data=[track_effects],
            return_stems=True,
            create_master=True,
            desired_loudness=DesiredLoudness.MEDIUM,
            webhook_url="https://example.com/webhook"
        )
        
        # Execute
        result = controller.retrieve_final_mix_advanced(request)
        
        # Assert
        assert result["download_url_mixed"] == "https://example.com/final_advanced.wav"
        
        # Verify payload structure
        payload = mock_api_provider.post.call_args[0][1]
        assert "applyAudioEffectsData" in payload
        aed = payload["applyAudioEffectsData"]
        
        # Check main fields
        assert aed["multitrackTaskId"] == "task_123"
        assert aed["returnStems"] is True
        assert aed["createMaster"] is True
        assert aed["desiredLoudness"] == "MEDIUM"
        assert aed["webhookURL"] == "https://example.com/webhook"
        
        # Check track data
        track_data = aed["trackData"][0]
        assert track_data["trackURL"] == "https://example.com/track.wav"
        assert track_data["gainDb"] == 2.5
        
        # Check EQ settings
        assert "eq_settings" in track_data
        eq = track_data["eq_settings"]
        assert "band_1" in eq
        assert eq["band_1"]["gain"] == 3.0
        assert eq["band_1"]["q"] == 1.0
        assert eq["band_1"]["centre_freq"] == 80.0
        assert "band_4" in eq
        
        # Check compression settings
        assert "compression_settings" in track_data
        comp = track_data["compression_settings"]
        assert comp["threshold"] == -18.0
        assert comp["ratio"] == 4.0
        assert comp["attack_ms"] == 5.0
        assert comp["release_ms"] == 40.0
        
        # Check panning settings
        assert "panning_settings" in track_data
        assert track_data["panning_settings"]["panning_angle"] == -30.0
    
    def test_advanced_final_mix_minimal_effects(self, mock_api_provider):
        """Test advanced final mix with minimal effects (only gain)"""
        # Setup
        mock_api_provider.post.return_value = {
            "applyAudioEffectsResults": {
                "download_url_mixed": "https://example.com/final.wav"
            }
        }
        
        controller = MixController(mock_api_provider)
        
        # Create track with only gain (no other effects)
        track = TrackEffectsData(
            track_url="https://example.com/track.wav",
            gain_db=1.0
        )
        
        request = FinalMixRequestAdvanced(
            multitrack_task_id="task_456",
            track_data=[track]
        )
        
        # Execute
        result = controller.retrieve_final_mix_advanced(request)
        
        # Verify payload
        payload = mock_api_provider.post.call_args[0][1]
        track_data = payload["applyAudioEffectsData"]["trackData"][0]
        
        # Should only have trackURL and gainDb
        assert track_data["trackURL"] == "https://example.com/track.wav"
        assert track_data["gainDb"] == 1.0
        assert "eq_settings" not in track_data
        assert "compression_settings" not in track_data
        assert "panning_settings" not in track_data
    
    def test_advanced_final_mix_with_presets(self, mock_api_provider):
        """Test advanced final mix using preset configurations"""
        # Setup
        mock_api_provider.post.return_value = {
            "applyAudioEffectsResults": {
                "download_url_mixed": "https://example.com/final_presets.wav"
            }
        }
        
        controller = MixController(mock_api_provider)
        
        # Create tracks with presets
        bass_track = TrackEffectsData(
            track_url="https://example.com/bass.wav",
            gain_db=1.5,
            eq_settings=EQSettings.preset_bass_boost(),
            compression_settings=CompressionSettings.preset_bass(),
            panning_settings=PanningSettings.center()
        )
        
        vocal_track = TrackEffectsData(
            track_url="https://example.com/vocals.wav",
            gain_db=-0.5,
            eq_settings=EQSettings.preset_vocal_clarity(),
            compression_settings=CompressionSettings.preset_vocal(),
            panning_settings=PanningSettings.center()
        )
        
        request = FinalMixRequestAdvanced(
            multitrack_task_id="task_789",
            track_data=[bass_track, vocal_track],
            return_stems=False,
            create_master=False
        )
        
        # Execute
        result = controller.retrieve_final_mix_advanced(request)
        
        # Verify payload has both tracks with effects
        payload = mock_api_provider.post.call_args[0][1]
        tracks = payload["applyAudioEffectsData"]["trackData"]
        assert len(tracks) == 2
        
        # Both tracks should have EQ and compression
        for track in tracks:
            assert "eq_settings" in track
            assert "compression_settings" in track
            assert "panning_settings" in track
    
    def test_advanced_final_mix_http_error(self, mock_api_provider):
        """Test error handling for advanced final mix"""
        # Setup
        mock_api_provider.post.side_effect = requests.HTTPError("API Error")
        
        controller = MixController(mock_api_provider)
        
        track = TrackEffectsData(
            track_url="https://example.com/track.wav",
            gain_db=0.0
        )
        
        request = FinalMixRequestAdvanced(
            multitrack_task_id="task_error",
            track_data=[track]
        )
        
        # Execute & Assert
        with pytest.raises(Exception, match="Failed to retrieve advanced final mix"):
            controller.retrieve_final_mix_advanced(request)
