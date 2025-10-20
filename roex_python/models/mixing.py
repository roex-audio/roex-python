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
    """
    Represents the data and mixing preferences for a single track within a multitrack mix request.

    Used as an item in the `track_data` list of `MultitrackMixRequest`.
    """
    track_url: str
    """str: The URL of the audio file (WAV or FLAC) for this track. Must be accessible by the RoEx API."""
    instrument_group: InstrumentGroup
    """InstrumentGroup: The classification of the instrument (e.g., VOCAL_GROUP, BASS_GROUP)."""
    presence_setting: PresenceSetting
    """PresenceSetting: Desired prominence in the mix (e.g., LEAD, NORMAL, BACKGROUND)."""
    pan_preference: PanPreference
    """PanPreference: Desired stereo placement (e.g., LEFT, CENTRE, RIGHT, NO_PREFERENCE)."""
    reverb_preference: ReverbPreference = ReverbPreference.NONE
    """ReverbPreference: Desired amount of reverb (e.g., NONE, LOW, MEDIUM, HIGH). Defaults to NONE."""


@dataclass
class TrackGainData:
    """
    Represents gain adjustment data for a specific track when requesting the final mix.

    Used as an item in the `track_data` list of `FinalMixRequest` to apply gain changes
    determined after evaluating the mix preview.
    """
    track_url: str
    """str: The URL of the audio file for this track (should match one from the original preview request)."""
    gain_db: float
    """float: The desired gain adjustment in decibels (dB) to apply to this track in the final mix."""


@dataclass
class MultitrackMixRequest:
    """
    Represents the input parameters for requesting a multitrack mix preview.

    This dataclass structures the data sent to the RoEx API's `/mixpreview` endpoint.
    """
    track_data: List[TrackData]
    """List[TrackData]: A list of `TrackData` objects, one for each track to include in the mix."""
    musical_style: MusicalStyle
    """MusicalStyle: The overall musical style reference for the mix (e.g., POP, ROCK_INDIE)."""
    return_stems: bool = False
    """bool: If True, requests the generation of individual track stems alongside the mix preview. Defaults to False."""
    sample_rate: str = "44100"
    """str: The desired sample rate for the output mix and stems. Defaults to "44100" Hz."""
    webhook_url: Optional[str] = None
    """Optional[str]: A URL to which a notification will be sent upon task completion."""


@dataclass
class MultitrackTaskResponse:
    """
    Represents the immediate response after successfully submitting a multitrack mix task (preview or final).

    Confirms task acceptance and provides the ID for polling results.
    """
    multitrack_task_id: str
    """str: The unique identifier for the initiated multitrack mixing task."""


@dataclass
class FinalMixRequest:
    """
    Represents the input parameters for requesting the final version of a multitrack mix,
    typically after reviewing a preview.

    This dataclass structures the data sent to the RoEx API's `/getfinalmix` endpoint.
    It uses the `multitrack_task_id` from the preview and allows applying gain adjustments.
    """
    multitrack_task_id: str
    """str: The unique task ID obtained from the initial `MultitrackMixRequest` response."""
    track_data: List[TrackGainData]
    """List[TrackGainData]: A list of `TrackGainData` objects specifying gain adjustments for each track in the final mix."""
    return_stems: bool = False
    """bool: If True, requests the generation of individual track stems alongside the final mix. Defaults to False."""
    sample_rate: str = "44100"
    """str: The desired sample rate for the output final mix and stems. Defaults to "44100" Hz."""