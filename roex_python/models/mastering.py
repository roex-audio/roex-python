"""
Models for the mastering-related API endpoints
"""

from dataclasses import dataclass, field
from typing import List, Optional



from roex_python.models.common import DesiredLoudness, MusicalStyle


@dataclass
class MasteringRequest:
    """
    Represents the input parameters for requesting audio mastering for a single track.

    This dataclass structures the data sent to the RoEx API's mastering endpoints
    (e.g., `/masterpreview`, `/mastertrack`).
    """
    track_url: str
    """str: The URL of the audio file (WAV or FLAC) to be mastered. Must be accessible by the RoEx API."""
    musical_style: MusicalStyle
    """MusicalStyle: The musical style reference for mastering (e.g., POP, ROCK_INDIE)."""
    desired_loudness: DesiredLoudness
    """DesiredLoudness: The target loudness level for the master (e.g., LOW, MEDIUM, HIGH)."""
    sample_rate: str = "44100"
    """str: The desired sample rate for the output mastered file. Defaults to "44100" Hz."""
    webhook_url: Optional[str] = None
    """Optional[str]: A URL to which a notification will be sent upon task completion."""


@dataclass
class MasteringTaskResponse:
    """
    Represents the immediate response after successfully submitting a mastering task.

    This response confirms the task has been accepted and provides the ID needed
    to poll for results.
    """
    mastering_task_id: str
    """str: The unique identifier for the initiated mastering task."""


@dataclass
class AlbumMasteringRequest:
    """
    Represents a request to master multiple tracks, potentially as part of an album.

    Note: While this model exists, the current `MasteringController` might not expose
    a direct method for album mastering. It typically handles tracks individually.
    This model might be reserved for future use or internal API structures.
    """
    tracks: List[MasteringRequest]
    """List[MasteringRequest]: A list of individual MasteringRequest objects, one for each track to be mastered."""


@dataclass
class PreviewMasterResult:
    """Result of a completed mastering preview from the ``/retrievepreviewmaster`` endpoint."""
    download_url_mastered_preview: Optional[str] = None
    """Optional[str]: Signed URL for the mastered preview audio file."""
    preview_start_time: Optional[float] = None
    """Optional[float]: Offset in seconds where the preview clip starts in the original track."""


@dataclass
class FinalMasterResult:
    """Result of a completed final master from the ``/retrievefinalmaster`` endpoint."""
    download_url_mastered: Optional[str] = None
    """Optional[str]: Signed URL for the final mastered audio file."""