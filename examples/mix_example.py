"""
Example demonstrating how to use the RoEx MCP client for multitrack mixing
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from roex_python.client import RoExClient
from roex_python.models import (
    TrackData, MultitrackMixRequest, FinalMixRequest, TrackGainData,
    InstrumentGroup, PresenceSetting, PanPreference, ReverbPreference, MusicalStyle
)


def mix_workflow():
    """Example workflow for mixing tracks"""

    # Replace with your actual API key
    api_key = "your_api_key_here"
    client = RoExClient(api_key=api_key)

    # Check API health
    health = client.health_check()
    print(f"API Health: {health}")

    # 1. Define track data for the mix
    print("\nStarting multitrack mixing workflow...")
    tracks = [
        TrackData(
            track_url="https://storage.googleapis.com/test-bucket-api-roex/masks_test/masks-bass.wav",
            instrument_group=InstrumentGroup.BASS_GROUP,
            presence_setting=PresenceSetting.NORMAL,
            pan_preference=PanPreference.CENTRE,
            reverb_preference=ReverbPreference.NONE
        ),
        TrackData(
            track_url="https://storage.googleapis.com/test-bucket-api-roex/masks_test/masks-chord.wav",
            instrument_group=InstrumentGroup.SYNTH_GROUP,
            presence_setting=PresenceSetting.LEAD,
            pan_preference=PanPreference.CENTRE,
            reverb_preference=ReverbPreference.NONE
        ),
        TrackData(
            track_url="https://storage.googleapis.com/test-bucket-api-roex/masks_test/masks-kick.wav",
            instrument_group=InstrumentGroup.KICK_GROUP,
            presence_setting=PresenceSetting.NORMAL,
            pan_preference=PanPreference.CENTRE,
            reverb_preference=ReverbPreference.NONE
        ),
        TrackData(
            track_url="https://storage.googleapis.com/test-bucket-api-roex/masks_test/masks-percssion.wav",
            instrument_group=InstrumentGroup.PERCS_GROUP,
            presence_setting=PresenceSetting.NORMAL,
            pan_preference=PanPreference.CENTRE,
            reverb_preference=ReverbPreference.NONE
        ),
        TrackData(
            track_url="https://storage.googleapis.com/test-bucket-api-roex/masks_test/masks-synth.wav",
            instrument_group=InstrumentGroup.SYNTH_GROUP,
            presence_setting=PresenceSetting.BACKGROUND,
            pan_preference=PanPreference.CENTRE,
            reverb_preference=ReverbPreference.NONE
        )
    ]

    # 2. Create mix request
    mix_request = MultitrackMixRequest(
        track_data=tracks,
        musical_style=MusicalStyle.ELECTRONIC,
        return_stems=False,
        webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
    )

    # 3. Create mix preview
    print("Creating mix preview...")
    mix_response = client.mix.create_mix_preview(mix_request)
    print(f"Mix Task ID: {mix_response.multitrack_task_id}")

    # 4. Retrieve preview mix (polls until ready)
    print("Retrieving preview mix...")
    preview_results = client.mix.retrieve_preview_mix(
        mix_response.multitrack_task_id,
        retrieve_fx_settings=True
    )

    preview_url = preview_results.get('download_url_preview_mixed')
    print(f"Preview Mix URL: {preview_url}")

    # Print mix settings if available
    mix_settings = preview_results.get('mix_output_settings', {})
    if mix_settings:
        print("\nMix settings received. Sample settings for first track:")
        first_track = next(iter(mix_settings.keys()), None)
        if first_track:
            print(f"Track: {first_track}")
            track_settings = mix_settings[first_track]
            for setting_type, values in track_settings.items():
                print(f"  {setting_type}: {values}")

    # 5. Prepare final mix with gain adjustments
    gain_tracks = [
        TrackGainData(
            track_url="https://storage.googleapis.com/test-bucket-api-roex/masks_test/masks-bass.wav",
            gain_db=-12
        ),
        TrackGainData(
            track_url="https://storage.googleapis.com/test-bucket-api-roex/masks_test/masks-chord.wav",
            gain_db=0
        ),
        TrackGainData(
            track_url="https://storage.googleapis.com/test-bucket-api-roex/masks_test/masks-kick.wav",
            gain_db=-12
        ),
        TrackGainData(
            track_url="https://storage.googleapis.com/test-bucket-api-roex/masks_test/masks-percssion.wav",
            gain_db=0
        ),
        TrackGainData(
            track_url="https://storage.googleapis.com/test-bucket-api-roex/masks_test/masks-synth.wav",
            gain_db=0
        )
    ]

    final_request = FinalMixRequest(
        multitrack_task_id=mix_response.multitrack_task_id,
        track_data=gain_tracks,
        return_stems=True
    )

    # 6. Retrieve final mix
    print("Retrieving final mix...")
    final_results = client.mix.retrieve_final_mix(final_request)

    final_url = final_results.get('download_url_mixed')
    print(f"Final Mix URL: {final_url}")

    # 7. Download the final mix if needed
    output_dir = "final_mixes"
    os.makedirs(output_dir, exist_ok=True)

    if final_url:
        local_filename = os.path.join(output_dir, "final_mix.wav")
        success = client.api_provider.download_file(final_url, local_filename)
        if success:
            print(f"Downloaded final mix to {local_filename}")
        else:
            print("Failed to download final mix")

    # 8. Print stem URLs if available
    stems = final_results.get('stems', {})
    if stems:
        print("\nStem URLs:")
        for name, url in stems.items():
            print(f"  {name}: {url}")

            # Download stems if desired
            stem_filename = os.path.join(output_dir, f"stem_{name}.wav")
            client.api_provider.download_file(url, stem_filename)
            print(f"  Downloaded stem to {stem_filename}")


if __name__ == "__main__":
    mix_workflow()