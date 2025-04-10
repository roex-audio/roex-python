"""
Controller for mix enhancement operations
"""

import os
import time
from typing import Dict, Any, List

import requests

from roex_mcp.models.enhance import MixEnhanceRequest, MixEnhanceResponse
from roex_mcp.providers.api_provider import ApiProvider


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

    def process_mix_enhance_flow(self, request: MixEnhanceRequest, output_dir: str = "enhanced_tracks") -> Dict[
        str, str]:
        """
        Complete mix enhancement flow: preview, retrieve, then full process

        Args:
            request: Mix enhance request parameters
            output_dir: Directory to save downloaded tracks

        Returns:
            Dictionary with download URLs for preview and final tracks

        Raises:
            Exception: If either the preview or full enhancement fails
        """
        os.makedirs(output_dir, exist_ok=True)
        result_urls = {}

        # 1. Start preview job
        print("Creating mix enhance preview...")
        preview_response = self.create_mix_enhance_preview(request)
        preview_task_id = preview_response.mixrevive_task_id

        # 2. Poll until preview is ready
        print("Waiting for preview to complete...")
        preview_results = self.retrieve_enhanced_track(preview_task_id)

        # 3. Download preview track
        preview_url = preview_results.get("download_url_preview_revived")
        if preview_url:
            preview_filename = os.path.join(output_dir, "enhanced_preview.wav")
            self.api_provider.download_file(preview_url, preview_filename)
            result_urls["preview"] = preview_url
            print(f"Downloaded preview to {preview_filename}")

            # Download preview stems if available
            preview_stems = preview_results.get("stems", {})
            for stem_name, stem_url in preview_stems.items():
                stem_filename = os.path.join(output_dir, f"enhanced_preview_stem_{stem_name}.wav")
                self.api_provider.download_file(stem_url, stem_filename)
                result_urls[f"preview_stem_{stem_name}"] = stem_url

        # 4. Start full enhancement job
        print("Creating full mix enhancement...")
        full_response = self.create_mix_enhance(request)
        full_task_id = full_response.mixrevive_task_id

        # 5. Poll until full track is ready
        print("Waiting for full enhancement to complete...")
        full_results = self.retrieve_enhanced_track(full_task_id)

        # 6. Download final track
        final_url = full_results.get("download_url_revived")
        if final_url:
            final_filename = os.path.join(output_dir, "enhanced_full.wav")
            self.api_provider.download_file(final_url, final_filename)
            result_urls["final"] = final_url
            print(f"Downloaded final enhanced track to {final_filename}")

            # Download final stems if available
            final_stems = full_results.get("stems", {})
            for stem_name, stem_url in final_stems.items():
                stem_filename = os.path.join(output_dir, f"enhanced_full_stem_{stem_name}.wav")
                self.api_provider.download_file(stem_url, stem_filename)
                result_urls[f"final_stem_{stem_name}"] = stem_url

        return result_urls