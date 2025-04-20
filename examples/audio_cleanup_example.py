"""
Example demonstrating how to use the RoEx audio cleanup endpoint.
"""

from roex_python.client import RoExClient
from roex_python.models.audio_cleanup import AudioCleanupData, SoundSource

def main():
    # Initialize the client with your API key
    client = RoExClient(
        api_key="AIzaSyCd-uoRDeMbXek_vKn9w09FejwsTIRmlyQ",  # Replace with your actual API key
        base_url="https://tonn.roexaudio.com"
    )

    # Create the audio cleanup request data
    cleanup_data = AudioCleanupData(
        audio_file_location="https://storage.googleapis.com/test-bucket-api-roex/pop/alba_eyra_attention/alba-attention-v43-vocals.wav",  # Replace with your file URL
        sound_source=SoundSource.VOCAL_GROUP  # Or choose from other SoundSource enum values
    )

    # Send the cleanup request
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
