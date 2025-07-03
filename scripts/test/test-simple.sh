#!/bin/bash
# Simple test to verify the harden playbook works

set -e

# Activate virtual environment
source .venv/bin/activate

# Test ansible syntax
echo "Testing harden playbook syntax..."
ansible-playbook --syntax-check \
  cloudy/playbooks/recipes/core/harden.yml \
  -i cloudy/inventory/dev.yml \
  -e @.vault/dev.yml

echo "Testing security playbook syntax..."
ansible-playbook --syntax-check \
  cloudy/playbooks/recipes/core/security.yml \
  -i cloudy/inventory/dev.yml \
  -e @.vault/dev.yml

echo "Testing base playbook syntax..."
ansible-playbook --syntax-check \
  cloudy/playbooks/recipes/core/base.yml \
  -i cloudy/inventory/dev.yml \
  -e @.vault/dev.yml

echo "All syntax checks passed!"

# Test CLI commands
echo "Testing CLI harden help..."
python -m dev.cli.cli.main harden --help

echo "Testing CLI security help..."
python -m dev.cli.cli.main security --help

echo "Testing CLI base help..."
python -m dev.cli.cli.main base --help

echo "All tests passed!"