#!/bin/bash
set -euo pipefail

# Ansible Cloudy Bootstrap Script
echo "🚀 Bootstrapping Ansible Cloudy Environment"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv git curl
elif command -v yum &> /dev/null; then
    sudo yum install -y python3 python3-pip git curl
else
    echo "❌ Unsupported package manager"
    exit 1
fi

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Ansible and dependencies
echo "🔧 Installing Ansible..."
pip install --upgrade pip
pip install ansible ansible-lint molecule[docker] pytest

# Install Ansible collections
echo "📚 Installing Ansible collections..."
ansible-galaxy install -r requirements.yml

# Build base Docker image
echo "🐳 Building base Docker images..."
cd docker/debian-base
docker-compose build
cd ../..

echo "✅ Bootstrap complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Configure your inventory in inventory/"
echo "3. Run a playbook: ansible-playbook playbooks/server-baseline.yml"
echo "4. Test with Docker: cd docker/debian-base && docker-compose up -d"