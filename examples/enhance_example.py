"""Example demonstrating how to use the RoEx mix enhancement endpoint.

This example shows how to enhance a mix using RoEx's AI-powered mix enhancement engine.
The enhancement process can improve various aspects of your mix including:
- Tonal balance
- Dynamic range
- Stereo width
- Loudness
- Overall clarity and punch

Workflow:
1. Initialize client securely using environment variables
2. Upload local audio file to RoEx's secure storage
3. Create enhancement preview with optional stem separation
4. Review and download preview
5. Create full enhancement if preview is satisfactory
6. Download enhanced mix and stems

Before running:
1. Set your API key in the environment:
   export ROEX_API_KEY='your_api_key_here'

2. Have a WAV or FLAC file ready for enhancement
   - Supported sample rates: 44.1kHz, 48kHz
   - Supported bit depths: 16-bit, 24-bit
   - Maximum duration: 10 minutes

File Security:
- Files are uploaded using secure, signed URLs
- All processing happens in RoEx's secure environment
- Files are automatically removed after processing
- Download URLs are temporary and expire after 1 hour

Example Usage:
    # Set your API key
    export ROEX_API_KEY='your_api_key_here'
    
    # Run the example
    python enhance_example.py /path/to/your/mix.wav
"""

import os
import sys
import time
import json
from pathlib import Path
from soundfile import SoundFileError

from roex_python.client import RoExClient
from roex_python.models.enhance import MixEnhanceRequest, EnhanceMusicalStyle
from roex_python.models import LoudnessPreference, InstrumentGroup
from roex_python.utils import upload_file
from common import (
    get_api_key, 
    validate_audio_file, 
    ensure_output_dir, 
    setup_logger, 
    validate_audio_properties, 
    AudioValidationError
)

# Set up logger for this module
logger = setup_logger(__name__)

ENHANCE_MAX_DURATION_SECS = 600

def enhance_workflow(input_file: str = None):
    """Run the mix enhancement workflow.
    
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

    # First, upload your audio file
    # Validate and upload input file
    if input_file is None:
        input_file = "/path/to/your/audio.wav"  # Replace with your WAV or FLAC file
    
    try:
        file_path = validate_audio_file(input_file)
        validate_audio_properties(file_path, ENHANCE_MAX_DURATION_SECS)
        logger.info(f"\n=== Uploading {file_path.name} ===")
    except (FileNotFoundError, ValueError, AudioValidationError) as e:
        logger.error(f"Validation failed for {input_file}: {e}. Aborting enhance workflow.")
        return
    except Exception as e:
        logger.error(f"Unexpected validation error for {input_file}: {e}. Aborting enhance workflow.")
        return

    audio_url = upload_file(client, str(file_path))
    logger.info("File uploaded successfully to RoEx secure storage")
    logger.info(f"Temporary storage location: {audio_url}")

    logger.info("\n=== Creating Enhancement Request ===")

    enhance_request = MixEnhanceRequest(
        audio_file_location=audio_url,
        musical_style=EnhanceMusicalStyle.POP,  # Choose appropriate style
        is_master=False,  # Set to True if input is already mastered
        fix_clipping_issues=True,
        fix_drc_issues=True,
        fix_stereo_width_issues=True,
        fix_tonal_profile_issues=True,
        fix_loudness_issues=True,
        apply_mastering=True,
        loudness_preference=LoudnessPreference.STREAMING_LOUDNESS,
        stem_processing=True,  # Set to True to get separated stems
        webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
    )

    # Create and retrieve preview enhancement
    logger.info("\n=== Creating Enhancement Preview ===")
    preview_response = client.enhance.create_mix_enhance_preview(enhance_request)
    if not preview_response or preview_response.error:
        logger.error(f"Error creating preview: {preview_response.message if preview_response else 'Unknown error'}")
        return
    logger.info(f"Preview Task ID: {preview_response.mixrevive_task_id}")

    logger.info("\n=== Retrieving Preview Enhancement ===")
    try:
        preview_results = client.enhance.retrieve_enhanced_track(preview_response.mixrevive_task_id)
    except Exception as e:
        logger.error(f"Error retrieving preview: {e}")
        return

    preview_url = preview_results.get("download_url_preview_revived")
    if not preview_url:
        logger.error("No preview URL received")
        return
    logger.info("Preview enhancement ready for download")

    # Save preview files
    logger.info("\n=== Saving Preview Files ===")
    output_dir = ensure_output_dir("enhanced_tracks")
    preview_path = output_dir / "enhanced_preview.wav"
    if client.api_provider.download_file(preview_url, str(preview_path)):
        logger.info(f"Downloaded preview to {preview_path}")
    else:
        logger.error("Failed to download preview")
        return

    stems = preview_results.get('stems', {})
    if stems:
        logger.info("\nDownloading preview stems...")
        for stem_name, stem_url in stems.items():
            stem_path = output_dir / f"enhanced_preview_stem_{stem_name}.wav"
            if client.api_provider.download_file(stem_url, str(stem_path)):
                logger.info(f"Downloaded {stem_name} stem to {stem_path}")
            else:
                logger.error(f"Failed to download {stem_name} stem")

    # Create the full enhancement task
    logger.info("\n=== Creating Full Enhancement ===")
    full_response = client.enhance.create_mix_enhance(enhance_request)
    if not full_response or full_response.error:
        logger.error(f"Failed to create full enhancement task: {full_response.message if full_response else 'No response'}")
        return None

    full_task_id = full_response.mixrevive_task_id # Assuming the response model has this attribute
    logger.info(f"Full enhancement task created with ID: {full_task_id}")

    logger.info("\n=== Retrieving Full Enhancement ===")
    try:
        # Ensure the retrieve method name is correct based on EnhanceController
        # Assuming retrieve_enhanced_track is correct as per previous analysis
        full_results = client.enhance.retrieve_enhanced_track(full_task_id)
    except Exception as e:
        logger.error(f"Error retrieving full enhancement: {e}")
        return None

    final_url = full_results.get('download_url_revived')
    if not final_url:
        logger.error("No final enhancement URL received")
        return
    logger.info("Full enhancement ready for download")

    # Download full enhancement
    logger.info("\n=== Saving Full Enhancement ===")
    full_path = output_dir / "enhanced_full.wav"
    if not client.api_provider.download_file(final_url, str(full_path)):
        logger.error("Failed to download full enhancement")
        return
    logger.info(f"Downloaded full enhancement to {full_path}")

    stems = full_results.get('stems', {})
    if stems:
        logger.info("\nDownloading final stems...")
        for stem_name, stem_url in stems.items():
            stem_path = output_dir / f"enhanced_full_stem_{stem_name}.wav"
            if client.api_provider.download_file(stem_url, str(stem_path)):
                logger.info(f"Downloaded {stem_name} stem to {stem_path}")
            else:
                logger.error(f"Failed to download {stem_name} stem")

    logger.info("\n=== Enhancement Complete ===")
    logger.info(f"All files saved to: {output_dir}")

if __name__ == "__main__":
    try:
        input_file = sys.argv[1] if len(sys.argv) > 1 else None
        enhance_workflow(input_file)
    except KeyboardInterrupt:
        logger.info("\nEnhancement cancelled by user")
    except Exception as e:
        logger.exception(f"\nError: {e}")