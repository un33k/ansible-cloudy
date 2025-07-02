#!/bin/bash
# Quick local test using system Python and a simple SSH test

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Quick Ansible Syntax Test${NC}"

# Activate virtual environment
source .venv/bin/activate

# Test playbook syntax with actual vault values
echo -e "${YELLOW}1. Testing harden playbook syntax with vault...${NC}"
ansible-playbook --syntax-check \
  cloudy/playbooks/recipes/core/harden.yml \
  -i cloudy/inventory/dev.yml \
  -e @.vault/dev.yml

# Verify variable resolution
echo -e "${YELLOW}2. Checking variable resolution...${NC}"
ansible-inventory -i cloudy/inventory/dev.yml -e @.vault/dev.yml --list --vars | grep -E "(ssh_port|root_user|grunt)" | head -20

# Test with a minimal local setup
echo -e "${YELLOW}3. Creating minimal test inventory...${NC}"
cat > test-minimal.yml << EOF
all:
  hosts:
    localhost:
      ansible_connection: local
  children:
    harden_targets:
      hosts:
        localhost:
    security_targets:
      hosts:
        localhost:
    service_targets:
      hosts:
        localhost:
EOF

# Dry run the playbooks
echo -e "${YELLOW}4. Dry run harden playbook (local)...${NC}"
ansible-playbook \
  cloudy/playbooks/recipes/core/harden.yml \
  -i test-minimal.yml \
  -e @.vault/dev.yml \
  -e ansible_connection=local \
  --check \
  --diff

rm -f test-minimal.yml

echo -e "${GREEN}Syntax tests completed!${NC}"