#!/bin/bash
# 00-harden-security-base.sh - Test harden -> security -> base flow

set -euo pipefail

# Source common test functions
source "$(dirname "$0")/common.sh"

# Test configuration
SCENARIO_NAME="Harden Security Base Flow"
TEST_HOST="test-server-01"

# Run tests
run_test_suite() {
    log_test "Starting $SCENARIO_NAME tests"
    
    # Test 0: Initial connection test
    log_test "Test 0: Initial SSH connection on port 22"
    if sshpass -p testpass123 ssh -o StrictHostKeyChecking=no -p 2201 root@localhost 'echo "Connected"' &>/dev/null; then
        log_success "Initial SSH connection successful"
    else
        log_error "Initial SSH connection failed"
        return 1
    fi
    
    # Test 1: Harden installation
    log_test "Test 1: Harden installation"
    run_claudia_command "harden" "--install -i inventory/docker-harden.yml -e @vault/test-secrets.yml" || return 1
    
    # Verify SSH port change
    log_test "Verifying SSH port change to 22022..."
    if docker exec ansible-cloudy-${TEST_HOST} ss -tlnp | grep -q ":22022"; then
        log_success "SSH port changed successfully"
    else
        log_error "SSH port change failed"
        return 1
    fi
    
    # Test SSH key auth on new port
    log_test "Testing SSH key auth on port 22022..."
    if ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p 22022 root@172.20.0.10 'echo "Key auth works"' &>/dev/null; then
        log_success "SSH key authentication successful"
    else
        log_error "SSH key authentication failed"
        return 1
    fi
    
    # Test 2: Security installation
    log_test "Test 2: Security installation"
    run_claudia_command "security" "--install -i inventory/docker-harden.yml -e @vault/test-secrets.yml" || return 1
    
    # Verify grunt user creation
    log_test "Verifying grunt user creation..."
    if docker exec ansible-cloudy-${TEST_HOST} id grunt &>/dev/null; then
        log_success "Grunt user created successfully"
    else
        log_error "Grunt user creation failed"
        return 1
    fi
    
    # Verify firewall
    log_test "Verifying firewall configuration..."
    if docker exec ansible-cloudy-${TEST_HOST} ufw status | grep -q "Status: active"; then
        log_success "Firewall is active"
    else
        log_warning "Firewall not active (expected in Docker)"
    fi
    
    # Test 3: Base installation
    log_test "Test 3: Base installation"
    run_claudia_command "base" "--install -i inventory/docker-harden.yml -e @vault/test-secrets.yml" || return 1
    
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
    
    # Test 4: Verify complete flow
    log_test "Test 4: Verifying complete flow"
    
    # SSH as root on secure port
    if ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p 22022 root@172.20.0.10 'echo "Root SSH works"' &>/dev/null; then
        log_success "Root SSH on secure port works"
    else
        log_error "Root SSH on secure port failed"
        return 1
    fi
    
    # SSH as grunt on secure port
    if ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p 22022 grunt@172.20.0.10 'echo "Grunt SSH works"' &>/dev/null; then
        log_success "Grunt SSH on secure port works"
    else
        log_error "Grunt SSH on secure port failed"
        return 1
    fi
    
    log_success "All $SCENARIO_NAME tests passed!"
    return 0
}

# Execute test suite
run_test_suite
exit $?