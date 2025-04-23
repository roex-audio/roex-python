"""
Controller for mix enhancement operations
"""

import os
import time
from typing import Dict, Any, List
import logging

import requests

from roex_python.models.enhance import MixEnhanceRequest, MixEnhanceResponse
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
            ...     musical_style=EnhanceMusicalStyle.ROCK,
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

    def retrieve_enhanced_track(self, task_id: str, poll_interval: int = 5, timeout: int = 600) -> dict:
        """
        Retrieve the results of a mix enhancement task (preview or full).

        This method polls the RoEx API's task status endpoint using the provided
        `task_id`. It waits for the task to complete or until the `timeout` is reached.

        Args:
            task_id (str): The unique ID of the enhancement task (obtained from
                `create_mix_enhance_preview` or `create_mix_enhance`).
            poll_interval (int): Seconds to wait between status checks. Defaults to 5.
            timeout (int): Maximum seconds to wait for task completion. Defaults to 600 (10 minutes).

        Returns:
            dict: A dictionary containing the task results. The structure includes:
                - `status` (str): Final status ('completed', 'failed', etc.).
                - `results` (dict): Contains details upon completion:
                    - `preview_audio_file_location` (Optional[str]): URL for preview audio.
                    - `enhanced_audio_file_location` (Optional[str]): URL for full enhanced audio.
                    - `stems` (Optional[dict]): If `stem_processing` was True in the request,
                      this dictionary contains URLs for individual stems (e.g., `vocals`, `bass`, `drums`, `other`).
                    - `processing_time` (float): Time taken for processing.
                    - `error_message` (Optional[str]): Error details if the task failed.
                - Other task metadata.

        Raises:
            TimeoutError: If the task does not complete within the specified `timeout`.
            requests.exceptions.RequestException: Network or API endpoint errors during polling.
            Exception: If the API returns an error status code (4xx, 5xx) during polling
                       or if the task itself failed.

        Example:
            >>> # Assume 'client' is an initialized RoExClient and 'task_id' was obtained previously
            >>> try:
            >>>     results = client.enhance.retrieve_enhanced_track(task_id)
            >>>     if results.get('status') == 'completed':
            >>>         enhanced_url = results.get('results', {}).get('enhanced_audio_file_location')
            >>>         print(f"Enhancement complete! Audio URL: {enhanced_url}")
            >>>         stems = results.get('results', {}).get('stems')
            >>>         if stems:
            >>>             print(f"Stems generated:")
            >>>             for stem_name, stem_url in stems.items():
            >>>                 print(f"  - {stem_name}: {stem_url}")
            >>>     else:
            >>>         error_msg = results.get('results', {}).get('error_message', 'Unknown error')
            >>>         print(f"Task failed or timed out. Status: {results.get('status')}. Error: {error_msg}")
            >>> except TimeoutError:
            >>>     print("Task timed out.")
            >>> except Exception as e:
            >>>     print(f"An error occurred while retrieving results: {e}")
        """
        logger.info(f"Attempting to retrieve results for task ID: {task_id}")
        payload = {
            "mixReviveData": {
                "mixReviveTaskId": task_id
            }
        }

        # Poll for results
        for attempt in range(timeout // poll_interval):
            try:
                logger.debug(f"Polling attempt {attempt + 1}/{timeout // poll_interval}...")
                response = self.api_provider.post("/retrieveenhancedtrack", payload)

                if not response.get("error", False):
                    results = response.get("revived_track_tasks_results", {})
                    if results:
                        logger.info(f"Enhanced track retrieved successfully for task ID: {task_id}")
                        return results

                    # Some API versions might return a different format
                    for key in response:
                        if isinstance(response[key], dict) and (
                                "download_url_revived" in response[key] or
                                "download_url_preview_revived" in response[key]
                        ):
                            logger.info(f"Enhanced track retrieved successfully for task ID: {task_id}")
                            return response[key]
            except requests.HTTPError as e:
                logger.error(f"Error during polling: {str(e)}")
            except Exception as e:
                logger.exception(f"Unexpected error during polling for task ID: {task_id}: {e}")

            # Wait before next attempt
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
        return {
            "mixReviveData": {
                "audioFileLocation": request.audio_file_location,
                "musicalStyle": request.musical_style.value,
                "isMaster": request.is_master,
                "fixClippingIssues": request.fix_clipping_issues,
                "fixDRCIssues": request.fix_drc_issues,
                "fixStereoWidthIssues": request.fix_stereo_width_issues,
                "fixTonalProfileIssues": request.fix_tonal_profile_issues,
                "fixLoudnessIssues": request.fix_loudness_issues,
                "applyMastering": request.apply_mastering,
                "webhookURL": request.webhook_url,
                "loudnessPreference": request.loudness_preference.value,
                "stemProcessing": request.stem_processing
            }
        }
