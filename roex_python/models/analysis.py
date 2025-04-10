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
    """Model for a mix analysis request"""
    audio_file_location: str
    musical_style: AnalysisMusicalStyle
    is_master: bool