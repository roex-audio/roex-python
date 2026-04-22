"""
Controller for mastering operations
"""

import os
import time
from typing import Dict, Any, List

import logging
import requests

from roex_python.models.mastering import (
    AlbumMasteringRequest,
    FinalMasterResult,
    MasteringRequest,
    MasteringTaskResponse,
    PreviewMasterResult
)
from roex_python.providers.api_provider import ApiProvider

# Initialize logger for this module
logger = logging.getLogger(__name__)

class MasteringController:
    """Controller for managing audio mastering operations via the RoEx API."""

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the MasteringController.

        Typically, this controller is accessed via `client.mastering` rather than
        instantiated directly.

        Args:
            api_provider (ApiProvider): An instance of ApiProvider configured with
                the base URL and API key.
        """
        self.api_provider = api_provider
        logger.info("MasteringController initialized.")

    def create_mastering_preview(self, request: MasteringRequest) -> MasteringTaskResponse:
        """
        Initiate an audio mastering preview task.

        Sends the track URL and mastering parameters (style, loudness, etc.)
        to the RoEx API to start an asynchronous mastering process. Returns
        immediately with a task ID for polling results.

        Args:
            request (MasteringRequest): An object containing the track URL and
                mastering parameters (MusicalStyle, DesiredLoudness, etc.).
                The track URL must point to an accessible WAV or FLAC file.

        Returns:
            MasteringTaskResponse: An object containing the unique `mastering_task_id`
                for the initiated preview task.

        Raises:
            requests.exceptions.RequestException: If the API request fails due to network
                                                 issues or invalid endpoint.
            Exception: If the API returns an error response (e.g., 4xx, 5xx status codes)
                       indicating issues like invalid input, authentication failure, or
                       server errors.

        Example:
            >>> from roex_python.models import MasteringRequest, MusicalStyle, DesiredLoudness
            >>> # Assume 'client' is an initialized RoExClient
            >>> # Assume 'track_url' is a URL obtained after uploading a local file
            >>> master_request = MasteringRequest(
            ...     track_url=track_url,
            ...     musical_style=MusicalStyle.ELECTRONIC_EDM,
            ...     desired_loudness=DesiredLoudness.HIGH,
            ...     sample_rate="48000"
            ... )
            >>> try:
            >>>     task_response = client.mastering.create_mastering_preview(master_request)
            >>>     print(f"Mastering preview task started: {task_response.mastering_task_id}")
            >>>     # Proceed to poll using retrieve_preview_master with this task_id
            >>> except Exception as e:
            >>>     print(f"Error starting mastering preview: {e}")
        """
        logger.info("Creating mastering preview")
        logger.debug(f"Mastering preview request data: {request}")
        data = {
            "trackData": [
                {
                    "trackURL": request.track_url
                }
            ],
            "musicalStyle": request.musical_style.value,
            "desiredLoudness": request.desired_loudness.value,
            "sampleRate": request.sample_rate,
        }
        if request.webhook_url is not None:
            data["webhookURL"] = request.webhook_url
        payload = {"masteringData": data}

        try:
            response = self.api_provider.post("/masteringpreview", payload)
            logger.info(f"Mastering preview task created successfully. Task ID: {response.get('mastering_task_id', '')}")
            return MasteringTaskResponse(
                mastering_task_id=response.get("mastering_task_id", "")
            )
        except requests.HTTPError as e:
            logger.exception(f"HTTP error creating mastering preview task: {e}")
            raise Exception(f"Failed to create mastering preview: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error creating mastering preview task: {e}")
            raise

    def retrieve_preview_master(self, task_id: str, max_attempts: int = 30,
                                poll_interval: int = 5) -> PreviewMasterResult:
        """
        Retrieve the results of a mastering preview task, polling until complete.

        Polls the ``/retrievepreviewmaster`` endpoint until
        ``previewMasterTaskResults`` is present or *max_attempts* is exhausted.

        Args:
            task_id (str): The ``mastering_task_id`` from ``create_mastering_preview``.
            max_attempts (int): Maximum polling iterations. Defaults to 30.
            poll_interval (int): Seconds between polls. Defaults to 5.

        Returns:
            PreviewMasterResult: A typed result containing:
                - ``download_url_mastered_preview`` (Optional[str]): Signed URL for the mastered preview.
                - ``preview_start_time`` (Optional[float]): Offset in seconds where the
                  preview clip starts in the original track.

        Raises:
            Exception: If the task does not complete within *max_attempts* polls.

        Example:
            >>> result = client.mastering.retrieve_preview_master(task_id)
            >>> print(result.download_url_mastered_preview)
        """
        logger.info(f"Retrieving preview master for task ID: {task_id}")
        payload = {
            "masteringData": {
                "masteringTaskId": task_id
            }
        }

        def _parse(raw: Dict[str, Any]) -> PreviewMasterResult:
            return PreviewMasterResult(
                download_url_mastered_preview=raw.get("download_url_mastered_preview"),
                preview_start_time=raw.get("preview_start_time"),
            )

        try:
            response = self.api_provider.post("/retrievepreviewmaster", payload)
            if "previewMasterTaskResults" in response:
                logger.info(f"Preview master ready for task ID: {task_id}")
                return _parse(response["previewMasterTaskResults"])
        except requests.HTTPError:
            logger.warning(f"Initial request failed for task ID: {task_id}. Starting polling...")
            pass

        for attempt in range(max_attempts):
            try:
                logger.debug(f"Polling attempt {attempt + 1}/{max_attempts} for task ID: {task_id}")
                response = self.api_provider.post("/retrievepreviewmaster", payload)

                if "previewMasterTaskResults" in response:
                    logger.info(f"Preview master ready for task ID: {task_id}")
                    return _parse(response["previewMasterTaskResults"])

                status_code = response.get("status", 0)
                if status_code == 202:
                    logger.info(f"Task still processing for task ID: {task_id}...")
            except requests.HTTPError as e:
                logger.error(f"Error during polling for task ID: {task_id}: {e}")
            except Exception as e:
                logger.exception(f"Unexpected error during polling for task ID: {task_id}: {e}")

            time.sleep(poll_interval)

        logger.error(f"Timeout waiting for preview master for task ID: {task_id} after {max_attempts} attempts.")
        raise Exception(f"Preview master task {task_id} did not complete after polling for {max_attempts * poll_interval} seconds.")

    def retrieve_final_master(self, task_id: str) -> FinalMasterResult:
        """
        Retrieve the final mastered audio file.

        Fetches the result from ``/retrievefinalmaster``. Call after
        ``create_mastering_preview`` and ``retrieve_preview_master`` have
        confirmed the task is done.

        Args:
            task_id (str): The ``mastering_task_id`` from ``create_mastering_preview``.

        Returns:
            FinalMasterResult: A typed result containing:
                - ``download_url_mastered`` (Optional[str]): Signed URL for the final
                  mastered audio file.

        Raises:
            Exception: If the API returns an error response.

        Example:
            >>> result = client.mastering.retrieve_final_master(task_id)
            >>> print(result.download_url_mastered)
        """
        logger.info(f"Retrieving final master for task ID: {task_id}")
        payload = {
            "masteringData": {
                "masteringTaskId": task_id
            }
        }

        try:
            response = self.api_provider.post("/retrievefinalmaster", payload)

            if "finalMasterTaskResults" in response:
                raw = response["finalMasterTaskResults"]
                logger.info(f"Final master ready for task ID: {task_id}")
                return FinalMasterResult(
                    download_url_mastered=raw.get("download_url_mastered"),
                )
            elif isinstance(response, dict) and "download_url_mastered" in response:
                logger.info(f"Final master ready for task ID: {task_id}")
                return FinalMasterResult(
                    download_url_mastered=response.get("download_url_mastered"),
                )

            logger.warning(f"Unknown response format for task ID: {task_id}. Returning empty result.")
            return FinalMasterResult()
        except requests.HTTPError as e:
            logger.exception(f"HTTP error retrieving final master for task ID: {task_id}: {e}")
            raise Exception(f"Failed to retrieve final master: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error retrieving final master for task ID: {task_id}: {e}")
            raise

    def process_album(self, album_request: AlbumMasteringRequest, output_dir: str = "final_masters") -> Dict[int, Any]:
        """
        Process multiple tracks as an album

        Args:
            album_request: Album mastering request containing multiple tracks
            output_dir: Directory to save downloaded masters

        Returns:
            Dictionary mapping track index to download URL

        Raises:
            Exception: If any track processing fails
        """
        logger.info(f"Processing album with {len(album_request.tracks)} tracks")
        os.makedirs(output_dir, exist_ok=True)
        results = {}

        for idx, track_request in enumerate(album_request.tracks, start=1):
            logger.info(f"Starting mastering for Track #{idx}")

            # Create preview
            preview_response = self.create_mastering_preview(track_request)
            task_id = preview_response.mastering_task_id

            # Wait for preview to complete
            try:
                preview_results = self.retrieve_preview_master(task_id)
                logger.info(f"Preview master ready for Track #{idx}")
            except Exception as e:
                logger.warning(f"Could not retrieve preview for Track #{idx}: {e}")
                # Continue to final master anyway

            # Get final master
            try:
                final_url = self.retrieve_final_master(task_id).download_url_mastered
                results[idx] = final_url

                # Download the file
                if isinstance(final_url, str) and (final_url.startswith("http://") or final_url.startswith("https://")):
                    local_filename = os.path.join(output_dir, f"final_master_track_{idx}.wav")
                    self.api_provider.download_file(final_url, local_filename)
                    logger.info(f"Downloaded Track #{idx} to {local_filename}")
                else:
                    logger.warning(f"Final URL for Track #{idx} is not a valid URL: {final_url}")
            except Exception as e:
                logger.error(f"Error processing Track #{idx}: {e}")

        return results