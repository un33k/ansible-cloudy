# Ansible Cloudy

A modular, scalable automation framework for Debian-based Linux servers using Ansible + Docker.

## Architecture

**Atomic → Composed → Recipes**

- **Atomic Roles**: Single-purpose, reusable components
- **Composed Playbooks**: Multi-role orchestration  
- **Complete Recipes**: Full-stack solutions

## Quick Start

```bash
# Bootstrap environment
./scripts/bootstrap.sh

# Activate virtual environment
source venv/bin/activate

# Deploy baseline server configuration
./scripts/deploy.sh -p playbooks/server-baseline.yml

# Deploy complete LAMP stack
./scripts/deploy.sh -p recipes/lamp-stack/site.yml -i inventory/production
```

## Project Structure

```
├── roles/           # Atomic, single-purpose roles
├── playbooks/       # Composed multi-role tasks  
├── recipes/         # Complete solutions
├── docker/          # Container configurations
├── inventory/       # Server definitions
├── group_vars/      # Global group variables
└── scripts/         # Utility scripts
```

## Available Roles

### System
- `system/apt-update` - Package management
- `system/timezone` - Timezone configuration  
- `system/users` - User account management

### Security
- `security/ssh-hardening` - SSH security configuration
- `security/firewall` - Firewall rules management

### Services
- `services/docker` - Docker engine installation
- `services/nginx` - Web server setup
- `services/postgresql` - Database server

## Docker Variants

- `debian-base` - Base Debian container
- `web-server` - Nginx + PHP-FPM stack
- `database` - PostgreSQL optimized
- `monitoring` - System monitoring stack

## Usage Examples

```bash
# Check syntax
ansible-playbook --syntax-check playbooks/web-server.yml

# Dry run
./scripts/deploy.sh -p playbooks/web-server.yml -c

# Deploy with custom variables
./scripts/deploy.sh -p playbooks/web-server.yml -e 'web_domain=example.com'

# Test with Docker
cd docker/debian-base && docker-compose up -d
```