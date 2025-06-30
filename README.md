# Ansible Cloudy - Infrastructure Automation

**Ansible Cloudy** is a comprehensive infrastructure automation toolkit featuring the **Claudia CLI** - an intelligent command-line interface that simplifies server deployment and management through Ansible playbooks.

## 🚀 Key Features

- **🔐 Enterprise Security**: Two-phase authentication with SSH keys and secure firewall configuration
- **🧠 Intelligent CLI**: Auto-discovery of services and operations with intuitive parameter mapping
- **⚡ Universal Parameters**: `./claudia redis --install --port 6380 --memory 512` instead of complex Ansible variables
- **🔄 Granular Operations**: Service-specific tasks like `./claudia psql --adduser foo --password 1234`
- **🛡️ Production-Ready**: Secure defaults, comprehensive validation, and enterprise-grade security model

## Quick Start

### Installation
```bash
# Bootstrap environment (recommended)
./bootstrap.sh
source .venv/bin/activate

# Or install manually
pip install ansible
```

### Basic Usage
```bash
# Show help and configuration options (default action)
./claudia security    # View security setup help and available variables
./claudia psql        # View PostgreSQL setup help and configuration
./claudia redis       # View Redis setup help and all parameters

# Execute recipes with universal parameter support
./claudia security --install                           # Security setup (admin user, SSH keys, firewall)
./claudia base --install                               # Base configuration (hostname, git, timezone, swap)
./claudia psql --install --port 5544 --pgis           # PostgreSQL with PostGIS on custom port
./claudia redis --install --port 6380 --memory 512    # Redis with custom port and memory
./claudia nginx --install --domain example.com --ssl  # Nginx with SSL domain

# Environment selection
./claudia psql --install --dev                        # Use dev environment (default)
./claudia psql --install --prod                       # Use production environment
./claudia psql --install --ci                         # Use CI environment
./claudia psql --install -i custom-inventory.yml      # Use custom inventory file

# Granular operations (no recipe installation)
./claudia psql --adduser myuser --password secret123  # Add PostgreSQL user
./claudia redis --configure-port 6379                 # Change Redis port
./claudia nginx --setup-ssl example.com               # Setup SSL for domain
```

## 🏗️ Architecture Overview

### Claudia CLI - Intelligent Command Interface
The **Claudia CLI** is the heart of Ansible Cloudy, providing:

- **🔍 Auto-Discovery**: Services and operations automatically discovered from filesystem
- **📋 Universal Parameters**: Intuitive CLI with `--port`, `--domain`, `--ssl` instead of complex Ansible variables
- **🎯 Granular Operations**: Service-specific tasks without full recipe installation
- **🔒 Smart Security**: Two-phase authentication model with connection validation
- **📊 Clean Output**: Shows only changes and failures by default

### Service Categories
- **Core**: `security`, `base` - Foundation server setup
- **Database**: `psql`, `postgis` - PostgreSQL with spatial extensions
- **Web**: `django`, `nginx` - Web applications and load balancing
- **Cache**: `redis` - High-performance caching
- **VPN**: `openvpn` - Secure remote access
- **Development**: `dev` - Validation and testing tools

### Security Model
- **🔑 SSH Key Authentication**: Root access via SSH keys only (no password brute force)
- **👤 Admin Emergency Access**: Dual authentication (password + SSH keys) for manual operations
- **🔥 Smart Firewall**: UFW automatically configured with service-specific ports
- **🚪 Custom SSH Port**: Default port 22022 with seamless migration
- **🛡️ Enterprise Hardening**: Fail2ban, connection limits, secure SSH configuration

### 📊 Output Control
```bash
# Show help by default (safe exploration)
./claudia security

# Execute with clean output (show only changes and failures)
./claudia security --install

# Compact output
ANSIBLE_STDOUT_CALLBACK=minimal ./claudia security --install

# Verbose debugging
./claudia security --install -v
```

## 📁 Project Structure

```
ansible-cloudy/
├── claudia                    # Main CLI entry point
├── bootstrap.sh              # Environment setup script
├── cloudy/                   # Ansible automation core
│   ├── playbooks/recipes/    # High-level deployment recipes
│   │   ├── core/            # security.yml, base.yml
│   │   ├── db/              # psql.yml, postgis.yml
│   │   ├── www/             # django.yml
│   │   ├── cache/           # redis.yml
│   │   ├── lb/              # nginx.yml
│   │   └── vpn/             # openvpn.yml
│   ├── tasks/                # Granular, reusable task files
│   │   ├── sys/             # System operations (SSH, firewall, users)
│   │   ├── db/              # Database automation (PostgreSQL, MySQL)
│   │   ├── web/             # Web server management
│   │   └── services/        # Service management (Docker, Redis, VPN)
│   ├── templates/           # Configuration file templates
│   ├── inventory/           # Server inventory configurations
│   └── ansible.cfg          # Ansible configuration
├── dev/                     # Development tools and CLI implementation
│   ├── claudia/             # Python CLI implementation
│   │   ├── cli/             # Command parsing and routing
│   │   ├── operations/      # Service-specific operations
│   │   ├── discovery/       # Auto-discovery of services
│   │   ├── execution/       # Ansible execution engine
│   │   └── utils/           # Configuration and utilities
│   └── validate.py         # Development validation tools
└── docs/                   # Project documentation
    ├── CONTRIBUTING.md     # Development guidelines
    ├── USAGE.md           # Complete usage guide
    ├── IMPLEMENTATION_PLAN.md  # Technical implementation details
    ├── DEVELOPMENT.md     # Development tools and CLI implementation guide
    └── SECRETS.md         # Ansible Vault configuration and credential management
```

## ⚙️ Configuration

### 1. Server Inventory
Configure servers in `cloudy/inventory/dev.yml`:
```yaml
all:
  vars:
    ansible_user: admin         # Connect as admin user (after setup)
    ansible_port: 22022         # Custom SSH port
    ansible_host_key_checking: false
    
  children:
    generic_servers:
      hosts:
        my-server:
          ansible_host: 10.10.10.100
          hostname: my-server.example.com
          admin_user: admin
          admin_password: secure123
```

### 2. Vault Configuration (Recommended)
For production deployments, use Ansible Vault for credentials:
```bash
# Create encrypted vault
./claudia vault --create

# Edit vault with real credentials
./claudia vault --edit
```

Example vault content:
```yaml
vault_root_password: "secure_root_password_123"
vault_admin_password: "secure_admin_password_456"
vault_admin_user: "admin"
vault_ssh_port: 22022
```

### 3. Two-Phase Authentication Model
**Phase 1 - Initial Security Setup** (Root + Password):
```yaml
# For fresh servers - inventory configuration
ansible_user: root
ansible_ssh_pass: "{{ vault_root_password }}"
ansible_port: 22
```

**Phase 2 - Service Operations** (Admin + SSH Keys):
```yaml
# After security setup - inventory configuration
ansible_user: "{{ vault_admin_user | default('admin') }}"
ansible_port: "{{ vault_ssh_port | default(22022) }}"
```

## 🎯 Workflow Examples

### Complete Web Application Stack
```bash
# Step 1: Secure server foundation (creates admin user, SSH keys, firewall)
./claudia security --install

# Step 2: Base server configuration (hostname, git, timezone, swap)
./claudia base --install

# Step 3: Database layer with custom parameters
./claudia psql --install --port 5544 --pgis

# Step 4: Web application layer
./claudia django --install

# Step 5: Load balancer with SSL domain
./claudia nginx --install --domain example.com --ssl
```

### Redis Cache Server with Custom Configuration
```bash
# View Redis configuration options
./claudia redis

# Install Redis with custom port and memory limit
./claudia redis --install --port 6380 --memory 512 --password secret123

# Granular operations (without recipe installation)
./claudia redis --configure-port 6379    # Change port
./claudia redis --set-password newpass   # Update password
```

### PostgreSQL Database Management
```bash
# Install PostgreSQL with PostGIS on custom port
./claudia psql --install --port 5544 --pgis

# Database user management (granular operations)
./claudia psql --adduser myapp --password secret123
./claudia psql --adddb myapp_db --owner myapp
./claudia psql --list-users
./claudia psql --list-databases
```

### VPN Server Deployment
```bash
# View OpenVPN configuration options
./claudia openvpn

# Deploy complete VPN server with Docker
./claudia openvpn --install
```

## 🧪 Development & Validation

Ansible Cloudy includes comprehensive development tools:

```bash
# Environment setup
./bootstrap.sh                    # Setup Python virtual environment with all tools
source .venv/bin/activate         # Activate development environment

# Validation commands via Claudia CLI
./claudia dev syntax              # Quick syntax check
./claudia dev validate            # Comprehensive validation suite
./claudia dev lint                # Ansible linting with rules
./claudia dev test                # Authentication flow testing
./claudia dev spell               # Spell check documentation

# Direct development tools
./dev/validate.py                 # Python validation script
./dev/syntax-check.sh             # Shell syntax validation
```

**Development Features:**
- ✅ **Auto-Discovery**: Services automatically discovered from filesystem
- ✅ **Universal Parameters**: Smart parameter mapping for all services
- ✅ **Comprehensive Validation**: YAML, Ansible, inventory, and template validation
- ✅ **Clean Architecture**: Modular design with clear separation of concerns
- ✅ **File Size Limits**: All files kept under 200 LOC for maintainability

## 📚 Documentation

- **📖 [docs/USAGE.md](docs/USAGE.md)**: Complete step-by-step tutorials and troubleshooting
- **🔧 [CLAUDE.md](CLAUDE.md)**: Developer reference and Claudia CLI command documentation  
- **🤝 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)**: Development guidelines and contribution workflow
- **📋 [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)**: Technical architecture and implementation details
- **🛠️ [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)**: Development tools and CLI implementation guide
- **🔐 [docs/SECRETS.md](docs/SECRETS.md)**: Ansible Vault configuration and credential management

## 🎯 Key Benefits

- **🔄 Idempotent Operations**: Tasks only run when changes are needed
- **🛡️ Enterprise Security**: Two-phase authentication with SSH keys and firewall automation
- **🧠 Intelligent CLI**: Auto-discovery with intuitive parameter mapping
- **📊 Clean Output**: Focus on changes and failures, hide unchanged tasks
- **🏗️ Modern Tooling**: Industry-standard Ansible with intelligent Python CLI layer
- **📈 Production Ready**: Secure defaults, comprehensive validation, vault integration
- **🔧 Developer Friendly**: Granular operations, modular architecture, extensive documentation

## 🤝 Contributing

**Quick Start**: Fork the repo → run `./bootstrap.sh` → make changes → run `./claudia dev validate` → commit → PR

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed development guidelines and workflow.
