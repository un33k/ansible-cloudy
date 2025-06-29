#!/bin/bash

# Install git hooks for security protection
# Run this script after cloning the repository

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Installing git security hooks...${NC}"

# Check if we're in a git repository
if [[ ! -d .git ]]; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Install pre-commit hook
if [[ -f .githooks/pre-commit ]]; then
    cp .githooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo -e "${GREEN}✅ Installed pre-commit hook${NC}"
else
    echo -e "${RED}❌ .githooks/pre-commit not found${NC}"
    exit 1
fi

# Install pre-push hook
if [[ -f .githooks/pre-push ]]; then
    cp .githooks/pre-push .git/hooks/pre-push
    chmod +x .git/hooks/pre-push
    echo -e "${GREEN}✅ Installed pre-push hook${NC}"
else
    echo -e "${RED}❌ .githooks/pre-push not found${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 Git security hooks installed successfully!${NC}"
echo -e "\n${YELLOW}What these hooks do:${NC}"
echo -e "  • ${GREEN}pre-commit${NC}: Warns about unencrypted vault files (allows commits)"
echo -e "  • ${GREEN}pre-push${NC}: Blocks push if vault files are unencrypted (shows how to fix)"
echo -e "\n${YELLOW}Simple Security Workflow:${NC}"
echo -e "  1. ${GREEN}git commit${NC} - Warns about unencrypted files but allows commits"
echo -e "  2. ${GREEN}./claudia vault encrypt${NC} - Encrypt vault files before pushing"
echo -e "  3. ${GREEN}git add . && git commit -m 'Encrypt vault files'${NC} - Commit encrypted files"
echo -e "  4. ${GREEN}git push${NC} - Push safely with encrypted secrets"
echo -e "\n${BLUE}Note: These hooks protect your repository from accidental secret exposure!${NC}"