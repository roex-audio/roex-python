"""
Integration tests for stem separation ("StemFlow") functionality
Requires: ROEX_API_KEY environment variable and test audio files

Note: Submitting a separation task reserves 75 credits (captured on
success, refunded on failure) from the account tied to ROEX_API_KEY.
These tests are skipped by default -- remove the `@pytest.mark.skip`
decorator to run them manually.
"""

import pytest
from roex_python.client import RoExClient
from roex_python.models import StemSeparationRequest
from roex_python.utils import upload_file


@pytest.mark.integration
@pytest.mark.slow
class TestStemFlowIntegration:
    """Integration tests for stem separation operations"""

    @pytest.mark.skip(
        reason="Separation runs on a GPU worker and can take several minutes "
        "including cold start, and reserves 75 real credits -- manual test only"
    )
    def test_stem_separation_workflow(self, requires_api_key, integration_audio_file):
        """
        Test complete stem separation workflow:
        1. Upload file
        2. Submit separation task
        3. Wait for completion
        4. Retrieve stem URLs
        """
        client = RoExClient(api_key=requires_api_key)

        track_url = upload_file(client, integration_audio_file)
        print(f"Uploaded track: {track_url[:60]}...")

        task = client.stem_separation.create_separation(
            StemSeparationRequest(audio_file_location=track_url)
        )
        assert task.stemflow_task_id
        assert task.error is False
        print(f"Separation task created: {task.stemflow_task_id}")

        client.stem_separation.wait_for_separation(
            task.stemflow_task_id, poll_interval=15, timeout=1200
        )

        stems = client.stem_separation.retrieve_stems(task.stemflow_task_id)
        assert stems.vocals is not None
        assert stems.bass is not None
        assert stems.drums is not None
        assert stems.other is not None
        print("Stems retrieved successfully")
