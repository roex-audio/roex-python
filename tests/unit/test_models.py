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
    MixEnhanceRequest, MixEnhanceResponse, EnhanceMusicalStyle,

    # StemFlow (stem separation) models
    StemSeparationRequest, StemSeparationTaskResponse,
    StemSeparationStatusResult, SeparatedStemsResult,

    # Recombine models
    RecombineMusicalStyle, RecombineRequest, RecombineTaskResponse,
    RecombineStatusResult, RecombinePreviewResult, RecombineFinalResult,
    RecombineProcessingInfo
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
    
    def test_loudness_preference_no_change(self):
        """Test LoudnessPreference enum includes NO_CHANGE"""
        assert LoudnessPreference.NO_CHANGE.value == "NO_CHANGE"
    
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
    
    def test_analysis_musical_style_has_mood_styles(self):
        """Test AnalysisMusicalStyle includes all 9 mood-based styles"""
        mood_styles = [
            "AIRY_EXPANSIVE", "AGGRESSIVE", "BRIGHT", "GRITTY_CRUNCHY",
            "MELLOW_SMOOTH", "SHARP_BASSY", "THUMPING_BOOMY", "WARM", "BALANCED"
        ]
        member_values = [m.value for m in AnalysisMusicalStyle]
        for style in mood_styles:
            assert style in member_values, f"{style} missing from AnalysisMusicalStyle"
    
    def test_analysis_musical_style_no_dance(self):
        """Test AnalysisMusicalStyle does not include DANCE"""
        member_names = [m.name for m in AnalysisMusicalStyle]
        assert "DANCE" not in member_names


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
        assert request.loudness_preference == LoudnessPreference.NO_CHANGE
    
    def test_mix_enhance_request_custom_values(self):
        """Test MixEnhanceRequest with custom values"""
        request = MixEnhanceRequest(
            audio_file_location="https://example.com/track.wav",
            musical_style=MusicalStyle.ROCK_INDIE,
            is_master=True,
            fix_clipping_issues=False,
            apply_mastering=True
        )
        
        assert request.is_master is True
        assert request.fix_clipping_issues is False
        assert request.apply_mastering is True
    
    def test_enhance_musical_style_values(self):
        """Test EnhanceMusicalStyle enum has all correct server values"""
        expected = [
            "ROCK_INDIE", "POP", "ACOUSTIC", "HIPHOP_GRIME", "ELECTRONIC",
            "REGGAE_DUB", "ORCHESTRAL", "METAL", "OTHER", "GRITTY_CRUNCHY",
            "BRIGHT", "WARM", "SHARP_BASSY", "THUMPING_BOOMY", "MELLOW_SMOOTH",
            "AIRY_EXPANSIVE", "AGGRESSIVE", "BALANCED"
        ]
        member_values = [m.value for m in EnhanceMusicalStyle]
        assert sorted(member_values) == sorted(expected)
    
    def test_mix_enhance_request_get_processed_stems(self):
        """Test get_processed_stems defaults to False and can be set to True"""
        request_default = MixEnhanceRequest(
            audio_file_location="https://example.com/track.wav",
            musical_style=MusicalStyle.POP
        )
        assert request_default.get_processed_stems is False
        
        request_enabled = MixEnhanceRequest(
            audio_file_location="https://example.com/track.wav",
            musical_style=MusicalStyle.POP,
            get_processed_stems=True
        )
        assert request_enabled.get_processed_stems is True
    
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
    
    def test_sound_source_backing_vox(self):
        """Test SoundSource has BACKING_VOX_GROUP (not BACKING_VOCALS_GROUP)"""
        assert SoundSource.BACKING_VOX_GROUP.value == "BACKING_VOX_GROUP"
        member_names = [m.name for m in SoundSource]
        assert "BACKING_VOCALS_GROUP" not in member_names
    
    def test_sound_source_brass(self):
        """Test SoundSource includes BRASS_GROUP"""
        assert SoundSource.BRASS_GROUP.value == "BRASS_GROUP"


class TestStemFlowModels:
    """Test stem separation ("StemFlow") models"""

    def test_stem_separation_request(self):
        """Test StemSeparationRequest creation"""
        request = StemSeparationRequest(audio_file_location="https://example.com/song.wav")
        assert request.audio_file_location == "https://example.com/song.wav"
        assert request.separation_mode is None
        assert request.webhook_url is None

    def test_stem_separation_request_with_mode_and_webhook(self):
        """Test StemSeparationRequest with separation_mode and webhook_url"""
        request = StemSeparationRequest(
            audio_file_location="https://example.com/song.wav",
            separation_mode="vocals_instrumental",
            webhook_url="https://example.com/hook",
        )
        assert request.separation_mode == "vocals_instrumental"
        assert request.webhook_url == "https://example.com/hook"

    def test_stem_separation_task_response_defaults(self):
        """Test StemSeparationTaskResponse defaults"""
        response = StemSeparationTaskResponse(stemflow_task_id="sf_task_123")
        assert response.stemflow_task_id == "sf_task_123"
        assert response.error is False
        assert response.message == ""

    def test_stem_separation_status_result(self):
        """Test StemSeparationStatusResult creation"""
        result = StemSeparationStatusResult(
            stemflow_task_id="sf_task_123",
            status="failed",
            error=True,
            info="worker crashed"
        )
        assert result.status == "failed"
        assert result.error is True
        assert result.info == "worker crashed"

    def test_separated_stems_result_defaults(self):
        """Test SeparatedStemsResult defaults to all-None"""
        result = SeparatedStemsResult()
        assert result.vocals is None
        assert result.instrumental is None
        assert result.bass is None
        assert result.drums is None
        assert result.other is None

    def test_separated_stems_result_with_urls(self):
        """Test SeparatedStemsResult with all four stem URLs set"""
        result = SeparatedStemsResult(
            vocals="https://example.com/vocals.wav",
            bass="https://example.com/bass.wav",
            drums="https://example.com/drums.wav",
            other="https://example.com/other.wav"
        )
        assert result.vocals == "https://example.com/vocals.wav"
        assert result.bass == "https://example.com/bass.wav"
        assert result.drums == "https://example.com/drums.wav"
        assert result.other == "https://example.com/other.wav"

    def test_separated_stems_result_with_instrumental(self):
        """Test SeparatedStemsResult with the instrumental (2-stem) URL"""
        result = SeparatedStemsResult(
            vocals="https://example.com/vocals.wav",
            instrumental="https://example.com/no_vocals.wav",
        )
        assert result.vocals == "https://example.com/vocals.wav"
        assert result.instrumental == "https://example.com/no_vocals.wav"


class TestRecombineModels:
    """Test stem recombination ("Recombine") models"""

    def test_recombine_musical_style_has_all_20_values(self):
        """Test RecombineMusicalStyle includes the wider style set beyond MusicalStyle"""
        expected = [
            "ROCK_INDIE", "POP", "ACOUSTIC", "HIPHOP_GRIME", "ELECTRONIC",
            "REGGAE_DUB", "ORCHESTRAL", "METAL", "OTHER", "JAZZ", "LO_FI",
            "LATIN", "TECHNO", "HOUSE", "TRAP", "COUNTRY_ACOUSTIC",
            "CINEMATIC", "AFROBEAT", "K_POP", "REGGAETON"
        ]
        member_values = [m.value for m in RecombineMusicalStyle]
        assert sorted(member_values) == sorted(expected)
        assert len(member_values) == 20

    def test_recombine_request_via_stem_job_id(self):
        """Test RecombineRequest with stem_job_id and default loudness/gain"""
        request = RecombineRequest(
            stem_job_id="sf_task_123",
            musical_style=RecombineMusicalStyle.POP
        )
        assert request.stem_job_id == "sf_task_123"
        assert request.vocal_stem_url is None
        assert request.backing_stem_url is None
        assert request.desired_loudness == DesiredLoudness.MEDIUM
        assert request.vocal_gain_db == 0.0
        assert request.webhook_url is None

    def test_recombine_request_with_webhook_url(self):
        """Test RecombineRequest with an optional webhook_url"""
        request = RecombineRequest(
            stem_job_id="sf_task_123",
            musical_style=RecombineMusicalStyle.POP,
            webhook_url="https://example.com/hook"
        )
        assert request.webhook_url == "https://example.com/hook"

    def test_recombine_request_via_direct_urls(self):
        """Test RecombineRequest with direct vocal + backing URLs"""
        request = RecombineRequest(
            vocal_stem_url="https://example.com/vocal.wav",
            backing_stem_url="https://example.com/backing.wav",
            musical_style=RecombineMusicalStyle.TRAP,
            desired_loudness=DesiredLoudness.HIGH,
            vocal_gain_db=-4.5
        )
        assert request.stem_job_id is None
        assert request.vocal_stem_url == "https://example.com/vocal.wav"
        assert request.backing_stem_url == "https://example.com/backing.wav"
        assert request.vocal_gain_db == -4.5

    def test_recombine_request_rejects_neither_mode(self):
        """Test that RecombineRequest requires either stem_job_id or both URLs"""
        with pytest.raises(ValueError):
            RecombineRequest(musical_style=RecombineMusicalStyle.POP)

    def test_recombine_request_rejects_both_modes(self):
        """Test that RecombineRequest rejects stem_job_id combined with direct URLs"""
        with pytest.raises(ValueError):
            RecombineRequest(
                stem_job_id="sf_task_123",
                vocal_stem_url="https://example.com/vocal.wav",
                backing_stem_url="https://example.com/backing.wav",
                musical_style=RecombineMusicalStyle.POP
            )

    def test_recombine_request_rejects_out_of_range_gain(self):
        """Test that vocal_gain_db outside -6.0..+6.0 is rejected"""
        with pytest.raises(ValueError):
            RecombineRequest(
                stem_job_id="sf_task_123",
                musical_style=RecombineMusicalStyle.POP,
                vocal_gain_db=10.0
            )

    def test_recombine_task_response(self):
        """Test RecombineTaskResponse creation"""
        response = RecombineTaskResponse(recombine_task_id="rc_task_123")
        assert response.recombine_task_id == "rc_task_123"
        assert response.error is False

    def test_recombine_status_result(self):
        """Test RecombineStatusResult creation"""
        result = RecombineStatusResult(
            recombine_task_id="rc_task_123",
            status="complete"
        )
        assert result.status == "complete"

    def test_recombine_preview_result(self):
        """Test RecombinePreviewResult creation"""
        result = RecombinePreviewResult(
            preview_url="https://example.com/preview.mp3",
            preview_start_seconds=42.5,
            measured_lufs_full=-13.4
        )
        assert result.preview_url == "https://example.com/preview.mp3"
        assert result.preview_start_seconds == 42.5
        assert result.measured_lufs_full == -13.4

    def test_recombine_final_result_with_processing(self):
        """Test RecombineFinalResult with nested processing info"""
        result = RecombineFinalResult(
            master_url="https://example.com/master.wav",
            measured_lufs=-13.4,
            processing=RecombineProcessingInfo(
                musical_style="POP",
                desired_loudness="MEDIUM",
                vocal_gain_db=0.0
            )
        )
        assert result.master_url == "https://example.com/master.wav"
        assert result.processing.musical_style == "POP"
        assert result.processing.vocal_gain_db == 0.0

    def test_recombine_final_result_defaults(self):
        """Test RecombineFinalResult defaults to all-None"""
        result = RecombineFinalResult()
        assert result.master_url is None
        assert result.processing is None


@pytest.mark.unit
class TestModelEdgeCases:
    """Test edge cases and validation"""
    
    def test_empty_track_list_rejected(self):
        """Test that empty track lists are rejected by validation (2-32 required)"""
        with pytest.raises(ValueError, match="must contain between 2 and 32 tracks"):
            MultitrackMixRequest(
                track_data=[],
                musical_style=MusicalStyle.POP
            )
    
    def test_optional_webhook_url(self):
        """Test that webhook_url can be None"""
        request = MasteringRequest(
            track_url="https://example.com/track.wav",
            musical_style=MusicalStyle.POP,
            desired_loudness=DesiredLoudness.MEDIUM,
            webhook_url=None
        )
        
        assert request.webhook_url is None
