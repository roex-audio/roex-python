"""
Integration tests for mixing functionality
Requires: ROEX_API_KEY environment variable and multiple test audio files
"""

import pytest
from roex_python.client import RoExClient
from roex_python.models import (
    MultitrackMixRequest, TrackData, InstrumentGroup,
    PresenceSetting, PanPreference, ReverbPreference, MusicalStyle,
    FinalMixRequestAdvanced, TrackEffectsData, EQSettings,
    CompressionSettings, PanningSettings
)
from roex_python.utils import upload_file


@pytest.mark.integration
@pytest.mark.slow
class TestMixIntegration:
    """Integration tests for mixing operations"""
    
    @pytest.mark.skip(reason="Requires multiple audio files - manual test only")
    def test_multitrack_mix_workflow(self, requires_api_key, integration_audio_file):
        """
        Test complete multitrack mixing workflow
        Note: This test requires multiple audio files for a realistic mix
        """
        client = RoExClient(api_key=requires_api_key)
        
        # Upload multiple tracks
        # In a real test, you'd have separate bass, vocals, drums files
        bass_url = upload_file(client, integration_audio_file)
        vocals_url = bass_url  # Using same file for demo
        
        print(f"Uploaded tracks")
        
        # Create track data
        tracks = [
            TrackData(
                track_url=bass_url,
                instrument_group=InstrumentGroup.BASS_GROUP,
                presence_setting=PresenceSetting.NORMAL,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.NONE
            ),
            TrackData(
                track_url=vocals_url,
                instrument_group=InstrumentGroup.VOCAL_GROUP,
                presence_setting=PresenceSetting.LEAD,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.LOW
            )
        ]
        
        # Create mix request
        mix_request = MultitrackMixRequest(
            track_data=tracks,
            musical_style=MusicalStyle.POP,
            return_stems=False,
            webhook_url="https://webhook-test-786984745538.europe-west1.run.app"  # Test webhook
        )
        
        # Create mix preview
        mix_task = client.mix.create_mix_preview(mix_request)
        assert mix_task.multitrack_task_id is not None
        print(f"Mix task created: {mix_task.multitrack_task_id}")
        
        # Retrieve preview (with polling)
        preview = client.mix.retrieve_preview_mix(
            mix_task.multitrack_task_id,
            max_attempts=20,
            poll_interval=5
        )
        assert preview is not None
        print(f"Mix preview ready")
    
    @pytest.mark.skip(reason="Requires multiple audio files - manual test only")
    def test_advanced_audio_effects_workflow(self, requires_api_key, integration_audio_file):
        """
        Test complete multitrack mixing workflow with advanced audio effects
        Note: This test requires multiple audio files for a realistic mix
        """
        client = RoExClient(api_key=requires_api_key)
        
        # Upload tracks
        bass_url = upload_file(client, integration_audio_file)
        vocals_url = bass_url  # Using same file for demo
        
        print(f"Uploaded tracks for advanced effects test")
        
        # Create track data for preview
        tracks = [
            TrackData(
                track_url=bass_url,
                instrument_group=InstrumentGroup.BASS_GROUP,
                presence_setting=PresenceSetting.NORMAL,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.NONE
            ),
            TrackData(
                track_url=vocals_url,
                instrument_group=InstrumentGroup.VOCAL_GROUP,
                presence_setting=PresenceSetting.LEAD,
                pan_preference=PanPreference.CENTRE,
                reverb_preference=ReverbPreference.LOW
            )
        ]
        
        # Create mix preview
        mix_request = MultitrackMixRequest(
            track_data=tracks,
            musical_style=MusicalStyle.POP,
            return_stems=False,
            webhook_url="https://webhook-test-786984745538.europe-west1.run.app"  # Test webhook
        )
        
        mix_task = client.mix.create_mix_preview(mix_request)
        assert mix_task.multitrack_task_id is not None
        print(f"Mix preview task created: {mix_task.multitrack_task_id}")
        
        # Retrieve preview
        preview = client.mix.retrieve_preview_mix(
            mix_task.multitrack_task_id,
            max_attempts=20,
            poll_interval=5
        )
        assert preview is not None
        print(f"Preview ready, now applying advanced effects")
        
        # Apply advanced audio effects for final mix
        bass_effects = TrackEffectsData(
            track_url=bass_url,
            gain_db=2.0,
            eq_settings=EQSettings.preset_bass_boost(),
            compression_settings=CompressionSettings.preset_bass(),
            panning_settings=PanningSettings.center()
        )
        
        vocal_effects = TrackEffectsData(
            track_url=vocals_url,
            gain_db=-0.5,
            eq_settings=EQSettings.preset_vocal_clarity(),
            compression_settings=CompressionSettings.preset_vocal(),
            panning_settings=PanningSettings.center()
        )
        
        # Request final mix with effects
        final_mix_request = FinalMixRequestAdvanced(
            multitrack_task_id=mix_task.multitrack_task_id,
            track_data=[bass_effects, vocal_effects],
            return_stems=False,
            create_master=False
        )
        
        final_mix = client.mix.retrieve_final_mix_advanced(final_mix_request)
        assert final_mix is not None
        assert 'download_url_mixed' in final_mix or 'download_url_final_mix' in final_mix
        print(f"Advanced final mix ready with EQ, compression, and panning applied")
