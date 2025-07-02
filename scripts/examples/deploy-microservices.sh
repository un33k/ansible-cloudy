#!/bin/bash
# Deploy a microservices infrastructure
# This deploys services across multiple servers

set -e

# Configuration
ENVIRONMENT="${1:-prod}"

# Server groups
DB_SERVERS=("db-01" "db-02")
CACHE_SERVERS=("cache-01" "cache-02")
APP_SERVERS=("app-01" "app-02" "app-03" "app-04")
LB_SERVERS=("lb-01")

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <environment>"
    echo "Example: $0 prod"
    exit 1
fi

echo -e "${BLUE}=== Deploying Microservices Infrastructure ===${NC}"
echo -e "Environment: ${ENVIRONMENT}"

# Ensure we're in the project root
cd "$(dirname "$0")/../.."
source .venv/bin/activate

# Function to deploy to multiple hosts
deploy_to_hosts() {
    local service=$1
    shift
    local hosts=("$@")
    
    for host in "${hosts[@]}"; do
        echo -e "${YELLOW}Deploying ${service} to ${host}...${NC}"
        cli ${service} --install --${ENVIRONMENT} -H ${host} || {
            echo -e "${RED}Failed to deploy ${service} to ${host}${NC}"
            exit 1
        }
    done
}

# 1. First, harden and secure all servers
echo -e "${BLUE}Phase 1: Hardening and securing all servers...${NC}"
ALL_SERVERS=("${DB_SERVERS[@]}" "${CACHE_SERVERS[@]}" "${APP_SERVERS[@]}" "${LB_SERVERS[@]}")

for server in "${ALL_SERVERS[@]}"; do
    echo -e "${YELLOW}Hardening ${server}...${NC}"
    cli harden --install --${ENVIRONMENT} -H ${server} || echo "Already hardened"
    cli security --install --${ENVIRONMENT} -H ${server}
    cli base --install --${ENVIRONMENT} -H ${server}
done

# 2. Deploy database servers
echo -e "${BLUE}Phase 2: Database servers...${NC}"
deploy_to_hosts "psql" "${DB_SERVERS[@]}"

# 3. Deploy cache servers
echo -e "${BLUE}Phase 3: Cache servers...${NC}"
deploy_to_hosts "redis" "${CACHE_SERVERS[@]}"

# 4. Deploy application servers
echo -e "${BLUE}Phase 4: Application servers...${NC}"
deploy_to_hosts "nodejs" "${APP_SERVERS[@]}"

# 5. Deploy load balancer
echo -e "${BLUE}Phase 5: Load balancer...${NC}"
BACKENDS=""
for app in "${APP_SERVERS[@]}"; do
    BACKENDS="${BACKENDS}${app}:3000,"
done
BACKENDS=${BACKENDS%,}  # Remove trailing comma

cli nginx --install --${ENVIRONMENT} -H ${LB_SERVERS[0]} --backends "${BACKENDS}"

echo -e "${GREEN}=== Microservices deployment complete! ===${NC}"
echo -e "Infrastructure:"
echo -e "  Database servers: ${DB_SERVERS[*]}"
echo -e "  Cache servers: ${CACHE_SERVERS[*]}"
echo -e "  App servers: ${APP_SERVERS[*]}"
echo -e "  Load balancer: ${LB_SERVERS[*]}"