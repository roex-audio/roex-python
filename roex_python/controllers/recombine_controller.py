"""
Controller for stem recombination ("Recombine") operations
"""

import time
from typing import Any, Dict
import logging

import requests

from roex_python.models.recombine import (
    RecombineRequest,
    RecombineTaskResponse,
    RecombineStatusResult,
    RecombinePreviewResult,
    RecombineProcessingInfo,
    RecombineFinalResult,
)
from roex_python.providers.api_provider import ApiProvider

# Initialize logger for this module
logger = logging.getLogger(__name__)


class RecombineController:
    """Controller for creating and retrieving stem recombination ("Recombine") tasks.

    Recombines an isolated vocal with a backing track -- either reusing a
    prior :class:`~roex_python.controllers.stemflow_controller.StemFlowController`
    separation job (``stem_job_id``) or directly supplied vocal/backing
    URLs -- into a mixed and mastered result. Submitting a task is free;
    the final master is charged 250 credits the first time it is
    successfully retrieved.
    """

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the RecombineController.

        Typically, this controller is accessed via ``client.recombine``
        rather than instantiated directly.

        Args:
            api_provider (ApiProvider): An instance of ApiProvider configured with
                the base URL and API key.
        """
        self.api_provider = api_provider
        logger.info("RecombineController initialized.")

    def create_recombine(self, request: RecombineRequest) -> RecombineTaskResponse:
        """
        Submit a recombine task.

        Sends a request to the RoEx API's ``/recombine`` endpoint. Free to
        submit; billing occurs only on the first successful
        ``retrieve_final_master`` call. It's asynchronous and returns a
        task ID immediately (see ``wait_for_recombine``).

        Args:
            request (RecombineRequest): Either ``stem_job_id``, or both
                ``vocal_stem_url`` and ``backing_stem_url``, plus
                ``musical_style`` and optional ``desired_loudness`` /
                ``vocal_gain_db``.

        Returns:
            RecombineTaskResponse: Contains:
                - ``recombine_task_id`` (str): The unique ID for the initiated task.
                - ``error`` (bool): Indicates if the initial API request failed.
                - ``message`` (str): Status message from the API.

        Raises:
            Exception: If the API returns an error status, e.g. HTTP 400 for
                an invalid/incomplete referenced separation job, or HTTP 404
                if ``stem_job_id`` is unknown or not owned by this API key.

        Example:
            >>> from roex_python.models import RecombineRequest, RecombineMusicalStyle
            >>> # Assume 'client' is an initialized RoExClient and 'sep_task' a completed separation
            >>> task = client.recombine.create_recombine(
            ...     RecombineRequest(
            ...         stem_job_id=sep_task.stemflow_task_id,
            ...         musical_style=RecombineMusicalStyle.POP,
            ...     )
            ... )
            >>> print(f"Recombine task started with ID: {task.recombine_task_id}")
        """
        logger.info("Submitting recombine task.")
        payload = self._prepare_recombine_payload(request)

        try:
            response = self.api_provider.post("/recombine", payload)
            logger.info(
                f"Recombine task submitted. Task ID: {response.get('recombineTaskId', '')}"
            )
            return RecombineTaskResponse(
                recombine_task_id=response.get("recombineTaskId", ""),
                error=response.get("error", False),
                message=response.get("message", ""),
            )
        except requests.HTTPError as e:
            logger.error(f"Failed to submit recombine task: {str(e)}")
            raise Exception(f"Failed to submit recombine task: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error submitting recombine task: {e}")
            raise

    def get_recombine_status(self, recombine_task_id: str) -> RecombineStatusResult:
        """
        Check the status of a recombine task.

        Sends a request to ``GET /recombinestatus/{recombine_task_id}``.

        Args:
            recombine_task_id (str): The task ID returned by ``create_recombine``.

        Returns:
            RecombineStatusResult: ``status`` is one of ``"processing"``,
                ``"complete"``, or ``"failed"``. When ``"failed"``, ``error``
                is True and ``info`` may contain failure details.

        Raises:
            Exception: If the API returns an error status, e.g. HTTP 404 if
                the task doesn't exist or isn't owned by this API key.

        Example:
            >>> status = client.recombine.get_recombine_status(task.recombine_task_id)
            >>> print(status.status)
        """
        logger.debug(f"Checking recombine status for task ID: {recombine_task_id}")

        try:
            response = self.api_provider.get(f"/recombinestatus/{recombine_task_id}")
            return RecombineStatusResult(
                recombine_task_id=response.get("recombineTaskId", recombine_task_id),
                status=response.get("status", "unknown"),
                error=response.get("error", False),
                message=response.get("message", ""),
                info=response.get("info", ""),
            )
        except requests.HTTPError as e:
            logger.error(f"Failed to get recombine status: {str(e)}")
            raise Exception(f"Failed to get recombine status: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error getting recombine status: {e}")
            raise

    def wait_for_recombine(
        self, recombine_task_id: str, poll_interval: int = 10, timeout: int = 600
    ) -> RecombineStatusResult:
        """
        Poll ``get_recombine_status`` until the task completes, fails, or times out.

        Args:
            recombine_task_id (str): The task ID returned by ``create_recombine``.
            poll_interval (int): Seconds to wait between status checks. Defaults to 10.
            timeout (int): Maximum seconds to wait for task completion.
                Defaults to 600 (10 minutes).

        Returns:
            RecombineStatusResult: The status result once ``status`` is
                ``"complete"``.

        Raises:
            Exception: If the task reports ``status == "failed"``, or does
                not complete within ``timeout`` seconds.

        Example:
            >>> client.recombine.wait_for_recombine(task.recombine_task_id)
            >>> master = client.recombine.retrieve_final_master(task.recombine_task_id)
        """
        # One check happens up front, then one more after each sleep, so the
        # last check lands at (or just after) the deadline itself instead of
        # `max_sleeps` sleeps being spent without ever re-checking status.
        max_sleeps = max(1, timeout // poll_interval)
        for attempt in range(max_sleeps + 1):
            result = self.get_recombine_status(recombine_task_id)

            if result.status == "complete":
                logger.info(f"Recombine task {recombine_task_id} complete.")
                return result
            if result.status == "failed":
                logger.error(f"Recombine task {recombine_task_id} failed: {result.info}")
                raise Exception(
                    f"Recombine task {recombine_task_id} failed: {result.info or result.message}"
                )

            if attempt < max_sleeps:
                logger.debug(
                    f"Recombine task {recombine_task_id} still processing "
                    f"(attempt {attempt + 1}/{max_sleeps + 1})."
                )
                time.sleep(poll_interval)

        logger.error(f"Recombine task {recombine_task_id} did not complete after polling.")
        raise Exception(
            f"Recombine task {recombine_task_id} did not complete after polling for {timeout} seconds."
        )

    def retrieve_preview(self, recombine_task_id: str) -> RecombinePreviewResult:
        """
        Retrieve a free ~30 second MP3 preview of a completed recombine task.

        Sends a request to ``POST /retrieverecombinepreview``. Free to call;
        safe to call repeatedly.

        Args:
            recombine_task_id (str): The task ID returned by ``create_recombine``.

        Returns:
            RecombinePreviewResult: Contains ``preview_url`` (an MP3 clip
                taken from the loudest section of the track, not necessarily
                the start), ``preview_start_seconds``, and
                ``measured_lufs_full`` (loudness measured across the full
                program, not just the preview excerpt).

        Raises:
            Exception: If the task is not yet complete, or the API returns
                an error, e.g. HTTP 404 for an unknown/unowned task.

        Example:
            >>> preview = client.recombine.retrieve_preview(task.recombine_task_id)
            >>> print(preview.preview_url)
        """
        logger.info(f"Retrieving recombine preview for task ID: {recombine_task_id}")
        payload = {"recombineData": {"recombineTaskId": recombine_task_id}}

        try:
            response = self.api_provider.post("/retrieverecombinepreview", payload)
            if response.get("error", False):
                message = response.get("message", "Recombine is not complete yet.")
                logger.warning(
                    f"Could not retrieve recombine preview for {recombine_task_id}: {message}"
                )
                raise Exception(message)

            preview = response.get("preview", {}) or {}
            return RecombinePreviewResult(
                preview_url=preview.get("preview_url"),
                preview_start_seconds=preview.get("preview_start_seconds"),
                measured_lufs_full=preview.get("measured_lufs_full"),
            )
        except requests.HTTPError as e:
            logger.error(f"Failed to retrieve recombine preview: {str(e)}")
            raise Exception(f"Failed to retrieve recombine preview: {str(e)}")

    def retrieve_final_master(self, recombine_task_id: str) -> RecombineFinalResult:
        """
        Retrieve the final mastered WAV for a completed recombine task.

        Sends a request to ``POST /retrieverecombine``. Charges 250 credits
        the first time this succeeds for a given task; safe to call again
        afterwards -- repeat calls return the same result without
        re-charging.

        Args:
            recombine_task_id (str): The task ID returned by ``create_recombine``.

        Returns:
            RecombineFinalResult: Contains ``master_url`` (a stereo,
                44.1kHz, 16-bit WAV signed for ~24 hours), measured
                loudness/peak/format metadata, and the ``processing``
                parameters that were applied.

        Raises:
            Exception: If the task is not yet complete, credits are
                insufficient (HTTP 402), or the API returns another error,
                e.g. HTTP 404 for an unknown/unowned task.

        Example:
            >>> master = client.recombine.retrieve_final_master(task.recombine_task_id)
            >>> print(master.master_url)
        """
        logger.info(f"Retrieving final recombine master for task ID: {recombine_task_id}")
        payload = {"recombineData": {"recombineTaskId": recombine_task_id}}

        try:
            response = self.api_provider.post("/retrieverecombine", payload)
            if response.get("error", False):
                message = response.get("message", "Recombine is not complete yet.")
                logger.warning(
                    f"Could not retrieve recombine master for {recombine_task_id}: {message}"
                )
                raise Exception(message)

            result = response.get("result", {}) or {}
            processing = result.get("processing") or {}
            return RecombineFinalResult(
                master_url=result.get("master_url"),
                measured_lufs=result.get("measured_lufs"),
                peak_level=result.get("peak_level"),
                track_length_seconds=result.get("track_length_seconds"),
                sample_rate=result.get("sample_rate"),
                bit_depth=result.get("bit_depth"),
                channels=result.get("channels"),
                processing=RecombineProcessingInfo(
                    musical_style=processing.get("musical_style"),
                    desired_loudness=processing.get("desired_loudness"),
                    vocal_gain_db=processing.get("vocal_gain_db"),
                ) if processing else None,
            )
        except requests.HTTPError as e:
            logger.error(f"Failed to retrieve recombine master: {str(e)}")
            raise Exception(f"Failed to retrieve recombine master: {str(e)}")

    def _prepare_recombine_payload(self, request: RecombineRequest) -> Dict[str, Any]:
        """
        Convert the model to an API payload for ``/recombine``.

        Args:
            request: Recombine request

        Returns:
            API payload dictionary
        """
        logger.debug(f"Preparing recombine payload for request: {request}")
        data: Dict[str, Any] = {
            "musicalStyle": request.musical_style.value,
            "desiredLoudness": request.desired_loudness.value,
            "vocalGainDb": request.vocal_gain_db,
        }
        if request.stem_job_id is not None:
            data["stemJobId"] = request.stem_job_id
        else:
            data["vocalStemURL"] = request.vocal_stem_url
            data["backingStemURL"] = request.backing_stem_url
        return {"recombineData": data}
