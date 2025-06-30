# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Code Execution Rules

**CRITICAL EXECUTION GUIDELINES** - Follow these rules before ANY execution:

### Communication Rules
- **NO enthusiastic confirmations**: Avoid phrases like "You're absolutely right!" or "Excellent point!" unless answering a specific question
- **Be direct and concise**: Get straight to implementation without excessive commentary

### Claudia CLI Mandatory Usage
- **ALWAYS use `./claudia` for operations**: Unless debugging internal mechanisms, use Claudia CLI for all testing and execution
- **NO direct ansible-playbook calls**: Use `./claudia [service] --install` instead of direct Ansible commands
- **Testing**: Use `./claudia [service] --install --check` for dry runs
- **Granular operations**: Use `./claudia psql --adduser foo --password 1234` for specific tasks

### Claudia Architecture Standards
- **Smart intuitive interface**: Make Claudia CLI intelligent and user-friendly with auto-discovery
- **Proper organization**: Keep everything under `dev/claudia/` directory with clear separation of responsibilities
- **File size limits**: Keep ALL files under 200 LOC, target 100 LOC maximum
- **Modular design**: Each component handles one responsibility (discovery, operations, execution, etc.)
- **Auto-discovery**: Services and operations automatically discovered from filesystem structure
- **Modular refactoring**: Large modules split into focused sub-modules (e.g., ansible/, postgresql/, dev_tools/)

### Development Workflow
1. **Use Claudia CLI**: `./claudia [service] --install` for recipe operations
2. **Use granular operations**: `./claudia psql --adduser foo --password 1234` for specific tasks
3. **Test with dry runs**: `./claudia [service] --install --check` before real execution  
4. **Maintain modularity**: Keep recipes focused, use `import_playbook` for orchestration
5. **File organization**: `/claudia/` for CLI, `/tasks/` for reusable components, `/recipes/` for orchestration
6. **Auto-discovery**: Add Claudia metadata headers to tasks for automatic CLI integration

## Development Commands

### Environment Setup

```bash
# Install Ansible
pip install ansible

# Navigate to project directory
cd ansible-cloudy/
```

### Core Development Commands

#### Simplified Server Setup (Recommended) - Using Claudia CLI

**🔒 Simplified Authentication Model:**

**Phase 1: Initial Security Setup** (Root + Password)
- **Connection**: `root` user with `vault_root_password` 
- **Purpose**: Install SSH keys, configure firewall, optionally create grunt service user
- **Command**: `./claudia security --install`

**Phase 2: All Operations** (Root + SSH Keys)  
- **Connection**: `root` user with SSH keys only (no passwords)
- **Purpose**: All service installations and configurations
- **Commands**: `./claudia base --install`, `./claudia psql --install`, etc.

**🚀 Workflow:**
- **Step 1 - Security**: `./claudia security --install` (root password → SSH keys)
- **Step 2 - Core**: `./claudia base --install` (basic server config)
- **Step 3 - Services**: `./claudia psql --install`, `./claudia redis --install --port 6380 --memory 512`, `./claudia nginx --install --domain example.com --ssl` (deploy services as root)

#### Environment Selection & Configuration
- **Development (default)**: `./claudia security --install` or `./claudia security --install --dev`
- **Production**: `./claudia security --install --prod`, `./claudia django --install --prod`
- **CI/CD**: `./claudia security --install --ci`, `./claudia redis --install --ci`
- **Custom Inventory**: `./claudia security --install -i inventory/custom.yml`
- **Custom Vault**: `./claudia security --install -e .vault/prod-secrets.yml`
- **Combined**: `./claudia psql --install --prod -e .vault/prod-db.yml -H 192.168.1.100`

#### Universal Parameter Support & Granular Operations
- **PostgreSQL**: `./claudia psql --install --port 5544 --pgis`, `./claudia psql --adduser foo --password 1234`, `./claudia psql --list-users`
- **Redis**: `./claudia redis --install --port 6380 --memory 512 --password secret`, `./claudia redis --configure-port 6380`, `./claudia redis --restart`
- **Nginx**: `./claudia nginx --install --domain example.com --ssl --backends "192.168.1.10:8080,192.168.1.11:8080"`, `./claudia nginx --setup-ssl example.com`
- **MySQL**: `./claudia mysql --install --port 3307 --root-password secret`
- **Auto-discovery**: All operations automatically discovered from task files
- **Smart parameters**: Intuitive parameter names mapped to Ansible variables
- **Backward compatibility**: Traditional `-- -e "var=value"` syntax still supported

#### Development Tools
- **Bootstrap**: `./bootstrap.sh` - Sets up .venv with all development tools
- **Claudia CLI**: `./claudia security --install` - Intelligent infrastructure management
- **Claudia Dev Commands**: `./claudia dev validate` (pre-commit suite), `./claudia dev syntax`, `./claudia dev comprehensive`, `./claudia dev lint`, `./claudia dev test`
- **Authentication test**: `./claudia dev test` - Test server authentication flow
- **Service discovery**: `./claudia --list-services` - Show all auto-discovered services
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
./claudia security --install
```

#### Method 2: Environment Variable
Set the sudo password via environment variable:

```bash
# Set sudo password for the session
export ANSIBLE_BECOME_PASS=secure123

# Or provide it directly with the command
ANSIBLE_BECOME_PASS=secure123 ./claudia security --install
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
./claudia security --install

# 2. Deploy base configuration
./claudia base --install

# 3. Deploy services
./claudia psql --install    # PostgreSQL database
./claudia django --install  # Django web application
./claudia redis --install   # Redis cache
./claudia nginx --install   # Nginx load balancer
```

**Security Features**:
- ✅ Root login disabled (`PermitRootLogin no`)
- ✅ Grunt user with SSH key authentication
- ✅ Custom SSH port (default: 22022)
- ✅ UFW firewall configured
- ✅ Sudo access for privileged operations

**Output Control System**:
- ✅ **Default**: Shows only changes and failures (clean output)
- ✅ **Minimal**: `ANSIBLE_STDOUT_CALLBACK=minimal` (compact format)
- ✅ **One-line**: `ANSIBLE_STDOUT_CALLBACK=oneline` (single line per task)
- ✅ **Verbose**: `./claudia ... -v` (detailed debugging)
- ✅ **Always Shown**: Changed tasks, failed tasks, unreachable hosts
- ✅ **Hidden by Default**: Successful unchanged tasks, skipped tasks

### Claudia Recipe Examples

```bash
# Claudia CLI - Universal Parameter Support
# Help and Discovery (default action)
./claudia security                  # Show security help and configuration options
./claudia base                      # Show base setup help and variables
./claudia psql                      # Show PostgreSQL help and configuration
./claudia redis                     # Show Redis help and all parameters
./claudia nginx                     # Show Nginx help and configuration

# Step 1: Security setup
./claudia security --install
./claudia security --install --dev    # Development environment (default)
./claudia security --install --prod   # Production environment
./claudia security --install --ci     # CI/CD environment

# Step 2: Core setup  
./claudia base --install
./claudia base --install --prod

# Step 3: Service deployment with parameters
./claudia psql --install --port 5544 --pgis           # PostgreSQL with PostGIS on custom port
./claudia django --install                             # Django web application
./claudia redis --install --port 6380 --memory 512    # Redis with custom port and memory
./claudia nginx --install --domain example.com --ssl  # Nginx with SSL domain

# Environment-specific deployments
./claudia security --install --prod
./claudia django --install --prod
./claudia redis --install --prod --memory 1024
./claudia psql --install --ci

# Custom inventory and vault files
./claudia security --install -i inventory/staging.yml
./claudia psql --install -e .vault/prod-secrets.yml
./claudia django --install --prod -i inventory/web-servers.yml -e .vault/prod-web.yml

# Target specific hosts
./claudia security --install -H 192.168.1.100
./claudia psql --install --prod -H 10.0.0.50 -e .vault/prod.yml

# Granular operations (no recipe installation)
./claudia psql --adduser myuser --password secret123  # Add PostgreSQL user
./claudia psql --adddb myapp --owner myuser           # Add database with owner
./claudia redis --configure-port 6380                 # Change Redis port
./claudia redis --set-password newpass               # Change Redis password
./claudia nginx --setup-ssl example.com              # Setup SSL for domain
./claudia nginx --add-domain api.example.com         # Add new domain

# Dry runs and testing
./claudia redis --install --check --port 6380
./claudia nginx --install --check --domain example.com --ssl
./claudia security --install --prod --check

# Legacy syntax (not recommended - use universal parameters instead)
# OLD: ./claudia redis --install -- -e "redis_port=6380" -e "redis_memory_mb=512"
# NEW: ./claudia redis --install --port 6380 --memory 512

# Development and validation
./claudia dev validate                  # Pre-commit validation suite (recommended)
./claudia dev comprehensive             # Comprehensive validation (includes structure)
./claudia dev syntax                    # Quick syntax check
./claudia dev test                      # Authentication flow test
./claudia dev lint                      # Ansible linting
./claudia dev spell                     # Spell checking

# Service discovery
./claudia --list-services               # Show all available services and operations
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
Claudia supports multiple environments with flexible configuration options:

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
./claudia security --install --prod -e .vault/prod-secrets.yml

# Use custom inventory with host override
./claudia psql --install -i inventory/staging.yml -H 10.0.0.100

# CI environment with custom variables
./claudia redis --install --ci -e ci-overrides.yml

# Development (default) with all options
./claudia nginx --install --dev -i custom.yml -e secrets.yml -H 192.168.1.50
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
│   └── services/         # Service management (Docker, Redis, VPN)
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
    ansible_port: 22022
    
  children:
    generic_servers:
      hosts:
        production-web:
          ansible_host: 10.10.10.100
          hostname: web.example.com
          admin_user: admin
          admin_password: secure123
          ssh_port: 22022
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

Claudia includes a comprehensive pytest-based test suite:

```bash
# Run all tests
cd dev/claudia
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

### Core Claudia Commands
- **Show service help**: `./claudia [service-name]` (security, base, psql, redis, nginx, etc.)
- **Execute recipes with parameters**: `./claudia [service-name] --install [options]` (requires explicit flag for safety)
- **Granular operations**: `./claudia psql --adduser foo --password 1234` (no recipe installation)
- **Test authentication flow**: `./claudia dev test`
- **Service discovery**: `./claudia --list-services` (show all available services and operations)
- **Clean output (changes only)**: Configured in `ansible.cfg` with `display_skipped_hosts = no`
- **Alternative output formats**:
  - `ANSIBLE_STDOUT_CALLBACK=minimal ./claudia ... --install` (compact format)
  - `ANSIBLE_STDOUT_CALLBACK=oneline ./claudia ... --install` (one line per task)
  - Standard verbose: `./claudia ... --install -v` (detailed debugging)

### Claudia Service Examples
```bash
# Help and configuration (default action)
./claudia security              # Show security help and options
./claudia base                  # Show base configuration help
./claudia psql                  # Show PostgreSQL help and parameters
./claudia redis                 # Show Redis help and all available parameters
./claudia nginx                 # Show Nginx help and configuration options

# Recipe execution with environment selection
./claudia security --install                              # Dev environment (default)
./claudia security --install --prod                       # Production environment
./claudia security --install --ci                         # CI/CD environment
./claudia security --install -i inventory/staging.yml     # Custom inventory
./claudia security --install -e .vault/prod.yml          # Custom vault
./claudia security --install --prod -e .vault/prod.yml -H 10.0.0.50  # All options

# Recipe execution with universal parameters
./claudia openvpn --install                              # VPN server setup (OpenVPN with Docker)
./claudia django --install --prod                        # Django in production
./claudia psql --install --port 5544 --pgis             # PostgreSQL with PostGIS on custom port
./claudia redis --install --ci --port 6380 --memory 512 # Redis in CI with custom settings
./claudia nginx --install --domain example.com --ssl    # Nginx with SSL domain configuration

# Granular operations (service-specific tasks)
./claudia psql --adduser myuser --password secret123    # Add PostgreSQL user
./claudia psql --adddb myapp --owner myuser             # Add database with owner
./claudia redis --configure-port 6380                   # Change Redis port
./claudia nginx --setup-ssl example.com                 # Setup SSL for specific domain
```

### Ansible Security Features
- ✅ **Safe Authentication Flow**: UFW firewall configured before SSH port changes
- ✅ **SSH Key Management**: Automated public key installation and validation
- ✅ **Connection Transition**: Seamless root-to-admin user switching
- ✅ **Firewall Integration**: Port 22022 opened before SSH service restart
- ✅ **Sudo Configuration**: NOPASSWD sudo access for admin operations
- ✅ **Root Login Disable**: Safely disabled after admin user verification

### Ansible Inventory Configuration
The `inventory/test-recipes.yml` file configures connection parameters:
```yaml
all:
  vars:
    ansible_user: admin          # Connect as admin user (after setup)
    ansible_ssh_pass: secure123  # Admin password
    ansible_port: 22022          # Custom SSH port
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

Claudia uses a simple vault system for credential management without encryption complexity.

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

# Use with Claudia commands
./claudia psql --install -- -e @.vault/my-dev.yml
```

**Simple Configuration Benefits:**
- 🎛️ **Centralized Config** - All credentials in one place per environment
- 📋 **Fallback Defaults** - Safe defaults if vault variables not set
- 🛡️ **Clear Organization** - vault_* prefix for all sensitive variables
- 📝 **No Encryption Overhead** - Simple YAML files for open source projects

### Usage with Playbooks

```bash
# Use vault with Claudia commands
./claudia psql --install -- -e @.vault/my-dev.yml

# Production deployment
./claudia psql --install --prod -- -e @.vault/my-prod.yml

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
vault_ssh_port: 22022

# === GLOBAL SERVER CONFIGURATION ===
vault_git_user_full_name: "Your Full Name"
vault_git_user_email: "your.email@example.com"
vault_timezone: "America/New_York"
vault_locale: "en_US.UTF-8"

# === SERVICE CREDENTIALS ===
vault_postgres_password: "your_postgres_password"
vault_redis_password: "your_redis_password"
vault_vpn_passphrase: "your_vpn_passphrase"
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
./claudia security --install

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
./claudia base --install
./claudia psql --install
./claudia redis --install

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
- ✅ Secure SSH port (22022 instead of 22)
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