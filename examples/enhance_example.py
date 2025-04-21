"""
Example demonstrating how to use the RoEx MCP client for mix enhancement
"""

import os
from roex_python.utils import upload_file

from roex_python.client import RoExClient
from roex_python.models import (
    MixEnhanceRequest, EnhanceMusicalStyle, LoudnessPreference
)


def enhance_workflow():
    """Example workflow demonstrating how to:
    1. Upload audio file (WAV/FLAC/MP3)
    2. Create and retrieve preview enhancement
    3. Create and retrieve full enhancement
    4. Download enhanced tracks and stems
    """

    # Initialize the client with your API key
    client = RoExClient(
        api_key="YOUR-API-KEY-HERE",  # Replace with your actual API key
        base_url="https://tonn.roexaudio.com"
    )

    # First, upload your audio file
    file_path = "/Users/davidronan/Desktop/mastering/mastering/mixing_secrets_mastering/0a-JesuJoy_UnmasteredWAV.wav"  # Replace with your audio file (WAV/FLAC/MP3)
    print("\n=== Uploading Audio File ===")
    audio_url = upload_file(client, file_path)
    print(f"File uploaded successfully: {audio_url}")

    print("\n=== Creating Enhancement Request ===")

    enhance_request = MixEnhanceRequest(
        audio_file_location=audio_url,
        musical_style=EnhanceMusicalStyle.POP,
        is_master=False,  # Set to True if the track is already mastered
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

    # Get preview enhancement
    print("\n=== Creating Enhancement Preview ===")
    preview_response = client.enhance.create_mix_enhance_preview(enhance_request)
    print(f"Preview Task ID: {preview_response.mixrevive_task_id}")

    print("\n=== Retrieving Preview Enhancement ===")
    preview_results = client.enhance.retrieve_enhanced_track(preview_response.mixrevive_task_id)
    preview_url = preview_results.get("download_url_preview_revived")
    print(f"Preview Enhancement URL: {preview_url}")

    # Save preview enhancement
    print("\n=== Saving Preview Enhancement ===")
    output_dir = "enhanced_tracks"
    os.makedirs(output_dir, exist_ok=True)

    if preview_url:
        preview_filename = os.path.join(output_dir, "enhanced_preview.wav")
        success = client.api_provider.download_file(preview_url, preview_filename)
        if success:
            print(f"Downloaded preview to {preview_filename}")
        else:
            print("Failed to download preview")

        # Save preview stems if available
        preview_stems = preview_results.get("stems", {})
        if preview_stems:
            print("\nDownloading preview stems...")
            for stem_name, stem_url in preview_stems.items():
                stem_filename = os.path.join(output_dir, f"enhanced_preview_stem_{stem_name}.wav")
                if client.api_provider.download_file(stem_url, stem_filename):
                    print(f"Downloaded {stem_name} stem to {stem_filename}")

    # Get full enhancement
    print("\n=== Creating Full Enhancement ===")
    full_response = client.enhance.create_mix_enhance(enhance_request)
    print(f"Full Enhancement Task ID: {full_response.mixrevive_task_id}")

    print("\n=== Retrieving Full Enhancement ===")
    full_results = client.enhance.retrieve_enhanced_track(full_response.mixrevive_task_id)
    final_url = full_results.get("download_url_revived")
    print(f"Final Enhancement URL: {final_url}")

    # Save full enhancement
    print("\n=== Saving Full Enhancement ===")
    if final_url:
        final_filename = os.path.join(output_dir, "enhanced_full.wav")
        success = client.api_provider.download_file(final_url, final_filename)
        if success:
            print(f"Downloaded full enhancement to {final_filename}")
        else:
            print("Failed to download full enhancement")

        # Save final stems if available
        final_stems = full_results.get("stems", {})
        if final_stems:
            print("\nDownloading final stems...")
            for stem_name, stem_url in final_stems.items():
                stem_filename = os.path.join(output_dir, f"enhanced_full_stem_{stem_name}.wav")
                if client.api_provider.download_file(stem_url, stem_filename):
                    print(f"Downloaded {stem_name} stem to {stem_filename}")

if __name__ == "__main__":
    enhance_workflow()