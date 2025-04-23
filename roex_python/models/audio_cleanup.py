from typing import Optional
from dataclasses import dataclass
from enum import Enum
from .common import BaseResponse

class SoundSource(str, Enum):
    """
    Enumeration of valid sound source types for the audio cleanup process.
    Used to specify the primary instrument or vocal type within the audio file.
    """
    KICK_GROUP = "KICK_GROUP"
    SNARE_GROUP = "SNARE_GROUP"
    VOCAL_GROUP = "VOCAL_GROUP"
    BACKING_VOCALS_GROUP = "BACKING_VOCALS_GROUP"
    PERCS_GROUP = "PERCS_GROUP"
    STRINGS_GROUP = "STRINGS_GROUP"
    E_GUITAR_GROUP = "E_GUITAR_GROUP"
    ACOUSTIC_GUITAR_GROUP = "ACOUSTIC_GUITAR_GROUP"

@dataclass
class AudioCleanupData:
    """
    Input data required for an audio cleanup request.

    This structure is sent as the payload to the `/audio-cleanup` endpoint.
    """
    audio_file_location: str
    """str: The URL of the audio file (WAV or FLAC, mono or stereo) to be cleaned. Must be accessible by the RoEx API."""
    sound_source: SoundSource
    """SoundSource: The type of sound source present in the audio file that needs cleaning (e.g., VOCAL_GROUP, KICK_GROUP)."""

@dataclass
class AudioCleanupResults:
    """
    Contains the results of a successful audio cleanup operation.

    This object is typically nested within the `AudioCleanupResponse`.
    """
    completion_time: str
    """str: Timestamp indicating when the cleanup process was completed."""
    error: bool
    """bool: Flag indicating if an error occurred specifically during the cleanup process (distinct from API call errors)."""
    info: str
    """str: Additional information or status messages related to the cleanup process."""
    cleaned_audio_file_location: Optional[str] = None
    """Optional[str]: The URL where the cleaned audio file can be downloaded. Present only if the cleanup was successful and resulted in an output file."""

@dataclass
class AudioCleanupResponse(BaseResponse):
    """
    Represents the full response received from the `/audio-cleanup` endpoint.

    Inherits common fields like `error`, `message`, and `info` from `BaseResponse`,
    which reflect the overall status of the API request.
    """
    audio_cleanup_results: Optional[AudioCleanupResults] = None
    """Optional[AudioCleanupResults]: Contains detailed results of the cleanup task, including the URL for the cleaned audio file, if successful. Is `None` if the API request itself failed before processing could start or if the cleanup process encountered a fatal error."""
