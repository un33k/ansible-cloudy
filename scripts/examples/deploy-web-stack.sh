#!/bin/bash
# Deploy a complete web application stack
# This includes security, database, cache, web app, and load balancer

set -e

# Configuration
ENVIRONMENT="${1:-prod}"
DOMAIN="${2:-example.com}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <environment> [domain]"
    echo "Example: $0 prod example.com"
    exit 1
fi

echo -e "${BLUE}=== Deploying Web Application Stack ===${NC}"
echo -e "Environment: ${ENVIRONMENT}"
echo -e "Domain: ${DOMAIN}"

# Ensure we're in the project root
cd "$(dirname "$0")/../.."
source .venv/bin/activate

# 1. Harden the server (if fresh)
echo -e "${YELLOW}Step 1: SSH Hardening...${NC}"
cli harden --install --${ENVIRONMENT} || echo "Server already hardened, continuing..."

# 2. Secure the server
echo -e "${YELLOW}Step 2: Security setup...${NC}"
cli security --install --${ENVIRONMENT}

# 3. Base configuration
echo -e "${YELLOW}Step 3: Base configuration...${NC}"
cli base --install --${ENVIRONMENT}

# 4. Database
echo -e "${YELLOW}Step 4: PostgreSQL database...${NC}"
cli psql --install --${ENVIRONMENT}

# 5. Cache
echo -e "${YELLOW}Step 5: Redis cache...${NC}"
cli redis --install --${ENVIRONMENT}

# 6. Web application (Django example)
echo -e "${YELLOW}Step 6: Web application...${NC}"
cli django --install --${ENVIRONMENT}

# 7. Load balancer with SSL
echo -e "${YELLOW}Step 7: Nginx load balancer...${NC}"
cli nginx --install --${ENVIRONMENT} --domain ${DOMAIN} --ssl

echo -e "${GREEN}=== Web stack deployment complete! ===${NC}"
echo -e "Your application should be available at: https://${DOMAIN}"