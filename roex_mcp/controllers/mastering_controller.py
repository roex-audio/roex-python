"""
Controller for mastering operations
"""

import os
import time
from typing import Dict, Any, List

import requests

from roex_mcp.models.mastering import (
    MasteringRequest,
    MasteringTaskResponse,
    AlbumMasteringRequest
)
from roex_mcp.providers.api_provider import ApiProvider


class MasteringController:
    """Controller for mastering operations"""

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the mastering controller

        Args:
            api_provider: Provider for API interactions
        """
        self.api_provider = api_provider

    def create_mastering_preview(self, request: MasteringRequest) -> MasteringTaskResponse:
        """
        Create a mastering preview

        Args:
            request: Mastering request parameters

        Returns:
            Response containing the mastering task ID

        Raises:
            Exception: If the API request fails
        """
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
            return MasteringTaskResponse(
                mastering_task_id=response.get("mastering_task_id", "")
            )
        except requests.HTTPError as e:
            raise Exception(f"Failed to create mastering preview: {str(e)}")

    def retrieve_preview_master(self, task_id: str, max_attempts: int = 30,
                                poll_interval: int = 5) -> Dict[str, Any]:
        """
        Retrieve the preview master, polling until it's ready

        Args:
            task_id: Mastering task ID from create_mastering_preview
            max_attempts: Maximum number of polling attempts
            poll_interval: Seconds between polling attempts

        Returns:
            Preview master results including download URL

        Raises:
            Exception: If polling times out or the API request fails
        """
        payload = {
            "masteringData": {
                "masteringTaskId": task_id
            }
        }

        # Try initial request
        try:
            response = self.api_provider.post("/retrievepreviewmaster", payload)
            if "previewMasterTaskResults" in response:
                return response["previewMasterTaskResults"]
        except requests.HTTPError:
            # Initial request failed, let's try polling
            pass

        # Poll for results
        for attempt in range(max_attempts):
            try:
                print(f"Polling attempt {attempt + 1}/{max_attempts}...")
                response = self.api_provider.post("/retrievepreviewmaster", payload)

                # If we get a 200 response with results
                if "previewMasterTaskResults" in response:
                    return response["previewMasterTaskResults"]

                # Check for specific status codes
                status_code = response.get("status", 0)
                if status_code == 202:
                    print("Task still processing...")
                elif status_code == 200:
                    # If we get a 200 but no results, try to parse the response differently
                    if isinstance(response, dict):
                        for key, value in response.items():
                            if isinstance(value, dict) and "download_url_mastered_preview" in value:
                                return value
            except requests.HTTPError as e:
                print(f"Error during polling: {str(e)}")

            # Wait before next attempt
            time.sleep(poll_interval)

        raise Exception("Preview master was not available after polling. Please try again later.")

    def retrieve_final_master(self, task_id: str) -> Any:
        """
        Retrieve the final master

        Args:
            task_id: Mastering task ID from create_mastering_preview

        Returns:
            Final master download URL or results dictionary

        Raises:
            Exception: If the API request fails
        """
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
                return response["finalMasterTaskResults"]
            elif isinstance(response, dict) and "download_url_mastered" in response:
                # If the URL is directly in the response
                return response["download_url_mastered"]
            elif isinstance(response, str) and (response.startswith("http://") or response.startswith("https://")):
                # If the response is just the URL as a string
                return response

            # Default fallback
            return response
        except requests.HTTPError as e:
            raise Exception(f"Failed to retrieve final master: {str(e)}")

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
        os.makedirs(output_dir, exist_ok=True)
        results = {}

        for idx, track_request in enumerate(album_request.tracks, start=1):
            print(f"Starting mastering for Track #{idx}")

            # Create preview
            preview_response = self.create_mastering_preview(track_request)
            task_id = preview_response.mastering_task_id

            # Wait for preview to complete
            try:
                preview_results = self.retrieve_preview_master(task_id)
                print(f"Preview master ready for Track #{idx}")
            except Exception as e:
                print(f"Warning: Could not retrieve preview for Track #{idx}: {e}")
                # Continue to final master anyway

            # Get final master
            try:
                final_url = self.retrieve_final_master(task_id)
                results[idx] = final_url

                # Download the file
                if isinstance(final_url, str) and (final_url.startswith("http://") or final_url.startswith("https://")):
                    local_filename = os.path.join(output_dir, f"final_master_track_{idx}.wav")
                    self.api_provider.download_file(final_url, local_filename)
                    print(f"Downloaded Track #{idx} to {local_filename}")
                else:
                    print(f"Warning: Final URL for Track #{idx} is not a valid URL: {final_url}")
            except Exception as e:
                print(f"Error processing Track #{idx}: {e}")

        return results