#!/bin/bash
# Test using the E2E infrastructure

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== Testing with E2E Infrastructure ===${NC}"

# Activate virtual environment
source .venv/bin/activate

# Update test secrets to match our vault
echo -e "${YELLOW}1. Updating test secrets...${NC}"
cat > test/e2e/vault/test-secrets.yml << 'EOF'
---
# Test Environment Vault Configuration
# Matches the structure of .vault/dev.yml

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

# === SERVICE PORTS ===
vault_postgresql_port: 5432
vault_redis_port: 6379
vault_nginx_http_port: 80
vault_nginx_https_port: 443
EOF

# Update Dockerfile to use testpass123
echo -e "${YELLOW}2. Updating Dockerfile...${NC}"
sed -i.bak 's/pass4now/testpass123/g' test/e2e/Dockerfile.ubuntu

# Update test inventory
echo -e "${YELLOW}3. Creating test inventory...${NC}"
cat > test/e2e/inventory/docker-harden.yml << 'EOF'
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
        ansible_port: 2201  # Docker mapped port
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
EOF

# Run the test scenario
echo -e "${YELLOW}4. Running test scenario...${NC}"
cd test/e2e
./scenarios/01-security-base.sh

echo -e "${GREEN}=== Test Complete ===${NC}"