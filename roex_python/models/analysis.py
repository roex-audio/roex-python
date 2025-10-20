"""
Models for the mix/master analysis API endpoints
"""

from dataclasses import dataclass
from enum import Enum


class AnalysisMusicalStyle(Enum):
    """Musical styles for mix/master analysis"""
    ROCK = "ROCK"
    METAL = "METAL"
    INSTRUMENTAL = "INSTRUMENTAL"
    ELECTRONIC = "ELECTRONIC"
    DANCE = "DANCE"
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