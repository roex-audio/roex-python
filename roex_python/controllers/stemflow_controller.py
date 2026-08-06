"""
Controller for stem separation ("StemFlow") operations
"""

import time
import logging

import requests

from roex_python.models.stemflow import (
    StemSeparationRequest,
    StemSeparationTaskResponse,
    StemSeparationStatusResult,
    SeparatedStemsResult,
)
from roex_python.providers.api_provider import ApiProvider

# Initialize logger for this module
logger = logging.getLogger(__name__)


class StemFlowController:
    """Controller for initiating and managing stem separation tasks via the RoEx API.

    Splits a full mix into isolated ``vocals``, ``bass``, ``drums``, and
    ``other`` stems using a GPU-backed separation model. Submitting a job
    reserves 75 credits from the caller's balance; they are captured only
    if separation succeeds, and refunded automatically if it fails.
    """

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the StemFlowController.

        Typically, this controller is accessed via ``client.stem_separation``
        rather than instantiated directly.

        Args:
            api_provider (ApiProvider): An instance of ApiProvider configured with
                the base URL and API key.
        """
        self.api_provider = api_provider
        logger.info("StemFlowController initialized.")

    def create_separation(self, request: StemSeparationRequest) -> StemSeparationTaskResponse:
        """
        Submit a stem separation task.

        Sends a request to the RoEx API's ``/separate`` endpoint. It's
        asynchronous and returns a task ID immediately; the separated stem
        URLs must be retrieved later via ``retrieve_stems`` once the task
        completes (see ``wait_for_separation``).

        Args:
            request (StemSeparationRequest): Contains ``audio_file_location``,
                the URL of the audio file to separate.

        Returns:
            StemSeparationTaskResponse: Contains:
                - ``stemflow_task_id`` (str): The unique ID for the initiated task.
                - ``error`` (bool): Indicates if the initial API request failed.
                - ``message`` (str): Status message from the API.

        Raises:
            Exception: If the API returns an error status code, e.g. HTTP 402
                if the caller has insufficient credits.

        Example:
            >>> from roex_python.models import StemSeparationRequest
            >>> # Assume 'client' is an initialized RoExClient
            >>> task = client.stem_separation.create_separation(
            ...     StemSeparationRequest(audio_file_location="https://example.com/song.wav")
            ... )
            >>> print(f"Separation task started with ID: {task.stemflow_task_id}")
        """
        logger.info("Submitting stem separation task.")
        payload = {"stemflowData": {"audioFileLocation": request.audio_file_location}}

        try:
            response = self.api_provider.post("/separate", payload)
            logger.info(
                f"Stem separation task submitted. Task ID: {response.get('stemflowTaskId', '')}"
            )
            return StemSeparationTaskResponse(
                stemflow_task_id=response.get("stemflowTaskId", ""),
                error=response.get("error", False),
                message=response.get("message", ""),
            )
        except requests.HTTPError as e:
            logger.error(f"Failed to submit stem separation task: {str(e)}")
            raise Exception(f"Failed to submit stem separation task: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error submitting stem separation task: {e}")
            raise

    def get_separation_status(self, stemflow_task_id: str) -> StemSeparationStatusResult:
        """
        Check the status of a stem separation task.

        Sends a request to ``GET /separatestatus/{stemflow_task_id}``.

        Args:
            stemflow_task_id (str): The task ID returned by ``create_separation``.

        Returns:
            StemSeparationStatusResult: ``status`` is one of ``"processing"``,
                ``"complete"``, or ``"failed"``. When ``"failed"``, ``error``
                is True and ``info`` may contain failure details.

        Raises:
            Exception: If the API returns an error status, e.g. HTTP 404 if
                the task doesn't exist or isn't owned by this API key.

        Example:
            >>> status = client.stem_separation.get_separation_status(task.stemflow_task_id)
            >>> print(status.status)
        """
        logger.debug(f"Checking stem separation status for task ID: {stemflow_task_id}")

        try:
            response = self.api_provider.get(f"/separatestatus/{stemflow_task_id}")
            return StemSeparationStatusResult(
                stemflow_task_id=response.get("stemflowTaskId", stemflow_task_id),
                status=response.get("status", "unknown"),
                error=response.get("error", False),
                message=response.get("message", ""),
                info=response.get("info", ""),
            )
        except requests.HTTPError as e:
            logger.error(f"Failed to get stem separation status: {str(e)}")
            raise Exception(f"Failed to get stem separation status: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error getting stem separation status: {e}")
            raise

    def wait_for_separation(
        self, stemflow_task_id: str, poll_interval: int = 15, timeout: int = 1200
    ) -> StemSeparationStatusResult:
        """
        Poll ``get_separation_status`` until the task completes, fails, or times out.

        Stem separation runs on a GPU worker and can take several minutes,
        including cold-start time; the defaults are sized accordingly.

        Args:
            stemflow_task_id (str): The task ID returned by ``create_separation``.
            poll_interval (int): Seconds to wait between status checks. Defaults to 15.
            timeout (int): Maximum seconds to wait for task completion.
                Defaults to 1200 (20 minutes).

        Returns:
            StemSeparationStatusResult: The status result once ``status`` is
                ``"complete"``.

        Raises:
            Exception: If the task reports ``status == "failed"``, or does
                not complete within ``timeout`` seconds.

        Example:
            >>> client.stem_separation.wait_for_separation(task.stemflow_task_id)
            >>> stems = client.stem_separation.retrieve_stems(task.stemflow_task_id)
        """
        # One check happens up front, then one more after each sleep, so the
        # last check lands at (or just after) the deadline itself instead of
        # `max_sleeps` sleeps being spent without ever re-checking status.
        max_sleeps = max(1, timeout // poll_interval)
        for attempt in range(max_sleeps + 1):
            result = self.get_separation_status(stemflow_task_id)

            if result.status == "complete":
                logger.info(f"Stem separation task {stemflow_task_id} complete.")
                return result
            if result.status == "failed":
                logger.error(f"Stem separation task {stemflow_task_id} failed: {result.info}")
                raise Exception(
                    f"Stem separation task {stemflow_task_id} failed: "
                    f"{result.info or result.message}"
                )

            if attempt < max_sleeps:
                logger.debug(
                    f"Stem separation task {stemflow_task_id} still processing "
                    f"(attempt {attempt + 1}/{max_sleeps + 1})."
                )
                time.sleep(poll_interval)

        logger.error(f"Stem separation task {stemflow_task_id} did not complete after polling.")
        raise Exception(
            f"Stem separation task {stemflow_task_id} did not complete after polling for {timeout} seconds."
        )

    def retrieve_stems(self, stemflow_task_id: str) -> SeparatedStemsResult:
        """
        Retrieve the separated stem URLs for a completed separation task.

        Sends a request to ``POST /retrievestems``. Free to call; safe to
        call repeatedly. Call ``wait_for_separation`` (or poll
        ``get_separation_status`` yourself) first to ensure the task has
        completed.

        Args:
            stemflow_task_id (str): The task ID returned by ``create_separation``.

        Returns:
            SeparatedStemsResult: Signed URLs (valid for ~24 hours) for the
                ``vocals``, ``bass``, ``drums``, and ``other`` stems.

        Raises:
            Exception: If the task is not yet complete, or the API returns
                an error, e.g. HTTP 404 for an unknown/unowned task.

        Example:
            >>> stems = client.stem_separation.retrieve_stems(task.stemflow_task_id)
            >>> print(stems.vocals)
        """
        logger.info(f"Retrieving separated stems for task ID: {stemflow_task_id}")
        payload = {"stemflowData": {"stemflowTaskId": stemflow_task_id}}

        try:
            response = self.api_provider.post("/retrievestems", payload)
            if response.get("error", False):
                message = response.get("message", "Stem separation is not complete yet.")
                logger.warning(f"Could not retrieve stems for {stemflow_task_id}: {message}")
                raise Exception(message)

            stems = response.get("stems", {}) or {}
            return SeparatedStemsResult(
                vocals=stems.get("vocals"),
                bass=stems.get("bass"),
                drums=stems.get("drums"),
                other=stems.get("other"),
            )
        except requests.HTTPError as e:
            logger.error(f"Failed to retrieve stems: {str(e)}")
            raise Exception(f"Failed to retrieve stems: {str(e)}")
