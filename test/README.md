# Ansible Cloudy Test Suite

This directory contains the comprehensive test suite for Ansible Cloudy, including both local end-to-end (E2E) tests using Docker and lightweight CI/CD tests for GitHub Actions.

## Directory Structure

```
test/
├── e2e/                    # End-to-end tests using Docker
│   ├── docker-compose.yml  # Multi-container test environment
│   ├── Dockerfile.*        # Container images (Ubuntu, Debian)
│   ├── run-e2e-tests.sh   # Main test runner
│   ├── inventory/         # Test inventories
│   ├── scenarios/         # Test scenarios
│   └── vault/            # Test credentials
└── ci/                    # CI/CD tests for GitHub Actions
    └── smoke-test.sh      # Quick smoke tests
```

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Python 3.8+ with virtual environment
- Ansible Cloudy environment activated

### Running E2E Tests

```bash
# Setup environment
cd ansible-cloudy
./bootstrap.sh
source .venv/bin/activate

# Run quick tests (5 minutes)
./test/e2e/run-e2e-tests.sh --quick

# Run standard tests (15 minutes)
./test/e2e/run-e2e-tests.sh --standard

# Run full test suite (30 minutes)
./test/e2e/run-e2e-tests.sh --full

# Run specific scenario
./test/e2e/run-e2e-tests.sh --scenario 02-database

# Keep containers running for debugging
./test/e2e/run-e2e-tests.sh --quick --keep

# Generate HTML test report
./test/e2e/run-e2e-tests.sh --full --report
```

## Test Scenarios

### 01-security-base.sh
- Two-phase authentication setup
- SSH key installation
- Firewall configuration
- Base system configuration

### 02-database.sh
- PostgreSQL installation
- PostGIS extension
- pgvector deployment
- Database operations

### 03-web-stack.sh
- Nginx load balancer
- Django web application
- Node.js with PM2
- PgBouncer connection pooling

### 04-cache.sh
- Redis deployment
- Memory configuration
- Persistence testing
- Password security

### 05-advanced.sh
- pgvector for AI/ML
- Node.js advanced features
- Monitoring setup
- Backup configuration

### 06-full-stack.sh
- Complete standalone deployment
- Multi-tier architecture
- Service integration
- High availability

## CI/CD Tests

The `ci/smoke-test.sh` script runs lightweight tests suitable for GitHub Actions:

- Environment setup validation
- CLI availability checks
- Syntax validation
- Help system verification
- Service discovery

## Docker Test Environment

The test suite uses Docker Compose to create realistic Linux environments:

- **Ubuntu 22.04**: Primary test OS
- **Debian 12**: Secondary test OS
- **systemd enabled**: For service management
- **SSH daemon**: For Ansible connectivity
- **Network isolation**: Custom bridge network

## Test Development

### Adding New Tests

1. Create a new scenario in `test/e2e/scenarios/`
2. Use `common.sh` for shared functions
3. Follow the naming convention: `XX-description.sh`
4. Update this README with scenario description

### Test Best Practices

- Always check prerequisites first
- Use idempotency checks
- Clean up resources after tests
- Log all test steps clearly
- Handle failures gracefully

## Troubleshooting

### Container Issues

```bash
# Reset all test containers
docker compose -f test/e2e/docker-compose.yml down -v

# View container logs
docker logs ansible-cloudy-test-server-01

# Connect to container
docker exec -it ansible-cloudy-test-server-01 bash
```

### SSH Connection Issues

```bash
# Check SSH service
docker exec ansible-cloudy-test-server-01 service ssh status

# Verify credentials
cat test/e2e/vault/test-secrets.yml
```

### Resource Limitations

- Ensure Docker has at least 4GB RAM allocated
- Use `--sequential` flag to reduce concurrent load
- Close other applications to free resources

## Integration with TESTS.md

This test suite implements the comprehensive test plan documented in `docs/TESTS.md`. Refer to that document for:

- Complete command reference
- All available options
- Variable overrides via `-- -e`
- Future enhancement opportunities