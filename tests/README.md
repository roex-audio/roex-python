# RoEx Python SDK - Test Suite

This directory contains comprehensive unit and integration tests for the RoEx Python SDK.

## Test Structure

```
tests/
├── unit/                          # Unit tests (no API calls)
│   ├── test_models.py            # Data model tests
│   ├── test_utils.py             # Utility function tests
│   ├── test_api_provider.py      # API provider tests
│   ├── test_client.py            # Main client tests
│   └── test_controllers/         # Controller tests
│       └── test_mastering_controller.py
├── integration/                   # Integration tests (real API calls)
│   ├── test_upload_integration.py
│   ├── test_mastering_integration.py
│   └── test_analysis_integration.py
├── fixtures/                      # Test data
│   └── audio/                    # Test audio files
└── conftest.py                   # Shared fixtures

```

## Prerequisites

### 1. Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. For Integration Tests

Integration tests require:
- A valid RoEx API key
- Test audio files in `tests/fixtures/audio/`

#### Set API Key

```bash
export ROEX_API_KEY="your_api_key_here"
```

#### Add Test Audio Files

Place a small (10-30 second) audio file in `tests/fixtures/audio/test_track.wav`

You can use any WAV file for testing. For best results:
- Duration: 10-30 seconds (faster processing)
- Format: 16-bit or 24-bit WAV
- Sample rate: 44100 Hz or 48000 Hz

## Running Tests

### Quick Start

Run all tests:
```bash
./run_tests.sh all
```

### Unit Tests Only (Fast, No API Calls)

```bash
# Using the script
./run_tests.sh unit

# Or directly with pytest
pytest tests/unit -m unit -v
```

**Expected duration**: < 5 seconds

### Integration Tests Only (Requires API Key)

```bash
# Using the script
./run_tests.sh integration

# Or directly with pytest
export ROEX_API_KEY="your_key_here"
pytest tests/integration -m integration -v
```

**Expected duration**: 5-15 minutes (due to API processing time)

⚠️ **Note**: Integration tests make real API calls and may incur charges.

### Run with Coverage Report

```bash
# Using the script
./run_tests.sh coverage

# Or directly with pytest
pytest tests/unit --cov=roex_python --cov-report=html --cov-report=term
```

Coverage report will be generated in `htmlcov/index.html`

### Run Specific Test File

```bash
pytest tests/unit/test_models.py -v
```

### Run Specific Test Class

```bash
pytest tests/unit/test_models.py::TestMasteringModels -v
```

### Run Specific Test Method

```bash
pytest tests/unit/test_models.py::TestMasteringModels::test_mastering_request_creation -v
```

## Test Markers

Tests are marked with pytest markers for easy filtering:

- `@pytest.mark.unit` - Unit tests (fast, no API calls)
- `@pytest.mark.integration` - Integration tests (real API calls)
- `@pytest.mark.slow` - Slow running tests

Run only fast unit tests:
```bash
pytest -m unit
```

Run integration tests:
```bash
pytest -m integration
```

Skip slow tests:
```bash
pytest -m "not slow"
```

## Writing New Tests

### Unit Test Template

```python
import pytest
from unittest.mock import Mock

@pytest.mark.unit
class TestYourFeature:
    """Test description"""
    
    def test_something(self, mock_api_provider):
        """Test a specific behavior"""
        # Setup
        # ...
        
        # Execute
        # ...
        
        # Assert
        assert result == expected
```

### Integration Test Template

```python
import pytest

@pytest.mark.integration
@pytest.mark.slow
class TestYourFeatureIntegration:
    """Integration test description"""
    
    def test_real_api_call(self, requires_api_key, integration_audio_file):
        """Test with real API"""
        # Setup
        client = RoExClient(api_key=requires_api_key)
        
        # Execute
        # ...
        
        # Assert
        assert result is not None
```

## Common Fixtures

Available in `conftest.py`:

- `api_key` - API key from environment or test key
- `mock_api_provider` - Mocked ApiProvider for unit tests
- `roex_client` - Configured RoExClient instance
- `sample_audio_file` - Temporary test audio file
- `integration_audio_file` - Real audio file for integration tests
- `requires_api_key` - Skip test if no API key available
- `sample_track_data` - Sample track data for mixing tests

## Continuous Integration

For CI/CD pipelines (e.g., GitHub Actions):

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: pytest tests/unit -m unit --cov=roex_python
      
      - name: Run integration tests (main branch only)
        if: github.ref == 'refs/heads/main'
        env:
          ROEX_API_KEY: ${{ secrets.ROEX_API_KEY }}
        run: pytest tests/integration -m integration
```

## Test Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| models/ | 95%+ |
| utils.py | 90%+ |
| api_provider.py | 90%+ |
| controllers/ | 85%+ |
| client.py | 90%+ |
| **Overall** | **85%+** |

## Troubleshooting

### "ROEX_API_KEY not set"

Integration tests require a valid API key:
```bash
export ROEX_API_KEY="your_key_here"
```

### "Integration test audio file not found"

Add a test audio file:
```bash
# Place your audio file
cp your_audio.wav tests/fixtures/audio/test_track.wav
```

### "Module not found" errors

Install the package in development mode:
```bash
pip install -e .
pip install -r requirements-dev.txt
```

### Tests are slow

Run only unit tests for faster feedback:
```bash
pytest tests/unit -m unit
```

## Additional Resources

- [Testing Plan](../TESTING_PLAN.md) - Detailed testing strategy
- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [RoEx API Documentation](https://roex.stoplight.io/)

## Contributing

When adding new features:

1. Write unit tests first (TDD)
2. Ensure all tests pass
3. Add integration tests if applicable
4. Verify coverage remains above 85%
5. Update this README if needed

---

**Last Updated**: 2025-10-17
