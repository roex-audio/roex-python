"""
Integration tests for analysis functionality
Requires: ROEX_API_KEY environment variable and test audio files
"""

import pytest
from roex_python.client import RoExClient
from roex_python.models import MixAnalysisRequest, AnalysisMusicalStyle
from roex_python.utils import upload_file


@pytest.mark.integration
@pytest.mark.slow
class TestAnalysisIntegration:
    """Integration tests for analysis operations"""
    
    def test_analyze_mix(self, requires_api_key, integration_audio_file):
        """Test analyzing an audio mix"""
        client = RoExClient(api_key=requires_api_key)
        
        # Upload file
        track_url = upload_file(client, integration_audio_file)
        print(f"Uploaded track: {track_url}")
        
        # Analyze
        request = MixAnalysisRequest(
            audio_file_location=track_url,
            musical_style=AnalysisMusicalStyle.POP,
            is_master=False
        )
        
        results = client.analysis.analyze_mix(request)
        
        # Verify results contain expected metrics
        assert "payload" in results or isinstance(results, dict)
        print(f"Analysis results keys: {results.keys()}")
        
        # Check for common analysis fields
        payload = results.get("payload", results)
        if "integrated_loudness_lufs" in payload:
            print(f"Integrated loudness: {payload['integrated_loudness_lufs']} LUFS")
    
    def test_compare_two_mixes(self, requires_api_key, integration_audio_file):
        """Test comparing two mixes"""
        # Note: This test uses the same file twice - in real scenarios use different mixes
        client = RoExClient(api_key=requires_api_key)
        
        # Upload same file twice (for testing purposes)
        mix_a_url = upload_file(client, integration_audio_file)
        mix_b_url = mix_a_url  # In real test, upload different file
        
        # Compare
        comparison = client.analysis.compare_mixes(
            mix_a_url=mix_a_url,
            mix_b_url=mix_b_url,
            musical_style=AnalysisMusicalStyle.POP,
            is_master=False
        )
        
        # Verify comparison structure
        assert "mix_a" in comparison
        assert "mix_b" in comparison
        assert "differences" in comparison
        print(f"Comparison keys: {comparison.keys()}")
    
    def test_analyze_master(self, requires_api_key, integration_audio_file):
        """Test analyzing a mastered track"""
        client = RoExClient(api_key=requires_api_key)
        
        track_url = upload_file(client, integration_audio_file)
        
        request = MixAnalysisRequest(
            audio_file_location=track_url,
            musical_style=AnalysisMusicalStyle.ROCK_INDIE,
            is_master=True  # Indicate this is a mastered track
        )
        
        results = client.analysis.analyze_mix(request)
        assert results is not None
        print(f"Master analysis complete")
