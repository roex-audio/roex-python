"""
Models for the mix/master analysis API endpoints
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class AnalysisMusicalStyle(Enum):
    """Musical styles for mix/master analysis"""
    ROCK = "ROCK"
    METAL = "METAL"
    INSTRUMENTAL = "INSTRUMENTAL"
    ELECTRONIC = "ELECTRONIC"
    HIP_HOP_GRIME = "HIP_HOP_GRIME"
    POP = "POP"
    ACOUSTIC = "ACOUSTIC"
    BLUES = "BLUES"
    JAZZ = "JAZZ"
    SOUL = "SOUL"
    FOLK = "FOLK"
    PUNK = "PUNK"
    AMBIENT = "AMBIENT"
    EXPERIMENTAL = "EXPERIMENTAL"
    COUNTRY = "COUNTRY"
    FUNK = "FUNK"
    RNB = "RNB"
    INDIE_POP = "INDIE_POP"
    INDIE_ROCK = "INDIE_ROCK"
    HOUSE = "HOUSE"
    TRAP = "TRAP"
    TECHNO = "TECHNO"
    ORCHESTRAL = "ORCHESTRAL"
    AFROBEAT = "AFROBEAT"
    DRUM_N_BASS = "DRUM_N_BASS"
    TRANCE = "TRANCE"
    LO_FI = "LO_FI"
    REGGAE = "REGGAE"
    LATIN = "LATIN"
    AIRY_EXPANSIVE = "AIRY_EXPANSIVE"
    AGGRESSIVE = "AGGRESSIVE"
    BRIGHT = "BRIGHT"
    GRITTY_CRUNCHY = "GRITTY_CRUNCHY"
    MELLOW_SMOOTH = "MELLOW_SMOOTH"
    SHARP_BASSY = "SHARP_BASSY"
    THUMPING_BOOMY = "THUMPING_BOOMY"
    WARM = "WARM"
    BALANCED = "BALANCED"


@dataclass
class MixAnalysisRequest:
    """
    Represents the input parameters for requesting a mix analysis.

    This dataclass is used to structure the data sent to the RoEx API's
    `/mixanalysis` endpoint.
    """
    audio_file_location: str
    """str: The URL of the audio file (WAV or FLAC) to be analyzed. This URL must be accessible by the RoEx API."""
    musical_style: AnalysisMusicalStyle
    """AnalysisMusicalStyle: The musical style of the track, used as a reference for the analysis (e.g., ROCK, POP, ELECTRONIC)."""
    is_master: bool
    """bool: Indicates whether the provided audio file is a mastered track (True) or a mix (False)."""


@dataclass
class AnalysisResult:
    """Result of a mix/master analysis from the ``/mixanalysis`` endpoint.

    The ``payload`` dict contains the detailed diagnosis metrics such as
    ``integrated_loudness_lufs``, ``peak_loudness_dbfs``, ``tonal_profile``,
    ``clipping``, ``stereo_field``, etc.
    """
    payload: Optional[Dict[str, Any]] = None
    """Optional[Dict[str, Any]]: The diagnosis metrics dictionary."""
    error: bool = False
    """bool: Whether the analysis encountered an error."""
    info: str = ""
    """str: Additional information from the API."""
    completion_time: str = ""
    """str: Timestamp when the analysis completed."""