"""
Unit tests for ApiProvider
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import requests
from roex_python.providers.api_provider import ApiProvider


@pytest.mark.unit
class TestApiProviderInit:
    """Test ApiProvider initialization"""
    
    def test_init_with_required_params(self):
        """Test initialization with base_url and api_key"""
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key_123"
        )
        
        assert provider.base_url == "https://test.roexaudio.com"
        assert provider.api_key == "test_key_123"
        assert provider.headers["Content-Type"] == "application/json"
        assert provider.headers["x-api-key"] == "test_key_123"


@pytest.mark.unit
class TestApiProviderPost:
    """Test POST request method"""
    
    @patch('roex_python.providers.api_provider.requests.post')
    def test_successful_post_request(self, mock_post):
        """Test successful POST request"""
        # Setup
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "task_id": "123"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute
        result = provider.post("/test", {"data": "value"})
        
        # Assert
        assert result == {"success": True, "task_id": "123"}
        mock_post.assert_called_once_with(
            "https://test.roexaudio.com/test",
            json={"data": "value"},
            headers=provider.headers
        )
    
    @patch('roex_python.providers.api_provider.requests.post')
    def test_post_with_http_error(self, mock_post):
        """Test POST request with HTTP error"""
        # Setup
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Error")
        mock_post.return_value = mock_response
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute & Assert
        with pytest.raises(requests.HTTPError):
            provider.post("/notfound", {"data": "value"})
    
    @patch('roex_python.providers.api_provider.requests.post')
    def test_post_with_non_json_response(self, mock_post):
        """Test POST request that returns non-JSON response"""
        # Setup
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.text = "Plain text response"
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute
        result = provider.post("/test", {"data": "value"})
        
        # Assert
        assert result == {"response": "Plain text response"}
    
    @patch('roex_python.providers.api_provider.requests.post')
    def test_post_with_connection_error(self, mock_post):
        """Test POST request with connection error"""
        # Setup
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute & Assert
        with pytest.raises(requests.exceptions.ConnectionError):
            provider.post("/test", {"data": "value"})
    
    @patch('roex_python.providers.api_provider.requests.post')
    def test_post_url_construction(self, mock_post):
        """Test that URLs are constructed correctly"""
        # Setup
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute
        provider.post("/api/endpoint", {})
        
        # Assert
        call_args = mock_post.call_args[0]
        assert call_args[0] == "https://test.roexaudio.com/api/endpoint"


@pytest.mark.unit
class TestApiProviderGet:
    """Test GET request method"""
    
    @patch('roex_python.providers.api_provider.requests.get')
    def test_successful_get_request(self, mock_get):
        """Test successful GET request"""
        # Setup
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute
        result = provider.get("/health")
        
        # Assert
        assert result == {"status": "healthy"}
        mock_get.assert_called_once_with(
            "https://test.roexaudio.com/health",
            headers=provider.headers
        )
    
    @patch('roex_python.providers.api_provider.requests.get')
    def test_get_with_http_error(self, mock_get):
        """Test GET request with HTTP error"""
        # Setup
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Error")
        mock_get.return_value = mock_response
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute & Assert
        with pytest.raises(requests.HTTPError):
            provider.get("/error")
    
    @patch('roex_python.providers.api_provider.requests.get')
    def test_get_with_text_response(self, mock_get):
        """Test GET request that returns plain text"""
        # Setup
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.text = "OK"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute
        result = provider.get("/health")
        
        # Assert
        assert result == "OK"


@pytest.mark.unit
class TestApiProviderDownloadFile:
    """Test file download functionality"""
    
    @patch('roex_python.providers.api_provider.requests.get')
    @patch('roex_python.providers.api_provider.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_successful_download(self, mock_file, mock_makedirs, mock_get):
        """Test successful file download"""
        # Setup
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_content = Mock(return_value=[b'chunk1', b'chunk2'])
        mock_get.return_value.__enter__ = Mock(return_value=mock_response)
        mock_get.return_value.__exit__ = Mock(return_value=None)
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute
        result = provider.download_file(
            "https://example.com/file.wav",
            "/tmp/downloaded.wav"
        )
        
        # Assert
        assert result is True
        mock_get.assert_called_once_with("https://example.com/file.wav", stream=True)
    
    @patch('roex_python.providers.api_provider.requests.get')
    @patch('roex_python.providers.api_provider.os.makedirs')
    def test_download_with_http_error(self, mock_makedirs, mock_get):
        """Test download with HTTP error"""
        # Setup
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Error")
        mock_get.return_value.__enter__ = Mock(return_value=mock_response)
        mock_get.return_value.__exit__ = Mock(return_value=None)
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute
        result = provider.download_file(
            "https://example.com/notfound.wav",
            "/tmp/downloaded.wav"
        )
        
        # Assert
        assert result is False
    
    @patch('roex_python.providers.api_provider.requests.get')
    @patch('roex_python.providers.api_provider.os.makedirs')
    @patch('builtins.open', side_effect=IOError("Write failed"))
    def test_download_with_write_error(self, mock_file, mock_makedirs, mock_get):
        """Test download with file write error"""
        # Setup
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_content = Mock(return_value=[b'chunk'])
        mock_get.return_value.__enter__ = Mock(return_value=mock_response)
        mock_get.return_value.__exit__ = Mock(return_value=None)
        
        provider = ApiProvider(
            base_url="https://test.roexaudio.com",
            api_key="test_key"
        )
        
        # Execute
        result = provider.download_file(
            "https://example.com/file.wav",
            "/invalid/path/downloaded.wav"
        )
        
        # Assert
        assert result is False
