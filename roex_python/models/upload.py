from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .common import BaseResponse

@dataclass
class UploadUrlRequest:
    """
    Represents the input parameters for requesting pre-signed URLs to upload a file.

    This dataclass structures the data sent to the RoEx API's `/upload` endpoint.
    """
    filename: str
    """str: The desired name for the file once uploaded (e.g., 'my_track.wav')."""
    content_type: str
    """str: The MIME type of the file being uploaded (e.g., 'audio/wav', 'audio/flac', 'audio/mpeg')."""

@dataclass
class UploadUrlResponse(BaseResponse):
    """
    Represents the response received after requesting upload URLs.

    Contains the necessary URLs for uploading a file and referencing it in subsequent API calls.
    Inherits common status fields (`error`, `message`, `info`) from `BaseResponse`.
    """
    signed_url: Optional[str] = None
    """Optional[str]: The pre-signed URL to use for uploading the file via an HTTP PUT request. This URL is temporary and has write permissions."""
    readable_url: Optional[str] = None
    """Optional[str]: The permanent URL that represents the uploaded file. Use this URL in other RoEx API calls (e.g., mixing, mastering) that require a file location."""
