"""Example demonstrating how to upload an audio file to RoEx secure storage.

This example uses the high-level `upload_file` utility from the `roex_python`
package, which simplifies the process by handling both getting the signed URL
and performing the upload.

Workflow:
1. Initialize client securely using environment variables.
2. Validate the input audio file.
3. Call `upload_file` with the client and file path.
4. Print the secure, readable URL provided by RoEx, which can be used in
   subsequent API calls (e.g., for analysis, mastering, cleanup).

Before running:
1. Set your API key in the environment:
   export ROEX_API_KEY='your_api_key_here'

2. Have a WAV, FLAC, or MP3 file ready to upload.
   - Supported sample rates: 44.1kHz, 48kHz
   - Supported bit depths: 16-bit, 24-bit (for WAV/FLAC)
   - Maximum duration: 10 minutes per track

File Security:
- The `upload_file` utility uses secure, signed URLs obtained from the RoEx API.
- The upload itself is performed directly to RoEx's secure storage.
- The returned `readable_url` is a secure reference to the file within RoEx's
  system, valid for a limited time and usable only in further RoEx API calls.

Example Usage:
    export ROEX_API_KEY='your_api_key_here'
    python upload_example.py /path/to/your/audio.mp3
"""

import sys
import os
from roex_python import RoExClient
from roex_python.utils import upload_file # Import the utility function
from common import setup_logger

# Set up logger for this module
logger = setup_logger(__name__)

def get_api_key():
    """Retrieve the API key from the environment variable."""
    api_key = os.environ.get('ROEX_API_KEY')
    if not api_key:
        raise ValueError("ROEX_API_KEY environment variable not set.")
    return api_key

def validate_audio_file(file_path: str):
    """Validate the input audio file."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)
    extension = os.path.splitext(filename)[1].lower()
    
    supported_extensions = ['.mp3', '.wav', '.flac']
    if extension not in supported_extensions:
        raise ValueError(f"Unsupported file type: {extension}. Must be one of: {', '.join(supported_extensions)}")
    
    return os.path.abspath(file_path)

def upload_workflow(file_path: str):
    """Handles validating the file, initializing the client, and uploading."""
    logger.info(f"\n=== Uploading File: {file_path} ===")

    # 1. Validate input file
    try:
        validated_path = validate_audio_file(file_path)
        logger.info(f"Validated file: {validated_path}")
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error: {e}")
        return

    # 2. Initialize client
    try:
        client = RoExClient(
            api_key=get_api_key(),
            base_url="https://tonn.roexaudio.com" # Or your specific endpoint
        )
        logger.info("RoEx client initialized.")
    except ValueError as e:
        logger.error(f"Error initializing client: {e}")
        return

    # 3. Upload file using the utility function
    try:
        logger.info(f"Uploading {validated_path} to RoEx storage...")
        # The upload_file utility handles getting the signed URL and PUT request
        readable_url = upload_file(client, validated_path)

        if readable_url:
            logger.info("\nFile uploaded successfully!")
            logger.info(f"Readable URL (for use in other API calls): {readable_url}")
            logger.info("\n=== Upload Workflow Completed Successfully ===")
        else:
            # upload_file usually raises exceptions on failure, but check just in case
            logger.error("\nUpload failed. No readable URL returned.")
            logger.error("\n=== Upload Workflow Failed ===")

    except Exception as e:
        logger.exception(f"\nAn error occurred during upload: {e}")
        logger.error("\n=== Upload Workflow Failed ===")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python upload_example.py <path_to_audio_file>")
        sys.exit(1)

    input_file_path = sys.argv[1]

    try:
        upload_workflow(input_file_path)
    except KeyboardInterrupt:
        logger.info("\nUpload cancelled by user.")
    except Exception as e:
        # Catch any unexpected errors
        logger.exception(f"\nAn unexpected error occurred: {e}")
