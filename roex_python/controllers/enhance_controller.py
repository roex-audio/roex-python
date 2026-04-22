"""
Controller for mix enhancement operations
"""

import os
import time
from typing import Dict, Any, List
import logging

import requests

from roex_python.models.enhance import EnhancedTrackResult, MixEnhanceRequest, MixEnhanceResponse
from roex_python.providers.api_provider import ApiProvider

# Initialize logger for this module
logger = logging.getLogger(__name__)

class EnhanceController:
    """Controller for initiating and managing mix enhancement (mix revive) tasks via the RoEx API."""

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the EnhanceController.

        Typically, this controller is accessed via `client.enhance` rather than
        instantiated directly.

        Args:
            api_provider (ApiProvider): An instance of ApiProvider configured with
                the base URL and API key.
        """
        self.api_provider = api_provider
        logger.info("EnhanceController initialized.")

    def create_mix_enhance_preview(self, request: MixEnhanceRequest) -> MixEnhanceResponse:
        """
        Initiate a mix enhancement preview task.

        This method sends a request to the RoEx API to start a preview version
        of the mix enhancement process. It's asynchronous and returns a task ID
        immediately. The actual enhanced preview audio needs to be retrieved later
        using the `retrieve_enhanced_track` method with the returned task ID.

        Args:
            request (MixEnhanceRequest): An object containing the parameters for
                the enhancement preview, including:
                - `audio_file_location` (str): URL of the audio file.
                - `musical_style` (EnhanceMusicalStyle): Target musical style.
                - `is_master` (bool): Whether the input is already mastered.
                - `fix_..._issues` (bool): Flags to control specific fixes.
                - `apply_mastering` (bool): Whether to apply mastering.
                - `loudness_preference` (LoudnessPreference): Target loudness.
                - `stem_processing` (bool): If True, generate stems (preview not guaranteed to contain full stems).
                - `webhook_url` (Optional[str]): URL for task completion notification.

        Returns:
            MixEnhanceResponse: An object containing:
                - `mixrevive_task_id` (str): The unique ID for the initiated task.
                - `error` (bool): Indicates if the initial API request failed.
                - `message` (str): Status message from the API.

        Raises:
            requests.exceptions.RequestException: Network or API endpoint errors.
            Exception: If the API returns an error status code (4xx, 5xx).

        Example:
            >>> from roex_python.models import MixEnhanceRequest, EnhanceMusicalStyle, LoudnessPreference
            >>> # Assume 'client' is an initialized RoExClient
            >>> enhance_req = MixEnhanceRequest(
            ...     audio_file_location="https://example.com/my_mix.wav",
            ...     musical_style=EnhanceMusicalStyle.POP,
            ...     loudness_preference=LoudnessPreference.STREAMING_LOUDNESS,
            ...     stem_processing=False  # Typically False for preview
            ... )
            >>> try:
            >>>     response = client.enhance.create_mix_enhance_preview(enhance_req)
            >>>     if not response.error:
            >>>         task_id = response.mixrevive_task_id
            >>>         print(f"Enhancement preview task started with ID: {task_id}")
            >>>         # Proceed to poll using retrieve_enhanced_track(task_id)
            >>>     else:
            >>>         print(f"API Error: {response.message}")
            >>> except Exception as e:
            >>>     print(f"An error occurred: {e}")
        """
        logger.info("Initiating mix enhancement preview.")
        logger.debug(f"Mix enhance request data: {request}")
        payload = self._prepare_mix_enhance_payload(request)

        try:
            response = self.api_provider.post("/mixenhancepreview", payload)
            logger.info(f"Mix enhance preview created successfully. Task ID: {response.get('mixrevive_task_id', '')}")
            return MixEnhanceResponse(
                mixrevive_task_id=response.get("mixrevive_task_id", ""),
                error=response.get("error", False),
                message=response.get("message", "")
            )
        except requests.HTTPError as e:
            logger.error(f"Failed to create mix enhance preview: {str(e)}")
            raise Exception(f"Failed to create mix enhance preview: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error creating mix enhance preview: {e}")
            raise

    def create_mix_enhance(self, request: MixEnhanceRequest) -> MixEnhanceResponse:
        """
        Initiate a full mix enhancement task.

        This method sends a request to the RoEx API to start the complete mix
        enhancement process. Similar to the preview, it's asynchronous and returns
        a task ID. The final enhanced audio (and potentially stems) must be retrieved
        later using `retrieve_enhanced_track`.

        Args:
            request (MixEnhanceRequest): An object containing the parameters for
                the full enhancement, including:
                - `audio_file_location` (str): URL of the audio file.
                - `musical_style` (EnhanceMusicalStyle): Target musical style.
                - `is_master` (bool): Whether the input is already mastered.
                - `fix_..._issues` (bool): Flags to control specific fixes.
                - `apply_mastering` (bool): Whether to apply mastering.
                - `loudness_preference` (LoudnessPreference): Target loudness.
                - `stem_processing` (bool): If True, also generate stems (vocals, bass, drums, other).
                - `webhook_url` (Optional[str]): URL for task completion notification.

        Returns:
            MixEnhanceResponse: An object containing:
                - `mixrevive_task_id` (str): The unique ID for the initiated task.
                - `error` (bool): Indicates if the initial API request failed.
                - `message` (str): Status message from the API.

        Raises:
            requests.exceptions.RequestException: Network or API endpoint errors.
            Exception: If the API returns an error status code (4xx, 5xx).

        Example:
            >>> from roex_python.models import MixEnhanceRequest, EnhanceMusicalStyle
            >>> # Assume 'client' is an initialized RoExClient
            >>> enhance_req = MixEnhanceRequest(
            ...     audio_file_location="https://example.com/my_final_mix.wav",
            ...     musical_style=EnhanceMusicalStyle.ROCK_INDIE,
            ...     apply_mastering=True,
            ...     stem_processing=True # Request stems along with the enhanced mix
            ... )
            >>> try:
            >>>     response = client.enhance.create_mix_enhance(enhance_req)
            >>>     if not response.error:
            >>>         task_id = response.mixrevive_task_id
            >>>         print(f"Full enhancement task started with ID: {task_id}")
            >>>         # Proceed to poll using retrieve_enhanced_track(task_id)
            >>>     else:
            >>>         print(f"API Error: {response.message}")
            >>> except Exception as e:
            >>>     print(f"An error occurred: {e}")
        """
        logger.info("Initiating full mix enhancement.")
        logger.debug(f"Mix enhance request data: {request}")
        payload = self._prepare_mix_enhance_payload(request)

        try:
            response = self.api_provider.post("/mixenhance", payload)
            logger.info(f"Mix enhance created successfully. Task ID: {response.get('mixrevive_task_id', '')}")
            return MixEnhanceResponse(
                mixrevive_task_id=response.get("mixrevive_task_id", ""),
                error=response.get("error", False),
                message=response.get("message", "")
            )
        except requests.HTTPError as e:
            logger.error(f"Failed to create mix enhance: {str(e)}")
            raise Exception(f"Failed to create mix enhance: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error creating mix enhance: {e}")
            raise

    def retrieve_enhanced_track(self, task_id: str, poll_interval: int = 5, timeout: int = 600) -> EnhancedTrackResult:
        """
        Retrieve the results of a mix enhancement task (preview or full).

        Polls the ``/retrieveenhancedtrack`` endpoint until results are ready
        or the *timeout* is reached.

        Args:
            task_id (str): The unique ID of the enhancement task (obtained from
                ``create_mix_enhance_preview`` or ``create_mix_enhance``).
            poll_interval (int): Seconds to wait between status checks. Defaults to 5.
            timeout (int): Maximum seconds to wait for task completion. Defaults to 600 (10 minutes).

        Returns:
            EnhancedTrackResult: A typed result containing:
                - ``download_url_preview_revived`` (Optional[str]): Signed URL for the MP3 preview.
                - ``download_url_revived`` (Optional[str]): Signed URL for the full WAV file.
                - ``stems`` (Optional[Dict[str, str]]): URLs keyed by stem name
                  (``vocal``, ``bass``, ``drums``, ``other``) when stem processing was requested.
                - ``preview_start_time`` (Optional[float]): Offset in seconds where
                  the preview clip begins in the original track.

        Raises:
            Exception: If the task does not complete within the specified *timeout*,
                or the API returns an error during polling.

        Example:
            >>> result = client.enhance.retrieve_enhanced_track(task_id)
            >>> print(result.download_url_preview_revived)
            >>> if result.stems:
            ...     for name, url in result.stems.items():
            ...         print(f"{name}: {url}")
        """
        logger.info(f"Attempting to retrieve results for task ID: {task_id}")
        payload = {
            "mixReviveData": {
                "mixReviveTaskId": task_id
            }
        }

        for attempt in range(timeout // poll_interval):
            try:
                logger.debug(f"Polling attempt {attempt + 1}/{timeout // poll_interval}...")
                response = self.api_provider.post("/retrieveenhancedtrack", payload)

                if not response.get("error", False):
                    results = response.get("revivedTrackTaskResults", {})
                    has_url = (
                        results.get("download_url_preview_revived")
                        or results.get("download_url_revived")
                    )
                    if results and has_url:
                        logger.info(f"Enhanced track retrieved successfully for task ID: {task_id}")
                        return EnhancedTrackResult(
                            download_url_preview_revived=results.get("download_url_preview_revived"),
                            download_url_revived=results.get("download_url_revived"),
                            stems=results.get("stems"),
                            preview_start_time=results.get("preview_start_time"),
                        )
            except requests.HTTPError as e:
                logger.error(f"Error during polling: {str(e)}")
            except Exception as e:
                logger.exception(f"Unexpected error during polling for task ID: {task_id}: {e}")

            time.sleep(poll_interval)

        logger.error(f"Enhanced track was not available after polling for task ID: {task_id}.")
        raise Exception(f"Enhanced track task {task_id} did not complete after polling for {timeout} seconds.")

    def _prepare_mix_enhance_payload(self, request: MixEnhanceRequest) -> Dict[str, Any]:
        """
        Convert the model to API payload for mix enhance

        Args:
            request: Mix enhance request

        Returns:
            API payload dictionary
        """
        logger.debug(f"Preparing mix enhance payload for request: {request}")
        data = {
            "audioFileLocation": request.audio_file_location,
            "musicalStyle": request.musical_style.value,
            "isMaster": request.is_master,
            "fixClippingIssues": request.fix_clipping_issues,
            "fixStereoWidthIssues": request.fix_stereo_width_issues,
            "fixTonalProfileIssues": request.fix_tonal_profile_issues,
            "fixLoudnessIssues": request.fix_loudness_issues,
            "applyMastering": request.apply_mastering,
            "applyDrumEnhancement": request.apply_drum_enhancement,
            "applyVocalEnhancement": request.apply_vocal_enhancement,
            "loudnessPreference": request.loudness_preference.value,
            "stemProcessing": request.stem_processing,
            "getProcessedStems": request.get_processed_stems
        }
        if request.webhook_url is not None:
            data["webhookURL"] = request.webhook_url
        return {"mixReviveData": data}
