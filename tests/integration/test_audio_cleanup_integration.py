"""
Integration tests for audio cleanup functionality
Requires: ROEX_API_KEY environment variable and test audio files
"""

import pytest
from roex_python.client import RoExClient
from roex_python.models.audio_cleanup import AudioCleanupData, SoundSource
from roex_python.utils import upload_file


@pytest.mark.integration
@pytest.mark.slow
class TestAudioCleanupIntegration:
    """Integration tests for audio cleanup operations"""
    
    @pytest.mark.skip(reason="Cleanup can take several minutes - manual test only")
    def test_audio_cleanup_workflow(self, requires_api_key, integration_audio_file):
        """
        Test complete audio cleanup workflow
        Note: This test can take several minutes
        """
        client = RoExClient(api_key=requires_api_key)
        
        # Upload file
        track_url = upload_file(client, integration_audio_file)
        print(f"Uploaded track: {track_url[:60]}...")
        
        # Create cleanup request
        cleanup_data = AudioCleanupData(
            audio_file_location=track_url,
            sound_source=SoundSource.VOCAL_GROUP
        )
        
        # Clean up audio
        result = client.audio_cleanup.clean_up_audio(cleanup_data)
        
        assert result is not None
        assert result.error is False
        
        if result.audio_cleanup_results:
            print(f"Cleanup complete")
            if result.audio_cleanup_results.cleaned_audio_file_location:
                print(f"Cleaned audio: {result.audio_cleanup_results.cleaned_audio_file_location[:60]}...")
        else:
            print(f"Cleanup initiated (async)")
