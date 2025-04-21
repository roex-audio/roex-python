"""
Example demonstrating how to use the RoEx client for audio mastering.

This example covers:
- Mastering a single audio track.
- Mastering multiple tracks together as an album for consistent loudness and tone.

Workflow:
1. Initialize client securely using environment variables.
2. Upload audio file(s) to RoEx's secure storage.
3. For single track mastering:
    a. Create a mastering request.
    b. Retrieve preview and final mastered tracks.
    c. Download the final master.
4. For album mastering:
    a. Upload all tracks for the album.
    b. Create an album mastering request with individual settings per track.
    c. Process the album (downloads handled internally by the client method).

Before running:
1. Set your API key in the environment:
   export ROEX_API_KEY='your_api_key_here'

2. Have WAV or FLAC file(s) ready for mastering.
   - Supported sample rates: 44.1kHz, 48kHz
   - Supported bit depths: 16-bit, 24-bit
   - Maximum duration: 10 minutes per track

File Security:
- Files are uploaded using secure, signed URLs.
- All processing happens in RoEx's secure environment.
- Files are automatically removed after processing.
- Download URLs are temporary and expire.

Example Usage:
    # Master a single track
    export ROEX_API_KEY='your_api_key_here'
    python mastering_example.py /path/to/your/track.wav

    # Master multiple tracks as an album (provide paths as arguments)
    export ROEX_API_KEY='your_api_key_here'
    python mastering_example.py /path/to/track1.wav /path/to/track2.wav /path/to/track3.wav
"""

import os
import sys
from pathlib import Path
from typing import List

from roex_python.client import RoExClient
from roex_python.models import (
    MasteringRequest, AlbumMasteringRequest,
    MusicalStyle, DesiredLoudness
)
from roex_python.utils import upload_file

from common import (
    get_api_key, 
    validate_audio_file, 
    ensure_output_dir, 
    setup_logger,
    validate_audio_properties, # Import new validation function
    AudioValidationError # Import base custom exception
)
from soundfile import SoundFileError # Import directly from soundfile

# Constants
MASTERING_MAX_DURATION_SECS = 600 # 10 minutes for mastering

# Set up logger for this module
logger = setup_logger(__name__)

def master_single_track(client: RoExClient, file_path: Path, output_dir: Path):
    """Handles the workflow for mastering a single track."""
    logger.info(f"\n=== Mastering Single Track: {file_path.name} ===")

    # 1. Upload file
    logger.info(f"Uploading {file_path.name}...")
    try:
        track_url = upload_file(client, str(file_path))
        logger.info("File uploaded to secure storage.")
    except Exception as e:
        logger.error(f"Error uploading {file_path.name}: {e}")
        return False

    # 2. Create mastering request
    logger.info("Creating mastering request...")
    mastering_request = MasteringRequest(
        track_url=track_url,
        musical_style=MusicalStyle.ACOUSTIC,
        desired_loudness=DesiredLoudness.MEDIUM,
        sample_rate="44100",
        webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
    )

    # 3. Get preview master
    mastering_task_id = None
    try:
        logger.info("Creating mastering preview...")
        try:
            mastering_response = client.mastering.create_mastering_preview(mastering_request)
            if not mastering_response or not mastering_response.mastering_task_id:
                logger.error("Failed to create mastering preview task: No task ID received.")
                return False
            mastering_task_id = mastering_response.mastering_task_id
            logger.info(f"Mastering Task ID: {mastering_task_id}")
        except Exception as e:
            logger.error(f"Error during preview generation: {e}")
            return False

        logger.info("Retrieving preview master (this may take some time)...")
        preview_results = client.mastering.retrieve_preview_master(mastering_task_id)
        preview_url = preview_results.get('download_url_mastered_preview')
        if preview_url:
            logger.info("Preview master ready.")
            # Optional: Download preview
            # preview_path = output_dir / f"preview_{file_path.stem}.wav"
            # client.api_provider.download_file(preview_url, str(preview_path))
            # logger.info(f"Preview saved to {preview_path}")
        else:
            logger.info("Could not retrieve preview master URL.")

    except Exception as e:
        logger.error(f"Error during preview generation: {e}")
        # Continue to final master retrieval if task ID exists
        if not mastering_task_id:
            return False

    # 4. Get final master URL
    try:
        logger.info("Retrieving final master URL (this may take some time)...")
        # This retrieves the download URL for the final mastered file
        final_url_response = client.mastering.retrieve_final_master(mastering_task_id)
        final_url = final_url_response.get('download_url_mastered')
        if not final_url:
            error_msg = final_url_response.get('message', 'No URL found')
            logger.error(f"Could not retrieve final master URL. Error: {error_msg}")
            return False
        logger.info("Final master URL ready.")
    except Exception as e:
        logger.error(f"Error retrieving final master URL: {e}")
        return False

    # 5. Download the final master file using the obtained URL
    logger.info("Downloading final master...")
    final_filename = output_dir / f"mastered_{file_path.stem}.wav"
    try:
        if client.api_provider.download_file(final_url, str(final_filename)):
            logger.info(f"Downloaded final master to {final_filename}")
            return True
        else:
            logger.error("Failed to download final master.")
            return False
    except Exception as e:
        logger.error(f"Error downloading final master: {e}")
        return False

def master_album(client: RoExClient, file_paths: List[Path], output_dir: Path):
    """Handles the workflow for mastering multiple tracks as an album."""
    logger.info("\n=== Mastering Album ===")
    if not file_paths:
        logger.warning("No files provided for album mastering.")
        return False

    album_mastering_requests = []
    track_urls = {}

    # 1. Upload all tracks
    logger.info("Uploading album tracks...")
    for file_path in file_paths:
        try:
            logger.info(f"  Uploading {file_path.name}...")
            url = upload_file(client, str(file_path))
            track_urls[file_path.name] = url # Store URL mapped to original name
            logger.info(f"  Uploaded {file_path.name}")

            # Define mastering settings for this track (customize as needed)
            req = MasteringRequest(
                track_url=url,
                musical_style=MusicalStyle.ACOUSTIC, # Apply style per track or use a common one
                desired_loudness=DesiredLoudness.MEDIUM,
                webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
            )
            album_mastering_requests.append(req)

        except Exception as e:
            logger.error(f"Error uploading {file_path.name}: {e}. Skipping track.")
            # Decide whether to stop or continue album processing
            # return False # Option: Stop if any track fails upload

    if not album_mastering_requests:
        logger.error("No tracks successfully uploaded for album mastering.")
        return False

    # 2. Create album mastering request
    logger.info("\nCreating album mastering request...")
    album_request = AlbumMasteringRequest(tracks=album_mastering_requests)

    # 3. Process album (downloads handled by the method)
    logger.info("Processing album (this may take some time)...")
    try:
        # The process_album method handles polling and downloading
        # It requires the output directory where files will be saved
        album_results = client.mastering.process_album(album_request, str(output_dir))

        # The result is typically a list of dicts or similar, indicating success/failure per track
        # We can add more detailed result checking here if needed based on client implementation
        logger.info("\n=== Album Mastering Results ===")
        # Basic check - assumes process_album returns something meaningful or raises exceptions
        if album_results is not None: # Adjust based on actual return type
            logger.info(f"Album mastering process initiated/completed. Check logs or webhook if configured.")
            logger.info(f"Mastered files saved to: {output_dir}")
            # You might want to check the contents of output_dir or parse album_results here
            # Example: Check if expected files exist
            all_files_exist = True
            for req in album_mastering_requests:
                # Try to reconstruct expected output filename (this is an assumption)
                # The actual naming might depend on the `process_album` implementation
                original_path = next((p for p, u in track_urls.items() if u == req.track_url), None)
                if original_path:
                    expected_name = f"mastered_{Path(original_path).stem}.wav"
                    if not (output_dir / expected_name).exists():
                        logger.warning(f"Warning: Expected output file not found: {expected_name}")
                        all_files_exist = False
                else:
                    logger.warning("Warning: Could not determine original filename for a track URL.")
                    all_files_exist = False
            if all_files_exist:
                logger.info("All expected output files appear to be present.")
            return True
        else:
            logger.error("Album mastering process returned unexpected result.")
            return False

    except Exception as e:
        logger.error(f"Error during album processing: {e}")
        return False


def mastering_workflow(input_files: List[str]):
    """Main workflow for mastering single or multiple tracks.

    Args:
        input_files: List of input file paths provided as arguments.
    """
    # Setup
    setup_logger() # Use the logger from common.py
    api_key = get_api_key()
    if not api_key:
        return # Error logged in get_api_key

    client = RoExClient(
        api_key=api_key,
        base_url="https://tonn.roexaudio.com"
    )

    validated_files = []
    for f in input_files:
        try:
            validated_path = validate_audio_file(f)
            validate_audio_properties(validated_path, MASTERING_MAX_DURATION_SECS)
            validated_files.append(validated_path)
        except (FileNotFoundError, ValueError, AudioValidationError, SoundFileError) as e:
            logger.error(f"Error: Input file not found or invalid - {e}. Aborting mastering workflow.")
            return # Stop if any file fails validation

    if len(validated_files) == 1:
        # Single track mastering
        output_dir = ensure_output_dir("single_masters")
        success = master_single_track(client, validated_files[0], output_dir)
    else:
        # Album mastering
        output_dir = ensure_output_dir("album_masters")
        success = master_album(client, validated_files, output_dir)

    if success:
        logger.info("\n=== Mastering Workflow Completed Successfully ===")
    else:
        logger.error("\n=== Mastering Workflow Failed ===")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.info("Usage:")
        logger.info("  Master single track: python mastering_example.py <path_to_track>")
        logger.info("  Master album:        python mastering_example.py <path_to_track1> <path_to_track2> ...")
        sys.exit(1)

    input_file_args = sys.argv[1:]

    try:
        mastering_workflow(input_file_args)
    except ValueError as e:
        logger.error(f"\nError: {e}")
    except KeyboardInterrupt:
        logger.info("\nMastering cancelled by user.")
    except Exception as e:
        logger.error(f"\nAn unexpected error occurred: {e}")