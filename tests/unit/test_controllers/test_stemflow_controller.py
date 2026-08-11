"""
Unit tests for StemFlowController
"""

import pytest
from unittest.mock import patch
import requests
from roex_python.controllers.stemflow_controller import StemFlowController
from roex_python.models import (
    StemSeparationRequest, StemSeparationTaskResponse,
    StemSeparationStatusResult, SeparatedStemsResult
)


@pytest.mark.unit
class TestStemFlowControllerInit:
    """Test StemFlowController initialization"""

    def test_init(self, mock_api_provider):
        """Test controller initialization"""
        controller = StemFlowController(mock_api_provider)
        assert controller.api_provider == mock_api_provider


@pytest.mark.unit
class TestCreateSeparation:
    """Test create_separation method"""

    def test_successful_creation(self, mock_api_provider):
        """Test successful stem separation task creation"""
        mock_api_provider.post.return_value = {
            "stemflowTaskId": "sf_task_123",
            "error": False,
            "message": "Successfully created stem separation task."
        }

        controller = StemFlowController(mock_api_provider)
        request = StemSeparationRequest(audio_file_location="https://example.com/song.wav")

        result = controller.create_separation(request)

        assert isinstance(result, StemSeparationTaskResponse)
        assert result.stemflow_task_id == "sf_task_123"
        assert result.error is False

        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/separate"
        assert call_args[0][1] == {
            "stemflowData": {"audioFileLocation": "https://example.com/song.wav"}
        }

    def test_successful_creation_two_stem_mode_and_webhook(self, mock_api_provider):
        """Test successful creation with separation_mode and webhook_url"""
        mock_api_provider.post.return_value = {
            "stemflowTaskId": "sf_task_124",
            "error": False,
            "message": "Successfully created stem separation task."
        }

        controller = StemFlowController(mock_api_provider)
        request = StemSeparationRequest(
            audio_file_location="https://example.com/song.wav",
            separation_mode="vocals_instrumental",
            webhook_url="https://example.com/hook",
        )

        result = controller.create_separation(request)

        assert result.stemflow_task_id == "sf_task_124"

        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/separate"
        assert call_args[0][1] == {
            "stemflowData": {
                "audioFileLocation": "https://example.com/song.wav",
                "separationMode": "vocals_instrumental",
                "webhookURL": "https://example.com/hook",
            }
        }

    def test_http_error_handling(self, mock_api_provider):
        """Test error handling when API returns HTTP error (e.g. insufficient credits)"""
        mock_api_provider.post.side_effect = requests.HTTPError("402 Payment Required")

        controller = StemFlowController(mock_api_provider)
        request = StemSeparationRequest(audio_file_location="https://example.com/song.wav")

        with pytest.raises(Exception, match="Failed to submit stem separation task"):
            controller.create_separation(request)


@pytest.mark.unit
class TestGetSeparationStatus:
    """Test get_separation_status method"""

    def test_processing_status(self, mock_api_provider):
        """Test polling while separation is still processing"""
        mock_api_provider.get.return_value = {
            "stemflowTaskId": "sf_task_123",
            "status": "processing",
            "error": False,
            "message": "Stem separation is processing."
        }

        controller = StemFlowController(mock_api_provider)
        result = controller.get_separation_status("sf_task_123")

        assert isinstance(result, StemSeparationStatusResult)
        assert result.status == "processing"
        assert result.error is False

        call_args = mock_api_provider.get.call_args
        assert call_args[0][0] == "/separatestatus/sf_task_123"

    def test_complete_status(self, mock_api_provider):
        """Test status result when separation has completed"""
        mock_api_provider.get.return_value = {
            "stemflowTaskId": "sf_task_123",
            "status": "complete",
            "error": False,
            "message": "Stem separation complete."
        }

        controller = StemFlowController(mock_api_provider)
        result = controller.get_separation_status("sf_task_123")

        assert result.status == "complete"

    def test_failed_status(self, mock_api_provider):
        """Test status result when separation has failed"""
        mock_api_provider.get.return_value = {
            "stemflowTaskId": "sf_task_123",
            "status": "failed",
            "error": True,
            "message": "Stem separation failed.",
            "info": "worker crashed"
        }

        controller = StemFlowController(mock_api_provider)
        result = controller.get_separation_status("sf_task_123")

        assert result.status == "failed"
        assert result.error is True
        assert result.info == "worker crashed"

    def test_http_error_handling(self, mock_api_provider):
        """Test error handling for e.g. a 404 on an unknown/unowned task"""
        mock_api_provider.get.side_effect = requests.HTTPError("404 Not Found")

        controller = StemFlowController(mock_api_provider)

        with pytest.raises(Exception, match="Failed to get stem separation status"):
            controller.get_separation_status("sf_unknown")


@pytest.mark.unit
class TestWaitForSeparation:
    """Test wait_for_separation method"""

    @patch('roex_python.controllers.stemflow_controller.time.sleep')
    def test_returns_immediately_when_already_complete(self, mock_sleep, mock_api_provider):
        """Test no polling delay needed when the task is already complete"""
        mock_api_provider.get.return_value = {
            "stemflowTaskId": "sf_task_123",
            "status": "complete",
            "error": False
        }

        controller = StemFlowController(mock_api_provider)
        result = controller.wait_for_separation("sf_task_123", poll_interval=1)

        assert result.status == "complete"
        mock_sleep.assert_not_called()

    @patch('roex_python.controllers.stemflow_controller.time.sleep')
    def test_polls_until_complete(self, mock_sleep, mock_api_provider):
        """Test polling continues until status becomes complete"""
        mock_api_provider.get.side_effect = [
            {"stemflowTaskId": "sf_task_123", "status": "processing", "error": False},
            {"stemflowTaskId": "sf_task_123", "status": "processing", "error": False},
            {"stemflowTaskId": "sf_task_123", "status": "complete", "error": False},
        ]

        controller = StemFlowController(mock_api_provider)
        result = controller.wait_for_separation("sf_task_123", poll_interval=1, timeout=30)

        assert result.status == "complete"
        assert mock_api_provider.get.call_count == 3

    @patch('roex_python.controllers.stemflow_controller.time.sleep')
    def test_raises_on_failed_status(self, mock_sleep, mock_api_provider):
        """Test that a failed task raises with the failure info"""
        mock_api_provider.get.return_value = {
            "stemflowTaskId": "sf_task_123",
            "status": "failed",
            "error": True,
            "info": "GPU worker timed out"
        }

        controller = StemFlowController(mock_api_provider)

        with pytest.raises(Exception, match="GPU worker timed out"):
            controller.wait_for_separation("sf_task_123", poll_interval=1)

    @patch('roex_python.controllers.stemflow_controller.time.sleep')
    def test_polling_timeout(self, mock_sleep, mock_api_provider):
        """Test polling timeout after max attempts when stuck processing.

        With timeout=3 and poll_interval=1, there are 3 sleeps but 4 checks:
        one up front, then one after each sleep -- so the final check lands
        at the deadline itself instead of being skipped."""
        mock_api_provider.get.return_value = {
            "stemflowTaskId": "sf_task_123",
            "status": "processing",
            "error": False
        }

        controller = StemFlowController(mock_api_provider)

        with pytest.raises(Exception, match="did not complete after polling"):
            controller.wait_for_separation("sf_task_123", poll_interval=1, timeout=3)

        assert mock_api_provider.get.call_count == 4
        assert mock_sleep.call_count == 3

    @patch('roex_python.controllers.stemflow_controller.time.sleep')
    def test_polls_at_the_deadline_before_giving_up(self, mock_sleep, mock_api_provider):
        """Test that a task completing on the final allowed check (the one
        after the last sleep) is reported as complete, not as timed out."""
        mock_api_provider.get.side_effect = [
            {"stemflowTaskId": "sf_task_123", "status": "processing", "error": False},
            {"stemflowTaskId": "sf_task_123", "status": "processing", "error": False},
            {"stemflowTaskId": "sf_task_123", "status": "processing", "error": False},
            {"stemflowTaskId": "sf_task_123", "status": "complete", "error": False},
        ]

        controller = StemFlowController(mock_api_provider)
        result = controller.wait_for_separation("sf_task_123", poll_interval=1, timeout=3)

        assert result.status == "complete"
        assert mock_api_provider.get.call_count == 4
        assert mock_sleep.call_count == 3


@pytest.mark.unit
class TestRetrieveStems:
    """Test retrieve_stems method"""

    def test_successful_retrieval(self, mock_api_provider):
        """Test successful stem retrieval"""
        mock_api_provider.post.return_value = {
            "stemflowTaskId": "sf_task_123",
            "stems": {
                "vocals": "https://example.com/vocals.wav",
                "bass": "https://example.com/bass.wav",
                "drums": "https://example.com/drums.wav",
                "other": "https://example.com/other.wav",
            },
            "error": False,
            "message": "Successfully retrieved separated stems."
        }

        controller = StemFlowController(mock_api_provider)
        result = controller.retrieve_stems("sf_task_123")

        assert isinstance(result, SeparatedStemsResult)
        assert result.vocals == "https://example.com/vocals.wav"
        assert result.bass == "https://example.com/bass.wav"
        assert result.drums == "https://example.com/drums.wav"
        assert result.other == "https://example.com/other.wav"

        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/retrievestems"
        assert call_args[0][1] == {"stemflowData": {"stemflowTaskId": "sf_task_123"}}

    def test_successful_retrieval_two_stem_mode(self, mock_api_provider):
        """Test successful retrieval of a 2-stem (vocals_instrumental) result"""
        mock_api_provider.post.return_value = {
            "stemflowTaskId": "sf_task_123",
            "stems": {
                "vocals": "https://example.com/vocals.wav",
                "instrumental": "https://example.com/no_vocals.wav",
                "bass": "",
                "drums": "",
                "other": "",
            },
            "error": False,
            "message": "Successfully retrieved separated stems."
        }

        controller = StemFlowController(mock_api_provider)
        result = controller.retrieve_stems("sf_task_123")

        assert isinstance(result, SeparatedStemsResult)
        assert result.vocals == "https://example.com/vocals.wav"
        assert result.instrumental == "https://example.com/no_vocals.wav"
        assert result.bass in (None, "")
        assert result.drums in (None, "")
        assert result.other in (None, "")

    def test_not_complete_yet_raises(self, mock_api_provider):
        """Test that a 202 'not complete yet' response raises rather than returning empty stems"""
        mock_api_provider.post.return_value = {
            "stemflowTaskId": "sf_task_123",
            "error": True,
            "message": "Stem separation is not complete yet."
        }

        controller = StemFlowController(mock_api_provider)

        with pytest.raises(Exception, match="not complete yet"):
            controller.retrieve_stems("sf_task_123")

    def test_http_error_handling(self, mock_api_provider):
        """Test error handling for e.g. a 404 on an unknown/unowned task"""
        mock_api_provider.post.side_effect = requests.HTTPError("404 Not Found")

        controller = StemFlowController(mock_api_provider)

        with pytest.raises(Exception, match="Failed to retrieve stems"):
            controller.retrieve_stems("sf_unknown")
