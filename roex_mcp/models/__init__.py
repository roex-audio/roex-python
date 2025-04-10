"""
Model definitions for the RoEx Tonn API
"""

# Import common models and enums
from roex_mcp.models.common import (
    DesiredLoudness,
    InstrumentGroup,
    LoudnessPreference,
    MusicalStyle,
    PanPreference,
    PresenceSetting,
    ReverbPreference
)

# Import mixing models
from roex_mcp.models.mixing import (
    FinalMixRequest,
    MultitrackMixRequest,
    MultitrackTaskResponse,
    TrackData,
    TrackGainData
)

# Import mastering models
from roex_mcp.models.mastering import (
    AlbumMasteringRequest,
    MasteringRequest,
    MasteringTaskResponse
)

# Import analysis models
from roex_mcp.models.analysis import (
    AnalysisMusicalStyle,
    MixAnalysisRequest
)

# Import enhance models
from roex_mcp.models.enhance import (
    EnhanceMusicalStyle,
    MixEnhanceRequest,
    MixEnhanceResponse
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
    "MultitrackMixRequest",
    "MultitrackTaskResponse",
    "TrackData",
    "TrackGainData",

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
    "MixEnhanceResponse"
]