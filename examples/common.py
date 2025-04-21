"""Common utilities for RoEx examples."""

import os
from pathlib import Path
from typing import Optional, Set, List
import logging
import json
import soundfile as sf
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def setup_logger(name='roex_example'):
    """Sets up and returns a logger instance."""
    # Basic configuration is done at the module level
    # You could customize further here if needed (e.g., add file handlers)
    return logging.getLogger(name)

def get_api_key() -> str:
    """Get the RoEx API key from environment variables.
    
    Returns:
        str: The API key
        
    Raises:
        ValueError: If ROEX_API_KEY is not set
    """
    api_key = os.getenv('ROEX_API_KEY')
    if not api_key:
        raise ValueError(
            "ROEX_API_KEY environment variable not set.\n"
            "Please set it with: export ROEX_API_KEY='your_api_key_here'"
        )
    return api_key

def validate_audio_file(file_path: str, allowed_extensions: Optional[Set[str]] = None) -> Path:
    """Validate that an audio file exists and has the correct extension.
    
    Args:
        file_path: Path to the audio file
        allowed_extensions: Set of allowed file extensions (without dot). 
                          Defaults to {wav, flac}
    
    Returns:
        Path: Validated Path object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file has wrong extension
    """
    if allowed_extensions is None:
        allowed_extensions = {'wav', 'flac'}
        
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Audio file not found: {file_path}\n"
            "Please update the file_path to point to your audio file."
        )
        
    if path.suffix.lower()[1:] not in allowed_extensions:
        raise ValueError(
            f"Invalid file type: {path.suffix}\n"
            f"File must be one of: {', '.join(allowed_extensions)}"
        )
        
    return path

def ensure_output_dir(dir_path: str) -> Path:
    """Ensure output directory exists, create if needed.
    
    Args:
        dir_path: Path to directory
        
    Returns:
        Path: Path object for the directory
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

# --- Custom Exceptions for Audio Validation ---
class AudioValidationError(ValueError):
    """Base class for audio validation errors."""
    pass

class AudioTooShortError(AudioValidationError):
    """Exception raised when audio is shorter than the minimum required duration."""
    pass

class AudioTooLongError(AudioValidationError):
    """Exception raised when audio is longer than the maximum allowed duration."""
    pass

class InvalidSampleRateError(AudioValidationError):
    """Exception raised when audio has an unsupported sample rate."""
    pass

class AudioTooQuietError(AudioValidationError):
    """Exception raised when audio is effectively silent (RMS too low)."""
    pass

# --- Constants ---
MIN_DURATION_SECS = 10
ALLOWED_SAMPLE_RATES = {44100, 48000}
MIN_RMS_THRESHOLD = 0.0001

def validate_audio_properties(audio_path: Path, max_duration_secs: float) -> None:
    """Validate audio properties: sample rate, duration, and silence.

    Args:
        audio_path: Path object to the audio file.
        max_duration_secs: Maximum allowed duration in seconds for this context.

    Raises:
        InvalidSampleRateError: If sample rate is not 44100 or 48000 Hz.
        AudioTooShortError: If duration is less than MIN_DURATION_SECS.
        AudioTooLongError: If duration exceeds max_duration_secs.
        AudioTooQuietError: If the audio's RMS value is below MIN_RMS_THRESHOLD.
        sf.SoundFileError: If the file cannot be read by soundfile.
    """
    try:
        logger.info(f"Validating audio properties for: {audio_path.name}")
        with sf.SoundFile(str(audio_path)) as f:
            sample_rate = f.samplerate
            frames = f.frames
            duration_secs = frames / sample_rate

            # 1. Check Sample Rate
            if sample_rate not in ALLOWED_SAMPLE_RATES:
                raise InvalidSampleRateError(
                    f"Invalid sample rate: {sample_rate} Hz. "
                    f"Must be one of: {', '.join(map(str, ALLOWED_SAMPLE_RATES))}."
                )

            # 2. Check Duration
            if duration_secs < MIN_DURATION_SECS:
                raise AudioTooShortError(
                    f"Audio duration ({duration_secs:.2f}s) is less than minimum allowed ({MIN_DURATION_SECS}s)."
                )
            if duration_secs > max_duration_secs:
                raise AudioTooLongError(
                    f"Audio duration ({duration_secs:.2f}s) exceeds maximum allowed ({max_duration_secs / 60:.1f} mins)."
                )

            # 3. Check Silence (RMS)
            # Read a chunk to check RMS - avoid loading huge files entirely if possible
            # Read up to 1 minute or the whole file if shorter
            read_frames = min(frames, sample_rate * 60)
            audio_data = f.read(frames=read_frames, dtype='float32', always_2d=True)

            if audio_data.shape[1] == 2: # Stereo
                rms_left = np.sqrt(np.mean(audio_data[:, 0]**2))
                rms_right = np.sqrt(np.mean(audio_data[:, 1]**2))
                rms = (rms_left + rms_right) / 2
            else: # Mono (or treat other channel counts as mono for RMS)
                rms = np.sqrt(np.mean(audio_data[:, 0]**2))

            if rms < MIN_RMS_THRESHOLD:
                raise AudioTooQuietError(
                    f"Audio appears too quiet (RMS: {rms:.6f}). Minimum threshold is {MIN_RMS_THRESHOLD}."
                )

        logger.info(f"Audio properties validated successfully for: {audio_path.name}")

    except sf.SoundFileError as e:
        logger.error(f"Could not read or process audio file {audio_path}: {e}")
        raise # Re-raise the soundfile error
    except AudioValidationError as e:
        logger.error(f"Audio validation failed for {audio_path.name}: {e}")
        raise # Re-raise our custom validation errors
    except Exception as e:
        logger.error(f"Unexpected error during audio validation for {audio_path.name}: {e}")
        raise AudioValidationError(f"Unexpected validation error: {e}") # Wrap unexpected errors

def ensure_dir_exists(dir_path: str) -> None:
    """Ensure a directory exists, creating it if necessary."""
