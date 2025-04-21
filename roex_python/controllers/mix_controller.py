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
    """Controller for multitrack mixing operations"""

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the mix controller

        Args:
            api_provider: Provider for API interactions
        """
        self.api_provider = api_provider
        logger.info("MixController initialized.")

    def create_mix_preview(self, request: MultitrackMixRequest) -> MultitrackTaskResponse:
        """
        Create a multitrack mix preview

        Args:
            request: Multitrack mix request parameters

        Returns:
            Response containing the multitrack task ID

        Raises:
            Exception: If the API request fails
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
            logger.error(f"Failed to create mix preview: {str(e)}")
            raise Exception(f"Failed to create mix preview: {str(e)}")

    def retrieve_preview_mix(self, task_id: str, retrieve_fx_settings: bool = False,
                             max_attempts: int = 30, poll_interval: int = 5) -> Dict[str, Any]:
        """
        Retrieve the preview mix, optionally polling until it's ready

        Args:
            task_id: Multitrack task ID from create_mix_preview
            retrieve_fx_settings: Whether to retrieve FX settings (may incur charges)
            max_attempts: Maximum number of polling attempts
            poll_interval: Seconds between polling attempts

        Returns:
            Preview mix results including download URL and settings

        Raises:
            Exception: If polling times out or the API request fails
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

        logger.error("Preview mix was not available after polling. Please try again later.")
        raise Exception("Preview mix was not available after polling. Please try again later.")

    def retrieve_final_mix(self, request: FinalMixRequest) -> Dict[str, Any]:
        """
        Retrieve the final mix with adjusted gain settings

        Args:
            request: Final mix request parameters

        Returns:
            Final mix results including download URL

        Raises:
            Exception: If the API request fails
        """
        logger.info("Retrieving final mix")
        logger.debug(f"Final mix request data: {request}")
        payload = self._prepare_final_mix_payload(request)

        try:
            response = self.api_provider.post("/retrievefinalmix", payload)
            logger.info("Final mix retrieved successfully.")
            if "applyAudioEffectsResults" in response:
                return response["applyAudioEffectsResults"]
            return response
        except requests.HTTPError as e:
            logger.error(f"Failed to retrieve final mix: {str(e)}")
            raise Exception(f"Failed to retrieve final mix: {str(e)}")

    def _prepare_mix_preview_payload(self, request: MultitrackMixRequest) -> Dict[str, Any]:
        """
        Convert the model to API payload for mix preview

        Args:
            request: Multitrack mix request

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
            request: Final mix request

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