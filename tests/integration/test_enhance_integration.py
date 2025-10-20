"""
Integration tests for enhancement functionality
Requires: ROEX_API_KEY environment variable and test audio files
"""

import pytest
from roex_python.client import RoExClient
from roex_python.models import MixEnhanceRequest, MusicalStyle
from roex_python.utils import upload_file


@pytest.mark.integration
@pytest.mark.slow
class TestEnhanceIntegration:
    """Integration tests for enhancement operations"""
    
    @pytest.mark.skip(reason="Enhancement can take 5+ minutes - manual test only")
    def test_mix_enhancement_workflow(self, requires_api_key, integration_audio_file):
        """
        Test complete mix enhancement workflow
        Note: This test takes a long time (5-10 minutes)
        """
        client = RoExClient(api_key=requires_api_key)
        
        # Upload file
        track_url = upload_file(client, integration_audio_file)
        print(f"Uploaded track: {track_url[:60]}...")
        
        # Create enhancement request
        enhance_request = MixEnhanceRequest(
            audio_file_location=track_url,
            musical_style=MusicalStyle.POP,
            is_master=False,
            fix_clipping_issues=True,
            fix_loudness_issues=True,
            apply_mastering=False,
            webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
        )
        
        # Create enhancement preview
        task = client.enhance.create_mix_enhance_preview(enhance_request)
        assert task.mixrevive_task_id is not None
        assert task.error is False
        print(f"Enhancement task created: {task.mixrevive_task_id}")
        
        # Retrieve enhanced track (with polling)
        enhanced = client.enhance.retrieve_enhanced_track(
            task.mixrevive_task_id,
            max_attempts=50,
            poll_interval=10
        )
        assert enhanced is not None
        print(f"Enhanced track ready")
