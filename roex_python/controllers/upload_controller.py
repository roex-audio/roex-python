"""
Controller for file upload operations
"""

from ..models.upload import UploadUrlRequest, UploadUrlResponse
from ..providers.api_provider import ApiProvider

class UploadController:
    """Controller for file upload operations."""

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the upload controller

        Args:
            api_provider: Provider for API interactions
        """
        self.api_provider = api_provider

    def get_upload_url(self, request: UploadUrlRequest) -> UploadUrlResponse:
        """
        Get signed URLs for uploading and accessing an audio file.

        Args:
            request: Upload URL request parameters

        Returns:
            Response containing signed upload URL and readable URL

        Raises:
            Exception: If the API request fails
        """
        payload = {
            "filename": request.filename,
            "contentType": request.content_type
        }

        response = self.api_provider.post("/upload", payload)
        
        return UploadUrlResponse(
            signed_url=response.get("signed_url"),
            readable_url=response.get("readable_url"),
            error=response.get("error", False),
            message=response.get("message", ""),
            info=response.get("info", "")
        )
