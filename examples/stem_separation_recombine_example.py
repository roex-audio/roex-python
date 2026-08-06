"""Example demonstrating RoEx stem separation and recombination ("StemFlow").

This example shows how to:
1. Separate a full mix into isolated vocals/bass/drums/other stems.
2. Recombine the separated vocal with the (summed) backing track into a
   remixed and mastered result, reusing the separation job via `stemJobId`.
3. Alternatively, recombine directly from a vocal URL + a backing/beat URL,
   skipping separation entirely.

Billing:
- Submitting a separation task reserves 75 credits; they are captured only
  on success and refunded automatically if the job fails.
- Submitting a recombine task is free. The final master is charged 250
  credits the first time `retrieve_final_master` succeeds for that task;
  repeat calls return the same result without re-charging.
- Status polls and the free preview retrieval never charge credits.

Signed URLs (stem URLs, preview URL, master URL) expire after ~24 hours.

Before running:
1. Set your API key in the environment:
   export ROEX_API_KEY='your_api_key_here'

2. Have a WAV or FLAC file ready for separation.
   - Supported sample rates: 44.1kHz, 48kHz
   - Supported bit depths: 16-bit, 24-bit

Example Usage:
    # Set your API key
    export ROEX_API_KEY='your_api_key_here'

    # Separate a mix, then recombine using the separated stems
    python stem_separation_recombine_example.py /path/to/your/song.wav

    # Recombine directly from an isolated vocal + a backing/beat track,
    # skipping separation entirely
    python stem_separation_recombine_example.py --direct /path/to/vocal.wav /path/to/backing.wav
"""

import sys
from pathlib import Path

from roex_python.client import RoExClient
from roex_python.models import (
    StemSeparationRequest,
    RecombineRequest,
    RecombineMusicalStyle,
    DesiredLoudness,
)
from roex_python.utils import upload_file
from common import (
    get_api_key,
    validate_audio_file,
    ensure_output_dir,
    setup_logger,
    validate_audio_properties,
    AudioValidationError,
)

logger = setup_logger(__name__)

# Separation input is capped generously; recombine inputs are typically short clips.
MAX_DURATION_SECS = 600


def separate_and_recombine_workflow(input_file: str):
    """Separate a full mix into stems, then recombine them into a new master.

    Args:
        input_file: Path to the input audio file (WAV/FLAC) to separate.
    """
    client = RoExClient(api_key=get_api_key())

    try:
        file_path = validate_audio_file(input_file)
        validate_audio_properties(file_path, MAX_DURATION_SECS)
    except (FileNotFoundError, ValueError, AudioValidationError) as e:
        logger.error(f"Validation failed for {input_file}: {e}. Aborting workflow.")
        return

    logger.info(f"\n=== Uploading {file_path.name} ===")
    audio_url = upload_file(client, str(file_path))
    logger.info(f"Uploaded to: {audio_url}")

    logger.info("\n=== Submitting Stem Separation ===")
    separation_task = client.stem_separation.create_separation(
        StemSeparationRequest(audio_file_location=audio_url)
    )
    if separation_task.error:
        logger.error(f"Failed to submit separation task: {separation_task.message}")
        return
    logger.info(f"Separation task ID: {separation_task.stemflow_task_id}")

    logger.info("\n=== Waiting for Separation (this can take several minutes) ===")
    try:
        client.stem_separation.wait_for_separation(
            separation_task.stemflow_task_id, poll_interval=15, timeout=1200
        )
    except Exception as e:
        logger.error(f"Separation did not complete successfully: {e}")
        return
    logger.info("Separation complete.")

    output_dir = ensure_output_dir("stemflow_recombine_output")

    logger.info("\n=== Downloading Separated Stems ===")
    stems = client.stem_separation.retrieve_stems(separation_task.stemflow_task_id)
    for stem_name, stem_url in (
        ("vocals", stems.vocals),
        ("bass", stems.bass),
        ("drums", stems.drums),
        ("other", stems.other),
    ):
        if not stem_url:
            continue
        stem_path = output_dir / f"stem_{stem_name}.wav"
        if client.api_provider.download_file(stem_url, str(stem_path)):
            logger.info(f"Downloaded {stem_name} stem to {stem_path}")
        else:
            logger.error(f"Failed to download {stem_name} stem")

    logger.info("\n=== Submitting Recombine (via stemJobId) ===")
    recombine_task = client.recombine.create_recombine(
        RecombineRequest(
            stem_job_id=separation_task.stemflow_task_id,
            musical_style=RecombineMusicalStyle.POP,  # Choose appropriate style
            desired_loudness=DesiredLoudness.MEDIUM,
            vocal_gain_db=0.0,
        )
    )
    if recombine_task.error:
        logger.error(f"Failed to submit recombine task: {recombine_task.message}")
        return
    logger.info(f"Recombine task ID: {recombine_task.recombine_task_id}")

    logger.info("\n=== Waiting for Recombine ===")
    try:
        client.recombine.wait_for_recombine(
            recombine_task.recombine_task_id, poll_interval=10, timeout=600
        )
    except Exception as e:
        logger.error(f"Recombine did not complete successfully: {e}")
        return
    logger.info("Recombine complete.")

    logger.info("\n=== Retrieving Free Preview ===")
    preview = client.recombine.retrieve_preview(recombine_task.recombine_task_id)
    if preview.preview_url:
        preview_path = output_dir / "preview_30s.mp3"
        if client.api_provider.download_file(preview.preview_url, str(preview_path)):
            logger.info(f"Downloaded preview to {preview_path}")

    logger.info("\n=== Retrieving Final Master (charges 250 credits) ===")
    final_result = client.recombine.retrieve_final_master(recombine_task.recombine_task_id)
    if not final_result.master_url:
        logger.error("No final master URL received")
        return

    master_path = output_dir / "final_master.wav"
    if client.api_provider.download_file(final_result.master_url, str(master_path)):
        logger.info(f"Downloaded final master to {master_path}")
        logger.info(
            f"Measured loudness: {final_result.measured_lufs} LUFS, "
            f"peak: {final_result.peak_level} dBFS"
        )

    logger.info("\n=== Workflow Complete ===")
    logger.info(f"All files saved to: {output_dir}")


def direct_recombine_workflow(vocal_file: str, backing_file: str):
    """Recombine directly from an isolated vocal + backing track, skipping separation.

    Args:
        vocal_file: Path to an isolated vocal track (WAV/FLAC).
        backing_file: Path to a backing/instrumental (beat) track (WAV/FLAC).
    """
    client = RoExClient(api_key=get_api_key())

    try:
        vocal_path = validate_audio_file(vocal_file)
        backing_path = validate_audio_file(backing_file)
        validate_audio_properties(vocal_path, MAX_DURATION_SECS)
        validate_audio_properties(backing_path, MAX_DURATION_SECS)
    except (FileNotFoundError, ValueError, AudioValidationError) as e:
        logger.error(f"Validation failed: {e}. Aborting workflow.")
        return

    logger.info("\n=== Uploading Vocal and Backing Tracks ===")
    vocal_url = upload_file(client, str(vocal_path))
    backing_url = upload_file(client, str(backing_path))

    logger.info("\n=== Submitting Recombine (direct vocal + backing URLs) ===")
    recombine_task = client.recombine.create_recombine(
        RecombineRequest(
            vocal_stem_url=vocal_url,
            backing_stem_url=backing_url,
            musical_style=RecombineMusicalStyle.HIPHOP_GRIME,  # Choose appropriate style
            desired_loudness=DesiredLoudness.HIGH,
            vocal_gain_db=1.5,
        )
    )
    if recombine_task.error:
        logger.error(f"Failed to submit recombine task: {recombine_task.message}")
        return
    logger.info(f"Recombine task ID: {recombine_task.recombine_task_id}")

    client.recombine.wait_for_recombine(recombine_task.recombine_task_id)
    logger.info("Recombine complete.")

    output_dir = ensure_output_dir("stemflow_recombine_output")
    final_result = client.recombine.retrieve_final_master(recombine_task.recombine_task_id)
    if not final_result.master_url:
        logger.error("No final master URL received")
        return

    master_path = output_dir / "direct_final_master.wav"
    if client.api_provider.download_file(final_result.master_url, str(master_path)):
        logger.info(f"Downloaded final master to {master_path}")


if __name__ == "__main__":
    try:
        if len(sys.argv) >= 2 and sys.argv[1] == "--direct":
            if len(sys.argv) != 4:
                print(
                    "Usage: python stem_separation_recombine_example.py --direct "
                    "<vocal_file> <backing_file>"
                )
                sys.exit(1)
            direct_recombine_workflow(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 2:
            separate_and_recombine_workflow(sys.argv[1])
        else:
            print(
                "Usage:\n"
                "  python stem_separation_recombine_example.py <audio_file>\n"
                "  python stem_separation_recombine_example.py --direct <vocal_file> <backing_file>"
            )
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nWorkflow cancelled by user")
    except Exception as e:
        logger.exception(f"\nError: {e}")
