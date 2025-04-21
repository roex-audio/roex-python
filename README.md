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

## Quick Start

```python
import os
from roex_python.client import RoExClient
from roex_python.models import (
    MasteringRequest, MusicalStyle, DesiredLoudness
)

# Get API key from environment variable (Recommended)
api_key = os.getenv("ROEX_API_KEY")
if not api_key:
    raise ValueError("ROEX_API_KEY environment variable not set.")

# Initialize the client with your API key
client = RoExClient(api_key=api_key)

# Create a mastering request
mastering_request = MasteringRequest(
    track_url="https://example.com/track.wav",
    musical_style=MusicalStyle.ROCK_INDIE,
    desired_loudness=DesiredLoudness.MEDIUM,
    sample_rate="44100"
)

# Create mastering preview
task = client.mastering.create_mastering_preview(mastering_request)

# Get the preview (will poll until ready)
preview = client.mastering.retrieve_preview_master(task.mastering_task_id)
print(f"Preview URL: {preview.get('download_url_mastered_preview')}")

# Get the final master
final_url = client.mastering.retrieve_final_master(task.mastering_task_id)
print(f"Final Master URL: {final_url}")
```

## Documentation

-   **API Documentation**: For details on the underlying RoEx Tonn API endpoints and parameters, refer to the [Official API Documentation](https://roex.stoplight.io/).
-   **Usage Examples**: Practical examples demonstrating various workflows can be found in the [`examples/`](./examples/README.md) directory. These scripts showcase common use cases and include robust audio validation (checking length, sample rate, silence) before processing.
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
