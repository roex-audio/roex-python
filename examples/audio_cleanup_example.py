"""Example demonstrating how to use the RoEx audio cleanup endpoint."""

from roex_python.client import RoExClient
from roex_python.models.audio_cleanup import AudioCleanupData, SoundSource
from roex_python.models import UploadUrlRequest

from roex_python.utils import upload_file

def main():
    # Initialize the client with your API key
    client = RoExClient(
        api_key="YOUR_API_KEY-HERE",  # Replace with your actual API key
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

    # Print the results
    print("\n=== Audio Cleanup Results ===")
    print(f"Error: {response.error}")
    print(f"Message: {response.message}")
    print(f"Info: {response.info}")

    if response.audio_cleanup_results:
        results = response.audio_cleanup_results
        print(f"\nCompletion Time: {results.completion_time}")
        print(f"Error Flag: {results.error}")
        print(f"Info: {results.info}")
        if results.cleaned_audio_file_location:
            print(f"Cleaned Audio File: {results.cleaned_audio_file_location}")

if __name__ == "__main__":
    main()
