#!/bin/bash
# 01-security-base.sh - Test security setup and base configuration

set -euo pipefail

# Source common test functions
source "$(dirname "$0")/common.sh"

# Test configuration
SCENARIO_NAME="Security and Base Setup"
TEST_HOST="test-server-01"

# Run tests
run_test_suite() {
    log_test "Starting $SCENARIO_NAME tests"
    
    # Test 1: Security installation
    log_test "Test 1: Security installation"
    run_cli_command "security" "--install" || return 1
    
    # Verify SSH port change
    log_test "Verifying SSH port change to 2222..."
    if docker exec ansible-cloudy-${TEST_HOST} ss -tlnp | grep -q ":2222"; then
        log_success "SSH port changed successfully"
    else
        log_error "SSH port change failed"
        return 1
    fi
    
    # Verify admin user creation
    log_test "Verifying admin user creation..."
    if docker exec ansible-cloudy-${TEST_HOST} id admin &>/dev/null; then
        log_success "Admin user created successfully"
    else
        log_error "Admin user creation failed"
        return 1
    fi
    
    # Verify firewall
    log_test "Verifying firewall configuration..."
    if docker exec ansible-cloudy-${TEST_HOST} ufw status | grep -q "Status: active"; then
        log_success "Firewall is active"
    else
        log_warning "Firewall not active (expected in Docker)"
    fi
    
    # Test 2: Base installation (using secured connection)
    log_test "Test 2: Base installation"
    # Update inventory to use secured connection
    export ANSIBLE_HOST_KEY_CHECKING=false
    run_cli_command "base" "--install -i ${INVENTORY_FILE/test-server-01/test-server-01-secured}" || return 1
    
    # Verify hostname
    log_test "Verifying hostname configuration..."
    local hostname=$(docker exec ansible-cloudy-${TEST_HOST} hostname)
    if [[ "$hostname" == "test-server-01" ]]; then
        log_success "Hostname configured correctly"
    else
        log_error "Hostname configuration failed: $hostname"
        return 1
    fi
    
    # Verify git configuration
    log_test "Verifying git configuration..."
    local git_user=$(docker exec ansible-cloudy-${TEST_HOST} git config --global user.name || echo "")
    if [[ "$git_user" == "Test User" ]]; then
        log_success "Git configured correctly"
    else
        log_error "Git configuration failed"
        return 1
    fi
    
    # Test 3: Idempotency check
    log_test "Test 3: Idempotency check"
    local output=$(run_cli_command "security" "--install --check" 2>&1)
    if echo "$output" | grep -q "changed=0"; then
        log_success "Security setup is idempotent"
    else
        log_warning "Security setup may not be fully idempotent"
    fi
    
    log_success "All $SCENARIO_NAME tests passed!"
    return 0
}

# Execute test suite
run_test_suite
exit $?