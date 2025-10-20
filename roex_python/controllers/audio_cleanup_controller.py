from typing import Dict, Any, Optional
from ..models.audio_cleanup import AudioCleanupData, AudioCleanupResponse, AudioCleanupResults
from ..providers.api_provider import ApiProvider
import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

class AudioCleanupController:
    """Controller for submitting audio tracks for noise reduction and cleanup via the RoEx API."""

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the AudioCleanupController.

        Typically, this controller is accessed via `client.audio_cleanup` rather than
        instantiated directly.

        Args:
            api_provider (ApiProvider): An instance of ApiProvider configured with
                the base URL and API key.
        """
        self.api_provider = api_provider
        logger.info("AudioCleanupController initialized.")

    def clean_up_audio(self, audio_cleanup_data: AudioCleanupData) -> Optional[AudioCleanupResponse]:
        """
        Submit an audio track for cleanup based on the specified sound source.

        This method sends the audio track URL and the type of instrument/sound
        to the RoEx API `/audio-cleanup` endpoint for processing. The API attempts
        to reduce noise and artifacts specific to that source.
        The operation is synchronous and returns the results directly.

        Supported Sound Sources (SoundSource Enum):
            KICK_GROUP, SNARE_GROUP, VOCAL_GROUP, BACKING_VOCALS_GROUP,
            PERCS_GROUP, STRINGS_GROUP, E_GUITAR_GROUP, ACOUSTIC_GUITAR_GROUP

        Supported File Formats: WAV, FLAC

        Args:
            audio_cleanup_data (AudioCleanupData): An object containing:
                - `audio_file_location` (str): URL of the audio file (WAV or FLAC).
                - `sound_source` (SoundSource): The type of instrument/sound in the track.

        Returns:
            Optional[AudioCleanupResponse]: An object containing the results:
                - `error` (bool): Indicates if the overall API call had an error.
                - `message` (str): A status message from the API.
                - `info` (str): Additional information from the API.
                - `audio_cleanup_results` (Optional[AudioCleanupResults]): Detailed results including:
                    - `completion_time` (str): Timestamp of completion.
                    - `error` (bool): Indicates if the cleanup *process* failed.
                    - `info` (str): Information specific to the cleanup process.
                    - `cleaned_audio_file_location` (Optional[str]): URL to the cleaned audio file.

                Returns `None` if an exception occurs during the API call.
                (Note: Consider adapting error handling for more specific feedback).

        Raises:
            requests.exceptions.RequestException: If the API request fails due to network
                                                 issues or invalid endpoint.
            Exception: If the API returns an unexpected error or fails to process the request.
                       (Currently caught and logged, returning None).

        Example:
            >>> from roex_python.models import AudioCleanupData, SoundSource
            >>> # Assume 'client' is an initialized RoExClient
            >>> # Assume 'vocal_track_url' is a URL for a WAV/FLAC vocal track
            >>> cleanup_request = AudioCleanupData(
            ...     audio_file_location=vocal_track_url,
            ...     sound_source=SoundSource.VOCAL_GROUP
            ... )
            >>> try:
            >>>     cleanup_response = client.audio_cleanup.clean_up_audio(cleanup_request)
            >>>     if cleanup_response and not cleanup_response.error:
            >>>         results = cleanup_response.audio_cleanup_results
            >>>         if results and not results.error:
            >>>             print(f"Cleanup successful! Cleaned file at: {results.cleaned_audio_file_location}")
            >>>         else:
            >>>             print(f"Cleanup process failed: {results.info if results else 'N/A'}")
            >>>     else:
            >>>         print(f"API call failed: {cleanup_response.message if cleanup_response else 'Exception occurred'}")
            >>> except Exception as e:
            >>>     # This part might not be reached due to current internal handling
            >>>     print(f"An unexpected error occurred: {e}")
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
            # Current implementation returns None on exception.
            # Consider re-raising or returning a more informative error response.
            return None
