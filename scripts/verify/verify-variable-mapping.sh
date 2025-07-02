#!/bin/bash
# Verify all variable mappings are correct

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Verifying Variable Mappings ===${NC}"

# Activate virtual environment
source .venv/bin/activate

# Check vault file
echo -e "${YELLOW}1. Vault variables in .vault/dev.yml:${NC}"
grep -E "vault_(root|grunt|ssh_port)" .vault/dev.yml | grep -v "^#"

# Check defaults
echo -e "${YELLOW}2. Default mappings in cloudy/defaults/vault.yml:${NC}"
grep -E "vault_(root|grunt|ssh_port|ansible)" cloudy/defaults/vault.yml | grep -v "^#"

# Check inventory usage
echo -e "${YELLOW}3. Inventory variable usage:${NC}"
echo "=== dev.yml ==="
grep -E "vault_(root|ssh_port|ansible)" cloudy/inventory/dev.yml | head -10

# Check playbook usage
echo -e "${YELLOW}4. Harden playbook variable usage:${NC}"
grep -E "vault_" cloudy/playbooks/recipes/core/harden.yml | grep -v "^#"

# Check security playbook
echo -e "${YELLOW}5. Security playbook variable usage:${NC}"
grep -E "vault_(ssh_port|grunt)" cloudy/playbooks/recipes/core/security.yml | head -10

# Test variable resolution
echo -e "${YELLOW}6. Testing variable resolution with ansible-inventory:${NC}"
ansible-inventory -i cloudy/inventory/dev.yml -e @.vault/dev.yml --list --yaml | grep -A5 -B5 "ssh_port"

echo -e "${GREEN}=== Verification Complete ===${NC}"