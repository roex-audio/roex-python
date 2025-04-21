from typing import Dict, Any, Optional
from ..models.audio_cleanup import AudioCleanupData, AudioCleanupResponse, AudioCleanupResults
from ..providers.api_provider import ApiProvider
import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

class AudioCleanupController:
    """Controller for audio cleanup operations."""

    def __init__(self, api_provider: ApiProvider):
        self.api_provider = api_provider
        logger.info("AudioCleanupController initialized.")

    def clean_up_audio(self, audio_cleanup_data: AudioCleanupData) -> AudioCleanupResponse:
        """
        Clean up an audio signal for a specified instrument track.

        Args:
            audio_cleanup_data: AudioCleanupData object containing the audio file location and sound source.

        Returns:
            AudioCleanupResponse object containing the results of the cleanup operation.
        """
        logger.info("Starting audio cleanup operation.")
        logger.debug(f"Audio cleanup request data: {audio_cleanup_data}")
        payload = {
            "audioCleanupData": {
                "audioFileLocation": audio_cleanup_data.audio_file_location,
                "soundSource": audio_cleanup_data.sound_source.value
            }
        }

        try:
            response = self.api_provider.post("/audio-cleanup", payload)
            logger.info("Received response from API.")
            results = None
            if "audioCleanupResults" in response:
                results_data = response["audioCleanupResults"]
                results = AudioCleanupResults(
                    completion_time=results_data.get("completion_time", ""),
                    error=results_data.get("error", False),
                    info=results_data.get("info", ""),
                    cleaned_audio_file_location=results_data.get("cleaned_audio_file_location")
                )
                logger.info("Audio cleanup results retrieved successfully.")

            return AudioCleanupResponse(
                error=response.get("error", False),
                message=response.get("message", ""),
                info=response.get("info", ""),
                audio_cleanup_results=results
            )
        except Exception as e:
            logger.exception(f"Exception during audio cleanup operation: {e}")
            return None
