"""
Unit tests for AnalysisController
"""

import pytest
from unittest.mock import Mock
import requests
from roex_python.controllers.analysis_controller import AnalysisController
from roex_python.models import MixAnalysisRequest, AnalysisMusicalStyle


@pytest.mark.unit
class TestAnalysisControllerInit:
    """Test AnalysisController initialization"""
    
    def test_init(self, mock_api_provider):
        """Test controller initialization"""
        controller = AnalysisController(mock_api_provider)
        assert controller.api_provider == mock_api_provider


@pytest.mark.unit
class TestAnalyzeMix:
    """Test analyze_mix method"""
    
    def test_successful_analysis(self, mock_api_provider):
        """Test successful mix analysis"""
        # Setup
        mock_api_provider.post.return_value = {
            "mixDiagnosisResults": {
                "payload": {
                    "integrated_loudness_lufs": -14.5,
                    "peak_loudness_dbfs": -1.2,
                    "bit_depth": 24,
                    "sample_rate": 44100,
                    "clipping": "NO",
                    "musical_style": "POP",
                    "stereo_field": "GOOD"
                }
            }
        }
        
        controller = AnalysisController(mock_api_provider)
        
        request = MixAnalysisRequest(
            audio_file_location="https://example.com/mix.wav",
            musical_style=AnalysisMusicalStyle.POP,
            is_master=False
        )
        
        # Execute
        result = controller.analyze_mix(request)
        
        # Assert
        assert "payload" in result
        assert result["payload"]["integrated_loudness_lufs"] == -14.5
        assert result["payload"]["clipping"] == "NO"
        
        # Verify correct payload was sent
        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/mixanalysis"
        payload = call_args[0][1]
        assert payload["mixDiagnosisData"]["audioFileLocation"] == "https://example.com/mix.wav"
        assert payload["mixDiagnosisData"]["musicalStyle"] == "POP"
        assert payload["mixDiagnosisData"]["isMaster"] is False
    
    def test_master_analysis(self, mock_api_provider):
        """Test analysis of a mastered track"""
        # Setup
        mock_api_provider.post.return_value = {
            "mixDiagnosisResults": {
                "payload": {
                    "integrated_loudness_lufs": -9.0,
                    "if_master_loudness": "GOOD"
                }
            }
        }
        
        controller = AnalysisController(mock_api_provider)
        
        request = MixAnalysisRequest(
            audio_file_location="https://example.com/master.wav",
            musical_style=AnalysisMusicalStyle.POP,
            is_master=True
        )
        
        # Execute
        result = controller.analyze_mix(request)
        
        # Assert
        payload = mock_api_provider.post.call_args[0][1]
        assert payload["mixDiagnosisData"]["isMaster"] is True
    
    def test_response_without_expected_format(self, mock_api_provider):
        """Test handling of response without expected format"""
        # Setup
        mock_api_provider.post.return_value = {
            "some_other_key": "value"
        }
        
        controller = AnalysisController(mock_api_provider)
        
        request = MixAnalysisRequest(
            audio_file_location="https://example.com/mix.wav",
            musical_style=AnalysisMusicalStyle.POP,
            is_master=False
        )
        
        # Execute
        result = controller.analyze_mix(request)
        
        # Assert - should return raw response
        assert result == {"some_other_key": "value"}
    
    def test_http_error_handling(self, mock_api_provider):
        """Test error handling when API returns HTTP error"""
        # Setup
        mock_api_provider.post.side_effect = requests.HTTPError("API Error")
        
        controller = AnalysisController(mock_api_provider)
        
        request = MixAnalysisRequest(
            audio_file_location="https://example.com/mix.wav",
            musical_style=AnalysisMusicalStyle.POP,
            is_master=False
        )
        
        # Execute & Assert
        with pytest.raises(Exception, match="Failed to analyze mix"):
            controller.analyze_mix(request)


@pytest.mark.unit
class TestCompareMixes:
    """Test compare_mixes method"""
    
    def test_successful_comparison(self, mock_api_provider):
        """Test successful comparison of two mixes"""
        # Setup - return different results for each call
        mock_api_provider.post.side_effect = [
            {
                "mixDiagnosisResults": {
                    "payload": {
                        "integrated_loudness_lufs": -14.0,
                        "peak_loudness_dbfs": -1.0,
                        "clipping": "NO",
                        "stereo_field": "GOOD"
                    }
                }
            },
            {
                "mixDiagnosisResults": {
                    "payload": {
                        "integrated_loudness_lufs": -12.0,
                        "peak_loudness_dbfs": -0.5,
                        "clipping": "YES",
                        "stereo_field": "NARROW"
                    }
                }
            }
        ]
        
        controller = AnalysisController(mock_api_provider)
        
        # Execute
        result = controller.compare_mixes(
            mix_a_url="https://example.com/mix_a.wav",
            mix_b_url="https://example.com/mix_b.wav",
            musical_style=AnalysisMusicalStyle.POP,
            is_master=False
        )
        
        # Assert structure
        assert "mix_a" in result
        assert "mix_b" in result
        assert "differences" in result
        
        # Assert API was called twice
        assert mock_api_provider.post.call_count == 2
    
    def test_comparison_differences(self, mock_api_provider):
        """Test that differences are calculated correctly"""
        # Setup
        mock_api_provider.post.side_effect = [
            {
                "mixDiagnosisResults": {
                    "payload": {
                        "integrated_loudness_lufs": -14.0,
                        "peak_loudness_dbfs": -1.0,
                        "bit_depth": 24,
                        "sample_rate": 44100,
                        "clipping": "NO"
                    }
                }
            },
            {
                "mixDiagnosisResults": {
                    "payload": {
                        "integrated_loudness_lufs": -10.0,
                        "peak_loudness_dbfs": -0.1,
                        "bit_depth": 16,
                        "sample_rate": 48000,
                        "clipping": "YES"
                    }
                }
            }
        ]
        
        controller = AnalysisController(mock_api_provider)
        
        # Execute
        result = controller.compare_mixes(
            mix_a_url="https://example.com/mix_a.wav",
            mix_b_url="https://example.com/mix_b.wav",
            musical_style=AnalysisMusicalStyle.POP
        )
        
        # Assert numeric differences
        diffs = result["differences"]
        assert "integrated_loudness_lufs" in diffs
        assert diffs["integrated_loudness_lufs"]["difference"] == 4.0
        assert diffs["integrated_loudness_lufs"]["mix_a_value"] == -14.0
        assert diffs["integrated_loudness_lufs"]["mix_b_value"] == -10.0
        
        # Assert categorical differences
        assert diffs["clipping"]["status"] == "DIFFERENT"
        assert diffs["clipping"]["mix_a_value"] == "NO"
        assert diffs["clipping"]["mix_b_value"] == "YES"


@pytest.mark.unit
class TestExtractMetrics:
    """Test _extract_metrics method"""
    
    def test_extract_all_metrics(self, mock_api_provider):
        """Test extraction of all available metrics"""
        controller = AnalysisController(mock_api_provider)
        
        diagnosis = {
            "payload": {
                "bit_depth": 24,
                "clipping": "NO",
                "integrated_loudness_lufs": -14.5,
                "peak_loudness_dbfs": -1.2,
                "sample_rate": 44100,
                "stereo_field": "GOOD",
                "musical_style": "POP",
                "tonal_profile": {
                    "bass_frequency": "GOOD",
                    "high_frequency": "BRIGHT"
                }
            }
        }
        
        # Execute
        metrics = controller._extract_metrics(diagnosis)
        
        # Assert
        assert metrics["bit_depth"] == 24
        assert metrics["clipping"] == "NO"
        assert metrics["integrated_loudness_lufs"] == -14.5
        assert metrics["sample_rate"] == 44100
        assert "tonal_profile" in metrics
        assert metrics["tonal_profile"]["bass_frequency"] == "GOOD"
    
    def test_extract_with_missing_fields(self, mock_api_provider):
        """Test extraction when some fields are missing"""
        controller = AnalysisController(mock_api_provider)
        
        diagnosis = {
            "payload": {
                "integrated_loudness_lufs": -14.5,
                # Missing many fields
            }
        }
        
        # Execute
        metrics = controller._extract_metrics(diagnosis)
        
        # Assert - missing fields should be "N/A"
        assert metrics["integrated_loudness_lufs"] == -14.5
        assert metrics["clipping"] == "N/A"
        assert metrics["bit_depth"] == "N/A"
    
    def test_extract_with_empty_payload(self, mock_api_provider):
        """Test extraction with empty payload"""
        controller = AnalysisController(mock_api_provider)
        
        diagnosis = {}
        
        # Execute
        metrics = controller._extract_metrics(diagnosis)
        
        # Assert - all fields should be "N/A"
        assert all(value == "N/A" or value == {} for value in metrics.values())


@pytest.mark.unit
class TestCompareMetrics:
    """Test _compare_metrics method"""
    
    def test_numeric_comparison(self, mock_api_provider):
        """Test comparison of numeric values"""
        controller = AnalysisController(mock_api_provider)
        
        results_a = {
            "payload": {
                "integrated_loudness_lufs": -14.0,
                "peak_loudness_dbfs": -1.0,
                "bit_depth": 24,
                "sample_rate": 44100
            }
        }
        
        results_b = {
            "payload": {
                "integrated_loudness_lufs": -10.0,
                "peak_loudness_dbfs": -0.5,
                "bit_depth": 16,
                "sample_rate": 48000
            }
        }
        
        # Execute
        differences = controller._compare_metrics(results_a, results_b)
        
        # Assert
        assert differences["integrated_loudness_lufs"]["difference"] == 4.0
        assert differences["peak_loudness_dbfs"]["difference"] == 0.5
        assert differences["bit_depth"]["difference"] == 8.0
        assert differences["sample_rate"]["difference"] == 3900.0
    
    def test_categorical_comparison(self, mock_api_provider):
        """Test comparison of categorical values"""
        controller = AnalysisController(mock_api_provider)
        
        results_a = {
            "payload": {
                "clipping": "NO",
                "stereo_field": "GOOD"
            }
        }
        
        results_b = {
            "payload": {
                "clipping": "YES",
                "stereo_field": "GOOD"
            }
        }
        
        # Execute
        differences = controller._compare_metrics(results_a, results_b)
        
        # Assert
        assert differences["clipping"]["status"] == "DIFFERENT"
        assert differences["stereo_field"]["status"] == "SAME"
    
    def test_tonal_profile_comparison(self, mock_api_provider):
        """Test comparison of tonal profiles"""
        controller = AnalysisController(mock_api_provider)
        
        results_a = {
            "payload": {
                "tonal_profile": {
                    "bass_frequency": "GOOD",
                    "high_frequency": "BRIGHT"
                }
            }
        }
        
        results_b = {
            "payload": {
                "tonal_profile": {
                    "bass_frequency": "WEAK",
                    "high_frequency": "BRIGHT"
                }
            }
        }
        
        # Execute
        differences = controller._compare_metrics(results_a, results_b)
        
        # Assert
        assert differences["tonal_profile"]["bass_frequency"]["status"] == "DIFFERENT"
        assert differences["tonal_profile"]["high_frequency"]["status"] == "SAME"
