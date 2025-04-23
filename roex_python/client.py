"""
Main RoEx client interface that unifies all controllers
"""

from .controllers.mix_controller import MixController
from .controllers.mastering_controller import MasteringController
from .controllers.analysis_controller import AnalysisController
from .controllers.enhance_controller import EnhanceController
from .controllers.audio_cleanup_controller import AudioCleanupController
from .controllers.upload_controller import UploadController
from .providers.api_provider import ApiProvider
import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

class RoExClient:
    """
    Main client for interacting with the RoEx Tonn API.

    This client provides access to various audio processing features through dedicated controllers:
    - `mix`: Multitrack mixing (preview, final, gain adjustments).
    - `mastering`: Audio mastering (preview, final).
    - `analysis`: Mix/master analysis.
    - `enhance`: Mix enhancement.
    - `audio_cleanup`: Audio source cleanup.
    - `upload`: File upload helpers (getting signed URLs).

    Authentication is handled via an API key.

    Attributes:
        api_provider (ApiProvider): Handles the underlying HTTP requests and authentication.
        mix (MixController): Controller for mixing operations.
        mastering (MasteringController): Controller for mastering operations.
        analysis (AnalysisController): Controller for analysis operations.
        enhance (EnhanceController): Controller for enhancement operations.
        audio_cleanup (AudioCleanupController): Controller for cleanup operations.
        upload (UploadController): Controller for file upload operations.

    Example:
        >>> from roex_python.client import RoExClient
        >>> import os
        >>>
        >>> api_key = os.environ.get("ROEX_API_KEY")
        >>> if not api_key:
        >>>     raise ValueError("ROEX_API_KEY environment variable not set.")
        >>>
        >>> client = RoExClient(api_key=api_key)
        >>> try:
        >>>     health_status = client.health_check()
        >>>     print(f"API Health: {health_status}")
        >>> except Exception as e:
        >>>     print(f"Failed to connect to API: {e}")
    """

    def __init__(self, api_key: str, base_url: str = "https://tonn.roexaudio.com"):
        """
        Initialize the RoEx client.

        Args:
            api_key (str): Your RoEx API key. Obtainable from the RoEx Tonn Portal:
                https://tonn-portal.roexaudio.com
            base_url (str, optional): The base URL for the RoEx Tonn API.
                Defaults to "https://tonn.roexaudio.com".
                Can be changed for testing or specific API environments.

        Raises:
            ValueError: If the API key is invalid or missing (though actual check happens on first API call).
        """
        if not api_key:
            # Early check for missing key, though ApiProvider might do more validation
            raise ValueError("API key cannot be empty.")
        self.api_provider = ApiProvider(base_url=base_url, api_key=api_key)
        logger.info(f"RoExClient initialized for base URL: {base_url}")

        # Initialize controllers
        self.mix = MixController(self.api_provider)
        self.mastering = MasteringController(self.api_provider)
        self.analysis = AnalysisController(self.api_provider)
        self.enhance = EnhanceController(self.api_provider)
        self.audio_cleanup = AudioCleanupController(self.api_provider)
        self.upload = UploadController(self.api_provider)

    def health_check(self) -> str:
        """
        Perform a simple health check against the RoEx API.

        This method sends a GET request to the API's health endpoint.
        A successful response indicates that the API is reachable and operational.

        Returns:
            str: A status message from the API, typically indicating health (e.g., "OK").

        Raises:
            requests.exceptions.RequestException: If there's an issue connecting to the API
                                                 (e.g., network error, invalid URL).
            Exception: For other potential API errors (e.g., 4xx/5xx responses handled by ApiProvider).

        Example:
            >>> client = RoExClient(api_key="YOUR_API_KEY")
            >>> try:
            >>>     status = client.health_check()
            >>>     print(f"API Status: {status}")
            >>> except Exception as e:
            >>>     print(f"Health check failed: {e}")
        """
        # The actual request is simple, but the docstring explains the context.
        try:
            response = self.api_provider.get("/health")
            # Assuming ApiProvider returns the response body directly for simple GETs
            # or raises an exception on failure.
            logger.info(f"API health check successful: {response}")
            return response
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            raise # Re-raise the exception after logging