"""
Main RoEx client interface that unifies all controllers
"""

from roex_mcp.controllers.analysis_controller import AnalysisController
from roex_mcp.controllers.enhance_controller import EnhanceController
from roex_mcp.controllers.mastering_controller import MasteringController
from roex_mcp.controllers.mix_controller import MixController
from roex_mcp.providers.api_provider import ApiProvider


class RoExClient:
    """
    Main client for the RoEx Tonn API, providing access to all audio processing features
    """

    def __init__(self, api_key: str, base_url: str = "https://tonn.roexaudio.com"):
        """
        Initialize the RoEx client

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
        """
        self.api_provider = ApiProvider(base_url=base_url, api_key=api_key)

        # Initialize controllers
        self.mix = MixController(self.api_provider)
        self.mastering = MasteringController(self.api_provider)
        self.analysis = AnalysisController(self.api_provider)
        self.enhance = EnhanceController(self.api_provider)

    def health_check(self) -> str:
        """
        Check if the API is healthy

        Returns:
            Health status message
        """
        return self.api_provider.get("/health")