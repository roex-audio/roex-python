"""
Models for the mix enhance API endpoints
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from roex_python.models.common import LoudnessPreference


class EnhanceMusicalStyle(Enum):
    """Musical styles for mix enhancement"""
    ROCK_INDIE = "ROCK_INDIE"
    POP = "POP"
    ACOUSTIC = "ACOUSTIC"
    HIPHOP_GRIME = "HIPHOP_GRIME"
    ELECTRONIC = "ELECTRONIC"
    REGGAE_DUB = "REGGAE_DUB"
    ORCHESTRAL = "ORCHESTRAL"
    METAL = "METAL"
    OTHER = "OTHER"
    GRITTY_CRUNCHY = "GRITTY_CRUNCHY"
    BRIGHT = "BRIGHT"
    WARM = "WARM"
    SHARP_BASSY = "SHARP_BASSY"
    THUMPING_BOOMY = "THUMPING_BOOMY"
    MELLOW_SMOOTH = "MELLOW_SMOOTH"
    AIRY_EXPANSIVE = "AIRY_EXPANSIVE"
    AGGRESSIVE = "AGGRESSIVE"
    BALANCED = "BALANCED"


@dataclass
class MixEnhanceRequest:
    """Model for a mix enhance preview/full request"""
    audio_file_location: str
    musical_style: EnhanceMusicalStyle
    is_master: bool = False
    fix_clipping_issues: bool = True
    fix_stereo_width_issues: bool = True
    fix_tonal_profile_issues: bool = True
    fix_loudness_issues: bool = True
    apply_mastering: bool = True
    apply_drum_enhancement: bool = True
    apply_vocal_enhancement: bool = True
    webhook_url: Optional[str] = None
    loudness_preference: LoudnessPreference = LoudnessPreference.NO_CHANGE
    stem_processing: bool = False
    """bool: If True, requests the generation of stems (e.g., vocals, bass, drums, other) alongside the enhanced mix. Defaults to False."""
    get_processed_stems: bool = False
    """bool: If True, requests the processed stems alongside the enhanced mix. Defaults to False."""


@dataclass
class MixEnhanceResponse:
    """Response model for mix enhancement task creation"""
    mixrevive_task_id: str
    error: bool
    message: str