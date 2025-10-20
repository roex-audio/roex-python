# Testing Guide

## Quick Start

This project has a comprehensive test suite with 119 unit tests and 13 integration tests.

### Running Tests

```bash
# Run all unit tests (fast, no API key needed)
./run_tests.sh unit

# Run with coverage report
./run_tests.sh coverage

# Run specific test file
pytest tests/unit/test_models.py -v

# Run integration tests (requires API key)
export ROEX_API_KEY="your_api_key"
./run_tests.sh integration
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (119 tests, 95% coverage)
│   ├── test_models.py       # Model validation
│   ├── test_utils.py        # Utility functions
│   ├── test_api_provider.py # API communication
│   ├── test_client.py       # Client initialization
│   └── test_controllers/    # Controller logic
│       ├── test_mastering_controller.py
│       ├── test_mix_controller.py
│       ├── test_analysis_controller.py
│       ├── test_enhance_controller.py
│       ├── test_audio_cleanup_controller.py
│       └── test_upload_controller.py
└── integration/             # Integration tests (13 tests)
    ├── test_upload_integration.py
    ├── test_analysis_integration.py
    ├── test_mastering_integration.py
    ├── test_mix_integration.py
    ├── test_enhance_integration.py
    └── test_audio_cleanup_integration.py
```

### Requirements

Install test dependencies:

```bash
pip install -r requirements-dev.txt
```

### Coverage

Current test coverage: **95%** (702/742 lines)

```bash
# Generate coverage report
pytest tests/unit --cov=roex_python --cov-report=html

# View report
open htmlcov/index.html
```

### CI/CD Integration

The test suite is designed for CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements-dev.txt
    pytest tests/unit -v --cov=roex_python
```

### Writing New Tests

1. Unit tests should mock external dependencies
2. Integration tests should use real API calls
3. Follow existing test patterns in the test suite
4. Aim for >80% coverage on new code

For more details, see the docstrings in test files.
