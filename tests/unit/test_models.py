"""
Unit tests for data models and enums
"""

import pytest
from roex_python.models import (
    # Common models
    MusicalStyle, DesiredLoudness, InstrumentGroup,
    PresenceSetting, PanPreference, ReverbPreference,
    LoudnessPreference,
    
    # Mastering models
    MasteringRequest, MasteringTaskResponse, AlbumMasteringRequest,
    
    # Mixing models
    TrackData, MultitrackMixRequest, MultitrackTaskResponse,
    FinalMixRequest, TrackGainData,
    
    # Upload models
    UploadUrlRequest, UploadUrlResponse,
    
    # Analysis models
    MixAnalysisRequest, AnalysisMusicalStyle,
    
    # Enhance models
    MixEnhanceRequest, MixEnhanceResponse, EnhanceMusicalStyle
)

# Audio cleanup models are separate
from roex_python.models.audio_cleanup import AudioCleanupData, SoundSource


class TestCommonEnums:
    """Test common enum classes"""
    
    def test_musical_style_values(self):
        """Test MusicalStyle enum has expected values"""
        assert MusicalStyle.ROCK_INDIE.value == "ROCK_INDIE"
        assert MusicalStyle.POP.value == "POP"
        assert MusicalStyle.ACOUSTIC.value == "ACOUSTIC"
        assert MusicalStyle.HIPHOP_GRIME.value == "HIPHOP_GRIME"
        assert MusicalStyle.ELECTRONIC.value == "ELECTRONIC"
    
    def test_desired_loudness_values(self):
        """Test DesiredLoudness enum has expected values"""
        assert DesiredLoudness.LOW.value == "LOW"
        assert DesiredLoudness.MEDIUM.value == "MEDIUM"
        assert DesiredLoudness.HIGH.value == "HIGH"
    
    def test_instrument_group_values(self):
        """Test InstrumentGroup enum has expected values"""
        assert InstrumentGroup.BASS_GROUP.value == "BASS_GROUP"
        assert InstrumentGroup.VOCAL_GROUP.value == "VOCAL_GROUP"
        assert InstrumentGroup.DRUMS_GROUP.value == "DRUMS_GROUP"
        assert InstrumentGroup.KICK_GROUP.value == "KICK_GROUP"
    
    def test_presence_setting_values(self):
        """Test PresenceSetting enum"""
        assert PresenceSetting.NORMAL.value == "NORMAL"
        assert PresenceSetting.LEAD.value == "LEAD"
        assert PresenceSetting.BACKGROUND.value == "BACKGROUND"
    
    def test_pan_preference_values(self):
        """Test PanPreference enum"""
        assert PanPreference.NO_PREFERENCE.value == "NO_PREFERENCE"
        assert PanPreference.LEFT.value == "LEFT"
        assert PanPreference.CENTRE.value == "CENTRE"
        assert PanPreference.RIGHT.value == "RIGHT"
    
    def test_reverb_preference_values(self):
        """Test ReverbPreference enum"""
        assert ReverbPreference.NONE.value == "NONE"
        assert ReverbPreference.LOW.value == "LOW"
        assert ReverbPreference.MEDIUM.value == "MEDIUM"
        assert ReverbPreference.HIGH.value == "HIGH"


class TestMasteringModels:
    """Test mastering-related models"""
    
    def test_mastering_request_creation(self):
        """Test creating a MasteringRequest with required fields"""
        request = MasteringRequest(
            track_url="https://example.com/track.wav",
            musical_style=MusicalStyle.POP,
            desired_loudness=DesiredLoudness.MEDIUM
        )
        
        assert request.track_url == "https://example.com/track.wav"
        assert request.musical_style == MusicalStyle.POP
        assert request.desired_loudness == DesiredLoudness.MEDIUM
        assert request.sample_rate == "44100"  # Default value
        assert request.webhook_url is None  # Default value
    
    def test_mastering_request_with_optional_fields(self):
        """Test MasteringRequest with optional fields"""
        request = MasteringRequest(
            track_url="https://example.com/track.wav",
            musical_style=MusicalStyle.ROCK_INDIE,
            desired_loudness=DesiredLoudness.HIGH,
            sample_rate="48000",
            webhook_url="https://example.com/webhook"
        )
        
        assert request.sample_rate == "48000"
        assert request.webhook_url == "https://example.com/webhook"
    
    def test_mastering_task_response(self):
        """Test MasteringTaskResponse model"""
        response = MasteringTaskResponse(mastering_task_id="task_123")
        assert response.mastering_task_id == "task_123"
    
    def test_album_mastering_request(self):
        """Test AlbumMasteringRequest with multiple tracks"""
        tracks = [
            MasteringRequest(
                track_url="https://example.com/track1.wav",
                musical_style=MusicalStyle.POP,
                desired_loudness=DesiredLoudness.MEDIUM
            ),
            MasteringRequest(
                track_url="https://example.com/track2.wav",
                musical_style=MusicalStyle.POP,
                desired_loudness=DesiredLoudness.MEDIUM
            )
        ]
        
        album_request = AlbumMasteringRequest(tracks=tracks)
        assert len(album_request.tracks) == 2


class TestMixingModels:
    """Test mixing-related models"""
    
    def test_track_data_creation(self):
        """Test creating a TrackData instance"""
        track = TrackData(
            track_url="https://example.com/bass.wav",
            instrument_group=InstrumentGroup.BASS_GROUP,
            presence_setting=PresenceSetting.NORMAL,
            pan_preference=PanPreference.CENTRE,
            reverb_preference=ReverbPreference.LOW
        )
        
        assert track.track_url == "https://example.com/bass.wav"
        assert track.instrument_group == InstrumentGroup.BASS_GROUP
        assert track.presence_setting == PresenceSetting.NORMAL
    
    def test_multitrack_mix_request(self):
        """Test MultitrackMixRequest creation"""
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
            musical_style=MusicalStyle.POP,
            return_stems=True
        )
        
        assert len(request.track_data) == 2
        assert request.musical_style == MusicalStyle.POP
        assert request.return_stems is True
    
    def test_multitrack_task_response(self):
        """Test MultitrackTaskResponse"""
        response = MultitrackTaskResponse(multitrack_task_id="mix_123")
        assert response.multitrack_task_id == "mix_123"
    
    def test_track_gain_data(self):
        """Test TrackGainData model"""
        gain_data = TrackGainData(
            track_url="https://example.com/track.wav",
            gain_db=3.5
        )
        
        assert gain_data.track_url == "https://example.com/track.wav"
        assert gain_data.gain_db == 3.5
    
    def test_final_mix_request(self):
        """Test FinalMixRequest creation"""
        track_data = [
            TrackGainData(
                track_url="https://example.com/track1.wav",
                gain_db=2.0
            )
        ]
        
        request = FinalMixRequest(
            multitrack_task_id="mix_123",
            track_data=track_data
        )
        
        assert request.multitrack_task_id == "mix_123"
        assert len(request.track_data) == 1


class TestUploadModels:
    """Test upload-related models"""
    
    def test_upload_url_request(self):
        """Test UploadUrlRequest creation"""
        request = UploadUrlRequest(
            filename="track.wav",
            content_type="audio/wav"
        )
        
        assert request.filename == "track.wav"
        assert request.content_type == "audio/wav"
    
    def test_upload_url_response(self):
        """Test UploadUrlResponse creation"""
        response = UploadUrlResponse(
            signed_url="https://signed.example.com/upload",
            readable_url="https://example.com/track.wav",
            error=False,
            message="Success"
        )
        
        assert response.signed_url == "https://signed.example.com/upload"
        assert response.readable_url == "https://example.com/track.wav"
        assert response.error is False


class TestAnalysisModels:
    """Test analysis-related models"""
    
    def test_mix_analysis_request(self):
        """Test MixAnalysisRequest creation"""
        request = MixAnalysisRequest(
            audio_file_location="https://example.com/track.wav",
            musical_style=AnalysisMusicalStyle.POP,
            is_master=False
        )
        
        assert request.audio_file_location == "https://example.com/track.wav"
        assert request.musical_style == AnalysisMusicalStyle.POP
        assert request.is_master is False


class TestEnhanceModels:
    """Test enhancement-related models"""
    
    def test_mix_enhance_request_defaults(self):
        """Test MixEnhanceRequest with default values"""
        request = MixEnhanceRequest(
            audio_file_location="https://example.com/track.wav",
            musical_style=MusicalStyle.POP
        )
        
        assert request.audio_file_location == "https://example.com/track.wav"
        assert request.musical_style == MusicalStyle.POP
        assert request.is_master is False
        assert request.fix_clipping_issues is True
        assert request.loudness_preference == LoudnessPreference.STREAMING_LOUDNESS
    
    def test_mix_enhance_request_custom_values(self):
        """Test MixEnhanceRequest with custom values"""
        request = MixEnhanceRequest(
            audio_file_location="https://example.com/track.wav",
            musical_style=MusicalStyle.ROCK_INDIE,
            is_master=True,
            fix_clipping_issues=False,
            fix_drc_issues=False,
            apply_mastering=True
        )
        
        assert request.is_master is True
        assert request.fix_clipping_issues is False
        assert request.apply_mastering is True
    
    def test_mix_enhance_response(self):
        """Test MixEnhanceResponse creation"""
        response = MixEnhanceResponse(
            mixrevive_task_id="enhance_123",
            error=False,
            message="Success"
        )
        
        assert response.mixrevive_task_id == "enhance_123"
        assert response.error is False


class TestAudioCleanupModels:
    """Test audio cleanup models"""
    
    def test_audio_cleanup_data(self):
        """Test AudioCleanupData creation"""
        data = AudioCleanupData(
            audio_file_location="https://example.com/vocals.wav",
            sound_source=SoundSource.VOCAL_GROUP
        )
        
        assert data.audio_file_location == "https://example.com/vocals.wav"
        assert data.sound_source == SoundSource.VOCAL_GROUP
    
    def test_sound_source_enum(self):
        """Test SoundSource enum values"""
        assert SoundSource.VOCAL_GROUP.value == "VOCAL_GROUP"
        assert SoundSource.E_GUITAR_GROUP.value == "E_GUITAR_GROUP"
        assert SoundSource.ACOUSTIC_GUITAR_GROUP.value == "ACOUSTIC_GUITAR_GROUP"


@pytest.mark.unit
class TestModelEdgeCases:
    """Test edge cases and validation"""
    
    def test_empty_track_list_allowed(self):
        """Test that empty track lists are allowed (validation happens at API level)"""
        request = MultitrackMixRequest(
            track_data=[],
            musical_style=MusicalStyle.POP
        )
        
        assert len(request.track_data) == 0
    
    def test_optional_webhook_url(self):
        """Test that webhook_url can be None"""
        request = MasteringRequest(
            track_url="https://example.com/track.wav",
            musical_style=MusicalStyle.POP,
            desired_loudness=DesiredLoudness.MEDIUM,
            webhook_url=None
        )
        
        assert request.webhook_url is None
