"""
Controller for file upload operations
"""

from ..models.upload import UploadUrlRequest, UploadUrlResponse
from ..providers.api_provider import ApiProvider
import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

class UploadController:
    """
    Controller for obtaining pre-signed URLs to upload local files for use with the RoEx API.

    The RoEx API operates on files accessible via URLs. To use a local file, you must first
    obtain a pre-signed upload URL using this controller, upload the file to that URL,
    and then use the corresponding `readable_url` in subsequent API requests (e.g., for
    mixing, mastering, analysis).
    """

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the UploadController.

        Typically, this controller is accessed via `client.upload` rather than
        instantiated directly.

        Args:
            api_provider (ApiProvider): An instance of ApiProvider configured with
                the base URL and API key.
        """
        self.api_provider = api_provider
        logger.info("UploadController initialized.")

    def get_upload_url(self, request: UploadUrlRequest) -> UploadUrlResponse:
        """
        Get a pre-signed URL for uploading a local file and a readable URL for API use.

        Calls the RoEx API's `/upload` endpoint to generate two URLs:
        
        1. ``signed_url``: A temporary URL to which you can upload your local file
           using an HTTP PUT request. This URL has write permissions.
        2. ``readable_url``: The permanent URL that represents the file once uploaded.
           Use this URL in other RoEx API calls (e.g., mastering, mixing) that require
           a file location.

        Args:
            request (UploadUrlRequest): An object containing:
                - ``filename`` (str): The desired filename for the uploaded file (e.g., "my_track.wav").
                - ``content_type`` (str): The MIME type of the file (e.g., "audio/wav", "audio/flac").

        Returns:
            UploadUrlResponse: An object containing `signed_url` and `readable_url`.

        Raises:
            requests.exceptions.RequestException: If the API request to `/upload` fails due to
                                                 network issues or invalid endpoint.
            Exception: If the API returns an error response (e.g., 4xx, 5xx status codes).

        Example:
            >>> import requests
            >>> from roex_python.models import UploadUrlRequest
            >>> # Assume 'client' is an initialized RoExClient
            >>> local_file_path = "path/to/your/audio.wav"
            >>> file_name = "uploaded_track.wav"
            >>> content_type = "audio/wav"
            >>>
            >>> upload_req = UploadUrlRequest(filename=file_name, content_type=content_type)
            >>>
            >>> try:
            >>>     # 1. Get the URLs
            >>>     url_response = client.upload.get_upload_url(upload_req)
            >>>     if url_response.error or not url_response.signed_url or not url_response.readable_url:
            >>>         print(f"Error getting upload URL: {url_response.message}")
            >>>     else:
            >>>         signed_url = url_response.signed_url
            >>>         readable_url = url_response.readable_url
            >>>         print(f"Got signed URL: {signed_url[:50]}...") # Truncated for display
            >>>         print(f"Got readable URL: {readable_url}")
            >>>
            >>>         # 2. Upload the local file using the signed URL
            >>>         with open(local_file_path, 'rb') as f:
            >>>             upload_put_response = requests.put(signed_url, data=f, headers={'Content-Type': content_type})
            >>>
            >>>         if upload_put_response.status_code == 200:
            >>>             print("File uploaded successfully!")
            >>>             # 3. Now use 'readable_url' in other client calls, e.g.:
            >>>             # mastering_request = MasteringRequest(track_url=readable_url, ...)
            >>>             # client.mastering.create_mastering_preview(mastering_request)
            >>>         else:
            >>>             print(f"File upload failed: {upload_put_response.status_code} - {upload_put_response.text}")
            >>>
            >>> except Exception as e:
            >>>     print(f"An error occurred: {e}")
        """
        logger.info("Requesting upload URL")
        logger.debug(f"Upload URL request data: {request}")
        payload = {
            "filename": request.filename,
            "contentType": request.content_type
        }

        try:
            response = self.api_provider.post("/upload", payload)
            logger.info("Upload URL request successful")
            return UploadUrlResponse(
                signed_url=response.get("signed_url"),
                readable_url=response.get("readable_url"),
                error=response.get("error", False),
                message=response.get("message", ""),
                info=response.get("info", "")
            )
        except Exception as e:
            logger.exception(f"Exception during upload URL creation: {e}")
            raise
