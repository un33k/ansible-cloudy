#!/bin/bash
# Quick development environment setup
# Sets up a single server with all services for development

set -e

# Configuration
SERVER_IP="${1:-localhost}"
ENVIRONMENT="dev"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Quick Development Setup ===${NC}"
echo -e "Target: ${SERVER_IP}"

# Ensure we're in the project root
cd "$(dirname "$0")/../.."
source .venv/bin/activate

# Use the standalone recipe for all-in-one setup
echo -e "${YELLOW}Deploying all-in-one development stack...${NC}"

# 1. Harden (if needed)
cli harden --install || echo "Already hardened"

# 2. Use standalone for everything else
cli standalone --install -- -e ansible_host=${SERVER_IP}

echo -e "${GREEN}=== Development setup complete! ===${NC}"
echo -e "Services available:"
echo -e "  - PostgreSQL: ${SERVER_IP}:5432"
echo -e "  - Redis: ${SERVER_IP}:6379"
echo -e "  - Nginx: http://${SERVER_IP}"
echo -e "  - SSH: ${SERVER_IP}:2222"