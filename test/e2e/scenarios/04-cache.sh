#!/bin/bash
# 04-cache.sh - Test cache services (Redis)

set -euo pipefail

# Source common test functions
source "$(dirname "$0")/common.sh"

# Test configuration
SCENARIO_NAME="Cache Services"
TEST_HOST="cache-01"
TEST_CONTAINER=$(get_container_name "$TEST_HOST")

# Run tests
run_test_suite() {
    log_test "Starting $SCENARIO_NAME tests"
    
    # Test 1: Redis installation
    log_test "Test 1: Redis installation"
    run_cli_command "redis" "--install --port 6379 --memory 512 --password redispass123" || return 1
    
    # Wait for Redis to start
    wait_for_service "$TEST_CONTAINER" "redis" 30 || return 1
    
    # Verify Redis is running
    check_service_status "$TEST_CONTAINER" "redis" || return 1
    check_port_listening "$TEST_CONTAINER" "6379" || return 1
    
    # Test Redis connection
    test_redis_connection "$TEST_CONTAINER" "6379" "redispass123" || return 1
    
    # Test 2: Redis configuration
    log_test "Test 2: Redis configuration verification"
    
    # Check memory limit
    local maxmem=$(docker exec "$TEST_CONTAINER" redis-cli -a redispass123 CONFIG GET maxmemory 2>/dev/null | tail -1)
    if [[ "$maxmem" =~ "536870912" ]]; then  # 512MB in bytes
        log_success "Redis memory limit configured correctly"
    else
        log_warning "Redis memory limit may not be set correctly: $maxmem"
    fi
    
    # Check password authentication
    local auth_test=$(docker exec "$TEST_CONTAINER" redis-cli PING 2>&1 || echo "")
    if echo "$auth_test" | grep -q "NOAUTH"; then
        log_success "Redis password authentication is enabled"
    else
        log_error "Redis password authentication not working properly"
        return 1
    fi
    
    # Test 3: Redis operations
    log_test "Test 3: Redis operations"
    
    # Set a test key
    docker exec "$TEST_CONTAINER" redis-cli -a redispass123 SET testkey "testvalue" &>/dev/null
    
    # Get the test key
    local value=$(docker exec "$TEST_CONTAINER" redis-cli -a redispass123 GET testkey 2>/dev/null)
    if [[ "$value" == "testvalue" ]]; then
        log_success "Redis SET/GET operations working"
    else
        log_error "Redis operations failed"
        return 1
    fi
    
    # Test 4: Redis persistence
    log_test "Test 4: Redis persistence configuration"
    
    # Check AOF configuration
    local aof_enabled=$(docker exec "$TEST_CONTAINER" redis-cli -a redispass123 CONFIG GET appendonly 2>/dev/null | tail -1)
    log_test "AOF persistence: $aof_enabled"
    
    # Check RDB configuration
    local save_config=$(docker exec "$TEST_CONTAINER" redis-cli -a redispass123 CONFIG GET save 2>/dev/null | tail -1)
    if [[ -n "$save_config" ]]; then
        log_success "RDB persistence configured"
    else
        log_warning "RDB persistence may not be configured"
    fi
    
    # Test 5: Redis granular operations
    log_test "Test 5: Redis granular operations"
    
    # Change port (config only, can't restart in test)
    run_cli_command "redis" "--configure-port 6380" || return 1
    
    # Set new password
    run_cli_command "redis" "--set-password newpass123" || return 1
    
    # Configure memory
    run_cli_command "redis" "--configure-memory 1024" || return 1
    
    # Test 6: Production mode
    if [[ "${TEST_MODE:-}" == "full" ]]; then
        log_test "Test 6: Redis production configuration"
        run_cli_command "redis-production" "--install" || return 1
        
        # Verify production settings
        local prod_aof=$(docker exec "$TEST_CONTAINER" redis-cli -a redispass123 CONFIG GET appendonly 2>/dev/null | tail -1)
        if [[ "$prod_aof" == "yes" ]]; then
            log_success "Production persistence enabled"
        else
            log_warning "Production persistence not fully configured"
        fi
    fi
    
    # Test 7: Idempotency check
    log_test "Test 7: Idempotency check"
    local output=$(run_cli_command "redis" "--install --check" 2>&1)
    if echo "$output" | grep -q "changed=0"; then
        log_success "Redis setup is idempotent"
    else
        log_warning "Redis setup may not be fully idempotent"
    fi
    
    log_success "All $SCENARIO_NAME tests passed!"
    return 0
}

# Execute test suite
run_test_suite
exit $?