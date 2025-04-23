"""
Models for the mix enhance API endpoints
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from roex_python.models.common import LoudnessPreference


class EnhanceMusicalStyle(Enum):
    """Musical styles for mix enhancement"""
    ROCK = "ROCK"
    POP = "POP"
    TECHNO = "TECHNO"
    TRAP = "TRAP"
    JAZZ = "JAZZ"
    METAL = "METAL"
    SOUL = "SOUL"
    FOLK = "FOLK"
    ORCHESTRAL = "ORCHESTRAL"
    PUNK = "PUNK"
    BLUES = "BLUES"
    AMBIENT = "AMBIENT"
    ACOUSTIC = "ACOUSTIC"
    EXPERIMENTAL = "EXPERIMENTAL"
    HIP_HOP_GRIME = "HIP_HOP_GRIME"
    COUNTRY = "COUNTRY"
    FUNK = "FUNK"
    RNB = "RNB"
    INDIE_POP = "INDIE_POP"
    INDIE_ROCK = "INDIE_ROCK"
    AFROBEAT = "AFROBEAT"
    DRUM_N_BASS = "DRUM_N_BASS"
    HOUSE = "HOUSE"
    TRANCE = "TRANCE"
    LO_FI = "LO_FI"
    ELECTRONIC = "ELECTRONIC"


@dataclass
class MixEnhanceRequest:
    """Model for a mix enhance preview/full request"""
    audio_file_location: str
    musical_style: EnhanceMusicalStyle
    is_master: bool = False
    fix_clipping_issues: bool = True
    fix_drc_issues: bool = True
    fix_stereo_width_issues: bool = True
    fix_tonal_profile_issues: bool = True
    fix_loudness_issues: bool = True
    apply_mastering: bool = True
    webhook_url: Optional[str] = None
    loudness_preference: LoudnessPreference = LoudnessPreference.STREAMING_LOUDNESS
    stem_processing: bool = False
    """bool: If True, requests the generation of stems (e.g., vocals, bass, drums, other) alongside the enhanced mix. Defaults to False."""


@dataclass
class MixEnhanceResponse:
    """Response model for mix enhancement task creation"""
    mixrevive_task_id: str
    error: bool
    message: str