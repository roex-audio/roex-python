"""
Example demonstrating how to use the RoEx MCP client for audio mastering
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from roex_mcp.client import RoExClient
from roex_mcp.models import (
    MasteringRequest, AlbumMasteringRequest,
    MusicalStyle, DesiredLoudness
)


def mastering_workflow():
    """Example workflow for mastering a single track and an album"""

    # Replace with your actual API key
    api_key = "your_api_key_here"
    client = RoExClient(api_key=api_key)

    # Check API health
    health = client.health_check()
    print(f"API Health: {health}")

    # 1. Single Track Mastering
    print("\nStarting single track mastering...")

    # Create mastering request
    mastering_request = MasteringRequest(
        track_url="https://storage.googleapis.com/test-bucket-api-roex/album/audio_track_1.mp3",
        musical_style=MusicalStyle.ACOUSTIC,
        desired_loudness=DesiredLoudness.MEDIUM,
        sample_rate="44100",
        webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
    )

    # Create mastering preview
    mastering_response = client.mastering.create_mastering_preview(mastering_request)
    print(f"Mastering Task ID: {mastering_response.mastering_task_id}")

    # Retrieve preview master (polls until ready)
    print("Retrieving preview master...")
    preview_results = client.mastering.retrieve_preview_master(mastering_response.mastering_task_id)

    # Print preview URL
    preview_url = preview_results.get('download_url_mastered_preview')
    print(f"Preview Master URL: {preview_url}")

    # Retrieve final master
    print("Retrieving final master...")
    final_url = client.mastering.retrieve_final_master(mastering_response.mastering_task_id)
    print(f"Final Master URL: {final_url}")

    # Download the final master
    output_dir = "final_masters"
    os.makedirs(output_dir, exist_ok=True)

    if final_url:
        local_filename = os.path.join(output_dir, "final_master.wav")
        success = client.api_provider.download_file(final_url, local_filename)
        if success:
            print(f"Downloaded final master to {local_filename}")
        else:
            print("Failed to download final master")

    # 2. Album Mastering
    print("\nStarting album mastering...")

    # Create album mastering request with multiple tracks
    album_request = AlbumMasteringRequest(
        tracks=[
            MasteringRequest(
                track_url="https://storage.googleapis.com/test-bucket-api-roex/album/audio_track_1.mp3",
                musical_style=MusicalStyle.ACOUSTIC,
                desired_loudness=DesiredLoudness.MEDIUM,
                webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
            ),
            MasteringRequest(
                track_url="https://storage.googleapis.com/test-bucket-api-roex/album/audio_track_1.mp3",
                musical_style=MusicalStyle.ROCK_INDIE,
                desired_loudness=DesiredLoudness.MEDIUM,
                webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
            ),
            MasteringRequest(
                track_url="https://storage.googleapis.com/test-bucket-api-roex/album/audio_track_1.mp3",
                musical_style=MusicalStyle.ELECTRONIC,
                desired_loudness=DesiredLoudness.MEDIUM,
                webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
            )
        ]
    )

    # Process all tracks in the album
    album_results = client.mastering.process_album(album_request, output_dir="album_masters")
    print("Album mastering complete!")
    print(f"Results: {album_results}")


if __name__ == "__main__":
    mastering_workflow()