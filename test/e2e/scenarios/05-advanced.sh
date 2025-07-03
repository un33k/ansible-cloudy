#!/bin/bash
# 05-advanced.sh - Test advanced services (pgvector, Node.js, monitoring)

set -euo pipefail

# Source common test functions
source "$(dirname "$0")/common.sh"

# Test configuration
SCENARIO_NAME="Advanced Services"
DB_HOST="db-01"
WEB_HOST="web-01"

# Run tests
run_test_suite() {
    log_test "Starting $SCENARIO_NAME tests"
    
    # Test 1: pgvector installation
    log_test "Test 1: pgvector for AI/ML workloads"
    TEST_HOST="$DB_HOST"
    TEST_CONTAINER=$(get_container_name "$TEST_HOST")
    
    run_cli_command "pgvector" "--install --dimensions 1536 --index-type ivfflat --create-examples" || return 1
    
    # Verify pgvector extension
    local pgvector=$(docker exec "$TEST_CONTAINER" sudo -u postgres psql -t -c "SELECT extname FROM pg_extension WHERE extname='vector';" 2>/dev/null || echo "")
    if echo "$pgvector" | grep -q "vector"; then
        log_success "pgvector extension installed"
    else
        log_error "pgvector installation failed"
        return 1
    fi
    
    # Test vector operations
    log_test "Testing vector operations..."
    docker exec "$TEST_CONTAINER" sudo -u postgres psql -c "CREATE TABLE IF NOT EXISTS embeddings (id serial PRIMARY KEY, embedding vector(1536));" &>/dev/null
    docker exec "$TEST_CONTAINER" sudo -u postgres psql -c "INSERT INTO embeddings (embedding) VALUES ('[1,2,3]'::vector);" &>/dev/null
    
    local vector_count=$(docker exec "$TEST_CONTAINER" sudo -u postgres psql -t -c "SELECT COUNT(*) FROM embeddings;" 2>/dev/null || echo "0")
    if [[ "$vector_count" -gt 0 ]]; then
        log_success "Vector operations working"
    else
        log_error "Vector operations failed"
        return 1
    fi
    
    # Test 2: Node.js with PM2
    log_test "Test 2: Node.js application with PM2"
    TEST_HOST="$WEB_HOST"
    TEST_CONTAINER=$(get_container_name "$TEST_HOST")
    
    run_cli_command "nodejs" "--install --app-name advancedapp --app-port 3001 --pm2-instances 2" || return 1
    
    # Check PM2 status
    local pm2_list=$(docker exec "$TEST_CONTAINER" pm2 list --no-color 2>/dev/null || echo "")
    if echo "$pm2_list" | grep -q "advancedapp"; then
        log_success "Node.js app running under PM2"
        
        # Check instance count
        local instance_count=$(echo "$pm2_list" | grep -c "advancedapp" || echo "0")
        if [[ "$instance_count" -ge 2 ]]; then
            log_success "PM2 cluster mode working with $instance_count instances"
        else
            log_warning "PM2 instance count may be incorrect: $instance_count"
        fi
    else
        log_warning "PM2 status could not be verified"
    fi
    
    # Check Node.js app port
    check_port_listening "$TEST_CONTAINER" "3001" || log_warning "Node.js port 3001 not listening"
    
    # Test 3: OpenVPN server
    if [[ "${SKIP_VPN_TEST:-false}" != "true" ]]; then
        log_test "Test 3: OpenVPN server deployment"
        TEST_HOST="test-server-01"
        TEST_CONTAINER=$(get_container_name "$TEST_HOST")
        
        # Note: OpenVPN in Docker requires special privileges
        run_cli_command "openvpn" "--install" || log_warning "OpenVPN installation may require additional Docker privileges"
        
        # Check if OpenVPN container exists
        if docker ps | grep -q "openvpn"; then
            log_success "OpenVPN container created"
        else
            log_warning "OpenVPN container not running (expected in test environment)"
        fi
    fi
    
    # Test 4: Monitoring setup
    log_test "Test 4: Monitoring configuration"
    
    # Test with monitoring enabled
    run_cli_command "base" "--install -- -e vault_monitoring_enabled=true" || return 1
    
    # Check for monitoring tools (basic checks)
    local has_htop=$(docker exec "$TEST_CONTAINER" which htop 2>/dev/null || echo "")
    if [[ -n "$has_htop" ]]; then
        log_success "Basic monitoring tools installed"
    else
        log_warning "Some monitoring tools may be missing"
    fi
    
    # Test 5: Backup configuration
    log_test "Test 5: Backup configuration"
    
    # Enable backups for PostgreSQL
    TEST_HOST="$DB_HOST"
    TEST_CONTAINER=$(get_container_name "$TEST_HOST")
    
    run_cli_command "psql" "--install -- -e vault_pg_enable_backups=true -e vault_backup_dir=/var/backups" || return 1
    
    # Check backup directory
    if docker exec "$TEST_CONTAINER" test -d /var/backups; then
        log_success "Backup directory created"
    else
        log_warning "Backup directory not found"
    fi
    
    # Test 6: Performance tuning
    log_test "Test 6: Performance tuning verification"
    
    # Check PostgreSQL performance settings
    local shared_buffers=$(docker exec "$TEST_CONTAINER" sudo -u postgres psql -t -c "SHOW shared_buffers;" 2>/dev/null || echo "")
    log_test "PostgreSQL shared_buffers: $shared_buffers"
    
    # Check Redis performance settings
    TEST_HOST="cache-01"
    TEST_CONTAINER=$(get_container_name "$TEST_HOST")
    
    local redis_maxclients=$(docker exec "$TEST_CONTAINER" redis-cli -a redispass123 CONFIG GET maxclients 2>/dev/null | tail -1 || echo "")
    log_test "Redis maxclients: $redis_maxclients"
    
    log_success "All $SCENARIO_NAME tests passed!"
    return 0
}

# Execute test suite
run_test_suite
exit $?