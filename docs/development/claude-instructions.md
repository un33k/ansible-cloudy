# Claude Instructions

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Code Execution Rules

**CRITICAL EXECUTION GUIDELINES** - Follow these rules before ANY execution:

### Communication Rules
- **NO enthusiastic confirmations**: Avoid phrases like "You're absolutely right!" or "Excellent point!" unless answering a specific question
- **Be direct and concise**: Get straight to implementation without excessive commentary

### CLI Mandatory Usage
- **ALWAYS use `cli` or `cli` for operations**: Unless debugging internal mechanisms, use CLI for all testing and execution (requires activated venv)
- **NO direct ansible-playbook calls**: Use `cli [service] --install` instead of direct Ansible commands
- **Testing**: Use `cli [service] --install --check` for dry runs
- **Granular operations**: Use `cli psql --adduser foo --password 1234` for specific tasks

### CLI Architecture Standards
- **Smart intuitive interface**: Make CLI intelligent and user-friendly with auto-discovery
- **Proper organization**: Keep everything under `dev/cli/` directory with clear separation of responsibilities
- **File size limits**: Keep ALL files under 200 LOC, target 100 LOC maximum
- **Modular design**: Each component handles one responsibility (discovery, operations, execution, etc.)
- **Auto-discovery**: Services and operations automatically discovered from filesystem structure
- **Modular refactoring**: Large modules split into focused sub-modules (e.g., ansible/, postgresql/, dev_tools/)

### Development Workflow
1. **Activate venv**: `source .venv/bin/activate` before using cli
2. **Use CLI**: `cli [service] --install` for recipe operations
3. **Use granular operations**: `cli psql --adduser foo --password 1234` for specific tasks
4. **Test with dry runs**: `cli [service] --install --check` before real execution  
4. **Maintain modularity**: Keep recipes focused, use `import_playbook` for orchestration
5. **File organization**: `/cli/` for CLI, `/tasks/` for reusable components, `/recipes/` for orchestration
6. **Auto-discovery**: Add CLI metadata headers to tasks for automatic CLI integration

## Development Commands

### Environment Setup

```bash
# Run bootstrap to set up environment
./bootstrap.sh

# Activate virtual environment
source .venv/bin/activate

# Navigate to project directory (if not already there)
cd ansible-cloudy/
```

**Note:** Once activated, you can use either `cli` or its shorter alias `cli`. Both commands are identical - `cli` is simply a convenient short alias for faster typing.

### Core Development Commands

#### Simplified Server Setup (Recommended) - Using CLI

**🔒 Simplified Authentication Model:**

**Phase 1: Initial Security Setup** (Root + Password)
- **Connection**: `root` user with `vault_root_password` 
- **Purpose**: Install SSH keys, configure firewall, optionally create grunt service user
- **Command**: `cli security --install`

**Phase 2: All Operations** (Root + SSH Keys)  
- **Connection**: `root` user with SSH keys only (no passwords)
- **Purpose**: All service installations and configurations
- **Commands**: `cli base --install`, `cli psql --install`, etc.

**🚀 Workflow:**
- **Step 1 - Security**: `cli security --install` (root password → SSH keys)
- **Step 2 - Core**: `cli base --install` (basic server config)
- **Step 3 - Services**: `cli psql --install`, `cli redis --install --port 6380 --memory 512`, `cli nginx --install --domain example.com --ssl` (deploy services as root)

#### Environment Selection & Configuration
- **Development (default)**: `cli security --install` or `cli security --install --dev`
- **Production**: `cli security --install --prod`, `cli django --install --prod`
- **CI/CD**: `cli security --install --ci`, `cli redis --install --ci`
- **Custom Inventory**: `cli security --install -i inventory/custom.yml`
- **Custom Vault**: `cli security --install -e .vault/prod-secrets.yml`
- **Combined**: `cli psql --install --prod -e .vault/prod-db.yml -H 192.168.1.100`

#### Universal Parameter Support & Granular Operations
- **PostgreSQL**: `cli psql --install --port 5544 --pgis`, `cli psql --adduser foo --password 1234`, `cli psql --list-users`
- **Redis**: `cli redis --install --port 6380 --memory 512 --password secret`, `cli redis --configure-port 6380`, `cli redis --restart`
- **Nginx**: `cli nginx --install --domain example.com --ssl --backends "192.168.1.10:8080,192.168.1.11:8080"`, `cli nginx --setup-ssl example.com`
- **MySQL**: `cli mysql --install --port 3307 --root-password secret`
- **Auto-discovery**: All operations automatically discovered from task files
- **Smart parameters**: Intuitive parameter names mapped to Ansible variables
- **Backward compatibility**: Traditional `-- -e "var=value"` syntax still supported

#### Development Tools
- **Bootstrap**: `./bootstrap.sh` - Sets up .venv with all development tools
- **CLI**: `cli security --install` - Intelligent infrastructure management
- **CLI Dev Commands**: `cli dev validate` (pre-commit suite), `cli dev syntax`, `cli dev comprehensive`, `cli dev lint`, `cli dev test`
- **Authentication test**: `cli dev test` - Test server authentication flow
- **Service discovery**: `cli --list-services` - Show all auto-discovered services
- **Clean output**: Configured in `ansible.cfg` with `display_skipped_hosts = no`
- **Spell checking**: Configured via `dev/.cspell.json` with 480+ technical terms
- **Linting**: Configured via `dev/.ansible-lint.yml` and `dev/.yamlint.yml`

### Simplified Server Setup

**🎯 SIMPLE APPROACH**: Three clear steps for any server.

**Workflow**:
1. **core/security.yml** → Sets up SSH keys, firewall, optionally creates grunt service user
2. **core/base.yml** → Basic server config (hostname, git, timezone, etc.)  
3. **[category]/[service].yml** → Deploy specific services (www/django, db/psql, cache/redis, etc.)

**Security Features**:
- ✅ **Root with SSH keys**: All operations use root with key authentication
- ✅ **Optional admin user**: Created only if `vault_admin_user` is defined - for service processes
- ✅ **Firewall**: UFW configured with custom SSH port
- ✅ **Simple**: Single connection context, no user switching

### Legacy Single-Phase Setup

**⚠️ IMPORTANT**: The old single-phase approach can pull the rug out from under itself during SSH security changes.

**⚠️ CRITICAL - Sudo Password Requirements**:

Ansible requires sudo password configuration for privileged operations after switching from root to admin user. There are two ways to provide this:

#### Method 1: Inventory Configuration (Recommended)
Add the sudo password directly in your inventory file:

```yaml
generic_servers:
  hosts:
    test-generic:
      admin_password: secure123        # Login password  
      ansible_become_pass: secure123   # Sudo password
```

Then run commands normally:
```bash
cli security --install
```

#### Method 2: Environment Variable
Set the sudo password via environment variable:

```bash
# Set sudo password for the session
export ANSIBLE_BECOME_PASS=secure123

# Or provide it directly with the command
ANSIBLE_BECOME_PASS=secure123 cli security --install
```

**SSH Key Configuration**:

For secure authentication, configure SSH keys in your inventory:

```yaml
all:
  vars:
    ansible_ssh_private_key_file: ~/.ssh/id_rsa  # SSH key for initial root connection
    
generic_servers:
  hosts:
    test-generic:
      admin_password: secure123        # Login password  
      ansible_become_pass: secure123   # Sudo password
```

**How SSH Key Installation Works**:
1. **Initial connection**: Uses `root` + SSH key (if available) or password fallback
2. **Create admin user**: Sets up admin user with password
3. **Install SSH key**: Copies the public key (`~/.ssh/id_rsa.pub`) to admin user's `~/.ssh/authorized_keys`
4. **Switch connection**: Changes to admin user with SSH key authentication
5. **Secure server**: Disables root login and password authentication

**Why This is Needed**:
- Initial connection uses `root` with SSH key authentication (preferred) or password fallback
- After admin user creation and SSH key installation, connection switches to admin user
- Grunt user requires sudo password for privileged operations (firewall, system config, etc.)
- The `admin_password` is for SSH login, `ansible_become_pass` is for sudo operations
- SSH keys provide secure, passwordless authentication after setup

**Complete Secure Workflow Example**:
```bash
# 1. Setup secure server (root SSH keys + admin user, firewall, port change)
cli security --install

# 2. Deploy base configuration
cli base --install

# 3. Deploy services
cli psql --install    # PostgreSQL database
cli django --install  # Django web application
cli redis --install   # Redis cache
cli nginx --install   # Nginx load balancer
```

**Security Features**:
- ✅ Root login disabled (`PermitRootLogin no`)
- ✅ Grunt user with SSH key authentication
- ✅ Custom SSH port (default: 2222)
- ✅ UFW firewall configured
- ✅ Sudo access for privileged operations

**Output Control System**:
- ✅ **Default**: Shows only changes and failures (clean output)
- ✅ **Minimal**: `ANSIBLE_STDOUT_CALLBACK=minimal` (compact format)
- ✅ **One-line**: `ANSIBLE_STDOUT_CALLBACK=oneline` (single line per task)
- ✅ **Verbose**: `cli ... -v` (detailed debugging)
- ✅ **Always Shown**: Changed tasks, failed tasks, unreachable hosts
- ✅ **Hidden by Default**: Successful unchanged tasks, skipped tasks

### CLI Recipe Examples

```bash
# CLI - Universal Parameter Support
# Help and Discovery (default action)
cli security                  # Show security help and configuration options
cli base                      # Show base setup help and variables
cli psql                      # Show PostgreSQL help and configuration
cli redis                     # Show Redis help and all parameters
cli nginx                     # Show Nginx help and configuration

# Step 1: Security setup
cli security --install
cli security --install --dev    # Development environment (default)
cli security --install --prod   # Production environment
cli security --install --ci     # CI/CD environment

# Step 2: Core setup  
cli base --install
cli base --install --prod

# Step 3: Service deployment with parameters
cli psql --install --port 5544 --pgis           # PostgreSQL with PostGIS on custom port
cli django --install                             # Django web application
cli redis --install --port 6380 --memory 512    # Redis with custom port and memory
cli nginx --install --domain example.com --ssl  # Nginx with SSL domain
cli pgbouncer --install                          # PgBouncer on web servers (localhost:6432)

# Environment-specific deployments
cli security --install --prod
cli django --install --prod
cli redis --install --prod --memory 1024
cli psql --install --ci

# Custom inventory and vault files
cli security --install -i inventory/staging.yml
cli psql --install -e .vault/prod-secrets.yml
cli django --install --prod -i inventory/web-servers.yml -e .vault/prod-web.yml

# Target specific hosts
cli security --install -H 192.168.1.100
cli psql --install --prod -H 10.0.0.50 -e .vault/prod.yml

# Granular operations (no recipe installation)
cli psql --adduser myuser --password secret123  # Add PostgreSQL user
cli psql --adddb myapp --owner myuser           # Add database with owner
cli redis --configure-port 6380                 # Change Redis port
cli redis --set-password newpass               # Change Redis password
cli nginx --setup-ssl example.com              # Setup SSL for domain
cli nginx --add-domain api.example.com         # Add new domain
cli pgbouncer --configure-port 6433            # Change PgBouncer port
cli pgbouncer --set-pool-size 30               # Update connection pool size
cli pgbouncer --restart                        # Restart PgBouncer service

# Dry runs and testing
cli redis --install --check --port 6380
cli nginx --install --check --domain example.com --ssl
cli pgbouncer --install --check --port 6433
cli security --install --prod --check

# Legacy syntax (not recommended - use universal parameters instead)
# OLD: cli redis --install -- -e "redis_port=6380" -e "redis_memory_mb=512"
# NEW: cli redis --install --port 6380 --memory 512

# Development and validation
cli dev validate                  # Pre-commit validation suite (recommended)
cli dev comprehensive             # Comprehensive validation (includes structure)
cli dev syntax                    # Quick syntax check
cli dev test                      # Authentication flow test
cli dev lint                      # Ansible linting
cli dev spell                     # Spell checking

# Service discovery
cli --list-services               # Show all available services and operations
```

#### Recipe Categories
- **core/security.yml**: Initial server security (admin user, SSH keys, firewall, disable root)
- **core/base.yml**: Basic server configuration (hostname, git, timezone, swap)
- **db/psql.yml**: PostgreSQL database server
- **db/postgis.yml**: PostgreSQL with PostGIS extensions
- **www/django.yml**: Django web server with Nginx/Apache/Supervisor
- **cache/redis.yml**: Redis cache server
- **lb/nginx.yml**: Nginx load balancer with SSL
- **vpn/openvpn.yml**: OpenVPN server with Docker

## Environment Configuration

### Environment Selection
CLI supports multiple environments with flexible configuration options:

**Built-in Environments:**
- `--dev` (default): Development environment using `inventory/dev.yml`
- `--prod`: Production environment using `inventory/prod.yml`
- `--ci`: CI/CD environment using `inventory/ci.yml`

**Custom Configuration:**
- `-i path/to/inventory.yml`: Use custom inventory file
- `-e path/to/vars.yml`: Load additional variables (e.g., vault files)
- `-H 192.168.1.100`: Override target host IP address

**Precedence Order:**
1. Command line host override (`-H`) takes highest precedence
2. Custom inventory file (`-i`) overrides environment selection
3. Extra vars file (`-e`) adds/overrides variables
4. Environment flags (`--dev`, `--prod`, `--ci`) select built-in inventories
5. Default to development environment if nothing specified

**Examples:**
```bash
# Use production with custom vault
cli security --install --prod -e .vault/prod-secrets.yml

# Use custom inventory with host override
cli psql --install -i inventory/staging.yml -H 10.0.0.100

# CI environment with custom variables
cli redis --install --ci -e ci-overrides.yml

# Development (default) with all options
cli nginx --install --dev -i custom.yml -e secrets.yml -H 192.168.1.50
```

## Architecture Overview

### Directory Structure
```
cloudy/
├── playbooks/recipes/     # High-level deployment recipes
├── tasks/                 # Modular task files
│   ├── sys/              # System operations (SSH, firewall, users)
│   ├── db/               # Database automation (PostgreSQL)
│   ├── web/              # Web server management
│   └── services/         # Service management (Docker, Redis, VPN, PgBouncer)
├── templates/            # Configuration file templates
├── inventory/            # Server inventory configurations
└── ansible.cfg          # Ansible configuration
```

### Configuration System
Server configurations are defined in YAML inventory files:

**inventory/test-recipes.yml:**
```yaml
all:
  vars:
    ansible_user: admin
    ansible_ssh_pass: secure123
    ansible_port: 2222
    
  children:
    generic_servers:
      hosts:
        production-web:
          ansible_host: 10.10.10.100
          hostname: web.example.com
          admin_user: admin
          admin_password: secure123
          ssh_port: 2222
```

### Recipe Pattern
Recipes are high-level Ansible playbooks that:
- Include multiple task files in logical order
- Use inventory variables for configuration
- Provide idempotent server deployment
- Include error handling and validation

Example recipe structure:
```yaml
---
- name: Deploy Generic Server
  hosts: generic_servers
  become: true
  
  tasks:
    - include_tasks: ../tasks/sys/core/update.yml
    - include_tasks: ../tasks/sys/user/add-user.yml
    - include_tasks: ../tasks/sys/ssh/install-public-key.yml
    - include_tasks: ../tasks/sys/firewall/install.yml
```

## Development Requirements

- **Ansible**: ≥2.9
- **Python**: ≥3.8 (for Ansible)
- **SSH Access**: To target servers
- **Development tools**: VS Code with Ansible extension recommended

## Test Suite

CLI includes a comprehensive pytest-based test suite:

```bash
# Run all tests
cd dev/cli
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_config.py

# Run with verbose output
python -m pytest -v

# Use the test runner script
./run_tests.py
```

**Test Structure:**
- `tests/conftest.py` - Shared fixtures and test configuration
- `tests/test_config.py` - Configuration and inventory manager tests
- `tests/test_vault_loader.py` - Vault auto-loading tests
- `tests/test_argument_parser.py` - CLI argument parsing tests
- `tests/test_port_manager.py` - SSH port detection tests
- `tests/test_dev_tools.py` - Development tools tests

## Ansible Migration Commands

### Environment Setup for Ansible
```bash
# Ensure Ansible is installed
pip install ansible

# Navigate to Ansible implementation
cd ansible-cloudy/
```

### Core CLI Commands
- **Show service help**: `cli [service-name]` (security, base, psql, redis, nginx, etc.)
- **Execute recipes with parameters**: `cli [service-name] --install [options]` (requires explicit flag for safety)
- **Granular operations**: `cli psql --adduser foo --password 1234` (no recipe installation)
- **Test authentication flow**: `cli dev test`
- **Service discovery**: `cli --list-services` (show all available services and operations)
- **Clean output (changes only)**: Configured in `ansible.cfg` with `display_skipped_hosts = no`
- **Alternative output formats**:
  - `ANSIBLE_STDOUT_CALLBACK=minimal cli ... --install` (compact format)
  - `ANSIBLE_STDOUT_CALLBACK=oneline cli ... --install` (one line per task)
  - Standard verbose: `cli ... --install -v` (detailed debugging)

### CLI Service Examples
```bash
# Help and configuration (default action)
cli security              # Show security help and options
cli base                  # Show base configuration help
cli psql                  # Show PostgreSQL help and parameters
cli redis                 # Show Redis help and all available parameters
cli nginx                 # Show Nginx help and configuration options

# Recipe execution with environment selection
cli security --install                              # Dev environment (default)
cli security --install --prod                       # Production environment
cli security --install --ci                         # CI/CD environment
cli security --install -i inventory/staging.yml     # Custom inventory
cli security --install -e .vault/prod.yml          # Custom vault
cli security --install --prod -e .vault/prod.yml -H 10.0.0.50  # All options

# Recipe execution with universal parameters
cli openvpn --install                              # VPN server setup (OpenVPN with Docker)
cli django --install --prod                        # Django in production
cli psql --install --port 5544 --pgis             # PostgreSQL with PostGIS on custom port
cli redis --install --ci --port 6380 --memory 512 # Redis in CI with custom settings
cli nginx --install --domain example.com --ssl    # Nginx with SSL domain configuration

# New production-ready deployment flavors
cli pgvector --install --dimensions 1536          # PostgreSQL with AI/ML vector embeddings
cli nodejs --install --app-name api --pm2        # Node.js with PM2 process manager
cli standalone --install --app-type django       # All-in-one server deployment
cli pgbouncer --install --pool-size 30           # Connection pooling for PostgreSQL

# Granular operations (service-specific tasks)
cli psql --adduser myuser --password secret123    # Add PostgreSQL user
cli psql --adddb myapp --owner myuser             # Add database with owner
cli redis --configure-port 6380                   # Change Redis port
cli nginx --setup-ssl example.com                 # Setup SSL for specific domain
cli pgbouncer --configure-port 6433               # Configure connection pooler port
cli pgbouncer --set-pool-size 50                  # Update connection pool size
```

### Ansible Security Features
- ✅ **Safe Authentication Flow**: UFW firewall configured before SSH port changes
- ✅ **SSH Key Management**: Automated public key installation and validation
- ✅ **Connection Transition**: Seamless root-to-admin user switching
- ✅ **Firewall Integration**: Port 2222 opened before SSH service restart
- ✅ **Sudo Configuration**: NOPASSWD sudo access for admin operations
- ✅ **Root Login Disable**: Safely disabled after admin user verification
- ✅ **Kernel Hardening**: Production-ready sysctl parameters, ASLR, secure shared memory
- ✅ **SSH Hardening**: Modern ciphers, rate limiting, disabled weak protocols
- ✅ **Audit Logging**: Comprehensive audit trail with auditd and automatic rotation
- ✅ **DDoS Protection**: Nginx rate limiting, connection throttling, SYN flood protection
- ✅ **Automatic Updates**: Unattended security patches with smart reboot windows

### Ansible Inventory Configuration
The `inventory/test-recipes.yml` file configures connection parameters:
```yaml
all:
  vars:
    ansible_user: admin          # Connect as admin user (after setup)
    ansible_ssh_pass: secure123  # Admin password
    ansible_port: 2222          # Custom SSH port
    ansible_host_key_checking: false
    
  children:
    generic_servers:
      hosts:
        test-generic:
          ansible_host: 10.10.10.198
          hostname: test-generic.example.com
          admin_user: admin
          admin_password: secure123
```

### Ansible Output Control
The `ansible.cfg` file is configured for clean output:
```ini
[defaults]
host_key_checking = False
display_skipped_hosts = no    # Hide successful/unchanged tasks
display_ok_hosts = no         # Show only changes and failures
```

This shows only:
- ✅ **CHANGED** tasks (what modified the server)
- ❌ **FAILED** tasks (what went wrong)  
- ⏭️ **UNREACHABLE** hosts (connection issues)

## 🔒 Simple Vault Configuration

CLI uses a simple vault system for credential management without encryption complexity.

### Vault Directory Structure

```
.vault/
├── dev.yml.example       # Development environment template
├── prod.yml.example      # Production environment template
├── ci.yml.example        # CI/CD environment template
└── README.md            # Usage instructions
```

### Quick Start

```bash
# Copy template for your environment
cp .vault/dev.yml.example .vault/my-dev.yml

# Edit with your real credentials
vim .vault/my-dev.yml

# Use with CLI commands
cli psql --install -- -e @.vault/my-dev.yml
```

**Simple Configuration Benefits:**
- 🎛️ **Centralized Config** - All credentials in one place per environment
- 📋 **Fallback Defaults** - Safe defaults if vault variables not set
- 🛡️ **Clear Organization** - vault_* prefix for all sensitive variables
- 📝 **No Encryption Overhead** - Simple YAML files for open source projects

### Usage with Playbooks

```bash
# Use vault with CLI commands
cli psql --install -- -e @.vault/my-dev.yml

# Production deployment
cli psql --install --prod -- -e @.vault/my-prod.yml

# Direct Ansible usage
ansible-playbook -i inventory/dev.yml -e @.vault/my-dev.yml playbooks/recipes/db/psql.yml
```

### Security Best Practices

- 🔒 **Add to .gitignore** - Never commit your vault files
- 🔑 **Use strong passwords** - Generate secure credentials
- 🛡️ **Environment separation** - Different files for dev/prod
- 📋 **Regular rotation** - Update credentials periodically

### Example Vault Content

```yaml
---
# === AUTHENTICATION CREDENTIALS ===
vault_root_password: "your_root_password_here"
vault_admin_password: "your_admin_password_here"

# === CONNECTION CONFIGURATION ===
vault_admin_user: "admin"
vault_ssh_port: 2222

# === GLOBAL SERVER CONFIGURATION ===
vault_git_user_full_name: "Your Full Name"
vault_git_user_email: "your.email@example.com"
vault_timezone: "America/New_York"
vault_locale: "en_US.UTF-8"

# === SERVICE CREDENTIALS ===
vault_postgres_password: "your_postgres_password"
vault_mysql_root_password: "your_mysql_root_password"
vault_redis_password: "your_redis_password"
vault_vpn_passphrase: "your_vpn_passphrase"

# === SERVICE PORTS ===
# Default ports used when not specified (standard service ports)
# vault_postgresql_port: 5432    # PostgreSQL standard (default)
# vault_pgbouncer_port: 6432     # PgBouncer standard (default)

# Production example: Security through obscurity
# vault_postgresql_port: 6543    # Non-standard port for PostgreSQL
# vault_pgbouncer_port: 5432     # PgBouncer masquerades as PostgreSQL
vault_redis_port: 6379         # Redis default
vault_nginx_http_port: 80      # HTTP
vault_nginx_https_port: 443    # HTTPS
```

### Configuration Fallback System

All vault variables have safe defaults:

```yaml
# Inventory files use vault variables with fallbacks
git_user_full_name: "{{ vault_git_user_full_name | default('John Doe') }}"
git_user_email: "{{ vault_git_user_email | default('jdoe@example.com') }}"
timezone: "{{ vault_timezone | default('America/New_York') }}"
locale: "{{ vault_locale | default('en_US.UTF-8') }}"
ansible_user: "{{ vault_admin_user | default('admin') }}"
ansible_port: "{{ vault_ssh_port | default(22) }}"
```

**Benefits:**
- ✅ **Works without vault** - Safe defaults for testing
- ✅ **Environment-specific** - Override defaults per environment
- ✅ **Simple workflow** - Copy template → edit → use

### 🔒 Authentication Flow & Security Model

#### **Simplified Authentication Architecture**

**🎯 Design Goal**: Root SSH key authentication for ALL operations. Optional admin user ONLY for service processes.

#### **Phase 1: Initial Security Setup**
```bash
# Connection: root user with password
# Purpose: Bootstrap SSH keys and secure server
cli security --install

# What happens:
# 1. Connects as root with vault_root_password
# 2. Installs SSH keys for root user
# 3. Optionally creates admin user (only if vault_admin_user is defined)
# 4. Configures firewall and secure SSH port
# 5. Disables root password authentication
```

#### **Phase 2: All Operations**
```bash
# Connection: root user with SSH keys ONLY
# Purpose: All service installations and management
cli base --install
cli psql --install
cli redis --install

# What happens:
# 1. Connects as root with SSH keys
# 2. Full root privileges - no sudo needed
# 3. Never uses passwords for authentication
# 4. All automation runs as root (simple and secure)
```

#### **Connection Validation**
Every service recipe automatically validates:
- ✅ Connected as root user with SSH keys
- ✅ Using SSH keys (no passwords)
- ✅ Secure SSH port (2222 instead of 22)
- ✅ Full root access available
- ❌ Fails with clear error messages if wrong connection type

#### **Security Features**
- 🔐 **Root Access**: SSH key authentication for all operations
- 🔑 **SSH Keys**: All automation uses keys after initial setup
- 🛡️ **Optional Grunt User**: Only created if vault defines it - for service processes
- 🚫 **No Password Automation**: Zero passwords in automation
- 📋 **Simple Context**: All operations run as root (no user switching)
- 🔍 **Connection Validation**: Automatic verification before operations

### **🤖 Optional Grunt Service User**

The admin user is **completely optional** and only created if you define it in vault:

```yaml
# .vault/dev.yml
vault_admin_user: "myservice"    # Uncomment to enable admin user creation
vault_admin_password: "secret"
```

**When to use admin user:**
- ✅ Running web applications (nginx, apache, etc.)
- ✅ Database processes that don't need root
- ✅ Application containers and services
- ✅ Isolating service permissions

**When NOT to use admin user:**
- ❌ System administration tasks (always use root)
- ❌ Installing packages and services (use root)
- ❌ Firewall and network configuration (use root)
- ❌ SSH and security management (use root)

**Default behavior:** If `vault_admin_user` is not defined, all operations run as root with SSH keys.

### Security Best Practices

1. **Never commit credentials** - Add vault files to .gitignore
2. **Use strong passwords** - Generate secure credentials for admin user (if used)
3. **Environment separation** - Different vault files for dev/prod
4. **Regular rotation** - Update credentials periodically
5. **Follow authentication flow** - Always run security setup first
6. **Use SSH keys** - Root with SSH keys for all automation

## Connection Pooling Architecture with PgBouncer

### Overview
PgBouncer is deployed on web servers to provide local connection pooling, reducing database connections by 10x or more.

### Architecture
```
Internet → Load Balancer (Nginx/SSL)
         ↓
    Web Server 1              Web Server 2              Web Server N
    ├─ Django/Node.js        ├─ Django/Node.js        ├─ Django/Node.js
    └─ PgBouncer:6432 →      └─ PgBouncer:6432 →      └─ PgBouncer:6432 →
                          ↘         ↓         ↙
                            PostgreSQL:5432
                           (Single Database)
```

### Benefits
- **Reduced Connections**: 50 web servers × 10 connections = 500 pooled connections vs 5000 direct
- **Transaction Pooling**: Most efficient for web applications
- **Zero Code Changes**: Applications connect to localhost:6432 instead of remote database
- **Distributed Architecture**: No single point of failure (each web server has its own pooler)
- **Security**: Configurable ports via vault (can use non-standard ports for security)

### Configuration Example
```yaml
# .vault/prod.yml (production with security hardening)
vault_postgresql_port: 6543      # Non-standard port (security through obscurity)
vault_pgbouncer_port: 5432       # PgBouncer masquerades as PostgreSQL

# .vault/dev.yml (development with standard ports)
# vault_postgresql_port: 5432    # Uses default if not specified
# vault_pgbouncer_port: 6432     # Uses default if not specified
vault_pgbouncer_pool_size: 25    # Connections per pool
vault_pgbouncer_max_clients: 100 # Max client connections

# Django settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',      # Connect to local PgBouncer
        'PORT': 6432,            # PgBouncer port
        'NAME': 'myapp',
        'USER': 'myapp_user',
        'PASSWORD': 'secure_password',
    }
}
```

### Deployment Commands
```bash
# Install PgBouncer on existing web servers
cli pgbouncer --install

# Configure with custom settings
cli pgbouncer --install --port 6433 --pool-size 30

# Verify installation
cli pgbouncer --health-check
```

## Port Configuration Philosophy

### Principle: No Hardcoded Ports
All service ports are configurable via vault files, with **standard defaults** when not specified.

### Why Standard Defaults Matter
- **No surprises**: PostgreSQL on 5432 by default (as documented everywhere)
- **Easy testing**: `psql -h localhost -p 5432` works without configuration
- **Development friendly**: Standard ports work out of the box
- **Documentation aligned**: Matches official service documentation

### Configuration Examples

#### Development (Standard Ports)
```yaml
# .vault/dev.yml - Uses all standard ports
# No port configuration needed - defaults are used
```

#### Production (Security Hardened)
```yaml
# .vault/prod.yml - Non-standard ports for security
vault_postgresql_port: 6543    # Obscure port (not 5432)
vault_pgbouncer_port: 5432     # Masquerade as PostgreSQL
vault_redis_port: 7001         # Non-standard Redis port
```

### How It Works
1. **Application** → connects to localhost:5432 (thinks it's PostgreSQL)
2. **PgBouncer** → listens on 5432, pools connections
3. **Network** → PgBouncer connects to remote PostgreSQL:6543
4. **Firewall** → blocks 5432, allows only 6543 from web servers

### Benefits
- **Transparent**: Apps use standard PostgreSQL port
- **Secure**: Real database on obscure port
- **Flexible**: Change ports anytime via vault
- **No code changes**: Applications remain unchanged