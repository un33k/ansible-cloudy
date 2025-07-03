#!/bin/bash
# Complete test runner for harden -> security -> base flow

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║      Ansible Cloudy Complete Test Suite              ║${NC}"
echo -e "${CYAN}║          Harden → Security → Base                    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"

# Configuration
TEST_DIR="test/e2e"
VAULT_FILE="$TEST_DIR/vault/test-secrets.yml"
INVENTORY_FILE="$TEST_DIR/inventory/docker-harden.yml"

# Cleanup function
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    cd $TEST_DIR
    docker-compose down -v 2>/dev/null || true
    cd ../..
}

# Trap cleanup
trap cleanup EXIT

# Start from project root
cd "$(dirname "$0")"

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Step 1: Setup test environment
echo -e "${YELLOW}Step 1: Setting up test environment...${NC}"

# Create test vault file
cat > $VAULT_FILE << 'EOF'
---
# Test Environment Vault Configuration

# === SUPERUSER CREDENTIALS ===
vault_root_user: "root"
vault_root_password: "testpass123"
vault_root_ssh_private_key_file: "~/.ssh/id_rsa"
vault_root_ssh_password_authentication: false

# === SSH CONFIGURATION ===
vault_ssh_host_key_checking: false
vault_ssh_common_args: "-o StrictHostKeyChecking=no"
vault_ssh_port_initial: 22
vault_ssh_port_final: 22022

# === GLOBAL SERVER CONFIGURATION ===
vault_git_user_full_name: "Test User"
vault_git_user_email: "test@example.com"
vault_timezone: "UTC"
vault_locale: "en_US.UTF-8"

# === GRUNT USER CREDENTIALS ===
vault_grunt_user: "grunt"
vault_grunt_password: "grunt4pass"
vault_grunt_ssh_private_key_file: "~/.ssh/id_rsa"
vault_grunt_groups: "sudo,www-data"

# === SERVICE CREDENTIALS ===
vault_postgres_password: "pgpass123"
vault_redis_password: "redispass123"
EOF

# Create test inventory
cat > $INVENTORY_FILE << 'EOF'
all:
  vars:
    # Global settings from vault
    git_user_full_name: "{{ vault_git_user_full_name }}"
    git_user_email: "{{ vault_git_user_email }}"
    timezone: "{{ vault_timezone }}"
    locale: "{{ vault_locale }}"
    
    # Default connection
    ansible_user: "{{ vault_root_user }}"
    ansible_port: "{{ vault_ssh_port_final }}"
    ansible_host_key_checking: "{{ vault_ssh_host_key_checking }}"
    ansible_ssh_private_key_file: "{{ vault_root_ssh_private_key_file }}"
    ansible_ssh_common_args: "{{ vault_ssh_common_args }}"
    
    # Grunt user
    grunt_user: "{{ vault_grunt_user }}"
    grunt_password: "{{ vault_grunt_password }}"
    grunt_groups: "{{ vault_grunt_groups }}"
    grunt_ssh_private_key_file: "{{ vault_grunt_ssh_private_key_file }}"
    
  children:
    harden_targets:
      vars:
        ansible_user: "{{ vault_root_user }}"
        ansible_port: 2201  # Docker mapped port for initial connection
        ansible_ssh_pass: "{{ vault_root_password }}"
        ansible_host_key_checking: "{{ vault_ssh_host_key_checking }}"
        ansible_ssh_common_args: "{{ vault_ssh_common_args }}"
      hosts:
        test-server-01:
          ansible_host: localhost
    
    security_targets:
      vars:
        ansible_user: "{{ vault_root_user }}"
        ansible_port: 22022
        ansible_ssh_private_key_file: "{{ vault_root_ssh_private_key_file }}"
        ansible_host_key_checking: "{{ vault_ssh_host_key_checking }}"
        ansible_ssh_common_args: "{{ vault_ssh_common_args }}"
      hosts:
        test-server-01:
          ansible_host: 172.20.0.10
    
    service_targets:
      vars:
        ansible_user: "{{ vault_root_user }}"
        ansible_port: 22022
        ansible_ssh_private_key_file: "{{ vault_root_ssh_private_key_file }}"
        ansible_host_key_checking: "{{ vault_ssh_host_key_checking }}"
        ansible_ssh_common_args: "{{ vault_ssh_common_args }}"
      hosts:
        test-server-01:
          ansible_host: 172.20.0.10

  hosts:
    test-server-01:
      hostname: test-server-01.example.com
EOF

# Update Dockerfile password
sed -i.bak 's/pass4now/testpass123/g' $TEST_DIR/Dockerfile.ubuntu || true

# Step 2: Build and start containers
echo -e "${YELLOW}Step 2: Building and starting Docker containers...${NC}"
cd $TEST_DIR
docker-compose down -v 2>/dev/null || true
docker-compose build test-server-01
docker-compose up -d test-server-01
cd ../..

# Wait for container
echo -e "${BLUE}Waiting for container to be ready...${NC}"
sleep 15

# Step 3: Test initial connection
echo -e "${YELLOW}Step 3: Testing initial connection...${NC}"
if sshpass -p testpass123 ssh -o StrictHostKeyChecking=no -p 2201 root@localhost 'echo "✅ Initial connection successful"'; then
    echo -e "${GREEN}Initial SSH connection working${NC}"
else
    echo -e "${RED}Initial SSH connection failed${NC}"
    exit 1
fi

# Step 4: Run harden playbook
echo -e "${YELLOW}Step 4: Running HARDEN playbook...${NC}"
ansible-playbook \
    cloudy/playbooks/recipes/core/harden.yml \
    -i $INVENTORY_FILE \
    -e @$VAULT_FILE \
    -e vault_ssh_port_initial=2201 \
    -vv

# Step 5: Test SSH on new port
echo -e "${YELLOW}Step 5: Testing SSH on port 22022...${NC}"
if ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p 22022 root@172.20.0.10 'echo "✅ SSH key auth on 22022 working"'; then
    echo -e "${GREEN}SSH key authentication successful${NC}"
else
    echo -e "${RED}SSH key authentication failed${NC}"
    exit 1
fi

# Step 6: Run security playbook
echo -e "${YELLOW}Step 6: Running SECURITY playbook...${NC}"
ansible-playbook \
    cloudy/playbooks/recipes/core/security.yml \
    -i $INVENTORY_FILE \
    -e @$VAULT_FILE \
    -vv

# Step 7: Test grunt user
echo -e "${YELLOW}Step 7: Testing grunt user...${NC}"
if ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p 22022 grunt@172.20.0.10 'sudo whoami' | grep -q root; then
    echo -e "${GREEN}Grunt user sudo access working${NC}"
else
    echo -e "${RED}Grunt user setup failed${NC}"
    exit 1
fi

# Step 8: Run base playbook
echo -e "${YELLOW}Step 8: Running BASE playbook...${NC}"
ansible-playbook \
    cloudy/playbooks/recipes/core/base.yml \
    -i $INVENTORY_FILE \
    -e @$VAULT_FILE \
    -vv

# Step 9: Final verification
echo -e "${YELLOW}Step 9: Final verification...${NC}"
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p 22022 root@172.20.0.10 << 'EOF'
echo "=== System Status ==="
echo "Hostname: $(hostname)"
echo "SSH Port: $(grep "^Port" /etc/ssh/sshd_config | awk '{print $2}')"
echo "Users: $(getent passwd | grep -E "^(root|grunt):" | cut -d: -f1 | tr '\n' ' ')"
echo "Firewall: $(ufw status 2>/dev/null | head -1 || echo 'Not available in container')"
echo "Timezone: $(timedatectl show --property=Timezone --value 2>/dev/null || cat /etc/timezone)"
echo "Git User: $(git config --global user.name)"
echo "Git Email: $(git config --global user.email)"
EOF

echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║              ALL TESTS PASSED! 🎉                    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"

# Cleanup is handled by trap