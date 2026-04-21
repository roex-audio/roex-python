# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2026-04-21

### Fixed
- Aligned `EnhanceMusicalStyle` enum with server — replaced incorrect values with 18 correct styles (e.g. `ROCK_INDIE`, `GRITTY_CRUNCHY`, `BALANCED`)
- Aligned `AnalysisMusicalStyle` enum with server — removed `DANCE`, added 9 mood-based styles (`AIRY_EXPANSIVE`, `AGGRESSIVE`, `BRIGHT`, etc.)
- Renamed `SoundSource.BACKING_VOCALS_GROUP` to `BACKING_VOX_GROUP` to match server
- Added missing `SoundSource.BRASS_GROUP` enum member
- Added missing `LoudnessPreference.NO_CHANGE` enum member
- Changed `MixEnhanceRequest.loudness_preference` default from `STREAMING_LOUDNESS` to `NO_CHANGE` to match server default
- Removed `MixEnhanceRequest.fix_drc_issues` field (not supported by server)
- Mix preview and enhance payloads now always include `webhookURL` as a string (empty string if unset), preventing server rejection
- Added `tenacity` to `install_requires` / `dependencies` — was imported but missing from package metadata, causing `ModuleNotFoundError` at import time

### Added
- `MixEnhanceRequest.get_processed_stems` field for requesting separated stems from enhancement
- `MixEnhanceRequest.apply_drum_enhancement` and `apply_vocal_enhancement` fields (required by server)

### Changed
- Updated examples, docstrings, and README to reflect all model and enum changes

## [1.3.0] - 2025-10-30

### Added
- **Advanced Audio Effects Processing**: New comprehensive audio effects system for final mix retrieval
  - **6-Band Parametric EQ**: Full parametric EQ with per-band gain (-20 to +20 dB), Q factor (0.1 to 10.0), and centre frequency (20 Hz to 20 kHz) control
  - **Dynamic Range Compression**: Professional compression with threshold, ratio, attack, and release controls
  - **Stereo Panning**: Precise stereo positioning with -60? to +60? range
  - **Effect Presets**: Built-in professional presets for common use cases:
    - EQ Presets: `preset_bass_boost()`, `preset_vocal_clarity()`, `preset_kick_punch()`, `preset_snare_crack()`, `preset_high_pass()`, `preset_brightness()`
    - Compression Presets: `preset_vocal()`, `preset_bass()`, `preset_drum_bus()`, `preset_gentle()`, `preset_aggressive()`
    - Panning Presets: `center()`, `hard_left()`, `hard_right()`, `slight_left()`, `slight_right()`
- **New Models**:
  - `EQBandSettings`: Individual EQ band configuration
  - `EQSettings`: 6-band parametric EQ container
  - `CompressionSettings`: Dynamic range compression configuration
  - `PanningSettings`: Stereo panning control
  - `TrackEffectsData`: Advanced track data with all effects
  - `FinalMixRequestAdvanced`: Enhanced final mix request with audio effects
- **New Controller Method**: `retrieve_final_mix_advanced()` for applying advanced audio effects to final mixes
- **Track Count Validation**: Client-side validation enforcing 2-32 track limit for mix preview requests (API requirement)
- **Comprehensive Example**: `examples/advanced_mix_example.py` demonstrating full advanced audio effects workflow with preset showcase mode (`--show-examples`)

### Changed
- Updated `RoExClient` docstring to document advanced mixing features
- Enhanced error handling in mix controller with proper `HTTPError` attribute checking
- Improved test coverage to 95% with 119 unit tests and 13 integration tests

### Fixed
- Fixed test assertion in `test_mix_controller.py` to match actual error message format
- Corrected webhook URL documentation in examples to clarify test URL usage
- Fixed pre-existing test failures related to error message matching

### Documentation
- Added comprehensive docstrings for all new audio effects classes and methods
- Updated `examples/README.md` with advanced audio effects usage
- Added parameter range documentation and validation rules
- Included workflow examples for preset-based and custom effects configuration

## [1.2.1] - 2024-XX-XX

### Changed
- Various bug fixes and improvements
- Documentation enhancements

## [1.2.0] - 2024-XX-XX

### Added
- Sphinx documentation
- Comprehensive test suite with pytest
- Retry logic for API requests

### Changed
- Enhanced documentation throughout codebase
- Improved error handling

## [1.1.1] - 2024-XX-XX

### Fixed
- Minor bug fixes

## [1.1.0] - 2024-XX-XX

### Added
- Additional features and improvements

## [1.0.0] - 2024-XX-XX

### Added
- Initial release
- Core RoEx Tonn API client functionality
- Multitrack mixing support
- Audio mastering capabilities
- Mix analysis features
- Mix enhancement tools
- Audio cleanup functionality
- Asynchronous task polling
- Secure file upload/download

[1.3.1]: https://github.com/roexaudio/roex-python/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/roexaudio/roex-python/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/roexaudio/roex-python/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/roexaudio/roex-python/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/roexaudio/roex-python/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/roexaudio/roex-python/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/roexaudio/roex-python/releases/tag/v1.0.0
