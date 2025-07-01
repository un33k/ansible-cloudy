# Installation Guide

Detailed instructions for installing Ansible Cloudy on different platforms.

## System Requirements

### Control Machine (Where you run Ansible)
- **Operating System**: Linux, macOS, or WSL2 on Windows
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum
- **Disk**: 500MB free space

### Target Servers
- **Operating System**: Ubuntu 20.04+ or Debian 10+
- **Architecture**: x86_64 or ARM64
- **Memory**: 512MB minimum (2GB+ recommended)
- **Network**: SSH access (port 22 initially)

## Installation Methods

### Method 1: Git Clone (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/ansible-cloudy.git
cd ansible-cloudy

# Run the bootstrap script
./bootstrap.sh

# Activate the virtual environment
source .venv/bin/activate
```

### Method 2: Download Release

```bash
# Download the latest release
wget https://github.com/yourusername/ansible-cloudy/archive/v1.0.0.tar.gz
tar -xzf v1.0.0.tar.gz
cd ansible-cloudy-1.0.0

# Run bootstrap
./bootstrap.sh
source .venv/bin/activate
```

## Bootstrap Process

The bootstrap script performs the following:

1. **Creates Python virtual environment** in `.venv/`
2. **Installs Ansible** and all dependencies
3. **Sets up Claudia CLI** with aliases
4. **Configures development tools** (linters, validators)
5. **Verifies installation** and displays status

## Post-Installation Setup

### 1. Verify Installation

```bash
# Check Claudia CLI
cli --version

# List available services
cli --list-services

# Run validation
cli dev validate
```

### 2. Configure Vault

```bash
# Create your vault directory
mkdir -p .vault

# Copy example vault file
cp .vault/dev.yml.example .vault/my-environment.yml

# Edit with your credentials
vim .vault/my-environment.yml
```

### 3. Set Up Inventory

```bash
# Edit the development inventory
vim cloudy/inventory/dev.yml

# Or create a custom inventory
cp cloudy/inventory/dev.yml cloudy/inventory/my-servers.yml
```

## Platform-Specific Notes

### macOS

- Requires Xcode Command Line Tools: `xcode-select --install`
- May need to install Python 3: `brew install python@3.9`

### Ubuntu/Debian

```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git
```

### CentOS/RHEL/Rocky

```bash
# Install prerequisites
sudo yum install -y python3 python3-pip git
```

### Windows (WSL2)

1. Install WSL2 with Ubuntu
2. Follow Ubuntu instructions above
3. Clone repository in WSL2 filesystem (not /mnt/c/)

## Troubleshooting

### Python Version Issues

```bash
# Check Python version
python3 --version

# If too old, use pyenv or system package manager to install newer version
```

### Virtual Environment Issues

```bash
# Clean and recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Permission Issues

```bash
# Fix permissions if needed
chmod +x bootstrap.sh
chmod +x .venv/bin/cli
chmod +x .venv/bin/claudia
```

## Next Steps

- Continue to [First Deployment](first-deployment.md)
- Learn about [Configuration](../operations/configuration.md)
- Explore [Available Commands](../operations/commands.md)