"""
Models for the stem separation ("StemFlow") API endpoints
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class StemSeparationRequest:
    """
    Represents the input parameters for requesting stem separation for a track.

    This dataclass structures the data sent to the RoEx API's `/separate` endpoint.
    """
    audio_file_location: str
    """str: The URL of the audio file (WAV or FLAC) to be separated into stems.
    Must be accessible by the RoEx API."""


@dataclass
class StemSeparationTaskResponse:
    """
    Represents the immediate response after successfully submitting a stem
    separation task.

    Submitting a task reserves 75 credits from the caller's balance; they
    are captured only if separation succeeds, and refunded automatically if
    it fails.
    """
    stemflow_task_id: str
    """str: The unique identifier for the initiated separation task (format: ``sf_<uuid>``).
    Use this to poll ``get_separation_status`` and later call ``retrieve_stems``."""
    error: bool = False
    """bool: Indicates if the initial API request itself encountered an error."""
    message: str = ""
    """str: A general status message from the API regarding the request."""


@dataclass
class StemSeparationStatusResult:
    """Result of polling ``GET /separatestatus/{stemflow_task_id}``."""
    stemflow_task_id: str
    """str: The task ID this status result refers to."""
    status: str
    """str: One of ``"processing"``, ``"complete"``, or ``"failed"``."""
    error: bool = False
    """bool: True when ``status`` is ``"failed"``."""
    message: str = ""
    """str: A general status message from the API."""
    info: str = ""
    """str: Additional detail, populated when the task has failed."""


@dataclass
class SeparatedStemsResult:
    """Signed URLs for the four separated stems, from ``POST /retrievestems``.

    Each URL points to a stereo 44.1kHz WAV file and expires after
    approximately 24 hours.
    """
    vocals: Optional[str] = None
    """Optional[str]: Signed URL for the isolated vocal stem."""
    bass: Optional[str] = None
    """Optional[str]: Signed URL for the isolated bass stem."""
    drums: Optional[str] = None
    """Optional[str]: Signed URL for the isolated drums stem."""
    other: Optional[str] = None
    """Optional[str]: Signed URL for all remaining instrumentation."""
