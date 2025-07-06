#!/bin/bash
# run-e2e-tests.sh - Main E2E test orchestrator for Ansible Cloudy

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCENARIOS_DIR="$SCRIPT_DIR/scenarios"
INVENTORY_DIR="$SCRIPT_DIR/inventory"
VAULT_FILE="$SCRIPT_DIR/vault/test-secrets.yml"

# Default settings
TEST_MODE="quick"
OS_TYPE="ubuntu"
KEEP_CONTAINERS=false
GENERATE_REPORT=false
DEBUG_MODE=false
SEQUENTIAL=false
SPECIFIC_SCENARIO=""
CONTAINER_PREFIX="ansible-cloudy"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
declare -A TEST_RESULTS
TESTS_PASSED=0
TESTS_FAILED=0

# Help function
show_help() {
    cat << EOF
E2E Test Runner for Ansible Cloudy

Usage: $0 [OPTIONS]

Test Modes:
    --quick             Run quick tests (~5 minutes) [default]
    --standard          Run standard tests (~15 minutes)
    --full              Run full test suite (~30 minutes)
    --scenario NAME     Run specific scenario (e.g., 02-database)

Options:
    --os TYPE           OS to test (ubuntu|debian) [default: ubuntu]
    --keep              Keep containers running after tests
    --report            Generate HTML test report
    --debug             Enable debug output
    --sequential        Run tests sequentially (default: parallel)
    --cleanup           Remove all test containers before starting
    --help              Show this help message

Examples:
    $0 --quick                          # Quick test run
    $0 --standard --os debian           # Standard tests on Debian
    $0 --full --report                  # Full tests with report
    $0 --scenario 02-database --debug   # Debug specific scenario

EOF
    exit 0
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                TEST_MODE="quick"
                shift
                ;;
            --standard)
                TEST_MODE="standard"
                shift
                ;;
            --full)
                TEST_MODE="full"
                shift
                ;;
            --scenario)
                SPECIFIC_SCENARIO="$2"
                shift 2
                ;;
            --os)
                OS_TYPE="$2"
                shift 2
                ;;
            --keep)
                KEEP_CONTAINERS=true
                shift
                ;;
            --report)
                GENERATE_REPORT=true
                shift
                ;;
            --debug)
                DEBUG_MODE=true
                shift
                ;;
            --sequential)
                SEQUENTIAL=true
                shift
                ;;
            --cleanup)
                cleanup_containers
                exit 0
                ;;
            --help|-h)
                show_help
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                show_help
                ;;
        esac
    done
}

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check Python environment
    if [[ ! -f "$PROJECT_ROOT/.venv/bin/activate" ]]; then
        log_warning "Virtual environment not found. Running bootstrap..."
        cd "$PROJECT_ROOT"
        ./bootstrap.sh -y
    fi
    
    # Activate virtual environment
    source "$PROJECT_ROOT/.venv/bin/activate"
    
    # Verify CLI
    if ! command -v cli &> /dev/null; then
        log_error "CLI not found in virtual environment"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Cleanup existing containers
cleanup_containers() {
    log_info "Cleaning up existing test containers..."
    cd "$SCRIPT_DIR"
    docker compose down -v --remove-orphans || true
    docker ps -a | grep "$CONTAINER_PREFIX" | awk '{print $1}' | xargs -r docker rm -f || true
    log_success "Cleanup complete"
}

# Start Docker containers
start_containers() {
    local inventory_type="$1"
    log_info "Starting Docker containers for $inventory_type testing..."
    
    cd "$SCRIPT_DIR"
    
    # Select which services to start based on test mode
    case "$inventory_type" in
        single)
            docker compose up -d test-server-01
            ;;
        multi)
            docker compose up -d web-01 web-02 db-01 cache-01 lb-01
            ;;
        full)
            docker compose up -d
            ;;
    esac
    
    # Wait for containers to be ready
    log_info "Waiting for containers to initialize..."
    sleep 10
    
    # Verify SSH connectivity
    local containers=$(docker compose ps -q)
    for container in $containers; do
        local container_name=$(docker inspect -f '{{.Name}}' "$container" | sed 's/^\/\+//')
        log_info "Checking SSH on $container_name..."
        
        local max_attempts=30
        local attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if docker exec "$container" service ssh status | grep -q "running"; then
                log_success "SSH ready on $container_name"
                break
            fi
            attempt=$((attempt + 1))
            sleep 2
        done
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "SSH failed to start on $container_name"
            return 1
        fi
    done
    
    log_success "All containers ready"
}

# Run a test scenario
run_scenario() {
    local scenario_name="$1"
    local inventory_file="$2"
    local scenario_script="$SCENARIOS_DIR/$scenario_name"
    
    if [[ ! -f "$scenario_script" ]]; then
        log_error "Scenario script not found: $scenario_script"
        return 1
    fi
    
    log_info "Running scenario: $scenario_name"
    
    # Make scenario executable
    chmod +x "$scenario_script"
    
    # Run scenario with proper environment
    if $DEBUG_MODE; then
        ANSIBLE_VERBOSITY=2 \
        INVENTORY_FILE="$inventory_file" \
        VAULT_FILE="$VAULT_FILE" \
        PROJECT_ROOT="$PROJECT_ROOT" \
        DEBUG=true \
        "$scenario_script"
    else
        INVENTORY_FILE="$inventory_file" \
        VAULT_FILE="$VAULT_FILE" \
        PROJECT_ROOT="$PROJECT_ROOT" \
        "$scenario_script" 2>&1 | tee "/tmp/test-$scenario_name.log"
    fi
    
    local exit_code=$?
    
    # Record result
    if [ $exit_code -eq 0 ]; then
        TEST_RESULTS["$scenario_name"]="PASSED"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_success "Scenario $scenario_name: PASSED"
    else
        TEST_RESULTS["$scenario_name"]="FAILED"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_error "Scenario $scenario_name: FAILED"
    fi
    
    return $exit_code
}

# Get scenarios for test mode
get_scenarios() {
    case "$TEST_MODE" in
        quick)
            echo "01-security-base.sh"
            ;;
        standard)
            echo "01-security-base.sh 02-database.sh 03-web-stack.sh 04-cache.sh"
            ;;
        full)
            echo "01-security-base.sh 02-database.sh 03-web-stack.sh 04-cache.sh 05-advanced.sh 06-full-stack.sh"
            ;;
    esac
}

# Get inventory file for test mode
get_inventory() {
    case "$TEST_MODE" in
        quick)
            echo "$INVENTORY_DIR/docker-single.yml"
            ;;
        standard)
            echo "$INVENTORY_DIR/docker-multi.yml"
            ;;
        full)
            echo "$INVENTORY_DIR/docker-full.yml"
            ;;
    esac
}

# Generate test report
generate_report() {
    local report_file="/tmp/ansible-cloudy-test-report.html"
    log_info "Generating test report..."
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Ansible Cloudy E2E Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .summary { background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .passed { color: green; font-weight: bold; }
        .failed { color: red; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .test-passed { background-color: #d4edda; }
        .test-failed { background-color: #f8d7da; }
    </style>
</head>
<body>
    <h1>Ansible Cloudy E2E Test Report</h1>
    <div class="summary">
        <h2>Test Summary</h2>
        <p>Test Mode: <strong>$TEST_MODE</strong></p>
        <p>OS Type: <strong>$OS_TYPE</strong></p>
        <p>Date: <strong>$(date)</strong></p>
        <p>Total Tests: <strong>$((TESTS_PASSED + TESTS_FAILED))</strong></p>
        <p class="passed">Passed: $TESTS_PASSED</p>
        <p class="failed">Failed: $TESTS_FAILED</p>
    </div>
    
    <h2>Test Results</h2>
    <table>
        <tr>
            <th>Scenario</th>
            <th>Status</th>
            <th>Log File</th>
        </tr>
EOF

    for scenario in "${!TEST_RESULTS[@]}"; do
        local status="${TEST_RESULTS[$scenario]}"
        local css_class="test-passed"
        if [[ "$status" == "FAILED" ]]; then
            css_class="test-failed"
        fi
        
        cat >> "$report_file" << EOF
        <tr class="$css_class">
            <td>$scenario</td>
            <td>$status</td>
            <td><a href="file:///tmp/test-$scenario.log">View Log</a></td>
        </tr>
EOF
    done

    cat >> "$report_file" << EOF
    </table>
</body>
</html>
EOF

    log_success "Test report generated: $report_file"
    
    # Try to open in browser if available
    if command -v open &> /dev/null; then
        open "$report_file"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "$report_file"
    fi
}

# Main test execution
main() {
    parse_args "$@"
    
    log_info "Starting Ansible Cloudy E2E Tests"
    log_info "Test mode: $TEST_MODE"
    log_info "OS type: $OS_TYPE"
    
    # Check prerequisites
    check_prerequisites
    
    # Cleanup if not keeping containers
    if ! $KEEP_CONTAINERS; then
        cleanup_containers
    fi
    
    # Determine container configuration
    local container_type="single"
    case "$TEST_MODE" in
        standard)
            container_type="multi"
            ;;
        full)
            container_type="full"
            ;;
    esac
    
    # Start containers
    if ! start_containers "$container_type"; then
        log_error "Failed to start containers"
        exit 1
    fi
    
    # Get test configuration
    local inventory_file=$(get_inventory)
    local scenarios=""
    
    if [[ -n "$SPECIFIC_SCENARIO" ]]; then
        scenarios="$SPECIFIC_SCENARIO"
    else
        scenarios=$(get_scenarios)
    fi
    
    # Run scenarios
    if $SEQUENTIAL; then
        log_info "Running tests sequentially..."
        for scenario in $scenarios; do
            run_scenario "$scenario" "$inventory_file" || true
        done
    else
        log_info "Running tests in parallel..."
        for scenario in $scenarios; do
            run_scenario "$scenario" "$inventory_file" &
        done
        wait
    fi
    
    # Summary
    echo
    log_info "Test Summary:"
    log_info "Tests Passed: $TESTS_PASSED"
    log_info "Tests Failed: $TESTS_FAILED"
    
    # Generate report if requested
    if $GENERATE_REPORT; then
        generate_report
    fi
    
    # Cleanup or keep containers
    if $KEEP_CONTAINERS; then
        log_info "Containers kept running. Use 'docker compose down' to stop them."
    else
        cleanup_containers
    fi
    
    # Exit with appropriate code
    if [ $TESTS_FAILED -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

# Run main function
main "$@"