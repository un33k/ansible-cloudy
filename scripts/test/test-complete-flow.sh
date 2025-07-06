#!/bin/bash
# Complete test of harden -> security -> base flow

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    Ansible Cloudy Complete Flow Test       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"

# Configuration
CONTAINER_NAME="ansible-test-complete"
INITIAL_PORT=2222
FINAL_PORT=2222

# Cleanup function
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    docker rm -f $CONTAINER_NAME 2>/dev/null || true
    rm -f test-inventory-complete.yml
}

# Set trap for cleanup
trap cleanup EXIT

# Start fresh
cleanup

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# 1. Start test container
echo -e "${YELLOW}1. Starting test container...${NC}"
docker run -d \
  --name $CONTAINER_NAME \
  --privileged \
  -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
  -p ${INITIAL_PORT}:22 \
  -p ${FINAL_PORT}:2222 \
  ubuntu:22.04 \
  /bin/bash -c "
    apt-get update && \
    apt-get install -y openssh-server sudo systemd python3 && \
    echo 'root:pass4now' | chpasswd && \
    mkdir -p /run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    /usr/sbin/sshd -D
  "

# Wait for container
echo -e "${BLUE}Waiting for container to start...${NC}"
sleep 10

# 2. Test initial connection
echo -e "${YELLOW}2. Testing initial SSH connection...${NC}"
sshpass -p pass4now ssh -o StrictHostKeyChecking=no -p ${INITIAL_PORT} root@localhost 'echo "✅ Initial SSH connection successful"'

# 3. Create inventory
echo -e "${YELLOW}3. Creating test inventory...${NC}"
cat > test-inventory-complete.yml << EOF
all:
  vars:
    # From vault
    git_user_full_name: "{{ vault_git_user_full_name }}"
    git_user_email: "{{ vault_git_user_email }}"
    timezone: "{{ vault_timezone }}"
    locale: "{{ vault_locale }}"
    
    # Grunt user
    grunt_user: "{{ vault_grunt_user }}"
    grunt_password: "{{ vault_grunt_password }}"
    grunt_groups: "sudo,www-data"
    grunt_ssh_private_key_file: "{{ vault_grunt_ssh_private_key_file }}"
    
  children:
    harden_targets:
      vars:
        ansible_user: "{{ vault_root_user }}"
        ansible_port: ${INITIAL_PORT}
        ansible_ssh_pass: "{{ vault_root_password }}"
        ansible_host_key_checking: "{{ vault_ssh_host_key_checking }}"
        ansible_ssh_common_args: "{{ vault_ssh_common_args }}"
      hosts:
        test-complete:
          ansible_host: localhost
    
    security_targets:
      vars:
        ansible_user: "{{ vault_root_user }}"
        ansible_port: ${FINAL_PORT}
        ansible_ssh_private_key_file: "{{ vault_root_ssh_private_key_file }}"
        ansible_host_key_checking: "{{ vault_ssh_host_key_checking }}"
        ansible_ssh_common_args: "{{ vault_ssh_common_args }}"
      hosts:
        test-complete:
          ansible_host: localhost
    
    service_targets:
      vars:
        ansible_user: "{{ vault_root_user }}"
        ansible_port: ${FINAL_PORT}
        ansible_ssh_private_key_file: "{{ vault_root_ssh_private_key_file }}"
        ansible_host_key_checking: "{{ vault_ssh_host_key_checking }}"
        ansible_ssh_common_args: "{{ vault_ssh_common_args }}"
      hosts:
        test-complete:
          ansible_host: localhost

  hosts:
    test-complete:
      ansible_host: localhost
      hostname: test-complete.example.com
EOF

# 4. Run harden playbook
echo -e "${YELLOW}4. Running HARDEN playbook...${NC}"
echo -e "${BLUE}This will:${NC}"
echo -e "  - Install SSH keys"
echo -e "  - Disable password authentication"
echo -e "  - Change SSH port to ${FINAL_PORT}"

ansible-playbook \
  cloudy/playbooks/recipes/core/harden.yml \
  -i test-inventory-complete.yml \
  -e @.vault/dev.yml \
  -e vault_ssh_port_initial=${INITIAL_PORT} \
  -e vault_ssh_port_final=${FINAL_PORT} \
  -vv

# 5. Test new connection
echo -e "${YELLOW}5. Testing SSH on new port ${FINAL_PORT}...${NC}"
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p ${FINAL_PORT} root@localhost 'echo "✅ SSH key authentication on port ${FINAL_PORT} successful!"'

# 6. Run security playbook
echo -e "${YELLOW}6. Running SECURITY playbook...${NC}"
echo -e "${BLUE}This will:${NC}"
echo -e "  - Create grunt user"
echo -e "  - Setup firewall"
echo -e "  - Install fail2ban"

ansible-playbook \
  cloudy/playbooks/recipes/core/security.yml \
  -i test-inventory-complete.yml \
  -e @.vault/dev.yml \
  -vv

# 7. Test grunt user
echo -e "${YELLOW}7. Testing grunt user access...${NC}"
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p ${FINAL_PORT} grunt@localhost 'echo "✅ Grunt user SSH access successful!"'

# 8. Run base playbook
echo -e "${YELLOW}8. Running BASE playbook...${NC}"
echo -e "${BLUE}This will:${NC}"
echo -e "  - Configure system settings"
echo -e "  - Install common packages"
echo -e "  - Setup timezone and locale"

ansible-playbook \
  cloudy/playbooks/recipes/core/base.yml \
  -i test-inventory-complete.yml \
  -e @.vault/dev.yml \
  -vv

# 9. Final verification
echo -e "${YELLOW}9. Final verification...${NC}"
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -p ${FINAL_PORT} root@localhost << 'EOF'
echo "System Information:"
echo "  Hostname: $(hostname)"
echo "  SSH Port: $(grep "^Port" /etc/ssh/sshd_config | awk '{print $2}')"
echo "  Users: $(grep -E "^(root|grunt):" /etc/passwd | cut -d: -f1 | tr '\n' ' ')"
echo "  Firewall: $(ufw status | head -1)"
echo "  Timezone: $(timedatectl show --property=Timezone --value)"
EOF

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         ALL TESTS PASSED! 🎉               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"

# The cleanup trap will handle container removal