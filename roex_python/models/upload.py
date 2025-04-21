from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .common import BaseResponse

@dataclass
class UploadUrlRequest:
    """Request model for getting upload URLs."""
    filename: str
    content_type: str  # Should be one of: audio/mpeg, audio/wav, audio/flac

@dataclass
class UploadUrlResponse(BaseResponse):
    """Response model for upload URL endpoint."""
    signed_url: Optional[str] = None
    readable_url: Optional[str] = None
