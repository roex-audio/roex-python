"""
Common models and enums shared across different API features
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseResponse:
    """Base response model with common fields."""
    error: bool = False
    message: str = ""
    info: str = ""


class MusicalStyle(Enum):
    """Musical styles for mixing and mastering"""
    ROCK_INDIE = "ROCK_INDIE"
    POP = "POP"
    ACOUSTIC = "ACOUSTIC"
    HIPHOP_GRIME = "HIPHOP_GRIME"
    ELECTRONIC = "ELECTRONIC"
    REGGAE_DUB = "REGGAE_DUB"
    ORCHESTRAL = "ORCHESTRAL"
    METAL = "METAL"
    OTHER = "OTHER"


class InstrumentGroup(Enum):
    """Instrument group classifications for mixing"""
    BASS_GROUP = "BASS_GROUP"
    DRUMS_GROUP = "DRUMS_GROUP"
    KICK_GROUP = "KICK_GROUP"
    SNARE_GROUP = "SNARE_GROUP"
    CYMBALS_GROUP = "CYMBALS_GROUP"
    VOCAL_GROUP = "VOCAL_GROUP"
    BACKING_VOX_GROUP = "BACKING_VOX_GROUP"
    PERCS_GROUP = "PERCS_GROUP"
    STRINGS_GROUP = "STRINGS_GROUP"
    SYNTH_GROUP = "SYNTH_GROUP"
    FX_GROUP = "FX_GROUP"
    KEYS_GROUP = "KEYS_GROUP"
    BRASS_GROUP = "BRASS_GROUP"
    E_GUITAR_GROUP = "E_GUITAR_GROUP"
    ACOUSTIC_GUITAR_GROUP = "ACOUSTIC_GUITAR_GROUP"
    BACKING_TRACK_GROUP = "BACKING_TRACK_GROUP"
    OTHER_GROUP1 = "OTHER_GROUP1"
    OTHER_GROUP2 = "OTHER_GROUP2"
    OTHER_GROUP3 = "OTHER_GROUP3"
    OTHER_GROUP4 = "OTHER_GROUP4"
    OTHER_GROUP5 = "OTHER_GROUP5"


class PresenceSetting(Enum):
    """Track presence settings for mixing"""
    NORMAL = "NORMAL"
    LEAD = "LEAD"
    BACKGROUND = "BACKGROUND"


class PanPreference(Enum):
    """Track panning preferences for mixing"""
    NO_PREFERENCE = "NO_PREFERENCE"
    LEFT = "LEFT"
    CENTRE = "CENTRE"
    RIGHT = "RIGHT"


class ReverbPreference(Enum):
    """Track reverb preferences for mixing"""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DesiredLoudness(Enum):
    """Loudness presets for mastering"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class LoudnessPreference(Enum):
    """Loudness targets for enhancement"""
    CD_LOUDNESS = "CD_LOUDNESS"
    STREAMING_LOUDNESS = "STREAMING_LOUDNESS"