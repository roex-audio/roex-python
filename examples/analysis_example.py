"""
Example demonstrating how to use the RoEx MCP client for mix analysis
"""

import os
import json
from roex_python.utils import upload_file

from roex_python.client import RoExClient
from roex_python.models import MixAnalysisRequest, AnalysisMusicalStyle


def print_analysis_results(results):
    """Pretty print the analysis results from the mix analysis endpoint.
    
    Args:
        results: Dictionary containing the analysis results from the API
    """
    if "payload" not in results:
        print("No payload data found in results.")
        return

    payload = results["payload"]

    print("\n==== Mix Analysis Results ====")
    print(f"Loudness: {payload.get('integrated_loudness_lufs', 'N/A')} LUFS")
    print(f"Peak: {payload.get('peak_loudness_dbfs', 'N/A')} dBFS")
    print(f"Clipping: {payload.get('clipping', 'N/A')}")
    print(f"Sample Rate: {payload.get('sample_rate', 'N/A')} Hz")
    print(f"Bit Depth: {payload.get('bit_depth', 'N/A')} bits")
    print(f"Stereo Field: {payload.get('stereo_field', 'N/A')}")
    print(f"Phase Issues: {payload.get('phase_issues', 'N/A')}")
    print(f"Mono Compatible: {payload.get('mono_compatible', 'N/A')}")

    # Print tonal profile
    tonal_profile = payload.get("tonal_profile", {})
    if tonal_profile:
        print("\nTonal Profile:")
        for key, value in tonal_profile.items():
            print(f"  {key}: {value}")

    # Print summary if available
    summary = payload.get("summary", {})
    if summary:
        print("\nSummary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")


def analysis_workflow():
    """Example workflow demonstrating how to:
    1. Upload audio files (WAV/FLAC)
    2. Analyze a single mix
    3. Compare two mixes
    4. Save results to files
    """

    # Initialize the client with your API key
    client = RoExClient(
        api_key="YOUR_API-KEY-HERE",  # Replace with your actual API key
        base_url="https://tonn.roexaudio.com"
    )

    # First, upload your audio file (must be WAV or FLAC format)
    file_path = "/path/to/your/audio_1.wav"  # Replace with your WAV or FLAC file
    print("\n=== Uploading Audio File ===")
    audio_url = upload_file(client, file_path)
    print(f"File uploaded successfully: {audio_url}")

    print("\n=== Starting Mix Analysis ===")

    analysis_request = MixAnalysisRequest(
        audio_file_location=audio_url,
        musical_style=AnalysisMusicalStyle.ROCK,
        is_master=True
    )

    # Send the analysis request
    print("\n=== Analyzing Mix ===")
    analysis_results = client.analysis.analyze_mix(analysis_request)

    # Print analysis results
    print_analysis_results(analysis_results)

    # Save analysis results to file
    output_dir = "analysis_results"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "analysis.json"), "w") as f:
        json.dump(analysis_results, f, indent=2)

    print(f"\nAnalysis results saved to {output_dir}/analysis.json")

    # Optional: Compare two mixes
    print("\n=== Comparing Two Mixes ===")

    # Upload second mix for comparison
    mix_b_path = "/path/to/your/audio_2.wav"  # Replace with your WAV or FLAC file
    print("\nUploading second mix...")
    mix_b_url = upload_file(client, mix_b_path)
    print(f"Second mix uploaded successfully: {mix_b_url}")

    comparison_results = client.analysis.compare_mixes(
        mix_a_url=audio_url,  # Use our first mix as mix A
        mix_b_url=mix_b_url,
        musical_style=AnalysisMusicalStyle.ROCK,
        is_master=True
    )

    # Print comparison results
    print("\n==== Mix Comparison Results ====")

    # Print key differences
    differences = comparison_results.get("differences", {})
    if differences:
        print("\nKey Differences:")

        # Print loudness differences
        if "integrated_loudness_lufs" in differences:
            loudness_diff = differences["integrated_loudness_lufs"]
            print(f"Loudness Difference: {loudness_diff.get('difference', 'N/A')} LUFS")
            print(f"  Mix A: {loudness_diff.get('mix_a_value', 'N/A')} LUFS")
            print(f"  Mix B: {loudness_diff.get('mix_b_value', 'N/A')} LUFS")

        # Print other numeric differences
        for key in ["peak_loudness_dbfs", "bit_depth", "sample_rate"]:
            if key in differences and isinstance(differences[key], dict):
                diff = differences[key]
                print(f"{key.replace('_', ' ').title()} Difference: {diff.get('difference', 'N/A')}")
                print(f"  Mix A: {diff.get('mix_a_value', 'N/A')}")
                print(f"  Mix B: {diff.get('mix_b_value', 'N/A')}")

        # Print categorical differences
        for key in ["clipping", "stereo_field"]:
            if key in differences and isinstance(differences[key], dict):
                diff = differences[key]
                print(f"{key.replace('_', ' ').title()}: {diff.get('status', 'N/A')}")
                if diff.get('status') == "DIFFERENT":
                    print(f"  Mix A: {diff.get('mix_a_value', 'N/A')}")
                    print(f"  Mix B: {diff.get('mix_b_value', 'N/A')}")

        # Print tonal profile differences
        tonal_diff = differences.get("tonal_profile", {})
        if tonal_diff:
            print("\nTonal Profile Differences:")
            for freq, diff in tonal_diff.items():
                if isinstance(diff, dict):
                    status = diff.get('status', 'N/A')
                    print(f"  {freq}: {status}")
                    if status == "DIFFERENT":
                        print(f"    Mix A: {diff.get('mix_a_value', 'N/A')}")
                        print(f"    Mix B: {diff.get('mix_b_value', 'N/A')}")

    # Save comparison results to file
    with open(os.path.join(output_dir, "comparison.json"), "w") as f:
        json.dump(comparison_results, f, indent=2)

    print(f"\nComparison results saved to {output_dir}/comparison.json")


if __name__ == "__main__":
    analysis_workflow()