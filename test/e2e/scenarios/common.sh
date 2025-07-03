#!/bin/bash
# common.sh - Common functions for test scenarios

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${YELLOW}[DEBUG]${NC} $1"
    fi
}

# Run CLI command
run_cli_command() {
    local service="$1"
    local args="$2"
    local extra_args="${3:-}"
    
    log_debug "Running: cli $service $args"
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Prepare command
    local cmd="cli $service $args"
    
    # Add inventory and vault
    cmd="$cmd -i $INVENTORY_FILE -e @$VAULT_FILE"
    
    # Add extra arguments if provided
    if [[ -n "$extra_args" ]]; then
        cmd="$cmd $extra_args"
    fi
    
    # Add verbosity in debug mode
    if [[ "${DEBUG:-false}" == "true" ]]; then
        cmd="$cmd -v"
    fi
    
    log_debug "Full command: $cmd"
    
    # Execute command
    eval "$cmd"
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_success "Command completed successfully"
    else
        log_error "Command failed with exit code: $exit_code"
    fi
    
    return $exit_code
}

# Check service status
check_service_status() {
    local container="$1"
    local service="$2"
    
    log_debug "Checking service $service on $container"
    
    if docker exec "$container" systemctl is-active "$service" &>/dev/null; then
        log_success "Service $service is active"
        return 0
    else
        log_error "Service $service is not active"
        return 1
    fi
}

# Check port listening
check_port_listening() {
    local container="$1"
    local port="$2"
    
    log_debug "Checking port $port on $container"
    
    if docker exec "$container" ss -tlnp | grep -q ":$port"; then
        log_success "Port $port is listening"
        return 0
    else
        log_error "Port $port is not listening"
        return 1
    fi
}

# Test database connection
test_database_connection() {
    local container="$1"
    local port="${2:-5432}"
    local password="${3:-pgpass123}"
    
    log_debug "Testing PostgreSQL connection on $container:$port"
    
    local result=$(docker exec "$container" bash -c "PGPASSWORD=$password psql -h localhost -p $port -U postgres -c 'SELECT 1;' 2>&1")
    
    if echo "$result" | grep -q "1 row"; then
        log_success "PostgreSQL connection successful"
        return 0
    else
        log_error "PostgreSQL connection failed: $result"
        return 1
    fi
}

# Test Redis connection
test_redis_connection() {
    local container="$1"
    local port="${2:-6379}"
    local password="${3:-}"
    
    log_debug "Testing Redis connection on $container:$port"
    
    local auth_cmd=""
    if [[ -n "$password" ]]; then
        auth_cmd="AUTH $password"
    fi
    
    local result=$(docker exec "$container" bash -c "echo -e '$auth_cmd\nPING' | redis-cli -p $port 2>&1")
    
    if echo "$result" | grep -q "PONG"; then
        log_success "Redis connection successful"
        return 0
    else
        log_error "Redis connection failed: $result"
        return 1
    fi
}

# Test HTTP response
test_http_response() {
    local container="$1"
    local port="${2:-80}"
    local expected="${3:-200}"
    
    log_debug "Testing HTTP response on $container:$port"
    
    local response=$(docker exec "$container" curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/" 2>/dev/null || echo "000")
    
    if [[ "$response" == "$expected" ]]; then
        log_success "HTTP response correct: $response"
        return 0
    else
        log_error "HTTP response incorrect: $response (expected: $expected)"
        return 1
    fi
}

# Wait for service
wait_for_service() {
    local container="$1"
    local service="$2"
    local max_wait="${3:-60}"
    
    log_test "Waiting for $service to be ready..."
    
    local count=0
    while [ $count -lt $max_wait ]; do
        if check_service_status "$container" "$service" &>/dev/null; then
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    log_error "Service $service failed to start within $max_wait seconds"
    return 1
}

# Container name helper
get_container_name() {
    local host="$1"
    echo "ansible-cloudy-${host}"
}