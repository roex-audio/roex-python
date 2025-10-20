"""
Integration tests for mastering functionality
Requires: ROEX_API_KEY environment variable and test audio files
"""

import pytest
import os
import time
from roex_python.client import RoExClient
from roex_python.models import MasteringRequest, MusicalStyle, DesiredLoudness


@pytest.mark.integration
@pytest.mark.slow
class TestMasteringIntegration:
    """Integration tests for mastering operations"""
    
    def test_complete_mastering_workflow(self, requires_api_key, integration_audio_file):
        """
        Test complete mastering workflow:
        1. Upload file
        2. Create mastering preview
        3. Retrieve preview
        4. Retrieve final master
        """
        # Setup
        client = RoExClient(api_key=requires_api_key)
        
        # Upload file
        from roex_python.utils import upload_file
        track_url = upload_file(client, integration_audio_file)
        assert track_url is not None
        print(f"Uploaded track: {track_url}")
        
        # Create mastering request
        mastering_request = MasteringRequest(
            track_url=track_url,
            musical_style=MusicalStyle.POP,
            desired_loudness=DesiredLoudness.MEDIUM,
            sample_rate="44100",
            webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
        )
        
        # Create mastering preview
        task = client.mastering.create_mastering_preview(mastering_request)
        assert task.mastering_task_id is not None
        print(f"Created mastering task: {task.mastering_task_id}")
        
        # Retrieve preview master (with polling)
        preview = client.mastering.retrieve_preview_master(
            task.mastering_task_id,
            max_attempts=30,
            poll_interval=5
        )
        assert "download_url_mastered_preview" in preview
        print(f"Preview ready: {preview.get('download_url_mastered_preview')}")
        
        # Retrieve final master
        final_url = client.mastering.retrieve_final_master(task.mastering_task_id)
        assert final_url is not None
        print(f"Final master URL: {final_url}")
    
    def test_mastering_different_styles(self, requires_api_key, integration_audio_file):
        """Test mastering with different musical styles"""
        client = RoExClient(api_key=requires_api_key)
        
        from roex_python.utils import upload_file
        track_url = upload_file(client, integration_audio_file)
        
        # Test with ROCK_INDIE style
        request = MasteringRequest(
            track_url=track_url,
            musical_style=MusicalStyle.ROCK_INDIE,
            desired_loudness=DesiredLoudness.HIGH,
            webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
        )
        
        task = client.mastering.create_mastering_preview(request)
        assert task.mastering_task_id is not None
        print(f"Created mastering task with ROCK_INDIE style: {task.mastering_task_id}")
    
    def test_mastering_with_webhook(self, requires_api_key, integration_audio_file):
        """Test mastering with webhook URL (optional)"""
        # Note: This test creates a task with webhook but doesn't verify webhook delivery
        client = RoExClient(api_key=requires_api_key)
        
        from roex_python.utils import upload_file
        track_url = upload_file(client, integration_audio_file)
        
        request = MasteringRequest(
            track_url=track_url,
            musical_style=MusicalStyle.POP,
            desired_loudness=DesiredLoudness.MEDIUM,
            webhook_url="https://webhook.site/unique-id"  # Replace with real webhook
        )
        
        task = client.mastering.create_mastering_preview(request)
        assert task.mastering_task_id is not None
