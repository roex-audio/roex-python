"""Example demonstrating advanced multitrack mixing with audio effects (EQ, compression, panning).

This example showcases the advanced audio processing capabilities of the RoEx API,
including parametric EQ, dynamic compression, and stereo panning controls.

Workflow:
1. Initialize client securely using environment variables
2. Upload multiple audio files to RoEx's secure storage
3. Create and review mix preview
4. Apply advanced audio effects (EQ, compression, panning) for final mix
5. Download the final processed mix

Advanced Features Demonstrated:
- 6-band parametric EQ with preset configurations
- Dynamic range compression with preset profiles
- Stereo panning positioning
- Per-track gain adjustments
- Master loudness control
- Optional mastering

Before running:
1. Set your API key in the environment:
   export ROEX_API_KEY='your_api_key_here'

2. Have your audio files ready for mixing
   - Supported formats: WAV, FLAC
   - Supported sample rates: 44.1kHz, 48kHz
   - Supported bit depths: 16-bit, 24-bit
   - Maximum duration: 8 minutes per track

Example Usage:
    # Set your API key
    export ROEX_API_KEY='your_api_key_here'
    
    # Run the advanced example
    python advanced_mix_example.py --bass /path/to/bass.wav --vocals /path/to/vocals.wav --drums /path/to/drums.wav
"""

import argparse
import os
from pathlib import Path
from typing import Dict, List

from roex_python.client import RoExClient
from roex_python.models import (
    TrackData, MultitrackMixRequest, 
    InstrumentGroup, PresenceSetting, PanPreference, ReverbPreference, MusicalStyle,
    FinalMixRequestAdvanced, TrackEffectsData,
    EQSettings, EQBandSettings, CompressionSettings, PanningSettings,
    DesiredLoudness
)
from roex_python.utils import upload_file
from common import (
    get_api_key, 
    validate_audio_file, 
    setup_logger,
    validate_audio_properties, 
    AudioValidationError
)

# Set up logger for this module
logger = setup_logger(__name__)

# Constants
MIX_MAX_DURATION_SECS = 480


def advanced_mix_workflow(bass_path: str, vocals_path: str, drums_path: str = None, output_dir: str = "./advanced_mix_output"):
    """
    Demonstrates advanced multitrack mixing with comprehensive audio effects.
    
    Args:
        bass_path: Path to bass track
        vocals_path: Path to vocal track
        drums_path: Optional path to drums track
        output_dir: Directory to save output files
    """
    setup_logger()
    api_key = get_api_key()
    if not api_key:
        logger.error("API key not found. Please set ROEX_API_KEY environment variable.")
        return

    client = RoExClient(api_key=api_key, base_url="https://tonn.roexaudio.com")
    os.makedirs(output_dir, exist_ok=True)
    output_path = Path(output_dir)

    logger.info("\n" + "="*70)
    logger.info("ADVANCED MULTITRACK MIXING WITH AUDIO EFFECTS")
    logger.info("="*70)

    # ========================================================================
    # STEP 1: Validate and Upload Tracks
    # ========================================================================
    logger.info("\n=== STEP 1: Validating and Uploading Tracks ===")
    
    track_files = {
        'bass': bass_path,
        'vocals': vocals_path
    }
    if drums_path:
        track_files['drums'] = drums_path
    
    uploaded_urls = {}
    for track_name, file_path in track_files.items():
        try:
            validated_path = validate_audio_file(file_path, allowed_extensions={"wav", "flac"})
            validate_audio_properties(validated_path, MIX_MAX_DURATION_SECS)
            logger.info(f"? {track_name.capitalize()} track validated: {validated_path.name}")
            
            upload_url = upload_file(client, str(validated_path))
            if upload_url:
                uploaded_urls[track_name] = upload_url
                logger.info(f"? {track_name.capitalize()} uploaded successfully")
            else:
                logger.error(f"? Failed to upload {track_name}")
                return
        except (FileNotFoundError, ValueError, AudioValidationError) as e:
            logger.error(f"? Validation failed for {track_name}: {e}")
            return

    # ========================================================================
    # STEP 2: Create Mix Preview
    # ========================================================================
    logger.info("\n=== STEP 2: Creating Mix Preview ===")
    
    preview_tracks = [
        TrackData(
            track_url=uploaded_urls['bass'],
            instrument_group=InstrumentGroup.BASS_GROUP,
            presence_setting=PresenceSetting.NORMAL,
            pan_preference=PanPreference.CENTRE,
            reverb_preference=ReverbPreference.NONE
        ),
        TrackData(
            track_url=uploaded_urls['vocals'],
            instrument_group=InstrumentGroup.VOCAL_GROUP,
            presence_setting=PresenceSetting.LEAD,
            pan_preference=PanPreference.CENTRE,
            reverb_preference=ReverbPreference.LOW
        )
    ]
    
    if 'drums' in uploaded_urls:
        preview_tracks.append(
            TrackData(
                track_url=uploaded_urls['drums'],
                instrument_group=InstrumentGroup.DRUMS_GROUP,
                presence_setting=PresenceSetting.NORMAL,
                pan_preference=PanPreference.NO_PREFERENCE,
                reverb_preference=ReverbPreference.NONE
            )
        )
    
    mix_request = MultitrackMixRequest(
        track_data=preview_tracks,
        musical_style=MusicalStyle.POP,
        return_stems=False,
        # Note: This is a test webhook URL for demonstration purposes.
        # Replace with your own webhook endpoint or set to None if not needed.
        webhook_url="https://webhook-test-786984745538.europe-west1.run.app"
    )
    
    try:
        mix_response = client.mix.create_mix_preview(mix_request)
        mix_task_id = mix_response.multitrack_task_id
        logger.info(f"? Mix preview task created: {mix_task_id}")
    except Exception as e:
        logger.error(f"? Error creating mix preview: {e}")
        return

    # ========================================================================
    # STEP 3: Retrieve Mix Preview
    # ========================================================================
    logger.info("\n=== STEP 3: Retrieving Mix Preview ===")
    logger.info("Polling for preview completion (this may take a minute)...")
    
    try:
        preview_results = client.mix.retrieve_preview_mix(
            mix_task_id,
            retrieve_fx_settings=True,
            max_attempts=30,
            poll_interval=5
        )
        logger.info("? Mix preview ready!")
        
        # Download preview
        preview_url = preview_results.get('download_url_preview_mixed')
        if preview_url:
            preview_file = output_path / "mix_preview.wav"
            if client.api_provider.download_file(preview_url, str(preview_file)):
                logger.info(f"? Preview downloaded: {preview_file}")
        
    except Exception as e:
        logger.error(f"? Error retrieving mix preview: {e}")
        return

    # ========================================================================
    # STEP 4: Apply Advanced Audio Effects for Final Mix
    # ========================================================================
    logger.info("\n=== STEP 4: Applying Advanced Audio Effects ===")
    logger.info("\nConfiguring per-track effects:")
    
    # --- Bass Track: Enhance low-end presence ---
    logger.info("\n?? BASS TRACK:")
    logger.info("   ? EQ: Bass boost preset (enhanced sub and low-mids)")
    logger.info("   ? Compression: Tight 5:1 ratio for consistent level")
    logger.info("   ? Panning: Center")
    logger.info("   ? Gain: +2.0 dB")
    
    bass_effects = TrackEffectsData(
        track_url=uploaded_urls['bass'],
        gain_db=2.0,
        eq_settings=EQSettings.preset_bass_boost(),
        compression_settings=CompressionSettings.preset_bass(),
        panning_settings=PanningSettings.center()
    )
    
    # --- Vocal Track: Enhance clarity and presence ---
    logger.info("\n?? VOCAL TRACK:")
    logger.info("   ? EQ: Vocal clarity preset (reduced muddiness, enhanced presence)")
    logger.info("   ? Compression: Smooth 4:1 ratio for consistent dynamics")
    logger.info("   ? Panning: Center")
    logger.info("   ? Gain: -0.5 dB")
    
    vocal_effects = TrackEffectsData(
        track_url=uploaded_urls['vocals'],
        gain_db=-0.5,
        eq_settings=EQSettings.preset_vocal_clarity(),
        compression_settings=CompressionSettings.preset_vocal(),
        panning_settings=PanningSettings.center()
    )
    
    final_track_data: List[TrackEffectsData] = [bass_effects, vocal_effects]
    
    # --- Drums Track (if present): Add punch and definition ---
    if 'drums' in uploaded_urls:
        logger.info("\n?? DRUMS TRACK:")
        logger.info("   ? EQ: Custom - boosted sub (50Hz) and attack (3kHz)")
        logger.info("   ? Compression: Drum bus glue (3:1 ratio, slower attack)")
        logger.info("   ? Panning: Center")
        logger.info("   ? Gain: +1.0 dB")
        
        drums_effects = TrackEffectsData(
            track_url=uploaded_urls['drums'],
            gain_db=1.0,
            eq_settings=EQSettings(
                band_1=EQBandSettings(gain=4.0, q=1.2, centre_freq=50.0),   # Sub punch
                band_4=EQBandSettings(gain=3.0, q=1.5, centre_freq=3000.0)  # Attack/presence
            ),
            compression_settings=CompressionSettings.preset_drum_bus(),
            panning_settings=PanningSettings.center()
        )
        final_track_data.append(drums_effects)
    
    # ========================================================================
    # STEP 5: Create Final Mix with Advanced Effects
    # ========================================================================
    logger.info("\n=== STEP 5: Creating Final Mix with Effects ===")
    
    final_mix_request = FinalMixRequestAdvanced(
        multitrack_task_id=mix_task_id,
        track_data=final_track_data,
        return_stems=False,
        create_master=False,
        desired_loudness=DesiredLoudness.MEDIUM,
        sample_rate="44100"
    )
    
    try:
        logger.info("Processing final mix with advanced audio effects...")
        final_mix_results = client.mix.retrieve_final_mix_advanced(final_mix_request)
        logger.info("? Advanced final mix complete!")
        
        # Download final mix
        final_url = final_mix_results.get('download_url_mixed') or final_mix_results.get('download_url_final_mix')
        if final_url:
            final_file = output_path / "mix_final_advanced.wav"
            if client.api_provider.download_file(final_url, str(final_file)):
                logger.info(f"? Final mix downloaded: {final_file}")
        
    except Exception as e:
        logger.error(f"? Error creating advanced final mix: {e}")
        return
    
    # ========================================================================
    # Summary
    # ========================================================================
    logger.info("\n" + "="*70)
    logger.info("ADVANCED MIXING COMPLETE!")
    logger.info("="*70)
    logger.info(f"\nOutput files saved to: {output_path}")
    logger.info("\nAudio effects applied:")
    logger.info("  ? Parametric EQ (6-band)")
    logger.info("  ? Dynamic range compression")
    logger.info("  ? Stereo panning")
    logger.info("  ? Per-track gain adjustments")
    logger.info("\nPresets used:")
    logger.info("  ? Bass: Bass boost EQ + Bass compression")
    logger.info("  ? Vocals: Vocal clarity EQ + Vocal compression")
    if 'drums' in uploaded_urls:
        logger.info("  ? Drums: Custom EQ + Drum bus compression")
    logger.info("\n" + "="*70 + "\n")


def demonstrate_custom_effects():
    """
    Demonstrates creating custom audio effects from scratch.
    This function shows the available parameters and ranges without making API calls.
    """
    logger.info("\n" + "="*70)
    logger.info("CUSTOM AUDIO EFFECTS EXAMPLES")
    logger.info("="*70)
    
    # Custom EQ example
    logger.info("\n--- Custom Parametric EQ ---")
    custom_eq = EQSettings(
        band_1=EQBandSettings(gain=6.0, q=1.0, centre_freq=60.0),     # Sub bass boost
        band_2=EQBandSettings(gain=-3.0, q=0.8, centre_freq=200.0),   # Remove mud
        band_3=EQBandSettings(gain=0.0, q=1.0, centre_freq=500.0),    # Neutral low-mids
        band_4=EQBandSettings(gain=2.0, q=1.2, centre_freq=2500.0),   # Presence boost
        band_5=EQBandSettings(gain=3.0, q=0.9, centre_freq=6000.0),   # Clarity
        band_6=EQBandSettings(gain=2.0, q=0.7, centre_freq=12000.0)   # Air
    )
    logger.info("? Custom 6-band EQ configured")
    logger.info("  Band 1 (60Hz): +6dB | Band 2 (200Hz): -3dB")
    logger.info("  Band 4 (2.5kHz): +2dB | Band 5 (6kHz): +3dB | Band 6 (12kHz): +2dB")
    
    # Custom compression example
    logger.info("\n--- Custom Compression ---")
    custom_comp = CompressionSettings(
        threshold=-16.0,   # Compress signals above -16dB
        ratio=6.0,         # 6:1 compression ratio
        attack_ms=3.0,     # Fast attack (3ms)
        release_ms=80.0    # Medium-slow release (80ms)
    )
    logger.info("? Custom compression configured")
    logger.info(f"  Threshold: {custom_comp.threshold}dB | Ratio: {custom_comp.ratio}:1")
    logger.info(f"  Attack: {custom_comp.attack_ms}ms | Release: {custom_comp.release_ms}ms")
    
    # Custom panning example
    logger.info("\n--- Custom Panning ---")
    logger.info("? Available panning positions:")
    logger.info(f"  Hard Left: {PanningSettings.hard_left().panning_angle}?")
    logger.info(f"  Slight Left: {PanningSettings.slight_left().panning_angle}?")
    logger.info(f"  Center: {PanningSettings.center().panning_angle}?")
    logger.info(f"  Slight Right: {PanningSettings.slight_right().panning_angle}?")
    logger.info(f"  Hard Right: {PanningSettings.hard_right().panning_angle}?")
    
    # Available presets
    logger.info("\n--- Available EQ Presets ---")
    logger.info("  ? preset_bass_boost() - Enhance low-end presence")
    logger.info("  ? preset_vocal_clarity() - Enhance vocal intelligibility")
    logger.info("  ? preset_kick_punch() - Add punch to kick drums")
    logger.info("  ? preset_snare_crack() - Enhance snare attack")
    logger.info("  ? preset_high_pass() - Remove low-end rumble")
    logger.info("  ? preset_brightness() - Add sparkle and air")
    
    logger.info("\n--- Available Compression Presets ---")
    logger.info("  ? preset_vocal() - Smooth vocal compression")
    logger.info("  ? preset_bass() - Tight bass compression")
    logger.info("  ? preset_drum_bus() - Glue compression for drums")
    logger.info("  ? preset_gentle() - Subtle dynamic control")
    logger.info("  ? preset_aggressive() - Maximum impact")
    
    logger.info("\n" + "="*70 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Advanced multitrack mixing with audio effects using RoEx API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage with bass and vocals
    python advanced_mix_example.py --bass bass.wav --vocals vocals.wav
    
    # With drums track
    python advanced_mix_example.py --bass bass.wav --vocals vocals.wav --drums drums.wav
    
    # Show custom effects examples
    python advanced_mix_example.py --show-examples
        """
    )
    
    parser.add_argument('--bass', help='Path to the bass track file (WAV/FLAC)')
    parser.add_argument('--vocals', help='Path to the vocals track file (WAV/FLAC)')
    parser.add_argument('--drums', help='Path to the drums track file (WAV/FLAC) - optional')
    parser.add_argument('--output-dir', default='./advanced_mix_output', 
                       help='Directory to save output files')
    parser.add_argument('--show-examples', action='store_true',
                       help='Show examples of custom audio effects configuration')
    
    args = parser.parse_args()
    
    if args.show_examples:
        demonstrate_custom_effects()
    elif args.bass and args.vocals:
        advanced_mix_workflow(args.bass, args.vocals, args.drums, args.output_dir)
    else:
        parser.print_help()
        print("\n??  Error: --bass and --vocals are required (unless using --show-examples)")
