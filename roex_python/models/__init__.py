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
    MultitrackMixRequest,
    MultitrackTaskResponse,
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
    MasteringRequest,
    MasteringTaskResponse
)

# Import analysis models
from roex_python.models.analysis import (
    AnalysisMusicalStyle,
    MixAnalysisRequest
)

# Import enhance models
from roex_python.models.enhance import (
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
    "MultitrackMixRequest",
    "MultitrackTaskResponse",
    "TrackData",
    "TrackGainData",
    "TrackEffectsData",
    "EQBandSettings",
    "EQSettings",
    "CompressionSettings",
    "PanningSettings",

    # Mastering models
    "AlbumMasteringRequest",
    "MasteringRequest",
    "MasteringTaskResponse",

    # Analysis models
    "AnalysisMusicalStyle",
    "MixAnalysisRequest",

    # Enhance models
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