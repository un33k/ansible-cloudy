#!/bin/bash
# Example: Deploy to a fresh server using the hardening flow

# This script demonstrates the complete deployment process for a fresh server
# Adjust the SERVER_IP and other variables for your environment

set -e

# Configuration - EDIT THESE
SERVER_IP="10.0.0.100"
ENVIRONMENT="dev"  # dev, prod, or ci

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Ansible Cloudy Fresh Server Deployment ===${NC}"
echo -e "Target: ${SERVER_IP}"
echo -e "Environment: ${ENVIRONMENT}"

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Step 1: Harden SSH
echo -e "${YELLOW}Step 1: Hardening SSH...${NC}"
echo -e "This will:"
echo -e "  - Install SSH keys"
echo -e "  - Disable password authentication"
echo -e "  - Change SSH port to 22022"

python -m dev.claudia.cli.main harden --install -- \
  -e ansible_host=${SERVER_IP} \
  -e @.vault/${ENVIRONMENT}.yml

# Step 2: Security Setup
echo -e "${YELLOW}Step 2: Setting up security...${NC}"
echo -e "This will:"
echo -e "  - Create grunt user (if configured)"
echo -e "  - Setup firewall"
echo -e "  - Install fail2ban"

python -m dev.claudia.cli.main security --install -- \
  -e ansible_host=${SERVER_IP} \
  -e @.vault/${ENVIRONMENT}.yml

# Step 3: Base Configuration
echo -e "${YELLOW}Step 3: Base configuration...${NC}"
echo -e "This will:"
echo -e "  - Configure timezone and locale"
echo -e "  - Install common packages"
echo -e "  - Setup system settings"

python -m dev.claudia.cli.main base --install -- \
  -e ansible_host=${SERVER_IP} \
  -e @.vault/${ENVIRONMENT}.yml

echo -e "${GREEN}=== Basic setup complete! ===${NC}"
echo -e "Server is now:"
echo -e "  - Accessible via SSH on port 22022 with keys only"
echo -e "  - Secured with firewall and fail2ban"
echo -e "  - Configured with base system settings"

echo -e "${BLUE}Next steps:${NC}"
echo -e "  cli psql --install      # Install PostgreSQL"
echo -e "  cli redis --install     # Install Redis"
echo -e "  cli nginx --install     # Install Nginx"
echo -e "  cli nodejs --install    # Install Node.js"