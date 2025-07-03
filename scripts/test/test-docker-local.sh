#!/bin/bash
# Test hardening flow with local Docker container

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Ansible Cloudy Hardening Test ===${NC}"

# Cleanup any existing container
echo -e "${YELLOW}Cleaning up any existing test containers...${NC}"
docker rm -f ansible-harden-test 2>/dev/null || true

# Start a fresh Ubuntu container
echo -e "${YELLOW}1. Starting fresh Ubuntu container...${NC}"
docker run -d \
  --name ansible-harden-test \
  --privileged \
  -p 2222:22 \
  -p 22022:22022 \
  ubuntu:22.04 \
  /bin/bash -c "
    apt-get update && \
    apt-get install -y openssh-server sudo systemd systemd-sysv && \
    echo 'root:pass4now' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    mkdir -p /var/run/sshd && \
    /usr/sbin/sshd -D
  "

# Wait for container to be ready
echo -e "${YELLOW}Waiting for container to be ready...${NC}"
sleep 10

# Test SSH connection
echo -e "${YELLOW}2. Testing SSH connection on port 2222...${NC}"
sshpass -p pass4now ssh -o StrictHostKeyChecking=no -p 2222 root@localhost 'echo "SSH test successful"'

# Create test inventory
echo -e "${YELLOW}3. Creating test inventory...${NC}"
cat > test-docker-inventory.yml << 'EOF'
all:
  vars:
    # Global Settings
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
    
    # Grunt user settings
    grunt_user: "{{ vault_grunt_user }}"
    grunt_password: "{{ vault_grunt_password }}"
    grunt_groups: "sudo,www-data"
    grunt_ssh_private_key_file: "{{ vault_grunt_ssh_private_key_file }}"
    
  children:
    # Harden targets
    harden_targets:
      vars:
        ansible_user: "{{ vault_root_user }}"
        ansible_port: 2222  # Docker mapped port
        ansible_ssh_pass: "{{ vault_root_password }}"
        ansible_host_key_checking: "{{ vault_ssh_host_key_checking }}"
        ansible_ssh_common_args: "{{ vault_ssh_common_args }}"
      hosts:
        docker-test:
          ansible_host: localhost
    
    # Security targets
    security_targets:
      vars:
        ansible_user: "{{ vault_root_user }}"
        ansible_port: 22022  # After hardening
        ansible_ssh_private_key_file: "{{ vault_root_ssh_private_key_file }}"
        ansible_host_key_checking: "{{ vault_ssh_host_key_checking }}"
        ansible_ssh_common_args: "{{ vault_ssh_common_args }}"
      hosts:
        docker-test:
          ansible_host: localhost
    
    # Service targets
    service_targets:
      vars:
        ansible_user: "{{ vault_root_user }}"
        ansible_port: 22022
        ansible_ssh_private_key_file: "{{ vault_root_ssh_private_key_file }}"
        ansible_host_key_checking: "{{ vault_ssh_host_key_checking }}"
        ansible_ssh_common_args: "{{ vault_ssh_common_args }}"
      hosts:
        docker-test:
          ansible_host: localhost

  hosts:
    docker-test:
      ansible_host: localhost
      hostname: docker-test.example.com
EOF

# Activate virtual environment
source .venv/bin/activate

# Run harden playbook
echo -e "${YELLOW}4. Running harden playbook...${NC}"
python -m dev.claudia.cli.main harden --install -- \
  -i test-docker-inventory.yml \
  -e @.vault/dev.yml \
  -e vault_ssh_port_initial=2222 \
  -e vault_ssh_port_final=22022 \
  -vv

# Test SSH on new port
echo -e "${YELLOW}5. Testing SSH connection on port 22022...${NC}"
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p 22022 root@localhost 'echo "SSH key auth successful!"'

# Run security playbook
echo -e "${YELLOW}6. Running security playbook...${NC}"
python -m dev.claudia.cli.main security --install -- \
  -i test-docker-inventory.yml \
  -e @.vault/dev.yml \
  -vv

# Run base playbook
echo -e "${YELLOW}7. Running base playbook...${NC}"
python -m dev.claudia.cli.main base --install -- \
  -i test-docker-inventory.yml \
  -e @.vault/dev.yml \
  -vv

echo -e "${GREEN}=== All tests completed successfully! ===${NC}"

# Cleanup
echo -e "${YELLOW}Cleaning up...${NC}"
docker rm -f ansible-harden-test
rm -f test-docker-inventory.yml

echo -e "${GREEN}Done!${NC}"