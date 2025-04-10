"""
Controller for mix enhancement operations
"""

import os
import time
from typing import Dict, Any, List

import requests

from roex_python.models.enhance import MixEnhanceRequest, MixEnhanceResponse
from roex_python.providers.api_provider import ApiProvider


class EnhanceController:
    """Controller for mix enhancement operations"""

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the enhance controller

        Args:
            api_provider: Provider for API interactions
        """
        self.api_provider = api_provider

    def create_mix_enhance_preview(self, request: MixEnhanceRequest) -> MixEnhanceResponse:
        """
        Create a mix enhance preview

        Args:
            request: Mix enhance request parameters

        Returns:
            Response containing the mix enhance task ID

        Raises:
            Exception: If the API request fails
        """
        payload = self._prepare_mix_enhance_payload(request)

        try:
            response = self.api_provider.post("/mixenhancepreview", payload)
            return MixEnhanceResponse(
                mixrevive_task_id=response.get("mixrevive_task_id", ""),
                error=response.get("error", False),
                message=response.get("message", "")
            )
        except requests.HTTPError as e:
            raise Exception(f"Failed to create mix enhance preview: {str(e)}")

    def create_mix_enhance(self, request: MixEnhanceRequest) -> MixEnhanceResponse:
        """
        Create a full mix enhance

        Args:
            request: Mix enhance request parameters

        Returns:
            Response containing the mix enhance task ID

        Raises:
            Exception: If the API request fails
        """
        payload = self._prepare_mix_enhance_payload(request)

        try:
            response = self.api_provider.post("/mixenhance", payload)
            return MixEnhanceResponse(
                mixrevive_task_id=response.get("mixrevive_task_id", ""),
                error=response.get("error", False),
                message=response.get("message", "")
            )
        except requests.HTTPError as e:
            raise Exception(f"Failed to create mix enhance: {str(e)}")

    def retrieve_enhanced_track(self, task_id: str, max_attempts: int = 50,
                                poll_interval: int = 5) -> Dict[str, Any]:
        """
        Retrieve an enhanced track, polling until it's ready

        Args:
            task_id: Mix enhance task ID
            max_attempts: Maximum number of polling attempts
            poll_interval: Seconds between polling attempts

        Returns:
            Enhanced track results including download URL

        Raises:
            Exception: If polling times out or the API request fails
        """
        payload = {
            "mixReviveData": {
                "mixReviveTaskId": task_id
            }
        }

        # Poll for results
        for attempt in range(max_attempts):
            try:
                print(f"Polling attempt {attempt + 1}/{max_attempts}...")
                response = self.api_provider.post("/retrieveenhancedtrack", payload)

                if not response.get("error", False):
                    results = response.get("revived_track_tasks_results", {})
                    if results:
                        return results

                    # Some API versions might return a different format
                    for key in response:
                        if isinstance(response[key], dict) and (
                                "download_url_revived" in response[key] or
                                "download_url_preview_revived" in response[key]
                        ):
                            return response[key]
            except requests.HTTPError as e:
                print(f"Error during polling: {str(e)}")

            # Wait before next attempt
            time.sleep(poll_interval)

        raise Exception("Enhanced track was not available after polling. Please try again later.")

    def _prepare_mix_enhance_payload(self, request: MixEnhanceRequest) -> Dict[str, Any]:
        """
        Convert the model to API payload for mix enhance

        Args:
            request: Mix enhance request

        Returns:
            API payload dictionary
        """
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
