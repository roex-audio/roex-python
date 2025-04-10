"""
Models for the mastering-related API endpoints
"""

from dataclasses import dataclass, field
from typing import List, Optional

from roex_python.models.common import DesiredLoudness, MusicalStyle


@dataclass
class MasteringRequest:
    """Model for a mastering preview request"""
    track_url: str
    musical_style: MusicalStyle
    desired_loudness: DesiredLoudness
    sample_rate: str = "44100"
    webhook_url: Optional[str] = None


@dataclass
class MasteringTaskResponse:
    """Response model for mastering task creation"""
    mastering_task_id: str


@dataclass
class AlbumMasteringRequest:
    """Model for processing multiple mastering tasks as an album"""
    tracks: List[MasteringRequest]