#!/bin/bash
# Example: Check if a server needs hardening or is already secured

set -e

# Configuration
SERVER_IP="${1:-10.0.0.100}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo "Usage: $0 <server-ip>"
    exit 1
fi

echo -e "${BLUE}=== Checking Server Status ===${NC}"
echo -e "Server: ${SERVER_IP}"

# Activate virtual environment
cd "$(dirname "$0")/../.."
source .venv/bin/activate

# Function to test SSH connection
test_ssh() {
    local port=$1
    local method=$2
    local user=${3:-root}
    
    if [ "$method" = "password" ]; then
        # Test with password (requires sshpass)
        if command -v sshpass >/dev/null 2>&1; then
            sshpass -p "${VAULT_ROOT_PASSWORD:-pass4now}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -p $port $user@$SERVER_IP 'echo "OK"' 2>/dev/null
        else
            echo "SKIP"
        fi
    else
        # Test with SSH key
        ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i ~/.ssh/id_rsa -p $port $user@$SERVER_IP 'echo "OK"' 2>/dev/null
    fi
}

# Check port 22 with password
echo -e "${YELLOW}Testing port 22 with password...${NC}"
if [ "$(test_ssh 22 password)" = "OK" ]; then
    echo -e "${RED}✗ Server accepts password auth on port 22${NC}"
    echo -e "${YELLOW}→ Server needs hardening! Run: cli harden --install${NC}"
    NEEDS_HARDEN=true
else
    echo -e "${GREEN}✓ No password auth on port 22${NC}"
    NEEDS_HARDEN=false
fi

# Check port 22022 with SSH key
echo -e "${YELLOW}Testing port 22022 with SSH key...${NC}"
if [ "$(test_ssh 22022 key)" = "OK" ]; then
    echo -e "${GREEN}✓ SSH key auth works on port 22022${NC}"
    HARDENED=true
else
    echo -e "${RED}✗ Cannot connect on port 22022${NC}"
    HARDENED=false
fi

# Check for grunt user
echo -e "${YELLOW}Testing grunt user access...${NC}"
if [ "$(test_ssh 22022 key grunt)" = "OK" ]; then
    echo -e "${GREEN}✓ Grunt user exists and has SSH access${NC}"
    SECURITY_DONE=true
else
    echo -e "${YELLOW}○ Grunt user not configured${NC}"
    SECURITY_DONE=false
fi

# Summary
echo -e "${BLUE}=== Summary ===${NC}"
if [ "$NEEDS_HARDEN" = true ]; then
    echo -e "${RED}Status: Fresh server - needs hardening${NC}"
    echo -e "Next step: ${YELLOW}cli harden --install${NC}"
elif [ "$HARDENED" = true ] && [ "$SECURITY_DONE" = false ]; then
    echo -e "${YELLOW}Status: Hardened but security not complete${NC}"
    echo -e "Next step: ${YELLOW}cli security --install${NC}"
elif [ "$HARDENED" = true ] && [ "$SECURITY_DONE" = true ]; then
    echo -e "${GREEN}Status: Fully secured${NC}"
    echo -e "Next step: ${YELLOW}cli base --install${NC} (if not done)"
else
    echo -e "${RED}Status: Unknown - manual investigation needed${NC}"
fi