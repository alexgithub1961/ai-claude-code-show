#!/bin/bash

# VanEck ETF Downloader Test Script
# This script sets up the test environment, runs pytest with coverage, and generates reports

set -euo pipefail  # Exit on error, undefined variables, and pipe failures

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_PATH="${PROJECT_ROOT}/.venv"
COVERAGE_DIR="${PROJECT_ROOT}/htmlcov"
REPORTS_DIR="${PROJECT_ROOT}/test-reports"
MIN_COVERAGE=90

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colour

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to print usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -h, --help          Show this help message
    -v, --verbose       Run tests in verbose mode
    -k EXPRESSION       Run only tests matching EXPRESSION
    -m MARKERS          Run only tests with specified markers (e.g., "not slow")
    --cov-fail          Fail if coverage is below minimum threshold
    --no-cov            Skip coverage reporting
    --integration       Run integration tests (requires network)
    --unit              Run only unit tests
    --clean             Clean test artifacts before running
    --parallel          Run tests in parallel (requires pytest-xdist)
    --html              Generate HTML coverage report
    --xml               Generate XML coverage report for CI

Examples:
    $0                              # Run all tests with coverage
    $0 --unit                       # Run only unit tests
    $0 --integration                # Run integration tests
    $0 -m "not slow"                # Skip slow tests
    $0 -k "test_download"           # Run tests matching pattern
    $0 --parallel --html            # Run in parallel with HTML report
EOF
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup virtual environment
setup_venv() {
    log_info "Setting up virtual environment..."
    
    if [[ ! -d "$VENV_PATH" ]]; then
        log_info "Creating virtual environment at $VENV_PATH"
        python3 -m venv "$VENV_PATH"
    fi
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    
    # Upgrade pip and install dependencies
    log_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -e "$PROJECT_ROOT[dev]"
    
    log_success "Virtual environment ready"
}

# Function to check test dependencies
check_dependencies() {
    log_info "Checking test dependencies..."
    
    local missing_deps=()
    local python_modules=("pytest" "pytest_cov" "pytest_mock" "pytest_asyncio")
    
    for module in "${python_modules[@]}"; do
        if ! python -c "import ${module}" 2>/dev/null; then
            missing_deps+=("$module")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Run: pip install -e .[dev] to install missing dependencies"
        return 1
    fi
    
    log_success "All dependencies are available"
    return 0
}

# Function to clean test artifacts
clean_artifacts() {
    log_info "Cleaning test artifacts..."
    
    # Remove coverage files
    rm -rf "$PROJECT_ROOT/.coverage"
    rm -rf "$PROJECT_ROOT/.coverage.*"
    rm -rf "$COVERAGE_DIR"
    
    # Remove pytest cache
    rm -rf "$PROJECT_ROOT/.pytest_cache"
    rm -rf "$PROJECT_ROOT/**/__pycache__"
    
    # Remove test reports
    rm -rf "$REPORTS_DIR"
    
    # Remove temporary test files
    find "$PROJECT_ROOT" -name "*.pyc" -delete
    find "$PROJECT_ROOT" -name "*.pyo" -delete
    find "$PROJECT_ROOT" -name "*~" -delete
    
    log_success "Test artifacts cleaned"
}

# Function to create test reports directory
setup_reports_dir() {
    mkdir -p "$REPORTS_DIR"
    log_info "Test reports will be saved to: $REPORTS_DIR"
}

# Function to run linting
run_linting() {
    log_info "Running code linting..."
    
    # Run black check
    if command_exists black; then
        log_info "Checking code formatting with black..."
        if ! black --check --diff "$PROJECT_ROOT/src" "$PROJECT_ROOT/tests"; then
            log_warning "Code formatting issues found. Run 'black src tests' to fix."
        else
            log_success "Code formatting is correct"
        fi
    fi
    
    # Run isort check
    if command_exists isort; then
        log_info "Checking import sorting with isort..."
        if ! isort --check-only --diff "$PROJECT_ROOT/src" "$PROJECT_ROOT/tests"; then
            log_warning "Import sorting issues found. Run 'isort src tests' to fix."
        else
            log_success "Import sorting is correct"
        fi
    fi
    
    # Run flake8
    if command_exists flake8; then
        log_info "Running flake8 linting..."
        if ! flake8 "$PROJECT_ROOT/src" "$PROJECT_ROOT/tests"; then
            log_warning "Flake8 linting issues found"
        else
            log_success "Flake8 linting passed"
        fi
    fi
    
    # Run mypy type checking
    if command_exists mypy; then
        log_info "Running mypy type checking..."
        if ! mypy "$PROJECT_ROOT/src"; then
            log_warning "Type checking issues found"
        else
            log_success "Type checking passed"
        fi
    fi
}

# Function to build pytest command
build_pytest_cmd() {
    local pytest_cmd="pytest"
    local pytest_args=()
    
    # Base configuration
    pytest_args+=("--tb=short")
    pytest_args+=("--strict-markers")
    pytest_args+=("--strict-config")
    
    # Add coverage if not disabled
    if [[ "$NO_COVERAGE" != "true" ]]; then
        pytest_args+=("--cov=src")
        pytest_args+=("--cov-report=term-missing")
        pytest_args+=("--cov-report=html:$COVERAGE_DIR")
        
        if [[ "$XML_REPORT" == "true" ]]; then
            pytest_args+=("--cov-report=xml:$REPORTS_DIR/coverage.xml")
        fi
        
        if [[ "$COV_FAIL" == "true" ]]; then
            pytest_args+=("--cov-fail-under=$MIN_COVERAGE")
        fi
    fi
    
    # Add JUnit XML report for CI
    pytest_args+=("--junitxml=$REPORTS_DIR/junit.xml")
    
    # Add verbose mode
    if [[ "$VERBOSE" == "true" ]]; then
        pytest_args+=("-v")
    fi
    
    # Add parallel execution
    if [[ "$PARALLEL" == "true" ]] && command_exists pytest-xdist; then
        pytest_args+=("-n" "auto")
    fi
    
    # Add test selection
    if [[ -n "$TEST_MARKERS" ]]; then
        pytest_args+=("-m" "$TEST_MARKERS")
    fi
    
    if [[ -n "$TEST_EXPRESSION" ]]; then
        pytest_args+=("-k" "$TEST_EXPRESSION")
    fi
    
    # Test directory selection
    if [[ "$UNIT_ONLY" == "true" ]]; then
        pytest_args+=("tests/test_*.py")
        pytest_args+=("-m" "not integration")
    elif [[ "$INTEGRATION_ONLY" == "true" ]]; then
        pytest_args+=("tests/test_integration.py")
    else
        pytest_args+=("tests/")
    fi
    
    echo "$pytest_cmd ${pytest_args[*]}"
}

# Function to run pytest
run_pytest() {
    local pytest_cmd
    pytest_cmd=$(build_pytest_cmd)
    
    log_info "Running pytest with command: $pytest_cmd"
    log_info "Working directory: $PROJECT_ROOT"
    
    cd "$PROJECT_ROOT"
    
    # Set environment variables for testing
    export PYTHONPATH="${PROJECT_ROOT}/src:${PYTHONPATH:-}"
    export VANECK_LOG_LEVEL="DEBUG"
    export VANECK_DOWNLOAD_DIR="/tmp/vaneck_test_downloads"
    
    # Run pytest
    if eval "$pytest_cmd"; then
        log_success "All tests passed!"
        return 0
    else
        log_error "Some tests failed!"
        return 1
    fi
}

# Function to generate test summary
generate_summary() {
    log_info "Generating test summary..."
    
    local summary_file="$REPORTS_DIR/test_summary.txt"
    
    {
        echo "VanEck ETF Downloader Test Summary"
        echo "=================================="
        echo "Generated: $(date)"
        echo "Project: $PROJECT_ROOT"
        echo ""
        
        if [[ -f "$REPORTS_DIR/junit.xml" ]]; then
            echo "JUnit Results:"
            python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('$REPORTS_DIR/junit.xml')
    root = tree.getroot()
    print(f'  Total tests: {root.get(\"tests\", \"N/A\")}')
    print(f'  Failures: {root.get(\"failures\", \"N/A\")}')
    print(f'  Errors: {root.get(\"errors\", \"N/A\")}')
    print(f'  Skipped: {root.get(\"skipped\", \"N/A\")}')
    print(f'  Time: {root.get(\"time\", \"N/A\")}s')
except Exception as e:
    print(f'  Error parsing JUnit XML: {e}')
"
            echo ""
        fi
        
        if [[ -f "$PROJECT_ROOT/.coverage" && "$NO_COVERAGE" != "true" ]]; then
            echo "Coverage Summary:"
            coverage report --show-missing 2>/dev/null || echo "  Coverage data not available"
            echo ""
        fi
        
        echo "Reports Location: $REPORTS_DIR"
        if [[ -d "$COVERAGE_DIR" ]]; then
            echo "HTML Coverage Report: $COVERAGE_DIR/index.html"
        fi
        
    } > "$summary_file"
    
    # Display summary
    cat "$summary_file"
    log_success "Test summary saved to: $summary_file"
}

# Function to check coverage threshold
check_coverage() {
    if [[ "$NO_COVERAGE" == "true" ]]; then
        return 0
    fi
    
    if [[ ! -f "$PROJECT_ROOT/.coverage" ]]; then
        log_warning "No coverage data found"
        return 0
    fi
    
    log_info "Checking coverage threshold..."
    
    # Get coverage percentage
    local coverage_percent
    coverage_percent=$(coverage report | grep "^TOTAL" | awk '{print $4}' | sed 's/%//')
    
    if [[ -n "$coverage_percent" ]]; then
        log_info "Current coverage: ${coverage_percent}%"
        
        if (( $(echo "$coverage_percent >= $MIN_COVERAGE" | bc -l) )); then
            log_success "Coverage meets minimum threshold of ${MIN_COVERAGE}%"
            return 0
        else
            log_error "Coverage ${coverage_percent}% is below minimum threshold of ${MIN_COVERAGE}%"
            if [[ "$COV_FAIL" == "true" ]]; then
                return 1
            fi
        fi
    else
        log_warning "Could not determine coverage percentage"
    fi
    
    return 0
}

# Main execution function
main() {
    # Default values
    VERBOSE="false"
    TEST_MARKERS=""
    TEST_EXPRESSION=""
    COV_FAIL="false"
    NO_COVERAGE="false"
    INTEGRATION_ONLY="false"
    UNIT_ONLY="false"
    CLEAN_ARTIFACTS="false"
    PARALLEL="false"
    HTML_REPORT="false"
    XML_REPORT="false"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -k)
                TEST_EXPRESSION="$2"
                shift 2
                ;;
            -m)
                TEST_MARKERS="$2"
                shift 2
                ;;
            --cov-fail)
                COV_FAIL="true"
                shift
                ;;
            --no-cov)
                NO_COVERAGE="true"
                shift
                ;;
            --integration)
                INTEGRATION_ONLY="true"
                shift
                ;;
            --unit)
                UNIT_ONLY="true"
                shift
                ;;
            --clean)
                CLEAN_ARTIFACTS="true"
                shift
                ;;
            --parallel)
                PARALLEL="true"
                shift
                ;;
            --html)
                HTML_REPORT="true"
                shift
                ;;
            --xml)
                XML_REPORT="true"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Validate mutually exclusive options
    if [[ "$INTEGRATION_ONLY" == "true" && "$UNIT_ONLY" == "true" ]]; then
        log_error "Cannot specify both --integration and --unit"
        exit 1
    fi
    
    log_info "Starting VanEck ETF Downloader test suite..."
    log_info "Project root: $PROJECT_ROOT"
    
    # Change to project directory
    cd "$PROJECT_ROOT"
    
    # Clean artifacts if requested
    if [[ "$CLEAN_ARTIFACTS" == "true" ]]; then
        clean_artifacts
    fi
    
    # Setup reports directory
    setup_reports_dir
    
    # Setup virtual environment
    setup_venv
    
    # Check dependencies
    if ! check_dependencies; then
        exit 1
    fi
    
    # Run linting (optional, doesn't fail tests)
    run_linting
    
    # Run tests
    local test_exit_code=0
    if ! run_pytest; then
        test_exit_code=1
    fi
    
    # Check coverage threshold
    if ! check_coverage; then
        test_exit_code=1
    fi
    
    # Generate summary
    generate_summary
    
    # Final status
    if [[ $test_exit_code -eq 0 ]]; then
        log_success "All tests completed successfully!"
    else
        log_error "Tests completed with failures!"
    fi
    
    exit $test_exit_code
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi