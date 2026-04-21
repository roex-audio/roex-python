"""
Models for the mixing-related API endpoints
"""

from dataclasses import dataclass, field
from typing import List, Optional

from roex_python.models.common import (
    DesiredLoudness,
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

    def __post_init__(self):
        """Validate track count is within API limits."""
        if not 2 <= len(self.track_data) <= 32:
            raise ValueError(
                f"track_data must contain between 2 and 32 tracks (API limit), "
                f"got {len(self.track_data)} tracks"
            )


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


# ============================================================================
# Advanced Audio Effects Models
# ============================================================================


@dataclass
class EQBandSettings:
    """
    Settings for a single parametric EQ band.
    
    Allows precise control over frequency, gain, and bandwidth (Q factor) for
    shaping the tonal character of a track.
    """
    gain: float = 0.0
    """float: EQ gain in dB. Range: -20.0 to +20.0. Defaults to 0.0 (no change)."""
    q: float = 1.0
    """float: Q factor (bandwidth). Range: 0.1 to 10.0. Higher Q = narrower bandwidth. Defaults to 1.0."""
    centre_freq: float = 1000.0
    """float: Center frequency in Hz. Range: 20.0 to 20000.0. Defaults to 1000.0 Hz."""

    def __post_init__(self):
        """Validate EQ band parameter ranges."""
        if not -20.0 <= self.gain <= 20.0:
            raise ValueError(f"EQ gain must be between -20.0 and 20.0 dB, got {self.gain}")
        if not 0.1 <= self.q <= 10.0:
            raise ValueError(f"EQ Q factor must be between 0.1 and 10.0, got {self.q}")
        if not 20.0 <= self.centre_freq <= 20000.0:
            raise ValueError(f"EQ centre frequency must be between 20.0 and 20000.0 Hz, got {self.centre_freq}")


@dataclass
class EQSettings:
    """
    6-band parametric EQ configuration for detailed frequency shaping.
    
    Provides control over six frequency bands to sculpt the tonal balance of a track.
    Each band can boost or cut specific frequency ranges with adjustable bandwidth.
    """
    band_1: Optional[EQBandSettings] = None
    """Optional[EQBandSettings]: Low frequency band (typically sub-bass: 20-80 Hz)."""
    band_2: Optional[EQBandSettings] = None
    """Optional[EQBandSettings]: Low-mid frequency band (typically bass: 80-250 Hz)."""
    band_3: Optional[EQBandSettings] = None
    """Optional[EQBandSettings]: Mid frequency band (typically low-mids: 250-500 Hz)."""
    band_4: Optional[EQBandSettings] = None
    """Optional[EQBandSettings]: Mid-high frequency band (typically mids: 500-2000 Hz)."""
    band_5: Optional[EQBandSettings] = None
    """Optional[EQBandSettings]: High frequency band (typically presence: 2000-8000 Hz)."""
    band_6: Optional[EQBandSettings] = None
    """Optional[EQBandSettings]: Very high frequency band (typically air: 8000-20000 Hz)."""

    @staticmethod
    def preset_bass_boost() -> "EQSettings":
        """
        Preset: Enhance low-end presence and warmth.
        
        Returns:
            EQSettings with boosted bass frequencies.
        """
        return EQSettings(
            band_1=EQBandSettings(gain=4.0, q=1.0, centre_freq=60.0),
            band_2=EQBandSettings(gain=3.0, q=0.8, centre_freq=150.0),
            band_3=EQBandSettings(gain=-1.0, q=1.0, centre_freq=400.0)
        )

    @staticmethod
    def preset_vocal_clarity() -> "EQSettings":
        """
        Preset: Enhance vocal presence and intelligibility.
        
        Returns:
            EQSettings optimized for vocal clarity.
        """
        return EQSettings(
            band_2=EQBandSettings(gain=-2.0, q=0.7, centre_freq=200.0),  # Reduce muddiness
            band_4=EQBandSettings(gain=3.0, q=1.2, centre_freq=2500.0),  # Enhance presence
            band_5=EQBandSettings(gain=2.0, q=1.0, centre_freq=5000.0),  # Add clarity
            band_6=EQBandSettings(gain=1.5, q=0.8, centre_freq=10000.0)  # Add air
        )

    @staticmethod
    def preset_kick_punch() -> "EQSettings":
        """
        Preset: Add punch and definition to kick drums.
        
        Returns:
            EQSettings optimized for kick drum punch.
        """
        return EQSettings(
            band_1=EQBandSettings(gain=5.0, q=1.2, centre_freq=50.0),   # Sub thump
            band_2=EQBandSettings(gain=-3.0, q=0.8, centre_freq=250.0), # Remove boxiness
            band_4=EQBandSettings(gain=4.0, q=1.5, centre_freq=3000.0)  # Beater click
        )

    @staticmethod
    def preset_snare_crack() -> "EQSettings":
        """
        Preset: Enhance snare attack and body.
        
        Returns:
            EQSettings optimized for snare presence.
        """
        return EQSettings(
            band_2=EQBandSettings(gain=2.0, q=1.0, centre_freq=200.0),  # Body
            band_3=EQBandSettings(gain=-2.0, q=0.9, centre_freq=500.0), # Reduce honk
            band_5=EQBandSettings(gain=4.0, q=1.2, centre_freq=5000.0), # Crack/snap
            band_6=EQBandSettings(gain=2.0, q=0.7, centre_freq=10000.0) # Air
        )

    @staticmethod
    def preset_high_pass() -> "EQSettings":
        """
        Preset: Remove low-end rumble and mud.
        
        Returns:
            EQSettings with high-pass filter characteristics.
        """
        return EQSettings(
            band_1=EQBandSettings(gain=-12.0, q=0.5, centre_freq=40.0),
            band_2=EQBandSettings(gain=-6.0, q=0.7, centre_freq=80.0)
        )

    @staticmethod
    def preset_brightness() -> "EQSettings":
        """
        Preset: Add sparkle and air to the top end.
        
        Returns:
            EQSettings with enhanced high frequencies.
        """
        return EQSettings(
            band_5=EQBandSettings(gain=3.0, q=0.8, centre_freq=6000.0),
            band_6=EQBandSettings(gain=4.0, q=0.7, centre_freq=12000.0)
        )


@dataclass
class CompressionSettings:
    """
    Dynamic range compression settings for controlling track dynamics.
    
    Compression reduces the dynamic range of audio by attenuating signals above
    a threshold, making quiet parts more audible and loud parts more controlled.
    """
    threshold: float = -20.0
    """float: Compression threshold in dB. Signals above this level are compressed. Range: -60.0 to 0.0. Defaults to -20.0."""
    ratio: float = 4.0
    """float: Compression ratio. For example, 4.0 means 4:1 compression. Range: 1.0 to 20.0. Defaults to 4.0."""
    attack_ms: float = 5.0
    """float: Attack time in milliseconds. How quickly compression engages. Range: 0.1 to 100.0. Defaults to 5.0."""
    release_ms: float = 50.0
    """float: Release time in milliseconds. How quickly compression disengages. Range: 1.0 to 1000.0. Defaults to 50.0."""

    def __post_init__(self):
        """Validate compression parameter ranges."""
        if not -60.0 <= self.threshold <= 0.0:
            raise ValueError(f"Compression threshold must be between -60.0 and 0.0 dB, got {self.threshold}")
        if not 1.0 <= self.ratio <= 20.0:
            raise ValueError(f"Compression ratio must be between 1.0 and 20.0, got {self.ratio}")
        if not 0.1 <= self.attack_ms <= 100.0:
            raise ValueError(f"Compression attack must be between 0.1 and 100.0 ms, got {self.attack_ms}")
        if not 1.0 <= self.release_ms <= 1000.0:
            raise ValueError(f"Compression release must be between 1.0 and 1000.0 ms, got {self.release_ms}")

    @staticmethod
    def preset_vocal() -> "CompressionSettings":
        """
        Preset: Smooth vocal compression for consistent levels.
        
        Returns:
            CompressionSettings optimized for vocals.
        """
        return CompressionSettings(threshold=-18.0, ratio=4.0, attack_ms=5.0, release_ms=40.0)

    @staticmethod
    def preset_drum_bus() -> "CompressionSettings":
        """
        Preset: Glue compression for drum bus cohesion.
        
        Returns:
            CompressionSettings optimized for drum bus.
        """
        return CompressionSettings(threshold=-15.0, ratio=3.0, attack_ms=10.0, release_ms=100.0)

    @staticmethod
    def preset_bass() -> "CompressionSettings":
        """
        Preset: Tight compression for consistent bass levels.
        
        Returns:
            CompressionSettings optimized for bass instruments.
        """
        return CompressionSettings(threshold=-20.0, ratio=5.0, attack_ms=15.0, release_ms=80.0)

    @staticmethod
    def preset_gentle() -> "CompressionSettings":
        """
        Preset: Gentle compression for subtle dynamic control.
        
        Returns:
            CompressionSettings with gentle compression.
        """
        return CompressionSettings(threshold=-24.0, ratio=2.5, attack_ms=20.0, release_ms=150.0)

    @staticmethod
    def preset_aggressive() -> "CompressionSettings":
        """
        Preset: Aggressive compression for maximum impact.
        
        Returns:
            CompressionSettings with aggressive compression.
        """
        return CompressionSettings(threshold=-12.0, ratio=8.0, attack_ms=1.0, release_ms=30.0)


@dataclass
class PanningSettings:
    """
    Stereo panning settings for positioning tracks in the stereo field.
    
    Controls the left-right positioning of a track in the stereo image.
    """
    panning_angle: float = 0.0
    """float: Panning angle in degrees. Range: -60.0 (left) to +60.0 (right). 0.0 is center. Defaults to 0.0."""

    def __post_init__(self):
        """Validate panning parameter range."""
        if not -60.0 <= self.panning_angle <= 60.0:
            raise ValueError(f"Panning angle must be between -60.0 and 60.0 degrees, got {self.panning_angle}")

    @staticmethod
    def center() -> "PanningSettings":
        """Create centered panning."""
        return PanningSettings(panning_angle=0.0)

    @staticmethod
    def hard_left() -> "PanningSettings":
        """Create hard left panning."""
        return PanningSettings(panning_angle=-60.0)

    @staticmethod
    def hard_right() -> "PanningSettings":
        """Create hard right panning."""
        return PanningSettings(panning_angle=60.0)

    @staticmethod
    def slight_left() -> "PanningSettings":
        """Create slight left panning."""
        return PanningSettings(panning_angle=-20.0)

    @staticmethod
    def slight_right() -> "PanningSettings":
        """Create slight right panning."""
        return PanningSettings(panning_angle=20.0)


@dataclass
class TrackEffectsData:
    """
    Advanced track data with comprehensive audio effects for final mix processing.
    
    Extends basic gain control with detailed EQ, compression, and panning settings
    for professional-quality mix refinement. Used in `FinalMixRequest` for the
    `/retrievefinalmix` endpoint with the `applyAudioEffectsData` payload.
    """
    track_url: str
    """str: The URL of the audio file for this track (should match one from the original preview request)."""
    gain_db: float = 0.0
    """float: The desired gain adjustment in decibels (dB) to apply to this track. Defaults to 0.0."""
    panning_settings: Optional[PanningSettings] = None
    """Optional[PanningSettings]: Stereo panning configuration. If None, panning remains unchanged."""
    eq_settings: Optional[EQSettings] = None
    """Optional[EQSettings]: 6-band parametric EQ configuration. If None, no EQ is applied."""
    compression_settings: Optional[CompressionSettings] = None
    """Optional[CompressionSettings]: Dynamic range compression configuration. If None, no compression is applied."""


@dataclass
class FinalMixRequestAdvanced:
    """
    Advanced final mix request with support for detailed audio effects processing.
    
    This is the enhanced version of FinalMixRequest that supports the new advanced
    audio effects features including EQ, compression, and panning. Use this for
    professional mixing workflows that require precise control over track processing.
    
    Note: This request uses the multitrack_task_id from a previous mix preview,
    so the track count was already validated during the preview creation.
    """
    multitrack_task_id: str
    """str: The unique task ID obtained from the initial `MultitrackMixRequest` response."""
    track_data: List[TrackEffectsData]
    """List[TrackEffectsData]: A list of `TrackEffectsData` objects with advanced audio effects for each track."""
    return_stems: bool = False
    """bool: If True, requests the generation of individual track stems alongside the final mix. Defaults to False."""
    create_master: bool = False
    """bool: If True, creates a mastered version of the final mix. Defaults to False."""
    desired_loudness: Optional[DesiredLoudness] = None
    """Optional[DesiredLoudness]: Target loudness level (LOW, MEDIUM, HIGH). Only applicable when not creating stems."""
    sample_rate: str = "44100"
    """str: The desired sample rate for the output. "44100" for 44.1kHz (16-bit) or "48000" for 48kHz (24-bit). Defaults to "44100"."""
    webhook_url: Optional[str] = None
    """Optional[str]: A URL to which a notification will be sent upon task completion."""