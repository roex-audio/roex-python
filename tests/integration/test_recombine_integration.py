"""
Integration tests for stem recombination ("Recombine") functionality
Requires: ROEX_API_KEY environment variable and test audio files

Note: Retrieving the final master via `retrieve_final_master` charges 250
real credits the first time it succeeds for a task (recombine submission
itself is free). Running the full separate-then-recombine workflow costs
75 + 250 = 325 credits total. These tests are skipped by default -- remove
the `@pytest.mark.skip` decorator to run them manually.
"""

import pytest
from roex_python.client import RoExClient
from roex_python.models import (
    StemSeparationRequest, RecombineRequest, RecombineMusicalStyle, DesiredLoudness
)
from roex_python.utils import upload_file


@pytest.mark.integration
@pytest.mark.slow
class TestRecombineIntegration:
    """Integration tests for stem recombination operations"""

    @pytest.mark.skip(
        reason="Requires a completed separation job and charges 250 real "
        "credits on final retrieval -- manual test only"
    )
    def test_recombine_via_stem_job_id_workflow(self, requires_api_key, integration_audio_file):
        """
        Test the full separate -> recombine (via stemJobId) -> preview -> final workflow.
        """
        client = RoExClient(api_key=requires_api_key)

        track_url = upload_file(client, integration_audio_file)

        separation_task = client.stem_separation.create_separation(
            StemSeparationRequest(audio_file_location=track_url)
        )
        client.stem_separation.wait_for_separation(
            separation_task.stemflow_task_id, poll_interval=15, timeout=1200
        )
        print(f"Separation complete: {separation_task.stemflow_task_id}")

        recombine_task = client.recombine.create_recombine(
            RecombineRequest(
                stem_job_id=separation_task.stemflow_task_id,
                musical_style=RecombineMusicalStyle.POP,
                desired_loudness=DesiredLoudness.MEDIUM,
            )
        )
        assert recombine_task.recombine_task_id
        print(f"Recombine task created: {recombine_task.recombine_task_id}")

        client.recombine.wait_for_recombine(
            recombine_task.recombine_task_id, poll_interval=10, timeout=600
        )

        preview = client.recombine.retrieve_preview(recombine_task.recombine_task_id)
        assert preview.preview_url is not None
        print(f"Preview ready: {preview.preview_url}")

        final_result = client.recombine.retrieve_final_master(recombine_task.recombine_task_id)
        assert final_result.master_url is not None
        print(f"Final master ready: {final_result.master_url}")

    @pytest.mark.skip(
        reason="Charges 250 real credits on final retrieval -- manual test only"
    )
    def test_recombine_via_direct_urls_workflow(self, requires_api_key, integration_audio_file):
        """
        Test recombining directly from a vocal URL + backing URL, bypassing
        stem separation entirely (uses the same fixture file for both, which
        is not musically meaningful but exercises the API contract).
        """
        client = RoExClient(api_key=requires_api_key)

        vocal_url = upload_file(client, integration_audio_file)
        backing_url = upload_file(client, integration_audio_file)

        recombine_task = client.recombine.create_recombine(
            RecombineRequest(
                vocal_stem_url=vocal_url,
                backing_stem_url=backing_url,
                musical_style=RecombineMusicalStyle.HIPHOP_GRIME,
                vocal_gain_db=1.5,
            )
        )
        assert recombine_task.recombine_task_id

        client.recombine.wait_for_recombine(
            recombine_task.recombine_task_id, poll_interval=10, timeout=600
        )

        final_result = client.recombine.retrieve_final_master(recombine_task.recombine_task_id)
        assert final_result.master_url is not None
        assert final_result.processing.vocal_gain_db == 1.5
