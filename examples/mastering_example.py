"""
Example demonstrating how to use the RoEx MCP client for audio mastering
"""

import os
from roex_python.utils import upload_file

from roex_python.client import RoExClient
from roex_python.models import (
    MasteringRequest, AlbumMasteringRequest,
    MusicalStyle, DesiredLoudness
)


def mastering_workflow():
    """Example workflow demonstrating how to:
    1. Upload audio files (WAV/FLAC/MP3)
    2. Master a single track
    3. Download the mastered track
    4. Master multiple tracks as an album
    5. Save all mastered files
    """

    # Initialize the client with your API key
    client = RoExClient(
        api_key="AIzaSyB9iUIXk3IOxZKElJJqnzII3690ABfyZ_Y",  # Replace with your actual API key
        base_url="https://tonn.roexaudio.com"
    )

    # First, upload your audio file
    file_path = "/Users/davidronan/Desktop/mastering/mastering/mixing_secrets_mastering/0a-JesuJoy_UnmasteredWAV.wav"  # Replace with your audio file (WAV/FLAC/MP3)
    print("\n=== Uploading Audio File ===")
    track_url = upload_file(client, file_path)
    print(f"File uploaded successfully: {track_url}")

    print("\n=== Starting Track Mastering ===")

    # Create mastering request
    mastering_request = MasteringRequest(
        track_url=track_url,
        musical_style=MusicalStyle.ACOUSTIC,
        desired_loudness=DesiredLoudness.MEDIUM,
        sample_rate="44100",
        webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
    )

    # Send mastering request and get preview
    print("\n=== Creating Mastering Preview ===")
    mastering_response = client.mastering.create_mastering_preview(mastering_request)
    print(f"Mastering Task ID: {mastering_response.mastering_task_id}")

    # Get the preview master
    print("\n=== Retrieving Preview Master ===")
    preview_results = client.mastering.retrieve_preview_master(mastering_response.mastering_task_id)
    preview_url = preview_results.get('download_url_mastered_preview')
    print(f"Preview Master URL: {preview_url}")

    # Get the final master
    print("\n=== Retrieving Final Master ===")
    final_url = client.mastering.retrieve_final_master(mastering_response.mastering_task_id)
    final_url = final_url.get('download_url_mastered')
    print(f"Final Master URL: {final_url}")

    # Save the final master
    print("\n=== Saving Final Master ===")
    output_dir = "final_masters"
    os.makedirs(output_dir, exist_ok=True)

    if final_url:
        local_filename = os.path.join(output_dir, "final_master.wav")
        success = client.api_provider.download_file(final_url, local_filename)
        if success:
            print(f"Downloaded final master to {local_filename}")
        else:
            print("Failed to download final master")

    # Optional: Album Mastering
    print("\n=== Starting Album Mastering ===")

    # Upload additional tracks for the album
    print("\nUploading additional tracks...")
    track2_path = "/Users/davidronan/Desktop/mastering/mastering/mixing_secrets_mastering/0a-JesuJoy_UnmasteredWAV.wav"  # Replace with your audio file
    track2_url = upload_file(client, track2_path)
    print(f"Track 2 uploaded successfully: {track2_url}")

    track3_path = "/Users/davidronan/Desktop/mastering/mastering/mixing_secrets_mastering/0a-JesuJoy_UnmasteredWAV.wav"  # Replace with your audio file
    track3_url = upload_file(client, track3_path)
    print(f"Track 3 uploaded successfully: {track3_url}")

    # Create album mastering request
    album_request = AlbumMasteringRequest(
        tracks=[
            MasteringRequest(
                track_url=track_url,  # First track we uploaded
                musical_style=MusicalStyle.ACOUSTIC,
                desired_loudness=DesiredLoudness.MEDIUM,
                webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
            ),
            MasteringRequest(
                track_url=track2_url,
                musical_style=MusicalStyle.ROCK_INDIE,
                desired_loudness=DesiredLoudness.MEDIUM,
                webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
            ),
            MasteringRequest(
                track_url=track3_url,
                musical_style=MusicalStyle.ELECTRONIC,
                desired_loudness=DesiredLoudness.MEDIUM,
                webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
            )
        ]
    )

    # Process all tracks in the album
    print("\n=== Processing Album ===")
    album_results = client.mastering.process_album(album_request, output_dir="album_masters")
    print("Album mastering complete!")
    print(f"Results saved to album_masters/")


if __name__ == "__main__":
    mastering_workflow()