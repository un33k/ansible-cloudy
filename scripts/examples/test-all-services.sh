#!/bin/bash
# Test all Ansible Cloudy services
# This script runs syntax checks for all available services

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Testing All Ansible Cloudy Services ===${NC}"

# Ensure we're in the project root
cd "$(dirname "$0")/../.."

# Test environment setup
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Setting up environment...${NC}"
    ./bootstrap.sh -y
fi

source .venv/bin/activate

# Test development commands
echo -e "${YELLOW}Testing development commands...${NC}"
cli dev syntax
cli dev validate

# Test core services
echo -e "${YELLOW}Testing core services...${NC}"
cli harden --install --check
cli security --install --check
cli base --install --check

# Test database services
echo -e "${YELLOW}Testing database services...${NC}"
cli psql --install --check
cli pgvector --install --check
cli postgis --install --check

# Test web services
echo -e "${YELLOW}Testing web services...${NC}"
cli nginx --install --check
cli nodejs --install --check
cli django --install --check

# Test cache services
echo -e "${YELLOW}Testing cache services...${NC}"
cli redis --install --check

# Test advanced services
echo -e "${YELLOW}Testing advanced services...${NC}"
cli standalone --install --check
cli pgbouncer --install --check

echo -e "${GREEN}=== All tests passed! ===${NC}"