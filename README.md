# RoEx Python

[![PyPI version](https://badge.fury.io/py/roex-python.svg)](https://badge.fury.io/py/roex-python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

roex-python is a powerful Python package that simplifies and automates advanced audio processing tasks for music producers, sound engineers, and developers. Whether mixing, mastering, or applying custom DSP algorithms, roex-python directly brings cutting-edge audio manipulation to your Python environment.

This pip package is designed to work with the [RoEx Tonn API](https://tonn-portal.roexaudio.com). This package provides a clean, type-safe interface to interact with the RoEx Tonn API for audio mixing, mastering, analysis, and enhancement.

## Features

- **Multitrack Mixing**: Submit tracks for professional AI mixing
- **Audio Mastering**: Master individual tracks or entire albums
- **Mix Analysis**: Analyze and compare audio mixes
- **Mix Enhancement**: Enhance and improve existing mixes
- **Audio Cleanup**: Clean up specific instrument tracks (vocals, guitars, etc.)
- **Asynchronous Processing**: Built-in polling for long-running tasks
- **Secure File Uploads**: Uses temporary signed URLs for direct and secure uploads to cloud storage.
- **File Downloads**: Easily download processed audio files

## Installation

```bash
pip install roex-python
```

## Configuration

Before using the client, ensure you have your RoEx API key, which you can obtain from the [RoEx Tonn Portal](https://tonn-portal.roexaudio.com). It's recommended to set it as an environment variable:

```bash
export ROEX_API_KEY='your_api_key_here'
```

You can then initialize the client:

```python
import os
from roex_python.client import RoExClient

api_key = os.getenv("ROEX_API_KEY")
if not api_key:
    raise ValueError("ROEX_API_KEY environment variable not set.")

client = RoExClient(api_key=api_key)
```

## Usage

This section provides examples for the core functionalities of the `roex-python` package. For more comprehensive, runnable examples that include audio file validation, please see the scripts in the `examples/` directory.

### 1. Multitrack Mixing

Submit multiple instrument tracks for AI-powered mixing based on a chosen musical style. You can specify presence, panning, and reverb preferences for each track. If using local files, they must be uploaded first.

```python
from roex_python.models import (
    TrackData, MultitrackMixRequest, InstrumentGroup,
    PresenceSetting, PanPreference, ReverbPreference, MusicalStyle
)
# Assuming 'client' is an initialized RoExClient
# And 'upload_file' is a helper function like the one in examples/common.py or roex_python.utils

# Step 1: Upload local files (repeat for each track)
bass_local_path = "/path/to/your/bass.wav"
vocals_local_path = "/path/to/your/vocals.wav"

# Note: Error handling for upload failures should be added in real code
uploaded_bass_url = upload_file(client, bass_local_path)
uploaded_vocals_url = upload_file(client, vocals_local_path)

# Define tracks (ensure track_url points to accessible WAV/FLAC files)
# Step 2: Use the obtained URLs in the TrackData
tracks = [
    TrackData(
        track_url=uploaded_bass_url,
        instrument_group=InstrumentGroup.BASS_GROUP,
        presence_setting=PresenceSetting.NORMAL,
        pan_preference=PanPreference.CENTRE,
        reverb_preference=ReverbPreference.NONE
    ),
    TrackData(
        track_url=uploaded_vocals_url,
        instrument_group=InstrumentGroup.VOCAL_GROUP,
        presence_setting=PresenceSetting.LEAD,
        pan_preference=PanPreference.CENTRE,
        reverb_preference=ReverbPreference.LOW
    ),
    # Add more tracks...
]

mix_request = MultitrackMixRequest(
    track_data=tracks,
    musical_style=MusicalStyle.POP,
    return_stems=True # Optional: Get individual stems back
)

# Submit the mix request
mix_task = client.mix.create_mix_preview(mix_request)
print(f"Mix task submitted. Task ID: {mix_task.multitrack_task_id}")

# Retrieve the preview mix (polls until ready)
# This returns a dictionary with download URLs for the preview mix and stems (if requested)
preview_result = client.mix.retrieve_preview_mix(mix_task.multitrack_task_id)
print(f"Preview Mix URL: {preview_result.get('preview_mix_url')}")
```

**Output:** The process returns task IDs and, upon completion, URLs to download the mixed preview audio file and optionally, the processed stems.

### 2. Audio Mastering

Master a single audio track (e.g., a final mix) according to a specified musical style and desired loudness. If using a local file, it must be uploaded first.

```python
from roex_python.models import (
    MasteringRequest, MusicalStyle, DesiredLoudness
)
# Assuming 'client' is an initialized RoExClient
# And 'upload_file' is a helper function like the one in examples/common.py or roex_python.utils

# Step 1: Upload local file
mixdown_local_path = "/path/to/your/mixdown.wav"
uploaded_mixdown_url = upload_file(client, mixdown_local_path)

# Step 2: Use the obtained URL in the request
mastering_request = MasteringRequest(
    track_url=uploaded_mixdown_url,
    musical_style=MusicalStyle.ROCK_INDIE,
    desired_loudness=DesiredLoudness.MEDIUM,
    sample_rate="44100" # Match the source file's sample rate
)

# Create mastering preview task
task = client.mastering.create_mastering_preview(mastering_request)
print(f"Mastering task submitted. Task ID: {task.mastering_task_id}")

# Retrieve the preview master (polls until ready)
preview = client.mastering.retrieve_preview_master(task.mastering_task_id)
print(f"Preview Master URL: {preview.get('download_url_mastered_preview')}")

# Optionally, retrieve the final master (polls until ready)
final_url = client.mastering.retrieve_final_master(task.mastering_task_id)
print(f"Final Master URL: {final_url}")
```

**Output:** Returns task IDs and download URLs for the mastered preview and final audio files.

### 3. Mix Analysis

Analyze a mix or master file to get insights into its characteristics. If using a local file, it must be uploaded first.

```python
from roex_python.models import AnalysisRequest

# Assuming 'client' is an initialized RoExClient
# And 'upload_file' is a helper function like the one in examples/common.py or roex_python.utils

# Step 1: Upload local file
track_to_analyze_local_path = "/path/to/your/track_for_analysis.wav"
uploaded_analysis_url = upload_file(client, track_to_analyze_local_path)

# Step 2: Use the obtained URL in the request
analysis_request = AnalysisRequest(
    track_url=uploaded_analysis_url
)

# Submit analysis task
task = client.analysis.create_analysis(analysis_request)
print(f"Analysis task submitted. Task ID: {task.analysis_task_id}")

# Retrieve analysis results (polls until ready)
analysis_results = client.analysis.retrieve_analysis(task.analysis_task_id)
print("Analysis Results:", analysis_results)
```

**Output:** A dictionary containing various analysis metrics for the provided audio track.

### 4. Mix Enhancement

Enhance an existing mix using AI. If using a local file, it must be uploaded first.

```python
from roex_python.models import EnhanceMixRequest

# Assuming 'client' is an initialized RoExClient
# And 'upload_file' is a helper function like the one in examples/common.py or roex_python.utils

# Step 1: Upload local file
mix_to_enhance_local_path = "/path/to/your/mix_to_enhance.wav"
uploaded_enhance_url = upload_file(client, mix_to_enhance_local_path)

# Step 2: Use the obtained URL in the request
enhance_request = EnhanceMixRequest(
    track_url=uploaded_enhance_url
)

# Submit enhancement task
task = client.enhance.create_enhancement(enhance_request)
print(f"Enhancement task submitted. Task ID: {task.enhance_task_id}")

# Retrieve enhanced mix (polls until ready)
enhanced_mix = client.enhance.retrieve_enhancement(task.enhance_task_id)
print(f"Enhanced Mix URL: {enhanced_mix.get('download_url_enhanced_mix')}")
```

**Output:** Returns a task ID and the download URL for the enhanced audio file and it's stems if requested.

### 5. Audio Cleanup

Clean up specific types of audio sources within a track (e.g., remove bleed from a vocal track). If using a local file, it must be uploaded first.

```python
from roex_python.models import AudioCleanupRequest, SoundSource

# Assuming 'client' is an initialized RoExClient
# And 'upload_file' is a helper function like the one in examples/common.py or roex_python.utils

# Step 1: Upload local file
vocal_track_local_path = "/path/to/your/vocal_track.wav"
uploaded_vocal_url = upload_file(client, vocal_track_local_path)

# Step 2: Use the obtained URL in the request
cleanup_request = AudioCleanupRequest(
    audio_file_location=uploaded_vocal_url,
    sound_source=SoundSource.VOCAL_GROUP # Choose the appropriate source type
)

# Submit cleanup task
task = client.cleanup.create_audio_cleanup(cleanup_request)
print(f"Audio cleanup task submitted. Task ID: {task.cleanup_task_id}")

# Retrieve cleanup results (polls until ready)
cleanup_results = client.cleanup.retrieve_audio_cleanup(task.cleanup_task_id)
print("Cleanup Results:", cleanup_results)
```

**Available `SoundSource` options:** `KICK_GROUP`, `SNARE_GROUP`, `VOCAL_GROUP`, `BACKING_VOCALS_GROUP`, `PERCS_GROUP`, `STRINGS_GROUP`, `E_GUITAR_GROUP`, `ACOUSTIC_GUITAR_GROUP`.

**Output:** A dictionary containing status information and potentially details about the cleanup process. The primary result is often implicitly the cleaned audio accessible via a related process or understanding, though the API might provide specific output URLs depending on future implementation.

## Handling Local Files

The RoEx API endpoints require URLs pointing to audio files. If you are working with local files (e.g., `.wav` or `.flac` on your computer), you need to upload them first to obtain a URL that the API can access.

This package provides a utility function, typically found or referenced in the `examples/` directory (like `roex_python.utils.upload_file`), which simplifies this process:

1.  **Upload the File:** Use the utility function (e.g., `url = upload_file(client, "/path/to/local/audio.wav")`). This function handles:
    *   Requesting temporary signed upload credentials from the RoEx API.
    *   Uploading your file securely to cloud storage using these credentials.
    *   Returning the readable URL of the uploaded file.
2.  **Use the URL:** Provide the URL returned by the upload function in the appropriate field (`track_url`, `audio_file_location`, etc.) of the request object for the desired API operation (e.g., `MasteringRequest`, `MultitrackMixRequest`).

**Important:** The core client methods (`client.mix.create_mix_preview`, `client.mastering.create_mastering_preview`, etc.) do **not** automatically upload local files if you provide a path directly in the request model. You **must** perform the upload step first.

Refer to the scripts in the `examples/` directory for complete, runnable demonstrations of this local file workflow, including error handling for uploads.

## Documentation

-   **API Documentation**: For details on the underlying RoEx Tonn API endpoints and parameters, refer to the [Official API Documentation](https://roex.stoplight.io/).
-   **Usage Examples**: Practical examples demonstrating various workflows can be found in the [`examples/`](./examples/) directory. These scripts showcase common use cases and include robust audio validation (checking length, sample rate, silence) before processing.
    -   `mix_example.py`: Demonstrates submitting multiple tracks for AI mixing.
    -   `mastering_example.py`: Shows how to master a single audio file.
    -   `analysis_example.py`: Provides an example of analyzing a mix or master.
    -   `enhance_example.py`: Illustrates enhancing an existing mix.
    -   `audio_cleanup_example.py`: Shows how to use the audio cleanup feature for specific instrument types.
    *Note: Example scripts require the `soundfile` and `numpy` libraries (`pip install soundfile numpy`).*
-   **Package Reference**: Detailed information about the Python classes, methods, and models provided by this package can be found in the docstrings within the source code.

### Example Workflows

#### Multitrack Mixing

```python
from roex_python.client import RoExClient
from roex_python.models import (
    TrackData, MultitrackMixRequest, InstrumentGroup,
    PresenceSetting, PanPreference, ReverbPreference, MusicalStyle
)

client = RoExClient(api_key="your_api_key_here")

# Define tracks
tracks = [
    TrackData(
        track_url="https://example.com/bass.wav",
        instrument_group=InstrumentGroup.BASS_GROUP,
        presence_setting=PresenceSetting.NORMAL,
        pan_preference=PanPreference.CENTRE,
        reverb_preference=ReverbPreference.NONE
    ),
    TrackData(
        track_url="https://example.com/vocals.wav",
        instrument_group=InstrumentGroup.VOCAL_GROUP,
        presence_setting=PresenceSetting.LEAD,
        pan_preference=PanPreference.CENTRE,
        reverb_preference=ReverbPreference.LOW
    ),
    # Add more tracks...
]

# Create mix request
mix_request = MultitrackMixRequest(
    track_data=tracks,
    musical_style=MusicalStyle.POP,
    return_stems=True
)

# Get mix
mix_task = client.mix.create_mix_preview(mix_request)
preview = client.mix.retrieve_preview_mix(mix_task.multitrack_task_id)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository: [https://github.com/roex-audio/roex-python](https://github.com/roex-audio/roex-python)
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## About RoEx 
RoEx offers AI-powered audio production tools and APIs for musicians, producers, and developers. Learn more at [https://roexaudio.com](https://roexaudio.com).
