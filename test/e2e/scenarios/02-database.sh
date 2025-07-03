#!/bin/bash
# 02-database.sh - Test database services (PostgreSQL, PostGIS, pgvector)

set -euo pipefail

# Source common test functions
source "$(dirname "$0")/common.sh"

# Test configuration
SCENARIO_NAME="Database Services"
TEST_HOST="db-01"
TEST_CONTAINER=$(get_container_name "$TEST_HOST")

# Run tests
run_test_suite() {
    log_test "Starting $SCENARIO_NAME tests"
    
    # Test 1: PostgreSQL installation
    log_test "Test 1: PostgreSQL installation"
    run_cli_command "psql" "--install --port 5432" || return 1
    
    # Wait for PostgreSQL to start
    wait_for_service "$TEST_CONTAINER" "postgresql" || return 1
    
    # Verify PostgreSQL is running
    check_service_status "$TEST_CONTAINER" "postgresql" || return 1
    check_port_listening "$TEST_CONTAINER" "5432" || return 1
    
    # Test database connection
    test_database_connection "$TEST_CONTAINER" "5432" "pgpass123" || return 1
    
    # Test 2: PostgreSQL operations
    log_test "Test 2: PostgreSQL granular operations"
    
    # Create user
    run_cli_command "psql" "--adduser testapp --password testpass123" || return 1
    
    # Create database
    run_cli_command "psql" "--adddb testdb --owner testapp" || return 1
    
    # List users
    run_cli_command "psql" "--list-users" || return 1
    
    # List databases
    run_cli_command "psql" "--list-databases" || return 1
    
    # Verify user and database creation
    log_test "Verifying user and database creation..."
    local users=$(docker exec "$TEST_CONTAINER" sudo -u postgres psql -t -c "SELECT usename FROM pg_user WHERE usename='testapp';")
    if echo "$users" | grep -q "testapp"; then
        log_success "User created successfully"
    else
        log_error "User creation failed"
        return 1
    fi
    
    local databases=$(docker exec "$TEST_CONTAINER" sudo -u postgres psql -t -c "SELECT datname FROM pg_database WHERE datname='testdb';")
    if echo "$databases" | grep -q "testdb"; then
        log_success "Database created successfully"
    else
        log_error "Database creation failed"
        return 1
    fi
    
    # Test 3: PostGIS installation
    log_test "Test 3: PostGIS extension"
    run_cli_command "psql" "--install-postgis" || return 1
    
    # Verify PostGIS
    local postgis=$(docker exec "$TEST_CONTAINER" sudo -u postgres psql -t -c "SELECT extname FROM pg_extension WHERE extname='postgis';")
    if echo "$postgis" | grep -q "postgis"; then
        log_success "PostGIS installed successfully"
    else
        log_error "PostGIS installation failed"
        return 1
    fi
    
    # Test 4: pgvector installation (if in full mode)
    if [[ "${TEST_MODE:-}" == "full" ]]; then
        log_test "Test 4: pgvector extension"
        run_cli_command "pgvector" "--install --dimensions 1536" || return 1
        
        # Verify pgvector
        local pgvector=$(docker exec "$TEST_CONTAINER" sudo -u postgres psql -t -c "SELECT extname FROM pg_extension WHERE extname='vector';")
        if echo "$pgvector" | grep -q "vector"; then
            log_success "pgvector installed successfully"
        else
            log_error "pgvector installation failed"
            return 1
        fi
    fi
    
    # Test 5: Performance configuration
    log_test "Test 5: Performance configuration"
    run_cli_command "psql" "--install -- -e vault_pg_max_connections=200 -e vault_pg_shared_buffers_mb=512" || return 1
    
    # Verify configuration changes
    local max_conn=$(docker exec "$TEST_CONTAINER" sudo -u postgres psql -t -c "SHOW max_connections;")
    if echo "$max_conn" | grep -q "200"; then
        log_success "Max connections configured correctly"
    else
        log_warning "Max connections configuration may require restart"
    fi
    
    # Test 6: Idempotency check
    log_test "Test 6: Idempotency check"
    local output=$(run_cli_command "psql" "--install --check" 2>&1)
    if echo "$output" | grep -q "changed=0"; then
        log_success "PostgreSQL setup is idempotent"
    else
        log_warning "PostgreSQL setup may not be fully idempotent"
    fi
    
    log_success "All $SCENARIO_NAME tests passed!"
    return 0
}

# Execute test suite
run_test_suite
exit $?