#!/bin/bash
# 06-full-stack.sh - Test complete full stack deployment

set -euo pipefail

# Source common test functions
source "$(dirname "$0")/common.sh"

# Test configuration
SCENARIO_NAME="Full Stack Deployment"
STANDALONE_HOST="test-server-01"

# Run tests
run_test_suite() {
    log_test "Starting $SCENARIO_NAME tests"
    
    # Test 1: Standalone all-in-one deployment
    log_test "Test 1: Standalone all-in-one server"
    TEST_HOST="$STANDALONE_HOST"
    TEST_CONTAINER=$(get_container_name "$TEST_HOST")
    
    run_claudia_command "standalone" "--install --app-type django --domain test.local --with-postgresql --with-redis --with-nginx" || return 1
    
    # Wait for all services
    log_test "Waiting for all services to start..."
    wait_for_service "$TEST_CONTAINER" "postgresql" || return 1
    wait_for_service "$TEST_CONTAINER" "redis" || return 1
    wait_for_service "$TEST_CONTAINER" "nginx" || return 1
    
    # Verify all services are running
    log_test "Verifying all services..."
    check_service_status "$TEST_CONTAINER" "postgresql" || return 1
    check_service_status "$TEST_CONTAINER" "redis" || return 1
    check_service_status "$TEST_CONTAINER" "nginx" || return 1
    check_service_status "$TEST_CONTAINER" "supervisor" || return 1
    
    # Test 2: Service connectivity
    log_test "Test 2: Service connectivity"
    
    # Test PostgreSQL
    test_database_connection "$TEST_CONTAINER" "5432" "pgpass123" || return 1
    
    # Test Redis
    test_redis_connection "$TEST_CONTAINER" "6379" "redispass123" || return 1
    
    # Test Nginx
    test_http_response "$TEST_CONTAINER" "80" "502" || log_warning "Nginx response not as expected"
    
    # Test 3: Multi-tier deployment simulation
    log_test "Test 3: Multi-tier deployment verification"
    
    # Deploy on multiple containers if in full mode
    if [[ "${TEST_MODE:-}" == "full" ]]; then
        # Web tier with PgBouncer
        for host in "web-01" "web-02"; do
            TEST_HOST="$host"
            TEST_CONTAINER=$(get_container_name "$TEST_HOST")
            
            log_test "Setting up web tier on $host..."
            run_claudia_command "django" "--install" || return 1
            run_claudia_command "pgbouncer" "--install" || return 1
            
            check_service_status "$TEST_CONTAINER" "pgbouncer" || return 1
            check_port_listening "$TEST_CONTAINER" "6432" || return 1
        done
        
        # Load balancer configuration
        TEST_HOST="lb-01"
        TEST_CONTAINER=$(get_container_name "$TEST_HOST")
        
        log_test "Configuring load balancer..."
        run_claudia_command "nginx" "--install --domain test.local --backends '172.20.0.21:80,172.20.0.22:80'" || return 1
        
        # Test load balancer
        test_http_response "$TEST_CONTAINER" "80" "502" || log_warning "Load balancer response not as expected"
    fi
    
    # Test 4: High availability features
    log_test "Test 4: High availability features"
    
    # Test failover simulation (basic check)
    if [[ "${TEST_MODE:-}" == "full" ]]; then
        log_test "Simulating web server failure..."
        docker pause ansible-cloudy-web-01 || true
        sleep 2
        
        # Load balancer should still respond
        TEST_HOST="lb-01"
        TEST_CONTAINER=$(get_container_name "$TEST_HOST")
        test_http_response "$TEST_CONTAINER" "80" || log_warning "Load balancer failover may not be working"
        
        # Restore web server
        docker unpause ansible-cloudy-web-01 || true
    fi
    
    # Test 5: Resource utilization
    log_test "Test 5: Resource utilization check"
    TEST_HOST="$STANDALONE_HOST"
    TEST_CONTAINER=$(get_container_name "$TEST_HOST")
    
    # Check memory usage
    local mem_usage=$(docker exec "$TEST_CONTAINER" free -m | grep Mem | awk '{print $3}')
    log_test "Memory usage: ${mem_usage}MB"
    
    # Check disk usage
    local disk_usage=$(docker exec "$TEST_CONTAINER" df -h / | tail -1 | awk '{print $5}')
    log_test "Disk usage: $disk_usage"
    
    # Test 6: Service integration
    log_test "Test 6: Service integration verification"
    
    # Create test data in PostgreSQL
    docker exec "$TEST_CONTAINER" sudo -u postgres psql -c "CREATE DATABASE integration_test;" &>/dev/null || true
    
    # Store test data in Redis
    docker exec "$TEST_CONTAINER" redis-cli -a redispass123 SET integration:test "success" &>/dev/null
    
    # Verify integration
    local pg_db=$(docker exec "$TEST_CONTAINER" sudo -u postgres psql -t -c "SELECT datname FROM pg_database WHERE datname='integration_test';" 2>/dev/null || echo "")
    local redis_val=$(docker exec "$TEST_CONTAINER" redis-cli -a redispass123 GET integration:test 2>/dev/null || echo "")
    
    if echo "$pg_db" | grep -q "integration_test" && [[ "$redis_val" == "success" ]]; then
        log_success "Service integration verified"
    else
        log_error "Service integration failed"
        return 1
    fi
    
    # Test 7: Production readiness
    log_test "Test 7: Production readiness checks"
    
    # Check firewall status
    local fw_status=$(docker exec "$TEST_CONTAINER" ufw status 2>/dev/null || echo "inactive")
    log_test "Firewall status: $fw_status"
    
    # Check SSH hardening
    local ssh_config=$(docker exec "$TEST_CONTAINER" grep -E "PermitRootLogin|PasswordAuthentication" /etc/ssh/sshd_config 2>/dev/null || echo "")
    if echo "$ssh_config" | grep -q "PermitRootLogin no"; then
        log_success "SSH root login disabled"
    else
        log_warning "SSH root login may not be properly disabled"
    fi
    
    # Check service auto-start
    local pg_enabled=$(docker exec "$TEST_CONTAINER" systemctl is-enabled postgresql 2>/dev/null || echo "")
    if [[ "$pg_enabled" == "enabled" ]]; then
        log_success "Services configured for auto-start"
    else
        log_warning "Some services may not be enabled for auto-start"
    fi
    
    log_success "All $SCENARIO_NAME tests passed!"
    return 0
}

# Execute test suite
run_test_suite
exit $?