# Quick Start Guide

Get up and running with Ansible Cloudy in 5 minutes!

## Prerequisites

- Linux/macOS machine for running Ansible
- Target server with SSH access (Ubuntu/Debian)
- Python 3.8+ installed

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ansible-cloudy.git
cd ansible-cloudy

# Run bootstrap to set up environment
./bootstrap.sh

# Activate virtual environment
source .venv/bin/activate
```

## First Deployment

### 1. Set up your vault file

```bash
# Copy the example vault
cp .vault/dev.yml.example .vault/my-server.yml

# Edit with your server credentials
vim .vault/my-server.yml
```

### 2. Create inventory entry

Edit `cloudy/inventory/dev.yml` and update the test server:

```yaml
hosts:
  my-server:
    ansible_host: YOUR_SERVER_IP
    hostname: my-server.example.com
```

### 3. Run security setup

```bash
# Initial security setup (uses root password)
cli security --install
```

### 4. Deploy services

```bash
# Install PostgreSQL
cli psql --install

# Install Redis  
cli redis --install

# Install Nginx
cli nginx --install
```

## What's Next?

- Read the [First Deployment Guide](first-deployment.md) for detailed instructions
- Explore [Available Recipes](../operations/recipes.md) for different deployment options
- Learn about [Configuration](../operations/configuration.md) with vault files

## Getting Help

```bash
# Show available services
cli --list-services

# Get help for any service
cli psql --help
cli redis --help
cli security --help

# Run validation checks
cli dev precommit
```