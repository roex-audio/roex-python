"""
Common models and enums shared across different API features
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseResponse:
    """
    Base dataclass inherited by most API response models.

    Provides common fields to indicate the overall status of an API request.
    Specific results or data related to the operation are typically found in
    subclass-specific fields.
    """
    error: bool = False
    """bool: Indicates if the API request itself encountered an error (e.g., bad request, authentication failure). Defaults to False."""
    message: str = ""
    """str: A general status message from the API regarding the request."""
    info: str = ""
    """str: Additional informational text from the API, if any."""


class MusicalStyle(Enum):
    """
    Enumeration of musical styles used as references for mixing and mastering.

    Used in `MultitrackMixRequest` and `MasteringRequest` to guide the AI's
    processing decisions based on genre conventions.
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


class InstrumentGroup(Enum):
    """
    Enumeration of instrument group classifications for multitrack mixing.

    Used within a `MixTrack` object to identify the primary role of the audio track
    (e.g., vocals, bass, drums) to inform the mixing process.
    """
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
    """
    Enumeration for specifying the desired presence of a track in a mix.

    Used within a `MixTrack` object to guide the mixing AI on how prominent
    a track should be (e.g., LEAD, NORMAL, BACKGROUND).
    """
    NORMAL = "NORMAL"
    LEAD = "LEAD"
    BACKGROUND = "BACKGROUND"


class PanPreference(Enum):
    """
    Enumeration for specifying panning preferences for a track in a mix.

    Used within a `MixTrack` object to suggest a stereo placement (LEFT, CENTRE, RIGHT)
    or indicate NO_PREFERENCE, allowing the AI to decide.
    """
    NO_PREFERENCE = "NO_PREFERENCE"
    LEFT = "LEFT"
    CENTRE = "CENTRE"
    RIGHT = "RIGHT"


class ReverbPreference(Enum):
    """
    Enumeration for specifying the desired amount of reverb for a track in a mix.

    Used within a `MixTrack` object to guide the amount of reverb applied
    (NONE, LOW, MEDIUM, HIGH).
    """
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DesiredLoudness(Enum):
    """
    Enumeration of general loudness targets, primarily used for mastering.

    Used in `MasteringRequest` to set the overall loudness goal (LOW, MEDIUM, HIGH).
    Note: For mix enhancement, use `LoudnessPreference` instead.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class LoudnessPreference(Enum):
    """
    Enumeration of specific loudness targets, primarily used for mix enhancement.

    Used in `MixEnhanceRequest` to target standard loudness levels like
    CD_LOUDNESS or STREAMING_LOUDNESS.
    """
    CD_LOUDNESS = "CD_LOUDNESS"
    STREAMING_LOUDNESS = "STREAMING_LOUDNESS"