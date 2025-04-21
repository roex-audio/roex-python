# RoEx Python Client Examples

This directory contains example scripts demonstrating how to use the `roex-python` client library to interact with the RoEx API for various audio processing tasks.

## Prerequisites

1.  **Python**: Ensure you have Python installed.
2.  **RoEx Python Client**: Install the client library (if not installed from the parent directory):
    ```bash
    pip install roex-python
    ```
3.  **Example Dependencies**: The examples also require `soundfile` and `numpy` for audio validation:
    ```bash
    pip install soundfile numpy
    ```
4.  **API Key**: Obtain your API key from the [RoEx Tonn API Portal](https://tonn-portal.roexaudio.com). You need to set it as an environment variable before running any example:
    ```bash
    export ROEX_API_KEY='your_actual_api_key_here'
    ```
    Replace `'your_actual_api_key_here'` with your key.

## Common Usage

Most examples follow a similar pattern:

1.  Set the `ROEX_API_KEY` environment variable (as shown above).
2.  Run the desired example script from the command line, providing the required file paths as arguments.

```bash
python <example_script_name>.py [arguments...]
```

These examples utilize helper functions from `common.py` for tasks like retrieving the API key from the environment, validating input audio files (checking existence, format, and properties like length, sample rate, and silence), and ensuring output directories exist.

## Available Examples

Here's a summary of the available examples and their usage:

*   **`upload_example.py`**: 
    *   Purpose: Uploads a single audio file (WAV, FLAC, MP3) to RoEx secure storage and returns a readable URL for use in other API calls.
    *   Usage: `python upload_example.py <path_to_audio_file>`

*   **`analysis_example.py`**: 
    *   Purpose: Analyzes one or two audio files (WAV, FLAC, MP3) and prints the analysis results. If two files are provided, it also shows a comparison.
    *   Usage (Single File): `python analysis_example.py <path_to_audio_file>`
    *   Usage (Two Files): `python analysis_example.py <path_to_audio_file_1> <path_to_audio_file_2>`

*   **`audio_cleanup_example.py`**: 
    *   Purpose: Applies RoEx audio cleanup to a specific sound source within an audio file (WAV, FLAC).
    *   Usage: `python audio_cleanup_example.py <path_to_audio_file> <sound_source>`
    *   Valid `<sound_source>` values: `KICK_GROUP`, `SNARE_GROUP`, `VOCAL_GROUP`, `BACKING_VOCALS_GROUP`, `PERCS_GROUP`, `STRINGS_GROUP`, `E_GUITAR_GROUP`, `ACOUSTIC_GUITAR_GROUP`

*   **`enhance_example.py`**: 
    *   Purpose: Enhances a single audio mix file (WAV, FLAC, MP3).
    *   Usage: `python enhance_example.py <path_to_audio_file>`

*   **`mastering_example.py`**: 
    *   Purpose: Masters a single track or multiple tracks as an album (WAV, FLAC, MP3).
    *   Usage (Single Track): `python mastering_example.py <path_to_track>`
    *   Usage (Album): `python mastering_example.py <path_to_track1> <path_to_track2> ...`

*   **`mix_example.py`**: 
    *   Purpose: Performs multitrack mixing using provided stems (WAV, FLAC). Requires specific stem types passed as command-line arguments.
    *   Usage: 
      ```bash
      python examples/mix_example.py \
          --bass /path/to/your/bass.wav \
          --vocals /path/to/your/vocals.wav \
          [--kick /path/to/kick.wav] \
          [--snare /path/to/snare.wav] \
          [--drums /path/to/drums.wav] \
          [--cymbals /path/to/cymbals.wav] \
          [--backing-vocals /path/to/backing_vocals.wav] \
          [--percussion /path/to/percussion.wav] \
          [--strings /path/to/strings.wav] \
          [--synth /path/to/synth.wav] \
          [--keys /path/to/keys.wav] \
          [--brass /path/to/brass.wav] \
          [--guitar /path/to/acoustic_guitar.wav] \
          [--electric-guitar /path/to/electric_guitar.wav] \
          [--fx /path/to/fx.wav] \
          [--backing-track /path/to/backing_track.wav] \
          [--other /path/to/other1.wav] [--other /path/to/other2.wav] ... \
          [--output-dir ./my_mix_output]
      ```
    *   Notes:
        *   `--bass` and `--vocals` arguments are required.
        *   Provide paths to your WAV or FLAC audio files for each instrument group you have.
        *   Use `--drums` if you have a single drums track instead of separate kick/snare.
        *   Use `--other` multiple times for any tracks not covered by other specific arguments.
        *   The output directory defaults to `./mixed_tracks` if `--output-dir` is not specified.

Refer to the individual script docstrings for more detailed information about each workflow.
