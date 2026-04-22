"""
Model definitions for the RoEx Tonn API
"""

# Import common models and enums
from roex_python.models.common import (
    DesiredLoudness,
    InstrumentGroup,
    LoudnessPreference,
    MusicalStyle,
    PanPreference,
    PresenceSetting,
    ReverbPreference
)

# Import mixing models
from roex_python.models.mixing import (
    FinalMixRequest,
    FinalMixRequestAdvanced,
    FinalMixResult,
    MultitrackMixRequest,
    MultitrackTaskResponse,
    PreviewMixResult,
    TrackData,
    TrackGainData,
    TrackEffectsData,
    EQBandSettings,
    EQSettings,
    CompressionSettings,
    PanningSettings
)

# Import mastering models
from roex_python.models.mastering import (
    AlbumMasteringRequest,
    FinalMasterResult,
    MasteringRequest,
    MasteringTaskResponse,
    PreviewMasterResult
)

# Import analysis models
from roex_python.models.analysis import (
    AnalysisMusicalStyle,
    AnalysisResult,
    MixAnalysisRequest
)

# Import enhance models
from roex_python.models.enhance import (
    EnhancedTrackResult,
    EnhanceMusicalStyle,
    MixEnhanceRequest,
    MixEnhanceResponse
)

# Import upload models
from roex_python.models.upload import (
    UploadUrlRequest,
    UploadUrlResponse
)

# Import audio cleanup models
from roex_python.models.audio_cleanup import (
    AudioCleanupData,
    AudioCleanupResults,
    AudioCleanupResponse,
    SoundSource
)

__all__ = [
    # Common models
    "DesiredLoudness",
    "InstrumentGroup",
    "LoudnessPreference",
    "MusicalStyle",
    "PanPreference",
    "PresenceSetting",
    "ReverbPreference",

    # Mixing models
    "FinalMixRequest",
    "FinalMixRequestAdvanced",
    "FinalMixResult",
    "MultitrackMixRequest",
    "MultitrackTaskResponse",
    "PreviewMixResult",
    "TrackData",
    "TrackGainData",
    "TrackEffectsData",
    "EQBandSettings",
    "EQSettings",
    "CompressionSettings",
    "PanningSettings",

    # Mastering models
    "AlbumMasteringRequest",
    "FinalMasterResult",
    "MasteringRequest",
    "MasteringTaskResponse",
    "PreviewMasterResult",

    # Analysis models
    "AnalysisMusicalStyle",
    "AnalysisResult",
    "MixAnalysisRequest",

    # Enhance models
    "EnhancedTrackResult",
    "EnhanceMusicalStyle",
    "MixEnhanceRequest",
    "MixEnhanceResponse",

    # Upload models
    "UploadUrlRequest",
    "UploadUrlResponse",

    # Audio Cleanup models
    "AudioCleanupData",
    "AudioCleanupResults",
    "AudioCleanupResponse",
    "SoundSource"
]