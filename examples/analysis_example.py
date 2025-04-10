"""
Example demonstrating how to use the RoEx MCP client for mix analysis
"""

import os
import sys
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from roex_mcp.client import RoExClient
from roex_mcp.models import MixAnalysisRequest, AnalysisMusicalStyle


def print_analysis_results(results):
    """Pretty print analysis results"""
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
    """Example workflow for analyzing mixes"""

    # Replace with your actual API key
    api_key = "your_api_key_here"
    client = RoExClient(api_key=api_key)

    # Check API health
    health = client.health_check()
    print(f"API Health: {health}")

    # 1. Single Mix Analysis
    print("\nStarting mix analysis...")

    # Replace with your actual audio file URL
    audio_url = "https://your-audio-file-location/audio.wav"

    analysis_request = MixAnalysisRequest(
        audio_file_location=audio_url,
        musical_style=AnalysisMusicalStyle.ROCK,
        is_master=True
    )

    # 2. Analyze mix
    analysis_results = client.analysis.analyze_mix(analysis_request)

    # 3. Print analysis results
    print_analysis_results(analysis_results)

    # 4. Save results to file
    output_dir = "analysis_results"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "analysis.json"), "w") as f:
        json.dump(analysis_results, f, indent=2)

    print(f"\nAnalysis results saved to {output_dir}/analysis.json")

    # 5. Compare Two Mixes (if needed)
    print("\nComparing two mixes...")

    # Replace with your actual audio file URLs
    mix_a_url = "https://your-audio-file-location/mix_a.wav"
    mix_b_url = "https://your-audio-file-location/mix_b.wav"

    comparison_results = client.analysis.compare_mixes(
        mix_a_url=mix_a_url,
        mix_b_url=mix_b_url,
        musical_style=AnalysisMusicalStyle.ROCK,
        is_master=True
    )

    # 6. Print comparison results
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

    # 7. Save comparison results to file
    with open(os.path.join(output_dir, "comparison.json"), "w") as f:
        json.dump(comparison_results, f, indent=2)

    print(f"\nComparison results saved to {output_dir}/comparison.json")


if __name__ == "__main__":
    analysis_workflow()