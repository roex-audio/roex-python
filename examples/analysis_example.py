"""
Example demonstrating how to use the RoEx client for mix analysis.

This example shows how to:
- Analyze a single audio mix for technical and aesthetic qualities.
- Compare two audio mixes to highlight differences.

Features analyzed include:
- Loudness (LUFS, Peak)
- Clipping
- Sample Rate, Bit Depth
- Stereo Field, Phase Issues, Mono Compatibility
- Tonal Profile (frequency balance)

Workflow:
1. Initialize client securely using environment variables.
2. Upload audio file(s) to RoEx's secure storage.
3. Perform analysis on a single mix.
4. Optionally, perform a comparison between two mixes.
5. Print and save the results.

Before running:
1. Set your API key in the environment:
   export ROEX_API_KEY='your_api_key_here'

2. Have WAV or FLAC file(s) ready for analysis.
   - Supported sample rates: 44.1kHz, 48kHz
   - Supported bit depths: 16-bit, 24-bit
   - Maximum duration: 10 minutes

File Security:
- Files are uploaded using secure, signed URLs.
- All processing happens in RoEx's secure environment.
- Files are automatically removed after processing.
- Download URLs (if any) are temporary and expire.

Example Usage:
    # Analyze a single file
    export ROEX_API_KEY='your_api_key_here'
    python analysis_example.py /path/to/your/audio.wav

    # Compare two files
    export ROEX_API_KEY='your_api_key_here'
    python analysis_example.py /path/to/mix_a.wav /path/to/mix_b.wav
"""

import sys
import json
from pathlib import Path

from roex_python.client import RoExClient
from roex_python.models import MixAnalysisRequest, AnalysisMusicalStyle
from roex_python.utils import upload_file

from common import get_api_key, validate_audio_file, ensure_output_dir, setup_logger, validate_audio_properties, AudioValidationError
from soundfile import SoundFileError

# Set up logger for this module
logger = setup_logger(__name__)

# Constants
ANALYSIS_MAX_DURATION_SECS = 600

def print_analysis_results(results):
    """Pretty print the analysis results from the mix analysis endpoint.
    
    Args:
        results: Dictionary containing the analysis results from the API
    """
    if not results or "payload" not in results:
        logger.error("No payload data found in analysis results.")
        return

    payload = results["payload"]

    print("\n==== Mix Analysis Results ====")
    print(f"Integrated Loudness: {payload.get('integrated_loudness_lufs', 'N/A')} LUFS")
    print(f"Peak Loudness:       {payload.get('peak_loudness_dbfs', 'N/A')} dBFS")
    print(f"Clipping:            {payload.get('clipping', 'N/A')}")
    print(f"Sample Rate:         {payload.get('sample_rate', 'N/A')} Hz")
    print(f"Bit Depth:           {payload.get('bit_depth', 'N/A')} bits")
    print(f"Stereo Field:        {payload.get('stereo_field', 'N/A')}")
    print(f"Phase Issues:        {payload.get('phase_issues', 'N/A')}")
    print(f"Mono Compatible:     {payload.get('mono_compatible', 'N/A')}")

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


def print_comparison_results(results):
    """Pretty print the comparison results.

    Args:
        results: Dictionary containing the comparison results.
    """
    print("\n==== Mix Comparison Results ====\n")
    if not results or "differences" not in results:
        logger.error("No comparison difference data found.")
        return

    differences = results["differences"]
    print("Key Differences:\n")

    # Helper to print value differences
    def print_value_diff(key, unit=""):
        if key in differences and isinstance(differences[key], dict):
            diff_data = differences[key]
            diff_val = diff_data.get('difference', 'N/A')
            mix_a_val = diff_data.get('mix_a_value', 'N/A')
            mix_b_val = diff_data.get('mix_b_value', 'N/A')
            print(f"  {key.replace('_', ' ').title():<20}: {diff_val}{unit}")
            print(f"    {'Mix A:':<10} {mix_a_val}{unit}")
            print(f"    {'Mix B:':<10} {mix_b_val}{unit}")

    # Helper to print status differences
    def print_status_diff(key):
        if key in differences and isinstance(differences[key], dict):
            diff_data = differences[key]
            status = diff_data.get('status', 'N/A')
            print(f"  {key.replace('_', ' ').title():<20}: {status}")
            if status == "DIFFERENT":
                mix_a_val = diff_data.get('mix_a_value', 'N/A')
                mix_b_val = diff_data.get('mix_b_value', 'N/A')
                print(f"    {'Mix A:':<10} {mix_a_val}")
                print(f"    {'Mix B:':<10} {mix_b_val}")

    print_value_diff("integrated_loudness_lufs", unit=" LUFS")
    print_value_diff("peak_loudness_dbfs", unit=" dBFS")
    print_value_diff("bit_depth", unit=" bits")
    print_value_diff("sample_rate", unit=" Hz")
    print("") # Add spacing
    print_status_diff("clipping")
    print_status_diff("stereo_field")
    print_status_diff("phase_issues")
    print_status_diff("mono_compatible")

    # Print tonal profile differences
    tonal_diff = differences.get("tonal_profile", {})
    if tonal_diff:
        print("\n  Tonal Profile Differences:")
        for freq, diff_data in tonal_diff.items():
            if isinstance(diff_data, dict):
                status = diff_data.get('status', 'N/A')
                print(f"    {freq:<10}: {status}")
                if status == "DIFFERENT":
                    mix_a_val = diff_data.get('mix_a_value', 'N/A')
                    mix_b_val = diff_data.get('mix_b_value', 'N/A')
                    print(f"      {'Mix A:':<10} {mix_a_val}")
                    print(f"      {'Mix B:':<10} {mix_b_val}")


def analysis_workflow(input_file: str, compare_file: str = None):
    """Run the analysis workflow for one or two files.
    
    Args:
        input_file: Path to the primary audio file for analysis.
        compare_file: Optional path to a second audio file for comparison.
    
    Raises:
        ValueError: If API key is not set or input files are invalid.
        FileNotFoundError: If input files don't exist.
    """
    client = RoExClient(
        api_key=get_api_key(),
        base_url="https://tonn.roexaudio.com"
    )
    output_dir = ensure_output_dir("analysis_results")

    # --- Validate and Upload Mix A ---
    file_path_a = validate_audio_file(input_file)
    try:
        validate_audio_properties(file_path_a, ANALYSIS_MAX_DURATION_SECS)
    except (FileNotFoundError, ValueError, AudioValidationError, SoundFileError) as e:
        logger.error(f"Validation failed for {input_file}: {e}. Aborting analysis workflow.")
        return # Abort if validation fails
    except Exception as e:
        logger.error(f"Unexpected validation error for {input_file}: {e}. Aborting analysis workflow.")
        return # Abort on unexpected errors too

    logger.info(f"\n=== Uploading {file_path_a.name} (Mix A) ===")
    try:
        audio_url_a = upload_file(client, str(file_path_a))
        logger.info(f"Uploaded Mix A to secure storage.")
    except Exception as e:
        logger.error(f"Error uploading {file_path_a.name}: {e}")
        return

    # --- Perform Single Mix Analysis (Mix A) ---
    logger.info("\n=== Analyzing Mix A ===")
    analysis_request = MixAnalysisRequest(
        audio_file_location=audio_url_a,
        musical_style=AnalysisMusicalStyle.ROCK, # Choose appropriate style
        is_master=True # Set based on whether it's a final master
    )
    try:
        analysis_results = client.analysis.analyze_mix(analysis_request)
        if not analysis_results or analysis_results.get("error"): # Basic error check
             logger.error(f"Error analyzing mix: {analysis_results.get('message', 'Unknown API error')}")
             # Continue to comparison if possible, but don't save analysis results
        else:
            print_analysis_results(analysis_results)
            analysis_output_path = output_dir / f"analysis_{file_path_a.stem}.json"
            try:
                with open(analysis_output_path, "w") as f:
                    json.dump(analysis_results, f, indent=2)
                logger.info(f"\nAnalysis results saved to {analysis_output_path}")
            except IOError as e:
                logger.error(f"Error saving analysis results: {e}")

    except Exception as e:
        logger.exception(f"Error calling analysis API: {e}")
        # Decide if we should stop or try comparison
        if not compare_file: return # Stop if only doing single analysis


    # --- Perform Comparison if compare_file is provided ---
    if compare_file:
        # --- Validate and Upload Mix B ---
        file_path_b = validate_audio_file(compare_file)
        try:
            validate_audio_properties(file_path_b, ANALYSIS_MAX_DURATION_SECS)
        except (FileNotFoundError, ValueError, AudioValidationError, SoundFileError) as e:
            logger.error(f"Validation failed for {compare_file}: {e}. Aborting comparison.")
            return # Abort if validation fails
        except Exception as e:
            logger.error(f"Unexpected validation error for {compare_file}: {e}. Aborting comparison.")
            return # Abort on unexpected errors too

        logger.info(f"\n=== Uploading {file_path_b.name} (Mix B) ===")
        try:
            audio_url_b = upload_file(client, str(file_path_b))
            logger.info(f"Uploaded Mix B to secure storage.")
        except Exception as e:
            logger.error(f"Error uploading {file_path_b.name}: {e}")
            logger.error("Cannot perform comparison without Mix B.")
            return # Can't compare if upload fails

        # --- Compare Mix A vs Mix B ---
        logger.info("\n=== Comparing Mix A vs Mix B ===")
        try:
            comparison_results = client.analysis.compare_mixes(
                mix_a_url=audio_url_a,
                mix_b_url=audio_url_b,
                musical_style=AnalysisMusicalStyle.ROCK, # Use consistent style
                is_master=True # Assume both are masters if comparing
            )
            if not comparison_results or comparison_results.get("error"): # Basic error check
                logger.error(f"Error comparing mixes: {comparison_results.get('message', 'Unknown API error')}")
                return
            else:
                print_comparison_results(comparison_results)
                comparison_output_path = output_dir / f"comparison_{file_path_a.stem}_vs_{file_path_b.stem}.json"
                try:
                    with open(comparison_output_path, "w") as f:
                        json.dump(comparison_results, f, indent=2)
                    logger.info(f"\nComparison results saved to {comparison_output_path}")
                except IOError as e:
                     logger.error(f"Error saving comparison results: {e}")

        except Exception as e:
            logger.exception(f"Error calling comparison API: {e}")
            return

    logger.info("\n=== Analysis Complete ===\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage:")
        logger.error("  Analyze single file: python analysis_example.py <path_to_audio>")
        logger.error("  Compare two files:   python analysis_example.py <path_to_mix_a> <path_to_mix_b>")
        sys.exit(1)

    input_file_arg = sys.argv[1]
    compare_file_arg = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        analysis_workflow(input_file_arg, compare_file_arg)
    except FileNotFoundError as e:
         logger.error(f"\nError: Input file not found - {e}")
    except ValueError as e:
         logger.error(f"\nError: {e}") # Catches API key errors and validation errors
    except KeyboardInterrupt:
        logger.info("\nAnalysis cancelled by user.")
    except Exception as e:
        logger.exception(f"\nAn unexpected error occurred: {e}")
        # Consider adding more specific exception handling if needed