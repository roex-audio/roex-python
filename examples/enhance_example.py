"""
Example demonstrating how to use the RoEx MCP client for mix enhancement
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from roex_python.client import RoExClient
from roex_python.models import (
    MixEnhanceRequest, EnhanceMusicalStyle, LoudnessPreference
)


def enhance_workflow():
    """Example workflow for enhancing mixes"""

    # Replace with your actual API key
    api_key = "your_api_key_here"
    client = RoExClient(api_key=api_key)

    # Check API health
    health = client.health_check()
    print(f"API Health: {health}")

    # 1. Create enhance request
    print("\nStarting mix enhancement workflow...")

    # Replace with your actual audio file URL
    audio_url = "https://your-audio-file-location/audio.wav"

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

    # 2. Method 1: Step-by-step workflow
    print("\nMethod 1: Step-by-step workflow")

    # Create preview
    print("Creating mix enhance preview...")
    preview_response = client.enhance.create_mix_enhance_preview(enhance_request)
    print(f"Preview Task ID: {preview_response.mixrevive_task_id}")

    # Retrieve preview (polls until ready)
    print("Retrieving preview enhancement...")
    preview_results = client.enhance.retrieve_enhanced_track(preview_response.mixrevive_task_id)

    # Get preview URL
    preview_url = preview_results.get("download_url_preview_revived")
    print(f"Preview Enhancement URL: {preview_url}")

    # Download preview if available
    if preview_url:
        output_dir = "enhanced_tracks_method1"
        os.makedirs(output_dir, exist_ok=True)

        preview_filename = os.path.join(output_dir, "enhanced_preview.wav")
        success = client.api_provider.download_file(preview_url, preview_filename)
        if success:
            print(f"Downloaded preview to {preview_filename}")
        else:
            print("Failed to download preview")

        # Download preview stems if available
        preview_stems = preview_results.get("stems", {})
        for stem_name, stem_url in preview_stems.items():
            stem_filename = os.path.join(output_dir, f"enhanced_preview_stem_{stem_name}.wav")
            client.api_provider.download_file(stem_url, stem_filename)

    # Create full enhancement
    print("Creating full mix enhancement...")
    full_response = client.enhance.create_mix_enhance(enhance_request)
    print(f"Full Enhancement Task ID: {full_response.mixrevive_task_id}")

    # Retrieve full enhancement (polls until ready)
    print("Retrieving full enhancement...")
    full_results = client.enhance.retrieve_enhanced_track(full_response.mixrevive_task_id)

    # Get full enhancement URL
    final_url = full_results.get("download_url_revived")
    print(f"Final Enhancement URL: {final_url}")

    # Download full enhancement if available
    if final_url:
        output_dir = "enhanced_tracks_method1"
        os.makedirs(output_dir, exist_ok=True)

        final_filename = os.path.join(output_dir, "enhanced_full.wav")
        success = client.api_provider.download_file(final_url, final_filename)
        if success:
            print(f"Downloaded full enhancement to {final_filename}")
        else:
            print("Failed to download full enhancement")

        # Download final stems if available
        final_stems = full_results.get("stems", {})
        for stem_name, stem_url in final_stems.items():
            stem_filename = os.path.join(output_dir, f"enhanced_full_stem_{stem_name}.wav")
            client.api_provider.download_file(stem_url, stem_filename)

if __name__ == "__main__":
    enhance_workflow()