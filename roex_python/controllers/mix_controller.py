"""
Controller for multitrack mixing operations
"""

import time
from typing import Dict, Any, List
import logging

import requests

from roex_python.models.mixing import (
    MultitrackMixRequest,
    MultitrackTaskResponse,
    FinalMixRequest,
    TrackData,
    TrackGainData
)
from roex_python.providers.api_provider import ApiProvider

# Initialize logger for this module
logger = logging.getLogger(__name__)

class MixController:
    """Controller for managing multitrack mixing operations via the RoEx API."""

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the MixController.

        Typically, this controller is accessed via `client.mix` rather than
        instantiated directly.

        Args:
            api_provider (ApiProvider): An instance of ApiProvider configured with
                the base URL and API key.
        """
        self.api_provider = api_provider
        logger.info("MixController initialized.")

    def create_mix_preview(self, request: MultitrackMixRequest) -> MultitrackTaskResponse:
        """
        Initiate a multitrack mix preview task.

        This method sends the track data and mixing parameters to the RoEx API
        to start an asynchronous mixing process. It returns immediately with a
        task ID, which can be used with `retrieve_preview_mix` to check the status
        and get the results once processing is complete.

        Args:
            request (MultitrackMixRequest): An object containing the list of tracks
                (TrackData) and mixing parameters (musical style, return stems, etc.).
                Track URLs must point to accessible WAV or FLAC files.

        Returns:
            MultitrackTaskResponse: An object containing the unique `multitrack_task_id`
                for the initiated preview task.

        Raises:
            requests.exceptions.RequestException: If the API request fails due to network
                                                 issues or invalid endpoint.
            Exception: If the API returns an error response (e.g., 4xx, 5xx status codes)
                       indicating issues like invalid input, authentication failure, or
                       server errors.

        Example:
            >>> from roex_python.models import TrackData, MultitrackMixRequest, MusicalStyle, InstrumentGroup
            >>> # Assume 'client' is an initialized RoExClient
            >>> # Assume 'track_url_1', 'track_url_2' are URLs obtained after uploading local files
            >>> tracks = [
            ...     TrackData(track_url=track_url_1, instrument_group=InstrumentGroup.BASS_GROUP),
            ...     TrackData(track_url=track_url_2, instrument_group=InstrumentGroup.VOCAL_GROUP)
            ... ]
            >>> mix_request = MultitrackMixRequest(
            ...     track_data=tracks,
            ...     musical_style=MusicalStyle.POP,
            ...     return_stems=False
            ... )
            >>> try:
            >>>     task_response = client.mix.create_mix_preview(mix_request)
            >>>     print(f"Mix preview task started: {task_response.multitrack_task_id}")
            >>>     # Proceed to poll using retrieve_preview_mix with this task_id
            >>> except Exception as e:
            >>>     print(f"Error starting mix preview: {e}")

        """
        logger.info("Creating mix preview")
        logger.debug(f"Mix request data: {request}")
        payload = self._prepare_mix_preview_payload(request)

        try:
            response = self.api_provider.post("/mixpreview", payload)
            logger.info(f"Mix preview created successfully. Task ID: {response.get('multitrack_task_id', '')}")
            return MultitrackTaskResponse(
                multitrack_task_id=response.get("multitrack_task_id", "")
            )
        except requests.HTTPError as e:
            # Log specific HTTP errors
            logger.error(f"HTTP error creating mix preview: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to create mix preview: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            # Catch other potential exceptions (e.g., connection errors)
            logger.exception(f"Unexpected error creating mix preview: {e}")
            raise

    def retrieve_preview_mix(self, task_id: str, retrieve_fx_settings: bool = False,
                             max_attempts: int = 30, poll_interval: int = 5) -> Dict[str, Any]:
        """
        Retrieve the results of a multitrack mix preview task, polling until complete.

        This method checks the status of a mix preview task initiated by
        `create_mix_preview`. It polls the API endpoint periodically until the task
        status indicates completion (or failure) or the maximum number of attempts
        is reached.

        Args:
            task_id (str): The `multitrack_task_id` obtained from the
                `create_mix_preview` response.
            retrieve_fx_settings (bool, optional): Whether to retrieve detailed FX settings
                applied during the mix. Note: This might incur additional charges
                depending on the API plan. Defaults to False.
            max_attempts (int, optional): The maximum number of times to poll the API
                before timing out. Defaults to 30.
            poll_interval (int, optional): The number of seconds to wait between
                polling attempts. Defaults to 5.

        Returns:
            Dict[str, Any]: A dictionary containing the results of the preview mix task.
                The structure typically includes:
                - 'status': The final status of the task (e.g., 'MIX_TASK_PREVIEW_COMPLETED').
                - 'previewMixDownloadUrl': URL to download the preview mix audio file.
                - 'stemsDownloadUrl': URL to download stems (if requested).
                - 'settings': Applied settings (gain, pan, etc.).
                - 'fxSettings': Detailed FX settings (if requested and available).
                Check the official RoEx API documentation for the exact structure.

        Raises:
            requests.exceptions.RequestException: If an API request fails during polling.
            Exception: If the task does not complete successfully within the
                       `max_attempts` or if the API returns an error during polling.
                       Also raised for other API errors (4xx/5xx).

        Example:
            >>> # Assume 'client' is an initialized RoExClient
            >>> # Assume 'task_id' was obtained from create_mix_preview
            >>> try:
            >>>     preview_results = client.mix.retrieve_preview_mix(task_id)
            >>>     print(f"Preview Status: {preview_results.get('status')}")
            >>>     print(f"Preview Download URL: {preview_results.get('previewMixDownloadUrl')}")
            >>>     # Further process the results (e.g., download the file)
            >>> except Exception as e:
            >>>     print(f"Error retrieving mix preview: {e}")

        """
        logger.info(f"Retrieving preview mix for task ID: {task_id}")
        payload = {
            "multitrackData": {
                "multitrackTaskId": task_id,
                "retrieveFXSettings": retrieve_fx_settings
            }
        }

        # Initial request
        try:
            response = self.api_provider.post("/retrievepreviewmix", payload)

            # Check if the mix is already complete
            if "previewMixTaskResults" in response and response.get("status") == "MIX_TASK_PREVIEW_COMPLETED":
                logger.info(f"Preview mix for task {task_id} is ready.")
                return response["previewMixTaskResults"]

            # If status code is 200 but no results, it might still be processing
            if "status" in response and response.get("status") != "MIX_TASK_PREVIEW_COMPLETED":
                logger.info(f"Mix preview is pending. Starting polling...")
            else:
                # If the response doesn't indicate it's processing, return it as is
                return response
        except requests.HTTPError:
            # Initial request failed, let's try polling
            logger.error("Initial request failed. Starting polling...")
            pass

        # Poll for results
        for attempt in range(max_attempts):
            try:
                logger.debug(f"Polling attempt {attempt + 1}/{max_attempts}...")
                response = self.api_provider.post("/retrievepreviewmix", payload)

                # Check if the mix is complete
                if "previewMixTaskResults" in response:
                    results = response["previewMixTaskResults"]
                    status = results.get("status", "")
                    if status == "MIX_TASK_PREVIEW_COMPLETED":
                        logger.info(f"Preview mix for task {task_id} is ready.")
                        return results

                # Check if it's still processing
                if "status" in response:
                    logger.info(f"Current status: {response.get('status')}")
            except requests.HTTPError as e:
                logger.error(f"Error during polling: {str(e)}")

            # Wait before next attempt
            time.sleep(poll_interval)

        logger.error(f"Polling timed out for preview mix task {task_id} after {max_attempts} attempts.")
        raise Exception(f"Preview mix task {task_id} did not complete after polling for {max_attempts * poll_interval} seconds.")

    def retrieve_final_mix(self, request: FinalMixRequest) -> Dict[str, Any]:
        """
        Retrieve the final multitrack mix, potentially with gain adjustments.

        This method is used to generate the final mix output. It typically follows
        a `create_mix_preview` and `retrieve_preview_mix` sequence, allowing users
        to apply gain adjustments based on the preview before generating the final
        audio file(s).

        Args:
            request (FinalMixRequest): An object containing:

                multitrack_task_id (str): The task ID from the original preview.

                gain_adjustments (List[TrackGainData], optional): A list of gain
                    adjustments to apply to specific tracks before final mixing.

                return_stems (bool, optional): Whether to return individual track stems
                    along with the final mix. Defaults according to original preview request if omitted.

        Returns:
            Dict[str, Any]: A dictionary containing the results of the final mix task.
                The structure typically includes:
                - 'status': The status of the final mix generation (e.g., 'FINAL_MIX_COMPLETE').
                - 'finalMixDownloadUrl': URL to download the final mix audio file.
                - 'stemsDownloadUrl': URL to download stems (if requested).
                Check the official RoEx API documentation for the exact structure.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
            Exception: If the API returns an error response (e.g., 4xx, 5xx status codes)
                       indicating issues like invalid input, task not found, or server errors.

        Example:
            >>> from roex_python.models import FinalMixRequest, TrackGainData, InstrumentGroup
            >>> # Assume 'client' is an initialized RoExClient
            >>> # Assume 'task_id' was obtained from create_mix_preview
            >>>
            >>> # Optional: Define gain adjustments based on preview analysis
            >>> adjustments = [
            ...     TrackGainData(instrument_group=InstrumentGroup.BASS_GROUP, gain_db=1.5),
            ...     TrackGainData(instrument_group=InstrumentGroup.VOCAL_GROUP, gain_db=-0.5)
            ... ]
            >>>
            >>> final_mix_request = FinalMixRequest(
            ...     multitrack_task_id=task_id,
            ...     gain_adjustments=adjustments, # Can be None or empty list if no adjustments
            ...     return_stems=True # Optional: Override stem generation
            ... )
            >>>
            >>> try:
            >>>     final_mix_results = client.mix.retrieve_final_mix(final_mix_request)
            >>>     print(f"Final Mix Status: {final_mix_results.get('status')}")
            >>>     print(f"Final Mix URL: {final_mix_results.get('finalMixDownloadUrl')}")
            >>>     # Further process the results
            >>> except Exception as e:
            >>>     print(f"Error retrieving final mix: {e}")

        """
        logger.info(f"Retrieving final mix for task ID: {request.multitrack_task_id}")
        logger.debug(f"Final mix request data: {request}")
        payload = self._prepare_final_mix_payload(request)

        try:
            response = self.api_provider.post("/retrievefinalmix", payload)
            logger.info("Final mix retrieved successfully.")
            if "applyAudioEffectsResults" in response:
                return response["applyAudioEffectsResults"]
            return response
        except requests.HTTPError as e:
            # Log specific HTTP errors
            logger.error(f"HTTP error retrieving final mix: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to retrieve final mix: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            # Catch other potential exceptions
            logger.exception(f"Unexpected error retrieving final mix: {e}")
            raise

    def _prepare_mix_preview_payload(self, request: MultitrackMixRequest) -> Dict[str, Any]:
        """
        Convert the model to API payload for mix preview

        Args:
            request (MultitrackMixRequest): Multitrack mix request

        Returns:
            API payload dictionary
        """
        logger.debug("Preparing mix preview payload")
        track_data = []
        for track in request.track_data:
            track_data.append({
                "trackURL": track.track_url,
                "instrumentGroup": track.instrument_group.value,
                "presenceSetting": track.presence_setting.value,
                "panPreference": track.pan_preference.value,
                "reverbPreference": track.reverb_preference.value
            })

        return {
            "multitrackData": {
                "trackData": track_data,
                "musicalStyle": request.musical_style.value,
                "returnStems": request.return_stems,
                "sampleRate": request.sample_rate,
                "webhookURL": request.webhook_url
            }
        }

    def _prepare_final_mix_payload(self, request: FinalMixRequest) -> Dict[str, Any]:
        """
        Convert the model to API payload for final mix

        Args:
            request (FinalMixRequest): Final mix request

        Returns:
            API payload dictionary
        """
        logger.debug("Preparing final mix payload")
        track_data = []
        for track in request.track_data:
            track_data.append({
                "trackURL": track.track_url,
                "gainDb": track.gain_db
            })

        return {
            "applyAudioEffectsData": {
                "multitrackTaskId": request.multitrack_task_id,
                "trackData": track_data,
                "returnStems": request.return_stems,
                "sampleRate": request.sample_rate
            }
        }