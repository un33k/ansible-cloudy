# Cloudy - Ansible Infrastructure Automation

Modern infrastructure automation tool built with Ansible for secure server deployment and management.

## Quick Start

### Installation
```bash
# Install Ansible
pip install ansible

# Clone and navigate to project
cd cloudy/
```

### Basic Usage
```bash
# Show help and configuration options (default action)
./ali security    # View security setup help and available variables
./ali base        # View base configuration help and options
./ali psql        # View PostgreSQL setup help and configuration

# Execute recipes (requires --install flag for safety)
./ali security --install    # Security setup (creates admin user, SSH keys, firewall)
./ali base --install        # Base configuration (hostname, git, timezone, swap)
./ali django --install      # Deploy Django web application
./ali redis --install       # Deploy Redis cache server
./ali nginx --install       # Deploy Nginx load balancer
```

## Features

### 🔐 Secure Server Automation
- **Safe Authentication Flow**: UFW firewall configured before SSH port changes
- **SSH Key Management**: Automated public key installation and validation  
- **Root Login Disable**: Safely disabled after admin user verification
- **Custom SSH Ports**: Default port 22022 with firewall integration

### 🚀 One-Command Server Deployment
- **Generic Server**: Secure SSH, user management, firewall
- **VPN Server**: OpenVPN with Docker containerization
- **Web Server**: Nginx, Apache, Supervisor process management
- **Database Server**: PostgreSQL, PostGIS, PgBouncer pooling
- **Cache Server**: Redis with memory management
- **Load Balancer**: Nginx with SSL termination

### 📊 Clean Output Control
```bash
# Show help by default (safe exploration)
./ali security

# Execute with default output (show only changes and failures)
./ali security --install

# Compact output
ANSIBLE_STDOUT_CALLBACK=minimal ./ali security --install

# One line per task
ANSIBLE_STDOUT_CALLBACK=oneline ./ali security --install

# Verbose debugging
./ali security --install -v
```

## Architecture

### Directory Structure
```
cloudy/
├── playbooks/recipes/     # High-level deployment recipes
├── tasks/                 # Modular task files
│   ├── sys/              # System operations (SSH, firewall, users)
│   ├── db/               # Database automation (PostgreSQL, MySQL)
│   ├── web/              # Web server management
│   └── services/         # Service management (Docker, Redis, VPN)
├── templates/            # Configuration file templates
├── inventory/            # Server inventory configurations
└── ansible.cfg          # Ansible configuration
```

### Recipe Categories
- **`cloudy/playbooks/recipes/core/security.yml`**: Initial server security setup
- **`cloudy/playbooks/recipes/core/base.yml`**: Foundation server configuration
- **`cloudy/playbooks/recipes/vpn/openvpn.yml`**: VPN with OpenVPN Docker
- **`cloudy/playbooks/recipes/www/django.yml`**: Django web server deployment
- **`cloudy/playbooks/recipes/db/psql.yml`**: PostgreSQL database server
- **`cloudy/playbooks/recipes/cache/redis.yml`**: Redis cache server
- **`cloudy/playbooks/recipes/lb/nginx.yml`**: Nginx load balancer with SSL

## Configuration

### Inventory Setup
Configure servers in `cloudy/inventory/test.yml`:
```yaml
all:
  vars:
    ansible_user: admin
    ansible_ssh_pass: secure123
    ansible_port: 22022
    
  children:
    test_servers:
      hosts:
        test-server:
          ansible_host: 10.10.10.100
          hostname: test.example.com
```

### Output Customization
The `cloudy/ansible.cfg` provides clean output by default:
```ini
[defaults]
display_skipped_hosts = no    # Hide unchanged tasks
display_ok_hosts = no         # Show only changes/failures
```

## Security

### Authentication Flow
1. Connect as root with initial password
2. Create admin user with SSH key access
3. Configure UFW firewall for new SSH port
4. Change SSH port (default: 22022)
5. Test admin user connection
6. Disable root login safely
7. Remove old SSH port from firewall

### Best Practices
- SSH keys required for production
- Custom SSH ports (not 22)
- UFW firewall enabled by default
- Admin users with sudo access
- Root login disabled after setup

## Key Benefits

This Ansible implementation provides:
- **🔄 Idempotency**: Tasks only run when changes are needed
- **🛡️ Error handling**: Rollback and validation built-in
- **🎯 Clean output**: Focus on changes and failures
- **🏗️ Modern tooling**: Industry-standard configuration management
- **📈 Scalability**: Easy multi-server deployments
- **🧪 Validation tools**: Ali CLI provides syntax and structure checking
- **📚 Extensive documentation**: Complete guides and examples
- **🔧 Developer-friendly**: Granular tasks and composable recipes

## Examples

### Complete Web Stack
```bash
# 1. Secure server foundation
./ali security --install

# 2. Base configuration
./ali base --install

# 3. Database layer
./ali psql --install

# 4. Web application layer
./ali django --install

# 5. Load balancer (optional)
./ali nginx --install
```

### VPN Server
```bash
# View VPN setup help and configuration
./ali openvpn

# Execute VPN deployment
./ali openvpn --install
```

## Documentation

- **📚 [USAGE.md](USAGE.md)**: Complete step-by-step tutorials and troubleshooting
- **🔧 [CLAUDE.md](CLAUDE.md)**: Developer reference and command documentation  
- **🤝 [CONTRIBUTING.md](CONTRIBUTING.md)**: Development guidelines and contribution workflow
- **🐛 Issues**: Report bugs and feature requests via GitHub Issues

## Quick Links

- 🚀 [Getting Started](USAGE.md) - Complete setup and usage guide
- 🔧 [Ali CLI Commands](CLAUDE.md) - Simplified Ansible wrapper commands
- 🏗️ [Development Setup](CONTRIBUTING.md) - Contributing to the project
- 🧪 [Validation Tools](dev/) - Syntax checking and validation scripts

## 🧪 Testing & Validation

Ansible Cloudy includes development validation tools:

```bash
# Ali CLI validation commands  
./ali dev syntax      # Quick syntax check
./ali dev validate     # Comprehensive validation
./ali dev lint         # Ansible linting
./ali dev test         # Authentication flow test

# Traditional validation
./dev/syntax-check.sh  # Direct syntax validation
./dev/validate.py      # Python validation script
```

**Validation Coverage:**
- ✅ Syntax validation for all playbooks and tasks
- ✅ YAML structure validation
- ✅ Ansible configuration validation
- ✅ Authentication flow testing

## 🤝 Contributing

**Quick Contribution Workflow**: Fork the repo, install Ansible (`pip install ansible`), make your changes to tasks or recipes, run `./ali dev validate` to check syntax and structure, commit with descriptive messages, and submit a PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.
