# Ansible Cloudy Scripts

This directory contains utility scripts for testing, verification, and deployment examples.

## Directory Structure

```
scripts/
├── test/          # Testing scripts for various scenarios
├── verify/        # Verification and validation scripts
└── examples/      # Example deployment and utility scripts
```

## Quick Start

All scripts should be run from the project root directory:

```bash
# From ansible-cloudy root
source .venv/bin/activate  # Activate virtual environment first

# Run tests
./scripts/test/test-simple.sh
./scripts/verify/verify-variable-mapping.sh
./scripts/examples/check-server-status.sh <server-ip>
```

## Test Scripts (`test/`)

### test-simple.sh
Quick syntax validation of all playbooks without actual deployment.
- Tests playbook syntax with vault
- Verifies CLI commands work
- No Docker or SSH required

```bash
./scripts/test/test-simple.sh
```

### run-complete-test.sh
**Full integration test** using Docker containers. Tests the complete flow:
- Creates Docker container with test environment
- Runs: Harden → Security → Base
- Verifies each step works correctly
- Includes cleanup

```bash
./scripts/test/run-complete-test.sh
```

### test-quick-local.sh
Local syntax and variable resolution test:
- Checks playbook syntax with vault
- Verifies variable resolution
- Dry run on localhost
- Good for quick validation

```bash
./scripts/test/test-quick-local.sh
```

### test-complete-flow.sh
Alternative complete flow test with detailed step-by-step verification.
- More verbose output
- Step-by-step progress
- Good for debugging

### test-docker-local.sh
Docker-based test with local port mapping:
- Uses Docker container on localhost
- Maps ports (2222 → 22, 2222 → 2222)
- Tests port changes work correctly

### test-with-e2e.sh
Integration with E2E test infrastructure:
- Uses test/e2e Docker setup
- Creates proper test vault and inventory
- For advanced testing scenarios

## Verification Scripts (`verify/`)

### verify-variable-mapping.sh
Verifies all vault variables are correctly mapped throughout the project:
- Checks vault file variables
- Verifies defaults mapping
- Tests inventory resolution
- Confirms playbook usage
- Essential after variable name changes

```bash
./scripts/verify/verify-variable-mapping.sh
```

## Example Scripts (`examples/`)

### check-server-status.sh
Diagnose if a server needs hardening or is already secured:
- Tests SSH ports and authentication methods
- Detects current server state
- Suggests appropriate next steps
- Useful before deployment

```bash
./scripts/examples/check-server-status.sh <server-ip>
```

### deploy-fresh-server.sh
Complete deployment to a fresh server:
- Shows the full hardening → security → base flow
- Includes helpful progress messages
- Good template for automation
- Edit SERVER_IP and ENVIRONMENT variables

```bash
# Edit the script first to set SERVER_IP
./scripts/examples/deploy-fresh-server.sh
```

### deploy-web-stack.sh
Deploy a complete web application stack:
- Full stack: harden → security → database → cache → web → load balancer
- Production-ready deployment
- Includes SSL certificate setup
- Supports multiple environments

```bash
./scripts/examples/deploy-web-stack.sh prod example.com
```

### deploy-microservices.sh
Multi-server microservices deployment:
- Deploys services across multiple servers
- Handles database clusters, cache clusters, app servers
- Configures load balancer with backends
- Enterprise architecture example

```bash
# Edit script to define server arrays
./scripts/examples/deploy-microservices.sh prod
```

### quick-dev-setup.sh
Quick all-in-one development setup:
- Uses standalone recipe for simplicity
- Perfect for development/testing
- Single server with all services
- Minimal configuration needed

```bash
./scripts/examples/quick-dev-setup.sh [server-ip]
```

### test-all-services.sh
Comprehensive syntax check of all services:
- Tests all available playbooks
- Validates CLI commands
- Good for CI/CD pipelines
- No deployment, just validation

```bash
./scripts/examples/test-all-services.sh
```

## Requirements

- **Virtual Environment**: Always activate `.venv` before running scripts
  ```bash
  source .venv/bin/activate
  ```
- **Docker**: Required for test scripts (except syntax tests)
- **SSH Keys**: Must have `~/.ssh/id_rsa` for deployment scripts
- **sshpass**: Required for initial password auth tests
  ```bash
  # macOS
  brew install hudochenkov/sshpass/sshpass
  # Linux
  apt-get install sshpass
  ```

## Environment Variables

Scripts respect these environment variables:
- `VAULT_ROOT_PASSWORD`: Override default root password
- `ENVIRONMENT`: Set deployment environment (dev/prod/ci)
- `ANSIBLE_VAULT_PASSWORD_FILE`: Path to vault password file

## Best Practices

1. **Always run from project root**: Scripts assume they're run from the ansible-cloudy directory
2. **Check server status first**: Use `check-server-status.sh` before deploying
3. **Use syntax tests**: Run `test-simple.sh` before actual deployments
4. **Review examples**: Example scripts are templates - modify for your needs
5. **Clean up Docker**: Test scripts clean up after themselves, but check with `docker ps -a`

## Troubleshooting

### "Virtual environment not activated"
```bash
source .venv/bin/activate
```

### "Docker daemon not running"
```bash
# macOS
open -a Docker
# Linux
sudo systemctl start docker
```

### "SSH key not found"
```bash
# Generate SSH key if missing
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
```

### "Port already in use"
Check for conflicting services:
```bash
lsof -i :2222
lsof -i :2222
```

## Contributing

When adding new scripts:
1. Place in appropriate subdirectory (test/, verify/, or examples/)
2. Make executable: `chmod +x script.sh`
3. Add documentation to this README
4. Include clear usage instructions in script comments
5. Handle cleanup (especially for Docker containers)