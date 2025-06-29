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

**🔒 Two-Phase Authentication Model:**

**Phase 1: Initial Security Setup** (Root + Password)
- **Connection**: `root` user with `vault_root_password` 
- **Purpose**: Install SSH keys, create admin user, secure server
- **Command**: `./claudia security --install`

**Phase 2: All Service Operations** (Admin + SSH Keys)  
- **Connection**: `admin` user with SSH keys only (no passwords)
- **Purpose**: All service installations and configurations
- **Commands**: `./claudia base --install`, `./claudia psql --install`, etc.

**🚀 Workflow:**
- **Step 1 - Security**: `./claudia security --install` (root → admin transition)
- **Step 2 - Core**: `./claudia base --install` (basic server config)
- **Step 3 - Services**: `./claudia psql --install`, `./claudia redis --install --port 6380 --memory 512`, `./claudia nginx --install --domain example.com --ssl` (deploy services with parameters)

#### Production Setup
- **Claudia CLI**: `./claudia security --install --prod`, `./claudia django --install --prod`, `./claudia redis --install --prod`

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
- **Claudia Dev Commands**: `./claudia dev syntax`, `./claudia dev validate`, `./claudia dev lint`, `./claudia dev test`
- **Authentication test**: `./claudia dev test` - Test server authentication flow
- **Service discovery**: `./claudia --list-services` - Show all auto-discovered services
- **Clean output**: Configured in `ansible.cfg` with `display_skipped_hosts = no`
- **Spell checking**: Configured via `dev/.cspell.json` with 480+ technical terms
- **Linting**: Configured via `dev/.ansible-lint.yml` and `dev/.yamlint.yml`

### Simplified Server Setup

**🎯 SIMPLE APPROACH**: Three clear steps for any server.

**Workflow**:
1. **core/security.yml** → Sets up admin user, SSH keys, firewall, disables root
2. **core/base.yml** → Basic server config (hostname, git, timezone, etc.)  
3. **[category]/[service].yml** → Deploy specific services (www/django, db/psql, cache/redis, etc.)

**Security Features**:
- ✅ **Admin user**: Created with SSH key access
- ✅ **Root disabled**: No more root login after security step
- ✅ **Firewall**: UFW configured with custom SSH port
- ✅ **Simple**: No complex detection logic

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
- Admin user requires sudo password for privileged operations (firewall, system config, etc.)
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
- ✅ Admin user with SSH key authentication
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

# Step 2: Core setup  
./claudia base --install

# Step 3: Service deployment with parameters
./claudia psql --install --port 5544 --pgis           # PostgreSQL with PostGIS on custom port
./claudia django --install                             # Django web application
./claudia redis --install --port 6380 --memory 512    # Redis with custom port and memory
./claudia nginx --install --domain example.com --ssl  # Nginx with SSL domain
./claudia mysql --install --port 3307 --root-password secret  # MySQL on custom port

# Production deployment
./claudia security --install --prod
./claudia django --install --prod
./claudia redis --install --prod --memory 1024

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

# Legacy syntax (not recommended - use universal parameters instead)
# OLD: ./claudia redis --install -- -e "redis_port=6380" -e "redis_memory_mb=512"
# NEW: ./claudia redis --install --port 6380 --memory 512

# Development and validation
./claudia dev validate                  # Comprehensive validation (with fallback)
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

## Architecture Overview

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

# Recipe execution with universal parameters
./claudia security --install                              # Security setup (root SSH keys + admin user, firewall, port change)
./claudia openvpn --install                              # VPN server setup (OpenVPN with Docker)
./claudia django --install                               # Web server setup (Django with Nginx/Apache/Supervisor)
./claudia psql --install --port 5544 --pgis             # PostgreSQL with PostGIS on custom port
./claudia redis --install --port 6380 --memory 512      # Redis with custom port and memory limit
./claudia nginx --install --domain example.com --ssl    # Nginx with SSL domain configuration
./claudia mysql --install --port 3307 --root-password secret  # MySQL on custom port

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

## 🔒 Ansible Vault Management

Claudia provides integrated Ansible Vault support for secure credential management.

### Vault Commands

```bash
# Create new encrypted vault
./claudia vault --create

# Edit existing vault (prompts for password)
./claudia vault --edit

# View vault contents without editing
./claudia vault --view

# Encrypt existing plaintext file
./claudia vault --encrypt

# Decrypt vault file (⚠️ security risk)
./claudia vault --decrypt

# Change vault password
./claudia vault --rekey

# Work with environment-specific vault files
./claudia vault --create --file .secrets/dev.yml
./claudia vault --edit --file .secrets/prod.yml
./claudia vault --view --file .secrets/ci.yml

# Create vault from template
cp .secrets/vault.yml.template .secrets/dev.yml
# Edit with real credentials, then encrypt
./claudia vault --encrypt --file .secrets/dev.yml
```

### Vault File Structure

Claudia manages vault files in the `.secrets/` directory:
```
.secrets/
├── vault.yml.template     # Template showing required variables
├── dev.yml               # Development environment vault
├── prod.yml              # Production environment vault  
└── ci.yml                # CI/CD environment vault
```

**Vault Configuration Benefits:**
- 🔒 **Encrypted Storage** - All sensitive data encrypted at rest
- 🌍 **Environment-Specific** - Different configs per environment (dev/prod/staging)
- 🎛️ **Centralized Config** - Git info, timezone, SSH port, admin user in one place
- 📋 **Fallback Defaults** - Safe defaults if vault variables not set
- 🛡️ **Security Separation** - Credentials separate from code

**Security Best Practices:**
- `.secrets/` directory - Hidden, environment-separated, restrictive permissions
- Template file - Shows structure without real credentials
- Environment-specific vaults - Separate credentials per environment

### Vault Integration with Playbooks

```bash
# Use vault with Claudia commands
./claudia psql --install --prod --ask-vault-pass

# Set vault password file (for automation)
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass
./claudia psql --install --prod

# Pass vault password via file
./claudia redis --install --vault-password-file ~/.ansible-vault-pass
```

### 🔧 Vault vs .env.local Comparison

| Feature             | Ansible Vault      | .env.local             |
|---------------------|--------------------|------------------------|
| Encryption          | ✅ AES256           | ❌ Plaintext            |
| Git Safety          | ✅ Safe to commit   | ⚠️ Must be gitignored  |
| Ansible Integration | ✅ Native           | ⚠️ Manual loading      |
| Multi-environment   | ✅ Multiple vaults  | ⚠️ Multiple files      |
| Security            | ✅ Enterprise-grade | ❌ Filesystem dependent |

**Recommendation**: Use Ansible Vault for production deployments and sensitive credentials.

### Vault Security Features

- 🔒 **AES256 Encryption** - Military-grade encryption at rest
- 🛡️ **Git-Safe Storage** - Encrypted files can be safely committed
- 🔑 **Password Protection** - Vault password required for access
- 📋 **Ansible Integration** - Native support in all playbooks
- 🔄 **Multi-Environment** - Different vaults for test/prod environments
- 📝 **Audit Trail** - Encrypted changes tracked in git history

### Example Vault Content

```yaml
# After running: ./claudia vault --edit
---
# === AUTHENTICATION CREDENTIALS ===
vault_root_password: "secure_root_password_123"
vault_admin_password: "secure_admin_password_456"

# === CONNECTION CONFIGURATION ===
vault_admin_user: "admin"
vault_ssh_port: 22022

# === GLOBAL SERVER CONFIGURATION ===
vault_git_user_full_name: "Your Full Name"
vault_git_user_email: "your.email@example.com"
vault_timezone: "America/New_York"
vault_locale: "en_US.UTF-8"

# === SERVICE CREDENTIALS ===
vault_postgres_password: "database_password_789" 
vault_mysql_root_password: "mysql_root_password_abc"
vault_redis_password: "redis_password_def"
vault_vpn_passphrase: "vpn_passphrase_ghi"
```

### **📋 Configuration Fallback System**

All vault variables have safe defaults if not set:

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
- ✅ **Gradual adoption** - Can migrate to vault variables incrementally
- ✅ **No breaking changes** - Existing setups continue working

### 🔒 Authentication Flow & Security Model

#### **Two-Phase Authentication Architecture**

**🎯 Design Goal**: Admin passwords are NEVER used for automation - only SSH keys after initial setup.

#### **Phase 1: Initial Security Setup**
```bash
# Connection: root user with password
# Purpose: Bootstrap SSH keys and secure server
./claudia security --install

# What happens:
# 1. Connects as root with vault_root_password
# 2. Installs SSH keys for root and admin users  
# 3. Creates admin user with vault_admin_password
# 4. Configures firewall and secure SSH port
# 5. Disables root password authentication
```

#### **Phase 2: All Service Operations**
```bash
# Connection: admin user with SSH keys ONLY
# Purpose: All service installations and management
./claudia base --install
./claudia psql --install
./claudia redis --install

# What happens:
# 1. Connects as admin user with SSH keys
# 2. Uses sudo for privileged operations (NOPASSWD)
# 3. Never uses passwords for authentication
# 4. All automation runs under admin user context
```

#### **Connection Validation**
Every service recipe automatically validates:
- ✅ Connected as admin user (not root)
- ✅ Using SSH keys (no passwords)
- ✅ Secure SSH port (not 22)
- ✅ Sudo access works without password
- ❌ Fails with clear error messages if wrong connection type

#### **Security Features**
- 🔐 **Root Access**: Only during initial setup, then disabled
- 🔑 **SSH Keys**: All automation uses keys after setup
- 🛡️ **Admin Passwords**: Only for account creation and manual access
- 🚫 **No Password Automation**: Zero passwords in service configurations
- 📋 **Consistent Context**: All services run under admin user
- 🔍 **Connection Validation**: Automatic verification before operations

### Security Best Practices

1. **Never commit plaintext credentials** - Always use vault references
2. **Use strong vault passwords** - Consider password managers
3. **Rotate credentials regularly** - Update vault and server passwords
4. **Environment separation** - Different vaults for test/prod
5. **Access control** - Limit who has vault passwords
6. **Backup vault passwords** - Store securely outside the repository
7. **Follow authentication flow** - Always run security setup first
8. **Use SSH keys** - Admin passwords only for manual access