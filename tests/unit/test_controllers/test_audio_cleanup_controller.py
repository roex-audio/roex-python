"""
Unit tests for AudioCleanupController
"""

import pytest
from unittest.mock import Mock
from roex_python.controllers.audio_cleanup_controller import AudioCleanupController
from roex_python.models.audio_cleanup import (
    AudioCleanupData, AudioCleanupResponse, AudioCleanupResults, SoundSource
)


@pytest.mark.unit
class TestAudioCleanupControllerInit:
    """Test AudioCleanupController initialization"""
    
    def test_init(self, mock_api_provider):
        """Test controller initialization"""
        controller = AudioCleanupController(mock_api_provider)
        assert controller.api_provider == mock_api_provider


@pytest.mark.unit
class TestCleanUpAudio:
    """Test clean_up_audio method"""
    
    def test_successful_cleanup(self, mock_api_provider):
        """Test successful audio cleanup"""
        # Setup
        mock_api_provider.post.return_value = {
            "error": False,
            "message": "Success",
            "info": "Audio cleaned successfully",
            "audioCleanupResults": {
                "completion_time": "2025-10-17T12:00:00Z",
                "error": False,
                "info": "Cleanup completed",
                "cleaned_audio_file_location": "https://example.com/cleaned_vocals.wav"
            }
        }
        
        controller = AudioCleanupController(mock_api_provider)
        
        cleanup_data = AudioCleanupData(
            audio_file_location="https://example.com/vocals.wav",
            sound_source=SoundSource.VOCAL_GROUP
        )
        
        # Execute
        result = controller.clean_up_audio(cleanup_data)
        
        # Assert
        assert isinstance(result, AudioCleanupResponse)
        assert result.error is False
        assert result.message == "Success"
        assert result.audio_cleanup_results is not None
        assert result.audio_cleanup_results.cleaned_audio_file_location == "https://example.com/cleaned_vocals.wav"
        
        # Verify correct endpoint and payload
        call_args = mock_api_provider.post.call_args
        assert call_args[0][0] == "/audio-cleanup"
        payload = call_args[0][1]
        assert payload["audioCleanupData"]["audioFileLocation"] == "https://example.com/vocals.wav"
        assert payload["audioCleanupData"]["soundSource"] == "VOCAL_GROUP"
    
    def test_different_sound_sources(self, mock_api_provider):
        """Test cleanup with different sound sources"""
        # Setup
        mock_api_provider.post.return_value = {
            "error": False,
            "message": "Success",
            "audioCleanupResults": {
                "completion_time": "2025-10-17T12:00:00Z",
                "error": False,
                "info": "Cleanup completed",
                "cleaned_audio_file_location": "https://example.com/cleaned.wav"
            }
        }
        
        controller = AudioCleanupController(mock_api_provider)
        
        # Test with different sound sources
        sound_sources = [
            SoundSource.E_GUITAR_GROUP,
            SoundSource.ACOUSTIC_GUITAR_GROUP,
            SoundSource.KICK_GROUP,
            SoundSource.SNARE_GROUP
        ]
        
        for sound_source in sound_sources:
            cleanup_data = AudioCleanupData(
                audio_file_location="https://example.com/track.wav",
                sound_source=sound_source
            )
            
            result = controller.clean_up_audio(cleanup_data)
            
            # Verify sound source in payload
            payload = mock_api_provider.post.call_args[0][1]
            assert payload["audioCleanupData"]["soundSource"] == sound_source.value
    
    def test_response_without_results(self, mock_api_provider):
        """Test handling of response without cleanup results"""
        # Setup
        mock_api_provider.post.return_value = {
            "error": False,
            "message": "Processing",
            "info": "Task queued"
        }
        
        controller = AudioCleanupController(mock_api_provider)
        
        cleanup_data = AudioCleanupData(
            audio_file_location="https://example.com/vocals.wav",
            sound_source=SoundSource.VOCAL_GROUP
        )
        
        # Execute
        result = controller.clean_up_audio(cleanup_data)
        
        # Assert
        assert isinstance(result, AudioCleanupResponse)
        assert result.error is False
        assert result.audio_cleanup_results is None
    
    def test_error_response(self, mock_api_provider):
        """Test handling of error response"""
        # Setup
        mock_api_provider.post.return_value = {
            "error": True,
            "message": "File format not supported",
            "info": "Please use WAV or FLAC"
        }
        
        controller = AudioCleanupController(mock_api_provider)
        
        cleanup_data = AudioCleanupData(
            audio_file_location="https://example.com/vocals.mp3",
            sound_source=SoundSource.VOCAL_GROUP
        )
        
        # Execute
        result = controller.clean_up_audio(cleanup_data)
        
        # Assert
        assert isinstance(result, AudioCleanupResponse)
        assert result.error is True
        assert result.message == "File format not supported"
    
    def test_exception_handling(self, mock_api_provider):
        """Test exception handling"""
        # Setup
        mock_api_provider.post.side_effect = Exception("Network error")
        
        controller = AudioCleanupController(mock_api_provider)
        
        cleanup_data = AudioCleanupData(
            audio_file_location="https://example.com/vocals.wav",
            sound_source=SoundSource.VOCAL_GROUP
        )
        
        # Execute
        result = controller.clean_up_audio(cleanup_data)
        
        # Assert - should return None on exception
        assert result is None
    
    def test_cleanup_results_parsing(self, mock_api_provider):
        """Test proper parsing of cleanup results"""
        # Setup
        mock_api_provider.post.return_value = {
            "error": False,
            "message": "Success",
            "info": "Overall info",
            "audioCleanupResults": {
                "completion_time": "2025-10-17T15:30:00Z",
                "error": False,
                "info": "Removed noise and artifacts",
                "cleaned_audio_file_location": "https://storage.example.com/cleaned_track.wav"
            }
        }
        
        controller = AudioCleanupController(mock_api_provider)
        
        cleanup_data = AudioCleanupData(
            audio_file_location="https://example.com/noisy_track.wav",
            sound_source=SoundSource.STRINGS_GROUP
        )
        
        # Execute
        result = controller.clean_up_audio(cleanup_data)
        
        # Assert results object
        assert result.audio_cleanup_results is not None
        results = result.audio_cleanup_results
        assert isinstance(results, AudioCleanupResults)
        assert results.completion_time == "2025-10-17T15:30:00Z"
        assert results.error is False
        assert results.info == "Removed noise and artifacts"
        assert results.cleaned_audio_file_location == "https://storage.example.com/cleaned_track.wav"
    
    def test_all_sound_source_values(self, mock_api_provider):
        """Test that all SoundSource enum values work"""
        # Setup
        mock_api_provider.post.return_value = {
            "error": False,
            "message": "Success",
            "audioCleanupResults": {
                "completion_time": "2025-10-17T12:00:00Z",
                "error": False,
                "info": "Cleaned",
                "cleaned_audio_file_location": "https://example.com/cleaned.wav"
            }
        }
        
        controller = AudioCleanupController(mock_api_provider)
        
        # Test all available sound sources
        all_sources = [
            SoundSource.KICK_GROUP,
            SoundSource.SNARE_GROUP,
            SoundSource.VOCAL_GROUP,
            SoundSource.BACKING_VOCALS_GROUP,
            SoundSource.PERCS_GROUP,
            SoundSource.STRINGS_GROUP,
            SoundSource.E_GUITAR_GROUP,
            SoundSource.ACOUSTIC_GUITAR_GROUP
        ]
        
        for source in all_sources:
            cleanup_data = AudioCleanupData(
                audio_file_location="https://example.com/track.wav",
                sound_source=source
            )
            
            result = controller.clean_up_audio(cleanup_data)
            
            # Should succeed for all sources
            assert isinstance(result, AudioCleanupResponse)
            assert result.error is False
