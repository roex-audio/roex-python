"""Example demonstrating how to use the RoEx client for multitrack mixing.

This example shows how to mix multiple audio tracks using RoEx's AI-powered mixing engine.
The mixing process can:
- Balance track levels
- Apply appropriate EQ and compression
- Set stereo positioning
- Add reverb and effects
- Create a cohesive final mix

Workflow:
1. Initialize client securely using environment variables
2. Upload multiple audio files to RoEx's secure storage
3. Create and review mix preview
4. Apply gain adjustments if needed
5. Create final mix with optional stems
6. Download all files

Before running:
1. Set your API key in the environment:
   export ROEX_API_KEY='your_api_key_here'

2. Have your audio files ready for mixing
   - Supported formats: WAV, FLAC
   - Supported sample rates: 44.1kHz, 48kHz
   - Supported bit depths: 16-bit, 24-bit
   - Maximum duration: 8 minutes per track

File Security:
- Files are uploaded using secure, signed URLs
- All processing happens in RoEx's secure environment
- Files are automatically removed after processing
- Download URLs are temporary and expire after 1 hour

Example Usage:
    # Set your API key
    export ROEX_API_KEY='your_api_key_here'
    
    # Run the example
    python mix_example.py --bass /path/to/bass.wav --vocals /path/to/vocals.wav --kick /path/to/kick.wav
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from soundfile import SoundFileError

from roex_python.client import RoExClient
from roex_python.models import (
    TrackData, MultitrackMixRequest, FinalMixRequest, TrackGainData,
    InstrumentGroup, PresenceSetting, PanPreference, ReverbPreference, MusicalStyle
)

from roex_python.utils import upload_file
from common import (
    get_api_key, 
    validate_audio_file, 
    ensure_output_dir, 
    setup_logger,
    validate_audio_properties, 
    AudioValidationError
)

# Constants
MIX_MAX_DURATION_SECS = 480

# Set up logger for this module
logger = setup_logger(__name__)

def configure_track(file_path: Path, instrument: InstrumentGroup, presence: PresenceSetting, pan: PanPreference, volume: float = 0.0) -> Optional[Dict[str, Any]]:
    """Validates and configures a single track dictionary.

    Args:
        file_path: Path to the audio file.
        instrument: The InstrumentGroup enum value.
        presence: The PresenceSetting enum value.
        pan: The PanPreference enum value.
        volume: Volume adjustment (default 0.0).

    Returns:
        A dictionary containing track configuration or None if validation fails.
    """
    try:
        # Validate the audio file itself
        # validate_audio_file raises FileNotFoundError or ValueError on failure
        # and returns a Path object on success.
        file_path_obj = validate_audio_file(str(file_path), allowed_extensions={"wav", "flac"})

        # Validate audio properties (duration, sample rate, silence)
        validate_audio_properties(file_path_obj, MIX_MAX_DURATION_SECS)

        # If validation succeeds, return the config dict
        return {
            'path': file_path_obj, # Use the returned Path object
            'instrument': instrument,
            'presence': presence,
            'pan': pan,
            'volume': volume,
            'upload_url': None # Placeholder for uploaded URL
        }
    except (FileNotFoundError, ValueError, AudioValidationError, SoundFileError) as e:
        # Log the specific error raised by validation functions
        logger.error(f"Configuration failed for track {instrument.name} due to validation error: {e}")
        return None # Indicate failure

def mix_workflow(args: argparse.Namespace):
    """Handles the multitrack mix workflow using command-line arguments.

    Args:
        args: Parsed arguments from argparse containing file paths.
    """
    setup_logger()
    api_key = get_api_key()
    if not api_key:
        return

    client = RoExClient(api_key=api_key, base_url="https://tonn.roexaudio.com")

    output_dir = Path(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    logger.info("\n=== Configuring Tracks from Arguments ===")
    track_configs: Dict[str, Optional[Dict[str, Any]]] = {}

    # Helper to configure and add track if path provided
    def add_track_config(track_name: str, path_str: Optional[str], instrument: InstrumentGroup, required: bool = False, presence=PresenceSetting.NORMAL, pan=PanPreference.CENTRE, volume=0.0):
        if path_str:
            file_path = Path(path_str)
            config = configure_track(file_path, instrument, presence, pan, volume)
            if config:
                track_configs[track_name] = config
            else:
                # Error logged in configure_track
                # Optionally raise an exception or handle differently
                track_configs[track_name] = None # Mark as failed
        elif required:
            logger.error(f"Error: Required track '{track_name}' (--{track_name}) not provided.")
            track_configs[track_name] = None # Mark as failed

    # Configure tracks based on provided arguments
    # Required tracks (Example: making bass and vocals required)
    add_track_config('bass', args.bass, InstrumentGroup.BASS_GROUP, required=True)
    add_track_config('vocals', args.vocals, InstrumentGroup.VOCAL_GROUP, required=True)

    # Optional tracks
    add_track_config('kick', args.kick, InstrumentGroup.KICK_GROUP)
    add_track_config('snare', args.snare, InstrumentGroup.SNARE_GROUP)
    add_track_config('drums', args.drums, InstrumentGroup.DRUMS_GROUP)
    add_track_config('synth', args.synth, InstrumentGroup.SYNTH_GROUP)
    add_track_config('guitar', args.guitar, InstrumentGroup.ACOUSTIC_GUITAR_GROUP) # Or E_GUITAR_GROUP?
    add_track_config('electric_guitar', args.electric_guitar, InstrumentGroup.E_GUITAR_GROUP)
    add_track_config('cymbals', args.cymbals, InstrumentGroup.CYMBALS_GROUP)
    add_track_config('backing_vocals', args.backing_vocals, InstrumentGroup.BACKING_VOX_GROUP)
    add_track_config('percussion', args.percussion, InstrumentGroup.PERCS_GROUP)
    add_track_config('strings', args.strings, InstrumentGroup.STRINGS_GROUP)
    add_track_config('fx', args.fx, InstrumentGroup.FX_GROUP)
    add_track_config('keys', args.keys, InstrumentGroup.KEYS_GROUP)
    add_track_config('brass', args.brass, InstrumentGroup.BRASS_GROUP)
    add_track_config('backing_track', args.backing_track, InstrumentGroup.BACKING_TRACK_GROUP)

    # Handle multiple 'other' tracks
    if args.other:
        for i, other_path_str in enumerate(args.other):
             track_name = f'other_{i+1}'
             add_track_config(track_name, other_path_str, InstrumentGroup.OTHER_GROUP)

    # Check if any required tracks failed configuration or were missing
    if any(cfg is None for track_name, cfg in track_configs.items() if track_name in ['bass', 'vocals']): # Check required
         logger.error("Aborting mix due to missing or invalid required tracks.")
         return

    # Filter out tracks that failed validation
    valid_track_configs = {name: cfg for name, cfg in track_configs.items() if cfg is not None}
    if not valid_track_configs:
        logger.error("No valid tracks configured. Aborting mix.")
        return

    logger.info("\n=== Uploading Tracks ===")
    all_uploads_successful = True
    for track_name, config in valid_track_configs.items():
        logger.info(f"Uploading {track_name} from {config['path'].name}...")
        upload_response = upload_file(client, str(config['path']))
        if upload_response:
            config['upload_url'] = upload_response # Assign the string URL directly
            logger.info(f"Uploaded {track_name} to secure storage")
        else:
            logger.error(f"Upload failed for {track_name}.")
            all_uploads_successful = False
            # Decide how to handle: stop entirely or just exclude this track?
            # For now, let's stop if any upload fails.
            break

    if not all_uploads_successful:
        logger.error("Aborting mix due to upload failures.")
        return

    # Create mix_tracks list for the API request from successfully uploaded tracks
    mix_tracks = [
        TrackData(
            track_url=config['upload_url'],
            instrument_group=config['instrument'],
            presence_setting=config['presence'],
            pan_preference=config['pan'],
            reverb_preference=ReverbPreference.NONE
        )
        for config in valid_track_configs.values() if config['upload_url'] is not None
    ]

    if not mix_tracks:
        logger.error("No tracks were successfully uploaded. Cannot create mix request.")
        return

    logger.info("\n=== Creating Mix Request ===")
    mix_request = MultitrackMixRequest(
        track_data=mix_tracks,
        musical_style=MusicalStyle.ELECTRONIC,
        return_stems=True,
        webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
    )

    logger.info("\n=== Creating Mix Preview ===")
    try:
        mix_response = client.mix.create_mix_preview(mix_request)
        if not mix_response or not mix_response.multitrack_task_id:
             logger.error("Failed to create mix preview task: No task ID received.")
             return # Indicate failure
    except Exception as e:
        logger.error(f"Error creating mix preview: {e}")
        return # Indicate failure

    mix_task_id = mix_response.multitrack_task_id
    logger.info(f"Mix preview created successfully. Task ID: {mix_task_id}")

    logger.info("\n=== Retrieving Mix Preview ===")
    try:
        # Assume retrieve_mix_preview exists and polls until ready
        preview_results = client.mix.retrieve_preview_mix(
            mix_task_id,
            retrieve_fx_settings=True
        )
    except Exception as e:
        logger.error(f"Error retrieving mix preview: {e}")
        return

    preview_download_url = preview_results.get('download_url_preview_mixed')
    fx_settings = preview_results.get('mix_output_settings') # Capture FX settings

    if preview_download_url:
        logger.info(f"Preview mix ready: {preview_download_url}")
        preview_filename = output_dir / "mix_preview.wav"
        if client.api_provider.download_file(preview_download_url, str(preview_filename)):
            logger.info(f"Preview mix downloaded to {preview_filename}")
        else:
            logger.warning("Failed to download preview mix.")
    else:
        logger.warning("Could not get preview download URL.")

    if fx_settings:
         logger.info(f"Retrieved FX settings: {fx_settings}")
         # You might want to save these settings to a file
         fx_settings_path = output_dir / "mix_fx_settings.json"
         try:
             import json
             with open(fx_settings_path, 'w') as f:
                 json.dump(fx_settings, f, indent=4)
             logger.info(f"FX settings saved to {fx_settings_path}")
         except Exception as e:
             logger.error(f"Failed to save FX settings: {e}")

    # Option to create the final mix (requires changes to the request/controller maybe?)
    # logger.info("\n=== Creating Final Mix ===")
    # final_mix_request = ... # Potentially reuse mix_request or add fx_settings?
    # try:
    #     final_response = client.mix.create_final_mix(final_mix_request)
    #     final_task_id = final_response.multitrack_task_id
    #     logger.info(f"Final mix task created: {final_task_id}")
    #     # ... retrieve final mix ...
    # except Exception as e:
    #     logger.error(f"Error creating final mix: {e}")

    logger.info("\n=== Mix Workflow Complete ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform multitrack mixing using RoEx API.")

    # Define arguments for each track type
    parser.add_argument('--bass', required=True, help='Path to the bass track file (WAV/FLAC).')
    parser.add_argument('--vocals', required=True, help='Path to the main vocals track file (WAV/FLAC).')
    parser.add_argument('--kick', help='Path to the kick drum track file (WAV/FLAC).')
    parser.add_argument('--snare', help='Path to the snare drum track file (WAV/FLAC).')
    parser.add_argument('--drums', help='Path to the combined drums track file (WAV/FLAC).')
    parser.add_argument('--synth', help='Path to a synthesizer track file (WAV/FLAC).')
    parser.add_argument('--guitar', help='Path to an acoustic guitar track file (WAV/FLAC).')
    parser.add_argument('--electric-guitar', help='Path to an electric guitar track file (WAV/FLAC).')
    parser.add_argument('--cymbals', help='Path to a cymbals track file (WAV/FLAC).')
    parser.add_argument('--backing-vocals', help='Path to a backing vocals track file (WAV/FLAC).')
    parser.add_argument('--percussion', help='Path to a percussion track file (WAV/FLAC).')
    parser.add_argument('--strings', help='Path to a strings track file (WAV/FLAC).')
    parser.add_argument('--fx', help='Path to an FX track file (WAV/FLAC).')
    parser.add_argument('--keys', help='Path to a keys/piano track file (WAV/FLAC).')
    parser.add_argument('--brass', help='Path to a brass track file (WAV/FLAC).')
    parser.add_argument('--backing-track', help='Path to a backing track file (WAV/FLAC).')
    parser.add_argument('--other', action='append', help='Path to any other track file (WAV/FLAC). Use multiple times.')
    parser.add_argument('--output-dir', default='./mixed_tracks', help='Directory to save output files.')

    args = parser.parse_args()

    mix_workflow(args)