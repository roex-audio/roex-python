"""Example demonstrating how to use the RoEx audio cleanup endpoint.

This example shows how to clean up audio tracks using RoEx's AI-powered cleanup engine.
The cleanup process can improve various aspects of your audio including:
- Noise reduction
- Frequency balance
- Dynamic range
- Overall clarity

Workflow:
1. Initialize client securely using environment variables
2. Upload local audio file to RoEx's secure storage
3. Clean up audio based on source type
4. Download cleaned audio file

Before running:
1. Set your API key in the environment:
   export ROEX_API_KEY='your_api_key_here'

2. Have a WAV or FLAC file ready for cleanup
   - Supported sample rates: 44.1kHz, 48kHz
   - Supported bit depths: 16-bit, 24-bit
   - Maximum duration: 10 minutes

Supported Sound Sources:
- KICK_GROUP: Kick drums and low-frequency percussion
- SNARE_GROUP: Snare drums and mid-frequency percussion
- VOCAL_GROUP: Lead vocals and spoken word
- BACKING_VOCALS_GROUP: Background vocals and harmonies
- PERCS_GROUP: General percussion and drums
- STRINGS_GROUP: String instruments
- E_GUITAR_GROUP: Electric guitars
- ACOUSTIC_GUITAR_GROUP: Acoustic guitars

File Security:
- Files are uploaded using secure, signed URLs
- All processing happens in RoEx's secure environment
- Files are automatically removed after processing
- Download URLs are temporary and expire after 1 hour

Example Usage:
    # Set your API key
    export ROEX_API_KEY='your_api_key_here'
    
    # Run the example
    python audio_cleanup_example.py /path/to/your/audio.wav
"""

import os
import sys
from pathlib import Path

from roex_python.client import RoExClient
from roex_python.models.audio_cleanup import AudioCleanupData, SoundSource
from roex_python.models import UploadUrlRequest
from roex_python.utils import upload_file

from common import get_api_key, validate_audio_file, ensure_output_dir, setup_logger, validate_audio_properties, AudioValidationError
from soundfile import SoundFileError

# Constants
CLEANUP_MAX_DURATION_SECS = 600

# Set up logger for this module
logger = setup_logger(__name__)

def cleanup_workflow(input_file: str = None):
    """Run the audio cleanup workflow.
    
    Args:
        input_file: Path to input audio file (WAV/FLAC)
                   If not provided, uses default example path
    
    Raises:
        ValueError: If API key is not set or input file is invalid
        FileNotFoundError: If input file doesn't exist
    """
    # Initialize client with API key from environment
    client = RoExClient(
        api_key=get_api_key(),
        base_url="https://tonn.roexaudio.com"
    )

    # Validate and upload input file
    if input_file is None:
        input_file = "/path/to/your/audio.wav"  # Replace with your WAV or FLAC file
    
    file_path = validate_audio_file(input_file)
    logger.info(f"\n=== Uploading {file_path.name} ===")
    validate_audio_properties(file_path, CLEANUP_MAX_DURATION_SECS)
    file_url = upload_file(client, str(file_path))
    logger.info("File uploaded successfully to RoEx secure storage")
    logger.info(f"Temporary storage location: {file_url}")

    # Create cleanup request
    logger.info("\n=== Creating Cleanup Request ===")
    cleanup_data = AudioCleanupData(
        audio_file_location=file_url,
        sound_source=SoundSource.VOCAL_GROUP  # Choose appropriate source type
    )

    # Process audio cleanup
    logger.info("\n=== Cleaning Audio File ===")
    try:
        response = client.audio_cleanup.clean_up_audio(cleanup_data)
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return

    # Check results
    logger.info("\n=== Audio Cleanup Results ===")
    if response.error:
        logger.error(f"Error: {response.message}")
        return

    results = response.audio_cleanup_results
    if not results:
        logger.info("No cleanup results received")
        return

    logger.info(f"Completion Time: {results.completion_time}")
    logger.info(f"Info: {results.info}")

    # Save cleaned audio
    if not results.cleaned_audio_file_location:
        logger.info("No cleaned audio URL received")
        return

    logger.info("\n=== Saving Cleaned Audio ===")
    output_dir = ensure_output_dir("cleaned_audio")
    output_path = output_dir / f"cleaned_{file_path.stem}.wav"

    if client.api_provider.download_file(results.cleaned_audio_file_location, str(output_path)):
        logger.info(f"Downloaded cleaned audio to {output_path}")
    else:
        logger.error("Failed to download cleaned audio")
        return

    logger.info("\n=== Cleanup Complete ===")
    logger.info(f"All files saved to: {output_dir}")

if __name__ == "__main__":
    try:
        input_file = sys.argv[1] if len(sys.argv) > 1 else None
        cleanup_workflow(input_file)
    except (FileNotFoundError, ValueError, AudioValidationError, SoundFileError) as e:
        logger.error(f"Error: {e}")
    except KeyboardInterrupt:
        logger.info("\nCleanup cancelled by user")
    except Exception as e:
        logger.exception(f"\nError: {e}")
