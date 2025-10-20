"""
Pytest configuration and shared fixtures for all tests
"""

import os
import pytest
from unittest.mock import Mock, MagicMock
from roex_python.client import RoExClient
from roex_python.providers.api_provider import ApiProvider
from roex_python.models import (
    MusicalStyle, DesiredLoudness, InstrumentGroup,
    PresenceSetting, PanPreference, ReverbPreference
)


@pytest.fixture
def api_key():
    """Returns API key from environment or a test key"""
    return os.getenv("ROEX_API_KEY", "test_api_key_12345")


@pytest.fixture
def base_url():
    """Returns base URL for API"""
    return "https://tonn.roexaudio.com"


@pytest.fixture
def mock_api_provider():
    """Returns a mocked ApiProvider for unit testing"""
    mock = Mock(spec=ApiProvider)
    mock.base_url = "https://test.roexaudio.com"
    mock.api_key = "test_key"
    return mock


@pytest.fixture
def roex_client(api_key, base_url):
    """Returns a configured RoExClient instance for integration tests"""
    return RoExClient(api_key=api_key, base_url=base_url)


@pytest.fixture
def mock_requests_response():
    """Returns a mock requests Response object"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = {"success": True}
    mock_response.text = '{"success": true}'
    mock_response.raise_for_status = Mock()
    return mock_response


@pytest.fixture
def sample_audio_file(tmp_path):
    """Creates a temporary audio file for testing"""
    audio_file = tmp_path / "test_track.wav"
    # Create a minimal WAV file (just header, not actual audio)
    # In real tests, you'd use a proper audio file
    audio_file.write_bytes(b"RIFF" + b"\x00" * 44)
    return str(audio_file)


@pytest.fixture
def sample_mp3_file(tmp_path):
    """Creates a temporary MP3 file for testing"""
    mp3_file = tmp_path / "test_track.mp3"
    mp3_file.write_bytes(b"ID3" + b"\x00" * 100)
    return str(mp3_file)


@pytest.fixture
def sample_flac_file(tmp_path):
    """Creates a temporary FLAC file for testing"""
    flac_file = tmp_path / "test_track.flac"
    flac_file.write_bytes(b"fLaC" + b"\x00" * 100)
    return str(flac_file)


@pytest.fixture
def sample_track_data():
    """Returns sample track data for mixing tests"""
    from roex_python.models import TrackData
    
    return [
        TrackData(
            track_url="https://example.com/bass.wav",
            instrument_group=InstrumentGroup.BASS_GROUP,
            presence_setting=PresenceSetting.NORMAL,
            pan_preference=PanPreference.CENTRE,
            reverb_preference=ReverbPreference.NONE
        ),
        TrackData(
            track_url="https://example.com/vocals.wav",
            instrument_group=InstrumentGroup.VOCAL_GROUP,
            presence_setting=PresenceSetting.LEAD,
            pan_preference=PanPreference.CENTRE,
            reverb_preference=ReverbPreference.LOW
        )
    ]


@pytest.fixture
def mock_mastering_response():
    """Returns a mock mastering API response"""
    return {
        "mastering_task_id": "test_task_123",
        "status": "pending"
    }


@pytest.fixture
def mock_mix_response():
    """Returns a mock mix API response"""
    return {
        "multitrack_task_id": "mix_task_456",
        "status": "pending"
    }


@pytest.fixture
def mock_preview_master_response():
    """Returns a mock preview master results"""
    return {
        "previewMasterTaskResults": {
            "download_url_mastered_preview": "https://example.com/preview.wav",
            "status": "completed"
        }
    }


@pytest.fixture
def mock_analysis_response():
    """Returns a mock analysis response"""
    return {
        "mixDiagnosisResults": {
            "payload": {
                "integrated_loudness_lufs": -14.5,
                "peak_loudness_dbfs": -1.2,
                "bit_depth": 24,
                "sample_rate": 44100,
                "clipping": "NO",
                "musical_style": "POP",
                "stereo_field": "GOOD",
                "tonal_profile": {
                    "bass_frequency": "GOOD",
                    "low_mid_frequency": "GOOD",
                    "high_mid_frequency": "GOOD",
                    "high_frequency": "GOOD"
                }
            }
        }
    }


# Integration test fixtures
@pytest.fixture(scope="session")
def integration_audio_file():
    """
    Returns path to a real audio file for integration tests.
    This file should exist in tests/fixtures/audio/
    """
    audio_path = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "audio",
        "test_track.wav"
    )
    
    if not os.path.exists(audio_path):
        pytest.skip(f"Integration test audio file not found: {audio_path}")
    
    return audio_path


@pytest.fixture(scope="session")
def requires_api_key():
    """Skip test if no API key is available"""
    api_key = os.getenv("ROEX_API_KEY")
    if not api_key or api_key == "test_api_key_12345":
        pytest.skip("Integration tests require ROEX_API_KEY environment variable")
    return api_key
