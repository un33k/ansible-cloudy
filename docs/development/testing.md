# Ansible Cloudy - Comprehensive Test Plan

This document provides a complete test plan covering all features, commands, and options available in Ansible Cloudy. Use this guide to verify functionality and ensure all components work as expected.

## Table of Contents
- [Test Environment Setup](#test-environment-setup)
- [Core Services Testing](#core-services-testing)
- [Database Services Testing](#database-services-testing)
- [Web Services Testing](#web-services-testing)
- [Cache Services Testing](#cache-services-testing)
- [Advanced Services Testing](#advanced-services-testing)
- [Development Commands Testing](#development-commands-testing)
- [Global Options Testing](#global-options-testing)
- [Ansible Passthrough Testing](#ansible-passthrough-testing)
- [Integration Testing](#integration-testing)
- [Performance Testing](#performance-testing)

## Test Environment Setup

### Prerequisites
```bash
# Setup test environment
./bootstrap.sh
source .venv/bin/activate

# Verify CLI installation
cli --version
cli --help
```

### Test Inventory Configuration
Create test inventory files for different scenarios:

**inventory/test-single.yml** (Single server testing):
```yaml
all:
  vars:
    ansible_user: root
    ansible_ssh_pass: testpass123
    ansible_port: 22
  children:
    test_servers:
      hosts:
        test-server-01:
          ansible_host: 10.10.10.100
```

**inventory/test-multi.yml** (Multi-server testing):
```yaml
all:
  children:
    web_servers:
      hosts:
        web-01:
          ansible_host: 10.10.10.101
        web-02:
          ansible_host: 10.10.10.102
    db_servers:
      hosts:
        db-01:
          ansible_host: 10.10.10.110
    cache_servers:
      hosts:
        cache-01:
          ansible_host: 10.10.10.120
```

## Core Services Testing

### 1. Security Service Testing

#### Basic Installation
```bash
# Test help display
cli security

# Test dry run
cli security --install --check

# Test actual installation
cli security --install

# Test with custom inventory
cli security --install -i inventory/test-single.yml

# Test with vault
cli security --install -e .vault/test.yml

# Test with host override
cli security --install -H 10.10.10.100

# Test production variant
cli security-production --install

# Test verification
cli security-verify --install
```

#### Environment Testing
```bash
# Test dev environment (default)
cli security --install --dev

# Test production environment
cli security --install --prod

# Test CI environment
cli security --install --ci
```

#### Combined Options Testing
```bash
# Test all options combined
cli security --install --prod -i inventory/test-multi.yml -e .vault/prod.yml -H 10.10.10.100

# Test with verbose output
cli security --install -v
cli security --install -vv
cli security --install -vvv
```

### 2. Base Service Testing

```bash
# Test help
cli base

# Test installation
cli base --install

# Test environments
cli base --install --dev
cli base --install --prod
cli base --install --ci

# Test with custom configurations
cli base --install -i inventory/test-single.yml
cli base --install -e .vault/base-config.yml
```

## Database Services Testing

### 3. PostgreSQL (psql) Testing

#### Basic Operations
```bash
# Test help
cli psql

# Test basic installation
cli psql --install

# Test with custom port
cli psql --install --port 5544

# Test with PostGIS
cli psql --install --pgis

# Test production variant
cli psql-production --install
```

#### Granular Operations Testing
```bash
# User management
cli psql --adduser testuser --password testpass123
cli psql --list-users
cli psql --change-password testuser --password newpass123
cli psql --delete-user testuser

# Database management
cli psql --adddb testdb --owner testuser
cli psql --list-databases
cli psql --dump-database testdb
cli psql --delete-db testdb

# Privileges management
cli psql --grant-privileges testuser --database testdb --privileges "SELECT,INSERT"

# Version management
cli psql --get-version
cli psql --get-latest-version

# Configuration management
cli psql --configure-port 5433
cli psql --install-postgis
cli psql --install-client
cli psql --install-repo

# Cluster management
cli psql --create-cluster testcluster
cli psql --remove-cluster testcluster
```

### 4. pgvector Testing

```bash
# Test help
cli pgvector

# Basic installation
cli pgvector --install

# Test with all options
cli pgvector --install --port 5433 --version 17 --pgvector-version v0.5.1
cli pgvector --install --dimensions 768 --index-type hnsw
cli pgvector --install --pgis --create-examples

# Performance tuning options
cli pgvector --install --shared-buffers 2048 --work-mem 32 --max-connections 300

# Test production deployment
cli pgvector --install --prod --create-examples
```

### 5. PostGIS Testing

```bash
# Test help
cli postgis

# Test installation
cli postgis --install
cli postgis --install --prod
```

## Web Services Testing

### 6. Django Testing

```bash
# Test help
cli django

# Test installation
cli django --install
cli django --install --prod

# Test with custom configurations
cli django --install -e .vault/django-config.yml
```

### 7. Node.js Testing

```bash
# Test help
cli nodejs

# Basic installation
cli nodejs --install

# Test with all application options
cli nodejs --install --node-version 20 --app-name myapp
cli nodejs --install --app-repo https://github.com/test/app.git --app-branch develop
cli nodejs --install --app-port 8080 --app-env development

# Test PM2 options
cli nodejs --install --pm2-instances 4 --pm2-mode cluster --pm2-memory 1G

# Test with Nginx integration
cli nodejs --install --with-nginx --domain api.example.com --ssl

# Test environment variables
cli nodejs --install --env-vars '{"NODE_ENV":"production","API_KEY":"secret"}'

# Test production deployment
cli nodejs --install --prod --domain api.example.com --ssl --pm2-instances max
```

### 8. Nginx Testing

```bash
# Test help
cli nginx

# Basic installation
cli nginx --install

# Test with domain and SSL
cli nginx --install --domain example.com --ssl

# Test with custom options
cli nginx --install --protocol http --interface 0.0.0.0
cli nginx --install --cert-dir /etc/ssl/certs --no-firewall

# Test with backends
cli nginx --install --backends "10.0.0.1:8080,10.0.0.2:8080,10.0.0.3:8080"

# Granular operations
cli nginx --add-domain api.example.com
cli nginx --setup-ssl api.example.com
cli nginx --reload
cli nginx --test-config

# Test production variant
cli nginx-production --install
```

## Cache Services Testing

### 9. Redis Testing

```bash
# Test help
cli redis

# Basic installation
cli redis --install

# Test with all options
cli redis --install --port 6380 --memory 1024 --password secret123
cli redis --install --interface 127.0.0.1 --no-firewall

# Granular operations
cli redis --configure-port 6381
cli redis --set-password newpass123
cli redis --configure-memory 2048
cli redis --restart

# Test production variant
cli redis-production --install

# Test combined options
cli redis --install --prod --port 6380 --memory 2048 --password prodpass
```

## Advanced Services Testing

### 10. Standalone (All-in-One) Testing

```bash
# Test help
cli standalone

# Basic installation
cli standalone --install

# Test with application type
cli standalone --install --app-type django
cli standalone --install --app-type nodejs

# Test with all options
cli standalone --install --app-name myapp --app-repo https://github.com/test/app.git
cli standalone --install --domain example.com --enable-ssl --production

# Test component selection
cli standalone --install --with-postgresql --with-redis --with-nginx

# Test PostgreSQL options
cli standalone --install --pg-version 17 --pg-port 5433 --pg-password dbpass123

# Test Redis options
cli standalone --install --redis-port 6380 --redis-memory 1024 --redis-password cachepass

# Full production test
cli standalone --install --prod --app-type django --domain example.com --enable-ssl
```

### 11. PgBouncer Testing

```bash
# Test help
cli pgbouncer

# Test installation
cli pgbouncer --install
cli pgbouncer --install --pool-size 50
cli pgbouncer --install --port 6433

# Granular operations
cli pgbouncer --configure-port 6434
cli pgbouncer --set-pool-size 100
cli pgbouncer --restart
```

### 12. OpenVPN Testing

```bash
# Test help
cli openvpn

# Test installation
cli openvpn --install
cli openvpn --install --prod
```

## Development Commands Testing

### 13. Validation Commands

```bash
# Test comprehensive validation
cli dev validate

# Test individual validators
cli dev syntax
cli dev comprehensive
cli dev lint
cli dev yamlint
cli dev flake8
cli dev spell

# Test authentication flow
cli dev test
cli dev test --check
cli dev test --verbose
```

### 14. Development Options

```bash
# Test with custom paths
cli dev validate -i inventory/custom.yml
cli dev test -e .vault/test.yml

# Test verbose modes
cli dev validate -v
cli dev test -vv
```

## Global Options Testing

### 15. Environment Selection

```bash
# Test all environment flags
cli security --install --dev
cli security --install --development
cli security --install --prod
cli security --install --production
cli security --install --ci
cli security --install --continuous-integration
```

### 16. Custom Configuration Options

```bash
# Test inventory override
cli psql --install -i inventory/custom.yml
cli psql --install --inventory inventory/staging.yml

# Test extra vars
cli redis --install -e .vault/redis-config.yml
cli redis --install --extra-vars .vault/production.yml

# Test host override
cli nginx --install -H 192.168.1.100
cli nginx --install --host 10.0.0.50
```

### 17. Execution Options

```bash
# Test install aliases
cli security --install
cli security --run

# Test dry run aliases
cli base --install --check
cli base --install --dry-run

# Test verbose levels
cli psql --install -v
cli psql --install --verbose
cli psql --install -vv
cli psql --install -vvv
```

### 18. Information Commands

```bash
# Test help variations
cli --help
cli -h

# Test service listing
cli --list
cli -l

# Test version display
cli --version
```

## Ansible Passthrough Testing

### 19. Tag Management

```bash
# Test specific tags
cli psql --install -- --tags postgresql
cli psql --install -- --tags "postgresql,firewall"

# Test skip tags
cli redis --install -- --skip-tags firewall
cli redis --install -- --skip-tags "firewall,logging"
```

### 20. Variable Override

```bash
# Test single variable
cli nginx --install -- -e "nginx_port=8080"

# Test multiple variables
cli psql --install -- -e "pg_port=5433" -e "pg_version=16"

# Test JSON format
cli redis --install -- -e '{"redis_port":6380,"redis_memory_mb":2048}'
```

### 21. Advanced Ansible Options

```bash
# Test host limiting
cli security --install -- --limit web-01
cli security --install -- --limit "web-01,web-02"

# Test task control
cli base --install -- --start-at-task "Configure timezone"
cli base --install -- --step

# Test check and diff modes
cli psql --install -- -C
cli psql --install -- -D
cli psql --install -- -CD

# Test combined passthrough
cli nginx --install -- --tags nginx -e "nginx_domain=test.com" --limit web-01 -v
```

## Integration Testing

### 22. Multi-Service Deployment

```bash
# Test complete web stack deployment
cli security --install
cli base --install
cli psql --install --port 5432 --pgis
cli redis --install --port 6379 --memory 512
cli django --install
cli nginx --install --domain example.com --ssl

# Test with production settings
cli security --install --prod
cli base --install --prod
cli psql --install --prod --port 5433
cli redis --install --prod --memory 2048
cli nginx --install --prod --domain prod.example.com --ssl
```

### 23. Environment Consistency

```bash
# Test consistent environment usage
cli security --install --prod -i inventory/prod.yml -e .vault/prod.yml
cli psql --install --prod -i inventory/prod.yml -e .vault/prod.yml
cli redis --install --prod -i inventory/prod.yml -e .vault/prod.yml
```

### 24. Cross-Service Dependencies

```bash
# Test pgvector after PostgreSQL
cli psql --install
cli pgvector --install

# Test Django with dependencies
cli psql --install
cli redis --install
cli django --install

# Test standalone includes all
cli standalone --install --with-postgresql --with-redis --with-nginx
```

## Performance Testing

### 25. Large-Scale Deployment

```bash
# Test with multiple hosts
cli security --install -i inventory/50-servers.yml
cli base --install -i inventory/50-servers.yml

# Test parallel execution
cli nginx --install -i inventory/web-farm.yml -- -f 10

# Test with rate limiting
cli security --install -i inventory/production.yml -- --forks 5
```

### 26. Resource Configuration Testing

```bash
# Test memory-based configuration
cli redis --install --memory 256    # Small
cli redis --install --memory 2048   # Medium
cli redis --install --memory 8192   # Large

# Test connection limits
cli psql --install -- -e "pg_max_connections=100"
cli psql --install -- -e "pg_max_connections=500"
cli psql --install -- -e "pg_max_connections=1000"

# Test pgvector dimensions
cli pgvector --install --dimensions 384   # Small
cli pgvector --install --dimensions 1536  # Medium
cli pgvector --install --dimensions 3072  # Large
```

## Error Handling Testing

### 27. Invalid Options

```bash
# Test invalid service
cli nonexistent --install

# Test invalid options
cli psql --install --invalid-option
cli redis --install --port invalid

# Test conflicting options
cli nginx --install --ssl  # Without domain
```

### 28. Connection Failures

```bash
# Test unreachable host
cli security --install -H 999.999.999.999

# Test invalid credentials
cli security --install -e .vault/bad-creds.yml

# Test wrong port
cli base --install -- -e "ansible_port=9999"
```

## Validation Testing

### 29. Pre-Installation Validation

```bash
# Test dry run for all services
cli security --install --check
cli psql --install --check --port 5433
cli redis --install --check --memory 2048
cli nginx --install --check --domain test.com --ssl
cli pgvector --install --check --dimensions 1536
cli nodejs --install --check --app-name testapp
cli standalone --install --check --app-type django
```

### 30. Post-Installation Verification

```bash
# Test service-specific verification
cli security-verify --install
cli psql --get-version
cli redis --restart
cli nginx --test-config
cli dev test  # Test authentication
```

## Documentation Testing

### 31. Help System

```bash
# Test help for all services
for service in security base psql redis nginx pgvector nodejs standalone django postgis pgbouncer openvpn; do
    echo "Testing help for $service"
    cli $service
done

# Test help with invalid flags
cli security --invalid
cli psql --help --invalid
```

### 32. Service Discovery

```bash
# Test service listing formats
cli --list
cli -l

# Test with grep filtering
cli --list | grep database
cli --list | grep web
```

## Best Practices for Testing

1. **Always test in isolated environments** - Use VMs or containers
2. **Test dry run first** - Use `--check` before `--install`
3. **Verify idempotency** - Run commands twice to ensure no changes
4. **Test rollback scenarios** - Have snapshot/restore strategy
5. **Document test results** - Keep logs of successful test runs
6. **Test both success and failure paths** - Verify error handling
7. **Use version control** - Track inventory and vault changes
8. **Automate where possible** - Create test scripts for regression

## Test Automation Script Example

```bash
#!/bin/bash
# test-all-services.sh

set -e

echo "Testing Ansible Cloudy Services"

# Test environment setup
./bootstrap.sh -y
source .venv/bin/activate

# Test development commands
echo "Testing development commands..."
cli dev syntax
cli dev validate

# Test core services
echo "Testing core services..."
cli security --install --check
cli base --install --check

# Test database services
echo "Testing database services..."
cli psql --install --check
cli pgvector --install --check

# Test web services
echo "Testing web services..."
cli nginx --install --check
cli nodejs --install --check

# Test cache services
echo "Testing cache services..."
cli redis --install --check

# Test advanced services
echo "Testing advanced services..."
cli standalone --install --check

echo "All tests passed!"
```

This comprehensive test plan covers all features, commands, and options available in Ansible Cloudy. Use it to ensure complete functionality and identify any issues before production deployment.

## Appendix A: Variables Available via -- -e

The following variables can be overridden using the `-- -e` syntax. Many of these are candidates for future promotion to CLI-aware options.

### Security Variables
```bash
# SSH configuration
cli security --install -- -e vault_ssh_port=2222
cli security --install -- -e vault_ssh_max_auth_tries=5
cli security --install -- -e vault_ssh_client_alive_interval=300

# Firewall configuration
cli security --install -- -e vault_ufw_logging=off
cli security --install -- -e vault_ufw_default_incoming=reject

# User management
cli security --install -- -e vault_admin_user=sysadmin
cli security --install -- -e vault_admin_groups="sudo,docker,adm"
```

### System Variables
```bash
# System configuration
cli base --install -- -e vault_hostname=prod-server-01
cli base --install -- -e vault_timezone=America/New_York
cli base --install -- -e vault_locale=en_GB.UTF-8

# Swap configuration
cli base --install -- -e vault_swap_size_mb=4096
cli base --install -- -e vault_swappiness=5
```

### PostgreSQL Variables
```bash
# Performance tuning
cli psql --install -- -e vault_pg_max_connections=200
cli psql --install -- -e vault_pg_shared_buffers_mb=512
cli psql --install -- -e vault_pg_work_mem_mb=16
cli psql --install -- -e vault_pg_effective_cache_size=8GB

# Security settings
cli psql --install -- -e vault_pg_ssl=on
cli psql --install -- -e vault_pg_listen_addresses="localhost,10.0.0.5"

# Database management
cli psql --install -- -e 'vault_pg_databases=[{"name":"app1"},{"name":"app2"}]'
cli psql --install -- -e 'vault_pg_users=[{"name":"user1","password":"pass1"}]'
```

### Redis Variables
```bash
# Memory and persistence
cli redis --install -- -e vault_redis_maxmemory_policy=volatile-lru
cli redis --install -- -e vault_redis_appendonly=yes
cli redis --install -- -e vault_redis_appendfsync=always

# Connection settings
cli redis --install -- -e vault_redis_timeout=300
cli redis --install -- -e vault_redis_tcp_keepalive=60
cli redis --install -- -e vault_redis_tcp_backlog=1024

# Logging
cli redis --install -- -e vault_redis_loglevel=debug
cli redis --install -- -e vault_redis_logfile=/var/log/redis/custom.log
```

### Nginx Variables
```bash
# Performance settings
cli nginx --install -- -e vault_nginx_worker_processes=4
cli nginx --install -- -e vault_nginx_worker_connections=2048
cli nginx --install -- -e vault_nginx_client_max_body_size=100M

# Rate limiting
cli nginx --install -- -e vault_nginx_rate_limit_general=20r/s
cli nginx --install -- -e vault_nginx_rate_limit_api=5r/s
cli nginx --install -- -e vault_nginx_ddos_protection_enabled=true

# Cache settings
cli nginx --install -- -e vault_nginx_cache_size=100m
cli nginx --install -- -e vault_nginx_cache_inactive=60m
```

### Advanced Variable Testing

#### Complex Variable Overrides
```bash
# Multiple variables at once
cli psql --install -- \
  -e vault_pg_port=5433 \
  -e vault_pg_max_connections=300 \
  -e vault_pg_shared_buffers_mb=1024 \
  -e vault_postgres_password=secure123

# JSON format for complex structures
cli psql --install -- -e '{
  "vault_pg_databases": [
    {"name": "production", "owner": "app_user"},
    {"name": "staging", "owner": "test_user"}
  ],
  "vault_pg_users": [
    {"name": "app_user", "password": "apppass123"},
    {"name": "test_user", "password": "testpass123"}
  ]
}'
```

#### Environment-Specific Overrides
```bash
# Development overrides
cli redis --install --dev -- \
  -e vault_redis_maxmemory_mb=256 \
  -e vault_redis_appendonly=no \
  -e vault_redis_loglevel=debug

# Production overrides
cli redis --install --prod -- \
  -e vault_redis_maxmemory_mb=8192 \
  -e vault_redis_appendonly=yes \
  -e vault_redis_password=prod_secret_pass
```

### Variable Discovery Testing

```bash
# List all variables for a service (dry run with verbose)
cli psql --install --check -vvv 2>&1 | grep "vault_"

# Test variable validation
cli psql --install -- -e vault_pg_port=invalid  # Should fail
cli redis --install -- -e vault_redis_memory_mb=-1  # Should fail

# Test variable precedence
echo "vault_pg_port: 5555" > custom.yml
cli psql --install -e custom.yml -- -e vault_pg_port=5444  # 5444 should win
```

### Future CLI Enhancement Candidates

Based on usage patterns, these variables are prime candidates for CLI option promotion:

1. **System Settings**:
   - `vault_hostname` → `--hostname`
   - `vault_timezone` → `--timezone`
   - `vault_swap_size_mb` → `--swap-size`

2. **PostgreSQL Performance**:
   - `vault_pg_max_connections` → `--max-connections`
   - `vault_pg_shared_buffers_mb` → `--shared-buffers`
   - `vault_pg_work_mem_mb` → `--work-mem`

3. **Redis Settings**:
   - `vault_redis_maxmemory_policy` → `--eviction-policy`
   - `vault_redis_appendonly` → `--enable-persistence`
   - `vault_redis_timeout` → `--timeout`

4. **Nginx Configuration**:
   - `vault_nginx_worker_processes` → `--workers`
   - `vault_nginx_client_max_body_size` → `--max-body-size`
   - `vault_nginx_rate_limit_general` → `--rate-limit`

5. **Monitoring & Backups**:
   - `vault_monitoring_enabled` → `--enable-monitoring`
   - `vault_backup_enabled` → `--enable-backups`
   - `vault_backup_retention_days` → `--backup-retention`

This comprehensive test plan now includes all features, commands, options, and variables available in Ansible Cloudy. Use it to ensure complete functionality and identify opportunities for CLI enhancement.

## Appendix B: Docker-Based End-to-End Testing Framework

### Overview

This section describes the Docker-based E2E testing framework for running comprehensive tests locally using Docker Desktop. This approach enables full testing of Ansible Cloudy on real Linux systems without the complexity of cloud infrastructure.

### Architecture

The E2E testing framework uses Docker Compose to orchestrate multiple containers simulating real server environments:

```
test/
├── e2e/
│   ├── docker-compose.yml      # Multi-container test environment
│   ├── Dockerfile.ubuntu       # Ubuntu test image
│   ├── Dockerfile.debian       # Debian test image
│   ├── run-e2e-tests.sh       # Main test orchestrator
│   ├── inventory/
│   │   ├── docker-single.yml   # Single container tests
│   │   ├── docker-multi.yml    # Multi-container tests
│   │   └── docker-full.yml     # Full stack tests
│   ├── scenarios/
│   │   ├── 01-security-base.sh # Core setup tests
│   │   ├── 02-database.sh      # PostgreSQL tests
│   │   ├── 03-web-stack.sh     # Web application tests
│   │   ├── 04-cache.sh         # Redis tests
│   │   ├── 05-advanced.sh      # pgvector, nodejs, etc.
│   │   └── 06-full-stack.sh    # Complete deployment
│   └── vault/
│       └── test-secrets.yml    # Test credentials
```

### Test Execution Modes

1. **Quick Tests** (~5 minutes)
   - Core security and base setup
   - Single service deployments
   - Basic functionality verification

2. **Standard Tests** (~15 minutes)
   - All quick tests
   - Multiple service types
   - Integration testing

3. **Full Tests** (~30 minutes)
   - Complete test suite
   - Multi-server scenarios
   - Performance validation

### Running E2E Tests

#### Prerequisites
```bash
# Ensure Docker Desktop is running
docker --version
docker compose version

# Setup test environment
cd ansible-cloudy
./bootstrap.sh
source .venv/bin/activate
```

#### Basic Usage
```bash
# Run quick tests
./test/e2e/run-e2e-tests.sh --quick

# Run standard tests
./test/e2e/run-e2e-tests.sh --standard

# Run full test suite
./test/e2e/run-e2e-tests.sh --full

# Run specific scenario
./test/e2e/run-e2e-tests.sh --scenario 02-database

# Run with specific OS
./test/e2e/run-e2e-tests.sh --os debian --quick

# Keep containers running after tests
./test/e2e/run-e2e-tests.sh --quick --keep

# Generate HTML report
./test/e2e/run-e2e-tests.sh --full --report
```

### Test Scenarios

#### Scenario 01: Security & Base
- Tests two-phase authentication
- SSH key installation
- Firewall configuration
- Base system setup

#### Scenario 02: Database Services
- PostgreSQL installation
- PostGIS extension
- pgvector deployment
- Database operations

#### Scenario 03: Web Stack
- Nginx installation
- Django deployment
- Node.js with PM2
- SSL configuration

#### Scenario 04: Cache Services
- Redis deployment
- Memory configuration
- Persistence testing
- Password security

#### Scenario 05: Advanced Services
- PgBouncer connection pooling
- OpenVPN server
- Monitoring setup
- Backup configuration

#### Scenario 06: Full Stack
- Complete multi-tier deployment
- Service integration
- Load balancing
- High availability

### Container Configuration

The test containers are configured to closely match real servers:

- **Ubuntu 22.04 LTS** (primary test OS)
- **Debian 12** (secondary test OS)
- **systemd** enabled for service management
- **SSH daemon** for Ansible connectivity
- **Privileged mode** for system operations
- **Persistent volumes** for data testing

### Test Validation

Each test scenario includes:

1. **Pre-flight checks** - Container health, SSH connectivity
2. **Service deployment** - Ansible playbook execution
3. **Functional testing** - Service-specific validation
4. **Idempotency check** - Re-run verification
5. **Clean state test** - Service removal and cleanup

### Debugging Tests

```bash
# Run with debug output
./test/e2e/run-e2e-tests.sh --debug --scenario 01-security-base

# Connect to test container
docker exec -it ansible-cloudy-test-server-01 bash

# View test logs
docker logs ansible-cloudy-test-server-01

# Check service status in container
docker exec ansible-cloudy-test-server-01 systemctl status postgresql
```

### CI/CD Integration

While the full E2E suite runs locally, a minimal smoke test runs in GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Quick Tests
on: [push, pull_request]

jobs:
  syntax:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Syntax validation
        run: |
          ./bootstrap.sh -y
          source .venv/bin/activate
          cli dev syntax

  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Smoke test
        run: ./test/ci/smoke-test.sh
```

### Best Practices

1. **Run tests before commits** - Use quick mode for rapid feedback
2. **Full tests before releases** - Ensure comprehensive validation
3. **Keep containers clean** - Use `--cleanup` to remove old containers
4. **Monitor resources** - Full tests require ~4GB RAM
5. **Parallel execution** - Tests run in parallel where possible
6. **Incremental testing** - Start with quick, escalate to full

### Troubleshooting

#### Container Connection Issues
```bash
# Reset Docker networking
docker network prune
docker compose -f test/e2e/docker-compose.yml down -v
```

#### SSH Authentication Failures
```bash
# Check container SSH service
docker exec ansible-cloudy-test-server-01 service ssh status

# Verify test credentials
cat test/e2e/vault/test-secrets.yml
```

#### Performance Issues
```bash
# Increase Docker resources
# Docker Desktop > Preferences > Resources
# Recommended: 4 CPUs, 8GB RAM

# Run tests sequentially
./test/e2e/run-e2e-tests.sh --sequential
```

This Docker-based E2E testing framework provides comprehensive validation of Ansible Cloudy deployments in realistic Linux environments while maintaining simplicity for both local development and CI/CD pipelines.