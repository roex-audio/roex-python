"""
Unit tests for RecombineController
"""

import pytest
from unittest.mock import patch
import requests
from roex_python.controllers.recombine_controller import RecombineController
from roex_python.models import (
    RecombineRequest, RecombineMusicalStyle, RecombineTaskResponse,
    RecombineStatusResult, RecombinePreviewResult, RecombineFinalResult,
    DesiredLoudness
)


@pytest.mark.unit
class TestRecombineControllerInit:
    """Test RecombineController initialization"""

    def test_init(self, mock_api_provider):
        """Test controller initialization"""
        controller = RecombineController(mock_api_provider)
        assert controller.api_provider == mock_api_provider


@pytest.mark.unit
class TestCreateRecombine:
    """Test create_recombine method"""

    def test_successful_creation_via_stem_job_id(self, mock_api_provider):
        """Test submitting via a prior separation job's stem_job_id"""
        mock_api_provider.post.return_value = {
            "recombineTaskId": "rc_task_123",
            "error": False,
            "message": "Successfully created recombine task."
        }

        controller = RecombineController(mock_api_provider)
        request = RecombineRequest(
            stem_job_id="sf_task_123",
            musical_style=RecombineMusicalStyle.POP
        )

        result = controller.create_recombine(request)

        assert isinstance(result, RecombineTaskResponse)
        assert result.recombine_task_id == "rc_task_123"
        assert result.error is False

        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/recombine"
        payload = call_args[0][1]["recombineData"]
        assert payload["stemJobId"] == "sf_task_123"
        assert payload["musicalStyle"] == "POP"
        assert payload["desiredLoudness"] == "MEDIUM"
        assert payload["vocalGainDb"] == 0.0
        assert "vocalStemURL" not in payload
        assert "backingStemURL" not in payload

    def test_successful_creation_via_direct_urls(self, mock_api_provider):
        """Test submitting via directly supplied vocal + backing URLs"""
        mock_api_provider.post.return_value = {
            "recombineTaskId": "rc_task_456",
            "error": False,
            "message": "Successfully created recombine task."
        }

        controller = RecombineController(mock_api_provider)
        request = RecombineRequest(
            vocal_stem_url="https://example.com/vocal.wav",
            backing_stem_url="https://example.com/backing.wav",
            musical_style=RecombineMusicalStyle.HIPHOP_GRIME,
            desired_loudness=DesiredLoudness.HIGH,
            vocal_gain_db=3.0
        )

        result = controller.create_recombine(request)

        assert result.recombine_task_id == "rc_task_456"

        payload = mock_api_provider.post.call_args[0][1]["recombineData"]
        assert payload["vocalStemURL"] == "https://example.com/vocal.wav"
        assert payload["backingStemURL"] == "https://example.com/backing.wav"
        assert payload["musicalStyle"] == "HIPHOP_GRIME"
        assert payload["desiredLoudness"] == "HIGH"
        assert payload["vocalGainDb"] == 3.0
        assert "stemJobId" not in payload

    def test_http_error_handling(self, mock_api_provider):
        """Test error handling when API returns an HTTP error"""
        mock_api_provider.post.side_effect = requests.HTTPError("404 Not Found")

        controller = RecombineController(mock_api_provider)
        request = RecombineRequest(
            stem_job_id="sf_unknown",
            musical_style=RecombineMusicalStyle.POP
        )

        with pytest.raises(Exception, match="Failed to submit recombine task"):
            controller.create_recombine(request)


@pytest.mark.unit
class TestRecombineRequestValidation:
    """Test RecombineRequest input validation"""

    def test_rejects_neither_input_mode(self):
        """Test that omitting both stem_job_id and vocal/backing URLs raises"""
        with pytest.raises(ValueError, match="Provide either stem_job_id"):
            RecombineRequest(musical_style=RecombineMusicalStyle.POP)

    def test_rejects_both_input_modes(self):
        """Test that providing both stem_job_id and direct URLs raises"""
        with pytest.raises(ValueError, match="not both"):
            RecombineRequest(
                stem_job_id="sf_task_123",
                vocal_stem_url="https://example.com/vocal.wav",
                backing_stem_url="https://example.com/backing.wav",
                musical_style=RecombineMusicalStyle.POP
            )

    def test_rejects_only_vocal_url_without_backing(self):
        """Test that providing only vocal_stem_url without backing_stem_url raises"""
        with pytest.raises(ValueError, match="Provide either stem_job_id"):
            RecombineRequest(
                vocal_stem_url="https://example.com/vocal.wav",
                musical_style=RecombineMusicalStyle.POP
            )

    def test_rejects_vocal_gain_above_max(self):
        """Test that vocal_gain_db above +6.0 raises"""
        with pytest.raises(ValueError, match="vocal_gain_db must be between"):
            RecombineRequest(
                stem_job_id="sf_task_123",
                musical_style=RecombineMusicalStyle.POP,
                vocal_gain_db=6.1
            )

    def test_rejects_vocal_gain_below_min(self):
        """Test that vocal_gain_db below -6.0 raises"""
        with pytest.raises(ValueError, match="vocal_gain_db must be between"):
            RecombineRequest(
                stem_job_id="sf_task_123",
                musical_style=RecombineMusicalStyle.POP,
                vocal_gain_db=-6.1
            )

    def test_accepts_vocal_gain_at_boundaries(self):
        """Test that vocal_gain_db of exactly +/-6.0 is accepted"""
        low = RecombineRequest(
            stem_job_id="sf_task_123", musical_style=RecombineMusicalStyle.POP, vocal_gain_db=-6.0
        )
        high = RecombineRequest(
            stem_job_id="sf_task_123", musical_style=RecombineMusicalStyle.POP, vocal_gain_db=6.0
        )
        assert low.vocal_gain_db == -6.0
        assert high.vocal_gain_db == 6.0


@pytest.mark.unit
class TestGetRecombineStatus:
    """Test get_recombine_status method"""

    def test_processing_status(self, mock_api_provider):
        """Test polling while recombine is still processing"""
        mock_api_provider.get.return_value = {
            "recombineTaskId": "rc_task_123",
            "status": "processing",
            "error": False
        }

        controller = RecombineController(mock_api_provider)
        result = controller.get_recombine_status("rc_task_123")

        assert isinstance(result, RecombineStatusResult)
        assert result.status == "processing"

        call_args = mock_api_provider.get.call_args
        assert call_args[0][0] == "/recombinestatus/rc_task_123"

    def test_failed_status(self, mock_api_provider):
        """Test status result when recombine has failed"""
        mock_api_provider.get.return_value = {
            "recombineTaskId": "rc_task_123",
            "status": "failed",
            "error": True,
            "info": "mastering worker crashed"
        }

        controller = RecombineController(mock_api_provider)
        result = controller.get_recombine_status("rc_task_123")

        assert result.status == "failed"
        assert result.info == "mastering worker crashed"

    def test_http_error_handling(self, mock_api_provider):
        """Test error handling for e.g. a 404 on an unknown/unowned task"""
        mock_api_provider.get.side_effect = requests.HTTPError("404 Not Found")

        controller = RecombineController(mock_api_provider)

        with pytest.raises(Exception, match="Failed to get recombine status"):
            controller.get_recombine_status("rc_unknown")


@pytest.mark.unit
class TestWaitForRecombine:
    """Test wait_for_recombine method"""

    @patch('roex_python.controllers.recombine_controller.time.sleep')
    def test_polls_until_complete(self, mock_sleep, mock_api_provider):
        """Test polling continues until status becomes complete"""
        mock_api_provider.get.side_effect = [
            {"recombineTaskId": "rc_task_123", "status": "processing", "error": False},
            {"recombineTaskId": "rc_task_123", "status": "complete", "error": False},
        ]

        controller = RecombineController(mock_api_provider)
        result = controller.wait_for_recombine("rc_task_123", poll_interval=1, timeout=30)

        assert result.status == "complete"
        assert mock_api_provider.get.call_count == 2

    @patch('roex_python.controllers.recombine_controller.time.sleep')
    def test_raises_on_failed_status(self, mock_sleep, mock_api_provider):
        """Test that a failed task raises with the failure info"""
        mock_api_provider.get.return_value = {
            "recombineTaskId": "rc_task_123",
            "status": "failed",
            "error": True,
            "info": "mastering failed"
        }

        controller = RecombineController(mock_api_provider)

        with pytest.raises(Exception, match="mastering failed"):
            controller.wait_for_recombine("rc_task_123", poll_interval=1)

    @patch('roex_python.controllers.recombine_controller.time.sleep')
    def test_polling_timeout(self, mock_sleep, mock_api_provider):
        """Test polling timeout after max attempts when stuck processing.

        With timeout=3 and poll_interval=1, there are 3 sleeps but 4 checks:
        one up front, then one after each sleep -- so the final check lands
        at the deadline itself instead of being skipped."""
        mock_api_provider.get.return_value = {
            "recombineTaskId": "rc_task_123",
            "status": "processing",
            "error": False
        }

        controller = RecombineController(mock_api_provider)

        with pytest.raises(Exception, match="did not complete after polling"):
            controller.wait_for_recombine("rc_task_123", poll_interval=1, timeout=3)

        assert mock_api_provider.get.call_count == 4
        assert mock_sleep.call_count == 3

    @patch('roex_python.controllers.recombine_controller.time.sleep')
    def test_polls_at_the_deadline_before_giving_up(self, mock_sleep, mock_api_provider):
        """Test that a task completing on the final allowed check (the one
        after the last sleep) is reported as complete, not as timed out."""
        mock_api_provider.get.side_effect = [
            {"recombineTaskId": "rc_task_123", "status": "processing", "error": False},
            {"recombineTaskId": "rc_task_123", "status": "processing", "error": False},
            {"recombineTaskId": "rc_task_123", "status": "processing", "error": False},
            {"recombineTaskId": "rc_task_123", "status": "complete", "error": False},
        ]

        controller = RecombineController(mock_api_provider)
        result = controller.wait_for_recombine("rc_task_123", poll_interval=1, timeout=3)

        assert result.status == "complete"
        assert mock_api_provider.get.call_count == 4
        assert mock_sleep.call_count == 3


@pytest.mark.unit
class TestRetrievePreview:
    """Test retrieve_preview method"""

    def test_successful_retrieval(self, mock_api_provider):
        """Test successful preview retrieval"""
        mock_api_provider.post.return_value = {
            "recombineTaskId": "rc_task_123",
            "preview": {
                "preview_url": "https://example.com/preview.mp3",
                "preview_start_seconds": 42.5,
                "measured_lufs_full": -13.4
            },
            "error": False
        }

        controller = RecombineController(mock_api_provider)
        result = controller.retrieve_preview("rc_task_123")

        assert isinstance(result, RecombinePreviewResult)
        assert result.preview_url == "https://example.com/preview.mp3"
        assert result.preview_start_seconds == 42.5
        assert result.measured_lufs_full == -13.4

        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/retrieverecombinepreview"
        assert call_args[0][1] == {"recombineData": {"recombineTaskId": "rc_task_123"}}

    def test_not_complete_yet_raises(self, mock_api_provider):
        """Test that a 202 'not complete yet' response raises"""
        mock_api_provider.post.return_value = {
            "recombineTaskId": "rc_task_123",
            "error": True,
            "message": "Recombine is not complete yet."
        }

        controller = RecombineController(mock_api_provider)

        with pytest.raises(Exception, match="not complete yet"):
            controller.retrieve_preview("rc_task_123")


@pytest.mark.unit
class TestRetrieveFinalMaster:
    """Test retrieve_final_master method"""

    def test_successful_retrieval(self, mock_api_provider):
        """Test successful final master retrieval, including nested processing info"""
        mock_api_provider.post.return_value = {
            "recombineTaskId": "rc_task_123",
            "result": {
                "master_url": "https://example.com/master.wav",
                "measured_lufs": -13.4,
                "peak_level": -1.2,
                "track_length_seconds": 187.4,
                "sample_rate": 44100,
                "bit_depth": 16,
                "channels": 2,
                "processing": {
                    "musical_style": "POP",
                    "desired_loudness": "MEDIUM",
                    "vocal_gain_db": 0.0
                }
            },
            "error": False
        }

        controller = RecombineController(mock_api_provider)
        result = controller.retrieve_final_master("rc_task_123")

        assert isinstance(result, RecombineFinalResult)
        assert result.master_url == "https://example.com/master.wav"
        assert result.measured_lufs == -13.4
        assert result.peak_level == -1.2
        assert result.track_length_seconds == 187.4
        assert result.sample_rate == 44100
        assert result.bit_depth == 16
        assert result.channels == 2
        assert result.processing.musical_style == "POP"
        assert result.processing.desired_loudness == "MEDIUM"
        assert result.processing.vocal_gain_db == 0.0

        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/retrieverecombine"

    def test_repeated_retrieval_returns_same_result(self, mock_api_provider):
        """Test that calling retrieve_final_master twice (idempotent charge-once) works"""
        same_response = {
            "recombineTaskId": "rc_task_123",
            "result": {"master_url": "https://example.com/master.wav"},
            "error": False
        }
        mock_api_provider.post.return_value = same_response

        controller = RecombineController(mock_api_provider)
        first = controller.retrieve_final_master("rc_task_123")
        second = controller.retrieve_final_master("rc_task_123")

        assert first.master_url == second.master_url == "https://example.com/master.wav"
        assert mock_api_provider.post.call_count == 2

    def test_insufficient_credits_raises(self, mock_api_provider):
        """Test error handling for HTTP 402 insufficient credits"""
        mock_api_provider.post.side_effect = requests.HTTPError("402 Payment Required")

        controller = RecombineController(mock_api_provider)

        with pytest.raises(Exception, match="Failed to retrieve recombine master"):
            controller.retrieve_final_master("rc_task_123")

    def test_not_complete_yet_raises(self, mock_api_provider):
        """Test that a 202 'not complete yet' response raises"""
        mock_api_provider.post.return_value = {
            "recombineTaskId": "rc_task_123",
            "error": True,
            "message": "Recombine is not complete yet."
        }

        controller = RecombineController(mock_api_provider)

        with pytest.raises(Exception, match="not complete yet"):
            controller.retrieve_final_master("rc_task_123")


@pytest.mark.unit
class TestPreparePayload:
    """Test _prepare_recombine_payload method"""

    def test_payload_structure_via_stem_job_id(self, mock_api_provider):
        """Test payload structure when using stem_job_id"""
        controller = RecombineController(mock_api_provider)
        request = RecombineRequest(
            stem_job_id="sf_task_123",
            musical_style=RecombineMusicalStyle.K_POP,
            desired_loudness=DesiredLoudness.LOW,
            vocal_gain_db=-2.5
        )

        payload = controller._prepare_recombine_payload(request)

        assert "recombineData" in payload
        data = payload["recombineData"]
        assert data["stemJobId"] == "sf_task_123"
        assert data["musicalStyle"] == "K_POP"
        assert data["desiredLoudness"] == "LOW"
        assert data["vocalGainDb"] == -2.5
        assert "vocalStemURL" not in data
        assert "backingStemURL" not in data
        assert "webhookURL" not in data  # absent when webhook_url is not set

    def test_payload_includes_webhook_url_when_set(self, mock_api_provider):
        """Test that webhookURL is included in the payload when webhook_url is set"""
        controller = RecombineController(mock_api_provider)
        request = RecombineRequest(
            stem_job_id="sf_task_123",
            musical_style=RecombineMusicalStyle.POP,
            webhook_url="https://example.com/hook"
        )

        payload = controller._prepare_recombine_payload(request)
        data = payload["recombineData"]
        assert data["webhookURL"] == "https://example.com/hook"

    def test_payload_structure_via_direct_urls(self, mock_api_provider):
        """Test payload structure when using direct vocal/backing URLs"""
        controller = RecombineController(mock_api_provider)
        request = RecombineRequest(
            vocal_stem_url="https://example.com/vocal.wav",
            backing_stem_url="https://example.com/backing.wav",
            musical_style=RecombineMusicalStyle.TRAP
        )

        payload = controller._prepare_recombine_payload(request)

        data = payload["recombineData"]
        assert data["vocalStemURL"] == "https://example.com/vocal.wav"
        assert data["backingStemURL"] == "https://example.com/backing.wav"
        assert data["musicalStyle"] == "TRAP"
        assert "stemJobId" not in data
