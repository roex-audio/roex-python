#!/bin/bash
# Test execution script for roex-python SDK

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}RoEx Python SDK - Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not found!${NC}"
    echo "Please install test dependencies:"
    echo "  pip install -r requirements-dev.txt"
    exit 1
fi

# Function to run unit tests
run_unit_tests() {
    echo -e "${GREEN}Running Unit Tests (Fast)...${NC}"
    pytest tests/unit -m unit -v --tb=short
    echo ""
}

# Function to run integration tests
run_integration_tests() {
    echo -e "${GREEN}Running Integration Tests (Requires API Key)...${NC}"
    
    # Check for API key
    if [ -z "$ROEX_API_KEY" ]; then
        echo -e "${YELLOW}Warning: ROEX_API_KEY not set!${NC}"
        echo "Integration tests require a valid API key."
        echo "Set it with: export ROEX_API_KEY='your_key_here'"
        echo "Skipping integration tests..."
        return 1
    fi
    
    pytest tests/integration -m integration -v --tb=short --maxfail=3
    echo ""
}

# Function to run tests with coverage
run_with_coverage() {
    echo -e "${GREEN}Running Tests with Coverage...${NC}"
    pytest tests/unit -m unit --cov=roex_python --cov-report=html --cov-report=term
    echo ""
    echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
}

# Parse command line arguments
case "${1:-all}" in
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    coverage)
        run_with_coverage
        ;;
    all)
        run_unit_tests
        if [ -n "$ROEX_API_KEY" ]; then
            read -p "Run integration tests? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_integration_tests
            fi
        fi
        ;;
    *)
        echo "Usage: $0 {unit|integration|coverage|all}"
        echo ""
        echo "Commands:"
        echo "  unit        - Run unit tests only (fast, no API calls)"
        echo "  integration - Run integration tests (requires API key)"
        echo "  coverage    - Run unit tests with coverage report"
        echo "  all         - Run all tests (default)"
        exit 1
        ;;
esac

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Tests Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
