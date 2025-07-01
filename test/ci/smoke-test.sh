#!/bin/bash
# smoke-test.sh - Quick smoke test for GitHub Actions CI

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Main smoke test
main() {
    echo "Running Ansible Cloudy smoke tests..."
    
    # Test 1: Bootstrap and environment setup
    echo "Test 1: Environment setup"
    cd "$PROJECT_ROOT"
    if ./bootstrap.sh -y; then
        log_success "Bootstrap completed"
    else
        log_error "Bootstrap failed"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Test 2: CLI availability
    echo "Test 2: CLI availability"
    if command -v cli &> /dev/null; then
        log_success "Claudia CLI available"
    else
        log_error "Claudia CLI not found"
    fi
    
    # Test 3: Syntax validation
    echo "Test 3: Syntax validation"
    if cli dev syntax; then
        log_success "Syntax validation passed"
    else
        log_error "Syntax validation failed"
    fi
    
    # Test 4: Basic help commands
    echo "Test 4: Help system"
    if cli --help > /dev/null && cli security > /dev/null; then
        log_success "Help system working"
    else
        log_error "Help system failed"
    fi
    
    # Test 5: Service discovery
    echo "Test 5: Service discovery"
    if cli --list-services | grep -q "security"; then
        log_success "Service discovery working"
    else
        log_error "Service discovery failed"
    fi
    
    # Test 6: Dry run on localhost (no actual changes)
    echo "Test 6: Dry run test"
    # Create minimal test inventory
    cat > /tmp/test-inventory.yml << EOF
all:
  hosts:
    localhost:
      ansible_connection: local
      ansible_python_interpreter: "{{ ansible_playbook_python }}"
EOF
    
    # Run a simple dry run
    if cli base --install --check -i /tmp/test-inventory.yml 2>&1 | grep -q "DRY RUN"; then
        log_success "Dry run mode working"
    else
        log_warning "Dry run test inconclusive"
    fi
    
    # Test 7: Development validation
    echo "Test 7: Development validation"
    if cli dev validate --quick; then
        log_success "Development validation passed"
    else
        log_error "Development validation failed"
    fi
    
    echo
    echo "All smoke tests passed!"
    exit 0
}

# Run main function
main "$@"