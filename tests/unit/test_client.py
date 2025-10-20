"""
Unit tests for RoExClient
"""

import pytest
from unittest.mock import Mock, patch
from roex_python.client import RoExClient
from roex_python.controllers import (
    MixController, MasteringController, AnalysisController,
    EnhanceController, UploadController
)
from roex_python.controllers.audio_cleanup_controller import AudioCleanupController


@pytest.mark.unit
class TestRoExClientInit:
    """Test RoExClient initialization"""
    
    def test_init_with_defaults(self):
        """Test client initialization with default base URL"""
        client = RoExClient(api_key="test_key_123")
        
        assert client.api_provider.api_key == "test_key_123"
        assert client.api_provider.base_url == "https://tonn.roexaudio.com"
    
    def test_init_with_custom_base_url(self):
        """Test client initialization with custom base URL"""
        client = RoExClient(
            api_key="test_key_123",
            base_url="https://custom.roexaudio.com"
        )
        
        assert client.api_provider.base_url == "https://custom.roexaudio.com"
    
    def test_controllers_initialized(self):
        """Test that all controllers are properly initialized"""
        client = RoExClient(api_key="test_key_123")
        
        assert isinstance(client.mix, MixController)
        assert isinstance(client.mastering, MasteringController)
        assert isinstance(client.analysis, AnalysisController)
        assert isinstance(client.enhance, EnhanceController)
        assert isinstance(client.audio_cleanup, AudioCleanupController)
        assert isinstance(client.upload, UploadController)
    
    def test_controllers_share_api_provider(self):
        """Test that all controllers share the same ApiProvider instance"""
        client = RoExClient(api_key="test_key_123")
        
        # All controllers should have the same api_provider instance
        assert client.mix.api_provider is client.api_provider
        assert client.mastering.api_provider is client.api_provider
        assert client.analysis.api_provider is client.api_provider
        assert client.enhance.api_provider is client.api_provider
        assert client.audio_cleanup.api_provider is client.api_provider
        assert client.upload.api_provider is client.api_provider


@pytest.mark.unit
class TestRoExClientHealthCheck:
    """Test health_check method"""
    
    @patch('roex_python.providers.api_provider.requests.get')
    def test_health_check_success(self, mock_get):
        """Test successful health check"""
        # Setup
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = RoExClient(api_key="test_key_123")
        
        # Execute
        result = client.health_check()
        
        # Assert
        assert result == {"status": "healthy"}
        mock_get.assert_called_once()
        
        # Verify correct endpoint was called
        call_args = mock_get.call_args[0]
        assert call_args[0].endswith("/health")
