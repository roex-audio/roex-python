"""
Controller for mastering operations
"""

import os
import time
from typing import Dict, Any, List

import logging
import requests

from roex_python.models.mastering import (
    MasteringRequest,
    MasteringTaskResponse,
    AlbumMasteringRequest
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
        payload = {
            "masteringData": {
                "trackData": [
                    {
                        "trackURL": request.track_url
                    }
                ],
                "musicalStyle": request.musical_style.value,
                "desiredLoudness": request.desired_loudness.value,
                "sampleRate": request.sample_rate,
                "webhookURL": request.webhook_url
            }
        }

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
                                poll_interval: int = 5) -> Dict[str, Any]:
        """
        Retrieve the results of a mastering preview task, polling until complete.

        Checks the status of a mastering task initiated by `create_mastering_preview`.
        Polls the API periodically until the task completes or the maximum number
        of attempts is reached.

        Args:
            task_id (str): The `mastering_task_id` obtained from the
                `create_mastering_preview` response.
            max_attempts (int, optional): Maximum number of polling attempts before
                timing out. Defaults to 30.
            poll_interval (int, optional): Seconds to wait between polling attempts.
                Defaults to 5.

        Returns:
            Dict[str, Any]: A dictionary containing the results of the preview master.
                Key fields typically include:
                - 'status': Final status (e.g., 'MASTERING_TASK_PREVIEW_COMPLETED').
                - 'download_url_mastered_preview': URL to download the preview audio.
                Check the official RoEx API documentation for the exact structure.

        Raises:
            requests.exceptions.RequestException: If an API request fails during polling.
            Exception: If the task does not complete successfully within `max_attempts`,
                       if the API returns an error during polling, or for other
                       API errors (4xx/5xx).

        Example:
            >>> # Assume 'client' is an initialized RoExClient
            >>> # Assume 'task_id' was obtained from create_mastering_preview
            >>> try:
            >>>     master_results = client.mastering.retrieve_preview_master(task_id)
            >>>     print(f"Mastering Preview Status: {master_results.get('status')}")
            >>>     print(f"Preview Download URL: {master_results.get('download_url_mastered_preview')}")
            >>>     # Further process the results (e.g., download the file)
            >>> except Exception as e:
            >>>     print(f"Error retrieving mastering preview: {e}")
        """
        logger.info(f"Retrieving preview master for task ID: {task_id}")
        payload = {
            "masteringData": {
                "masteringTaskId": task_id
            }
        }

        # Try initial request
        try:
            response = self.api_provider.post("/retrievepreviewmaster", payload)
            if "previewMasterTaskResults" in response:
                logger.info(f"Preview master ready for task ID: {task_id}")
                return response["previewMasterTaskResults"]
        except requests.HTTPError:
            # Initial request failed, let's try polling
            logger.warning(f"Initial request failed for task ID: {task_id}. Starting polling...")
            pass

        # Poll for results
        for attempt in range(max_attempts):
            try:
                logger.debug(f"Polling attempt {attempt + 1}/{max_attempts} for task ID: {task_id}")
                response = self.api_provider.post("/retrievepreviewmaster", payload)

                # If we get a 200 response with results
                if "previewMasterTaskResults" in response:
                    logger.info(f"Preview master ready for task ID: {task_id}")
                    return response["previewMasterTaskResults"]

                # Check for specific status codes
                status_code = response.get("status", 0)
                if status_code == 202:
                    logger.info(f"Task still processing for task ID: {task_id}...")
                elif status_code == 200:
                    # If we get a 200 but no results, try to parse the response differently
                    if isinstance(response, dict):
                        for key, value in response.items():
                            if isinstance(value, dict) and "download_url_mastered_preview" in value:
                                logger.info(f"Preview master ready for task ID: {task_id}")
                                return value
            except requests.HTTPError as e:
                logger.error(f"Error during polling for task ID: {task_id}: {e}")
            except Exception as e:
                logger.exception(f"Unexpected error during polling for task ID: {task_id}: {e}")

            # Wait before next attempt
            time.sleep(poll_interval)

        logger.error(f"Timeout waiting for preview master for task ID: {task_id} after {max_attempts} attempts.")
        raise Exception(f"Preview master task {task_id} did not complete after polling for {max_attempts * poll_interval} seconds.")

    def retrieve_final_master(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve the final mastered audio file.

        This method fetches the final output of a completed mastering task.
        It's typically called after `create_mastering_preview` and potentially
        `retrieve_preview_master` confirm the task is done, although polling
        is not built into this specific retrieval method.

        Args:
            task_id (str): The `mastering_task_id` obtained from the
                `create_mastering_preview` response.

        Returns:
            Dict[str, Any]: A dictionary containing the results of the final master.
                Key fields typically include:
                - 'status': Final status (e.g., 'MASTERING_TASK_FINAL_COMPLETED').
                - 'download_url_mastered_final': URL to download the final audio.
                Check the official RoEx API documentation for the exact structure.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
            Exception: If the API returns an error response (e.g., 4xx, 5xx status codes),
                       indicating issues like task not found, task not complete, or server errors.

        Example:
            >>> # Assume 'client' is an initialized RoExClient
            >>> # Assume 'task_id' was obtained from create_mastering_preview and preview is complete
            >>> try:
            >>>     final_master_results = client.mastering.retrieve_final_master(task_id)
            >>>     print(f"Final Master Status: {final_master_results.get('status')}")
            >>>     print(f"Final Download URL: {final_master_results.get('download_url_mastered_final')}")
            >>>     # Further process the results
            >>> except Exception as e:
            >>>     print(f"Error retrieving final master: {e}")
        """
        logger.info(f"Retrieving final master for task ID: {task_id}")
        payload = {
            "masteringData": {
                "masteringTaskId": task_id
            }
        }

        try:
            response = self.api_provider.post("/retrievefinalmaster", payload)

            # Handle different response formats
            if "finalMasterTaskResults" in response:
                # If it's a structured response
                logger.info(f"Final master ready for task ID: {task_id}")
                return response["finalMasterTaskResults"]
            elif isinstance(response, dict) and "download_url_mastered" in response:
                # If the URL is directly in the response
                logger.info(f"Final master ready for task ID: {task_id}")
                return response["download_url_mastered"]
            elif isinstance(response, str) and (response.startswith("http://") or response.startswith("https://")):
                # If the response is just the URL as a string
                logger.info(f"Final master ready for task ID: {task_id}")
                return response

            # Default fallback
            logger.warning(f"Unknown response format for task ID: {task_id}. Returning raw response.")
            return response
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
                final_url = self.retrieve_final_master(task_id)['download_url_mastered']
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