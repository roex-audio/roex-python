"""
Models for the mixing-related API endpoints
"""

from dataclasses import dataclass, field
from typing import List, Optional

from roex_python.models.common import (
    InstrumentGroup,
    MusicalStyle,
    PanPreference,
    PresenceSetting,
    ReverbPreference,
)


@dataclass
class TrackData:
    """Model for a single track in a multitrack mix"""
    track_url: str
    instrument_group: InstrumentGroup
    presence_setting: PresenceSetting
    pan_preference: PanPreference
    reverb_preference: ReverbPreference = ReverbPreference.NONE


@dataclass
class TrackGainData:
    """Model for a track with gain settings for the final mix"""
    track_url: str
    gain_db: float


@dataclass
class MultitrackMixRequest:
    """Model for a multitrack mix preview request"""
    track_data: List[TrackData]
    musical_style: MusicalStyle
    return_stems: bool = False
    sample_rate: str = "44100"
    webhook_url: Optional[str] = None


@dataclass
class MultitrackTaskResponse:
    """Response model for multitrack mix task creation"""
    multitrack_task_id: str


@dataclass
class FinalMixRequest:
    """Model for retrieving a final mix with gain adjustments"""
    multitrack_task_id: str
    track_data: List[TrackGainData]
    return_stems: bool = False
    sample_rate: str = "44100"