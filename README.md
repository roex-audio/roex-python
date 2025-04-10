# RoEx Python

[![PyPI version](https://badge.fury.io/py/roex-mcp.svg)](https://badge.fury.io/py/roex-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python pip package for the [RoEx Tonn API](https://tonn.roexaudio.com) using the MCP (Model-Controller-Provider) architecture pattern. This package provides a clean, type-safe interface to interact with the RoEx Tonn API for audio mixing, mastering, analysis, and enhancement.

## Features

- 🎚️ **Multitrack Mixing**: Submit tracks for professional AI mixing
- 🎛️ **Audio Mastering**: Master individual tracks or entire albums
- 📊 **Mix Analysis**: Analyze and compare audio mixes
- 🔧 **Mix Enhancement**: Enhance and improve existing mixes
- 🔄 **Asynchronous Processing**: Built-in polling for long-running tasks
- 📥 **File Downloads**: Easily download processed audio files

## Installation

```bash
pip install roex-mcp
```

## Quick Start

```python
from roex_mcp.client import RoExClient
from roex_mcp.models import (
    MasteringRequest, MusicalStyle, DesiredLoudness
)

# Initialize the client with your API key
client = RoExClient(api_key="your_api_key_here")

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

For full documentation, including API reference and examples, visit:
[https://docs.tonn.roexaudio.com/api](https://docs.tonn.roexaudio.com/api)

### Example Workflows

#### Multitrack Mixing

```python
from roex_mcp.client import RoExClient
from roex_mcp.models import (
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

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## About RoEx 
RoEx offers AI-powered audio production tools and APIs for musicians, producers, and developers. Learn more at [https://roexaudio.com](https://roexaudio.com).
