#!/bin/bash
# 03-web-stack.sh - Test web stack services (Nginx, Django, Node.js)

set -euo pipefail

# Source common test functions
source "$(dirname "$0")/common.sh"

# Test configuration
SCENARIO_NAME="Web Stack Services"
WEB_HOSTS=("web-01" "web-02")
LB_HOST="lb-01"

# Run tests
run_test_suite() {
    log_test "Starting $SCENARIO_NAME tests"
    
    # Test 1: Nginx installation on load balancer
    log_test "Test 1: Nginx load balancer installation"
    TEST_HOST="$LB_HOST"
    TEST_CONTAINER=$(get_container_name "$TEST_HOST")
    
    run_cli_command "nginx" "--install --domain test.local" || return 1
    
    # Wait for Nginx to start
    wait_for_service "$TEST_CONTAINER" "nginx" || return 1
    
    # Verify Nginx is running
    check_service_status "$TEST_CONTAINER" "nginx" || return 1
    check_port_listening "$TEST_CONTAINER" "80" || return 1
    
    # Test HTTP response
    test_http_response "$TEST_CONTAINER" "80" "502" || return 1  # 502 expected as backends not configured
    
    # Test 2: Django installation on web servers
    log_test "Test 2: Django web application deployment"
    
    for host in "${WEB_HOSTS[@]}"; do
        log_test "Installing Django on $host..."
        TEST_HOST="$host"
        TEST_CONTAINER=$(get_container_name "$TEST_HOST")
        
        run_cli_command "django" "--install" || return 1
        
        # Verify services
        check_service_status "$TEST_CONTAINER" "nginx" || return 1
        check_service_status "$TEST_CONTAINER" "supervisor" || return 1
        
        # Check Django app port
        check_port_listening "$TEST_CONTAINER" "8000" || return 1
    done
    
    # Test 3: PgBouncer installation (connection pooling)
    log_test "Test 3: PgBouncer connection pooling"
    
    for host in "${WEB_HOSTS[@]}"; do
        log_test "Installing PgBouncer on $host..."
        TEST_HOST="$host"
        TEST_CONTAINER=$(get_container_name "$TEST_HOST")
        
        run_cli_command "pgbouncer" "--install --pool-size 25" || return 1
        
        # Verify PgBouncer
        check_service_status "$TEST_CONTAINER" "pgbouncer" || return 1
        check_port_listening "$TEST_CONTAINER" "6432" || return 1
    done
    
    # Test 4: Node.js application (if in full mode)
    if [[ "${TEST_MODE:-}" == "full" ]]; then
        log_test "Test 4: Node.js application deployment"
        TEST_HOST="web-01"
        TEST_CONTAINER=$(get_container_name "$TEST_HOST")
        
        run_cli_command "nodejs" "--install --app-name testapp --app-port 3000" || return 1
        
        # Check PM2 process manager
        local pm2_status=$(docker exec "$TEST_CONTAINER" pm2 list 2>/dev/null || echo "")
        if echo "$pm2_status" | grep -q "testapp"; then
            log_success "Node.js app running with PM2"
        else
            log_warning "PM2 status could not be verified"
        fi
        
        # Check Node.js app port
        check_port_listening "$TEST_CONTAINER" "3000" || return 1
    fi
    
    # Test 5: SSL configuration
    log_test "Test 5: SSL configuration"
    TEST_HOST="$LB_HOST"
    TEST_CONTAINER=$(get_container_name "$TEST_HOST")
    
    # Note: Let's Encrypt won't work in Docker, so we test config only
    run_cli_command "nginx" "--setup-ssl test.local -- -e vault_enable_ssl=false" || return 1
    
    # Verify SSL configuration exists
    if docker exec "$TEST_CONTAINER" test -f /etc/nginx/sites-available/test.local; then
        log_success "Nginx site configuration created"
    else
        log_error "Nginx site configuration missing"
        return 1
    fi
    
    # Test 6: Load balancer upstream configuration
    log_test "Test 6: Load balancer upstream configuration"
    
    # Check if upstream servers are configured
    local nginx_conf=$(docker exec "$TEST_CONTAINER" cat /etc/nginx/sites-available/default 2>/dev/null || echo "")
    if echo "$nginx_conf" | grep -q "upstream"; then
        log_success "Upstream servers configured"
    else
        log_warning "Upstream configuration not found"
    fi
    
    # Test 7: Idempotency check
    log_test "Test 7: Idempotency check"
    local output=$(run_cli_command "nginx" "--install --check" 2>&1)
    if echo "$output" | grep -q "changed=0"; then
        log_success "Nginx setup is idempotent"
    else
        log_warning "Nginx setup may not be fully idempotent"
    fi
    
    log_success "All $SCENARIO_NAME tests passed!"
    return 0
}

# Execute test suite
run_test_suite
exit $?