"""
Integration tests for file upload functionality
Requires: ROEX_API_KEY environment variable and test audio files
"""

import pytest
import os
from roex_python.client import RoExClient
from roex_python.utils import upload_file, get_content_type
from roex_python.models import UploadUrlRequest


@pytest.mark.integration
class TestUploadIntegration:
    """Integration tests for upload operations"""
    
    def test_get_upload_url(self, requires_api_key):
        """Test getting signed upload URL"""
        client = RoExClient(api_key=requires_api_key)
        
        request = UploadUrlRequest(
            filename="test_track.wav",
            content_type="audio/wav"
        )
        
        response = client.upload.get_upload_url(request)
        
        assert response.signed_url is not None
        assert response.readable_url is not None
        assert response.error is False
        print(f"Signed URL: {response.signed_url[:50]}...")
        print(f"Readable URL: {response.readable_url}")
    
    def test_upload_wav_file(self, requires_api_key, integration_audio_file):
        """Test uploading a WAV file"""
        client = RoExClient(api_key=requires_api_key)
        
        readable_url = upload_file(client, integration_audio_file)
        
        assert readable_url is not None
        assert readable_url.startswith("http")
        print(f"Uploaded file URL: {readable_url}")
    
    def test_upload_different_formats(self, requires_api_key, sample_mp3_file):
        """Test uploading different audio formats"""
        # This test uses a mock MP3 file - in real scenarios, use actual audio files
        pytest.skip("Requires real audio files in different formats")
        
        client = RoExClient(api_key=requires_api_key)
        
        # Test MP3
        mp3_url = upload_file(client, sample_mp3_file)
        assert mp3_url is not None
    
    def test_content_type_detection(self):
        """Test content type detection for different file types"""
        assert get_content_type("track.wav") == "audio/wav"
        assert get_content_type("track.mp3") == "audio/mpeg"
        assert get_content_type("track.flac") == "audio/flac"
        
        with pytest.raises(ValueError):
            get_content_type("track.txt")
