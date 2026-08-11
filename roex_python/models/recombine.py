"""
Models for the stem recombination ("Recombine") API endpoints
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from roex_python.models.common import DesiredLoudness


class RecombineMusicalStyle(Enum):
    """
    Enumeration of musical styles accepted by the ``/recombine`` endpoint.

    This is intentionally a separate enum from :class:`roex_python.models.common.MusicalStyle`:
    the recombine service supports a wider set of styles than mixing/mastering.
    """
    ROCK_INDIE = "ROCK_INDIE"
    POP = "POP"
    ACOUSTIC = "ACOUSTIC"
    HIPHOP_GRIME = "HIPHOP_GRIME"
    ELECTRONIC = "ELECTRONIC"
    REGGAE_DUB = "REGGAE_DUB"
    ORCHESTRAL = "ORCHESTRAL"
    METAL = "METAL"
    OTHER = "OTHER"
    JAZZ = "JAZZ"
    LO_FI = "LO_FI"
    LATIN = "LATIN"
    TECHNO = "TECHNO"
    HOUSE = "HOUSE"
    TRAP = "TRAP"
    COUNTRY_ACOUSTIC = "COUNTRY_ACOUSTIC"
    CINEMATIC = "CINEMATIC"
    AFROBEAT = "AFROBEAT"
    K_POP = "K_POP"
    REGGAETON = "REGGAETON"


@dataclass
class RecombineRequest:
    """
    Represents the input parameters for requesting stem recombination via
    ``POST /recombine``.

    Exactly one input mode must be provided:

    - ``stem_job_id``: reuse the vocal stem and summed backing (drums + bass +
      other) from a prior, completed :class:`~roex_python.controllers.stemflow_controller.StemFlowController`
      separation job.
    - ``vocal_stem_url`` and ``backing_stem_url`` together: directly supply an
      isolated vocal track and a backing/instrumental (beat) track.

    Submitting a recombine task is free; the final master is charged 250
    credits the first time it is successfully retrieved via
    ``RecombineController.retrieve_final_master``.
    """
    musical_style: RecombineMusicalStyle
    """RecombineMusicalStyle: The musical style reference guiding the mix and master."""
    stem_job_id: Optional[str] = None
    """Optional[str]: The ``stemflow_task_id`` of a prior, completed separation job.
    Mutually exclusive with ``vocal_stem_url``/``backing_stem_url``."""
    vocal_stem_url: Optional[str] = None
    """Optional[str]: URL of an isolated vocal track. Must be paired with ``backing_stem_url``."""
    backing_stem_url: Optional[str] = None
    """Optional[str]: URL of a backing/instrumental track. Must be paired with ``vocal_stem_url``."""
    desired_loudness: DesiredLoudness = DesiredLoudness.MEDIUM
    """DesiredLoudness: The target loudness preset for the final master. Defaults to MEDIUM."""
    vocal_gain_db: float = 0.0
    """float: Gain applied to the vocal stem in dB, from -6.0 to +6.0. Defaults to 0.0."""
    webhook_url: Optional[str] = None
    """Optional[str]: A URL to receive async status notifications for this
    recombine job (pending/started/completed/failed)."""

    def __post_init__(self):
        has_stem_job = self.stem_job_id is not None
        has_vocal_url = self.vocal_stem_url is not None
        has_backing_url = self.backing_stem_url is not None

        if has_stem_job and (has_vocal_url or has_backing_url):
            raise ValueError(
                "Provide either stem_job_id, or both vocal_stem_url and "
                "backing_stem_url -- not both."
            )
        if not has_stem_job and not (has_vocal_url and has_backing_url):
            raise ValueError(
                "Provide either stem_job_id, or both vocal_stem_url and backing_stem_url."
            )
        if not (-6.0 <= self.vocal_gain_db <= 6.0):
            raise ValueError(
                f"vocal_gain_db must be between -6.0 and 6.0 inclusive, got {self.vocal_gain_db}."
            )


@dataclass
class RecombineTaskResponse:
    """Represents the immediate response after successfully submitting a recombine task."""
    recombine_task_id: str
    """str: The unique identifier for the initiated recombine task (format: ``rc_<uuid>``).
    Use this to poll ``get_recombine_status`` and later retrieve results."""
    error: bool = False
    """bool: Indicates if the initial API request itself encountered an error."""
    message: str = ""
    """str: A general status message from the API regarding the request."""


@dataclass
class RecombineStatusResult:
    """Result of polling ``GET /recombinestatus/{recombine_task_id}``."""
    recombine_task_id: str
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
class RecombinePreviewResult:
    """Result of a free preview retrieval from ``POST /retrieverecombinepreview``."""
    preview_url: Optional[str] = None
    """Optional[str]: Signed URL for a ~30 second MP3 preview, taken from the
    loudest section of the track (not necessarily the start)."""
    preview_start_seconds: Optional[float] = None
    """Optional[float]: Offset in seconds where the preview clip starts in the full track."""
    measured_lufs_full: Optional[float] = None
    """Optional[float]: Integrated loudness (LUFS) measured across the full
    program, not just the preview excerpt."""


@dataclass
class RecombineProcessingInfo:
    """Echoes the processing parameters that were applied to the final master."""
    musical_style: Optional[str] = None
    """Optional[str]: The musical style that was applied."""
    desired_loudness: Optional[str] = None
    """Optional[str]: The desired loudness preset that was applied."""
    vocal_gain_db: Optional[float] = None
    """Optional[float]: The vocal gain (dB) that was applied."""


@dataclass
class RecombineFinalResult:
    """Result of the final mastered retrieval from ``POST /retrieverecombine``.

    Retrieving this result charges 250 credits the first time it succeeds
    for a given task; repeat calls return the same result without
    re-charging.
    """
    master_url: Optional[str] = None
    """Optional[str]: Signed URL for the final mastered WAV file
    (stereo, 44.1kHz, 16-bit PCM). Expires after approximately 24 hours."""
    measured_lufs: Optional[float] = None
    """Optional[float]: Measured integrated loudness (LUFS) of the final master."""
    peak_level: Optional[float] = None
    """Optional[float]: Measured peak level (dBFS) of the final master."""
    track_length_seconds: Optional[float] = None
    """Optional[float]: Duration of the final master, in seconds."""
    sample_rate: Optional[int] = None
    """Optional[int]: Sample rate of the final master, in Hz."""
    bit_depth: Optional[int] = None
    """Optional[int]: Bit depth of the final master."""
    channels: Optional[int] = None
    """Optional[int]: Number of audio channels in the final master."""
    processing: Optional[RecombineProcessingInfo] = None
    """Optional[RecombineProcessingInfo]: The processing parameters that were applied."""
