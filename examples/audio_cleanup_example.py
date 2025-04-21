"""Example demonstrating how to use the RoEx audio cleanup endpoint."""

from roex_python.client import RoExClient
from roex_python.models.audio_cleanup import AudioCleanupData, SoundSource
from roex_python.models import UploadUrlRequest

from roex_python.utils import upload_file

def cleanup_workflow():
    """Example workflow demonstrating how to:
    1. Upload audio file (WAV/FLAC)
    2. Clean up audio based on source type
    3. Download cleaned audio file
    """

    # Initialize the client with your API key
    client = RoExClient(
        api_key="YOUR-API-KEY-HERE",  # Replace with your actual API key
        base_url="https://tonn.roexaudio.com"
    )

    # First, upload your audio file (must be WAV or FLAC format)
    file_path = "/path/to/your/audio.wav"  # Replace with your WAV or FLAC file
    print("\n=== Uploading Audio File ===")
    file_url = upload_file(client, file_path)
    print(f"File uploaded successfully: {file_url}")

    # Create the audio cleanup request data
    cleanup_data = AudioCleanupData(
        audio_file_location=file_url,
        sound_source=SoundSource.VOCAL_GROUP  # Or choose from other SoundSource enum values
    )

    # Send the cleanup request
    print("\n=== Cleaning Audio File ===")
    response = client.audio_cleanup.clean_up_audio(cleanup_data)

    print("\n=== Audio Cleanup Results ===")
    if response.error:
        print(f"Error: {response.message}")
        return

    results = response.audio_cleanup_results
    if not results:
        print("No cleanup results received")
        return

    print(f"Completion Time: {results.completion_time}")
    print(f"Info: {results.info}")

    # Save cleaned audio file
    if results.cleaned_audio_file_location:
        print("\n=== Saving Cleaned Audio ===")
        output_dir = "cleaned_audio"
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "cleaned_audio.wav")
        success = client.api_provider.download_file(results.cleaned_audio_file_location, output_file)
        if success:
            print(f"Downloaded cleaned audio to {output_file}")
        else:
            print("Failed to download cleaned audio")

if __name__ == "__main__":
    cleanup_workflow()
