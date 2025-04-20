from typing import Optional
from dataclasses import dataclass
from enum import Enum
from .common import BaseResponse

class SoundSource(str, Enum):
    """Valid sound source types for audio cleanup."""
    KICK_GROUP = "KICK_GROUP"
    SNARE_GROUP = "SNARE_GROUP"
    VOCAL_GROUP = "VOCAL_GROUP"
    BACKING_VOCALS_GROUP = "BACKING_VOCALS_GROUP"
    PERCS_GROUP = "PERCS_GROUP"
    STRINGS_GROUP = "STRINGS_GROUP"
    E_GUITAR_GROUP = "E_GUITAR_GROUP"
    ACOUSTIC_GUITAR_GROUP = "ACOUSTIC_GUITAR_GROUP"

@dataclass
class AudioCleanupData:
    """Data model for audio cleanup request."""
    audio_file_location: str
    sound_source: SoundSource

@dataclass
class AudioCleanupResults:
    """Results from an audio cleanup operation."""
    completion_time: str
    error: bool
    info: str
    cleaned_audio_file_location: Optional[str] = None

@dataclass
class AudioCleanupResponse(BaseResponse):
    """Response model for audio cleanup endpoint."""
    audio_cleanup_results: Optional[AudioCleanupResults] = None
