# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

Note: Avoid saying things like: You're absolutely right!. Unless answering a specific question. 

### Environment Setup

```bash
# Install Ansible
pip install ansible

# Navigate to project directory
cd ansible-cloudy/
```

### Core Development Commands

#### Simplified Server Setup (Recommended) - Using Ali CLI
- **Help First**: `./ali security`, `./ali base`, `./ali psql` (shows help, configuration, and usage)
- **Step 1 - Security**: `./ali security --install` (root SSH keys + admin user, firewall, port change)
- **Step 2 - Core**: `./ali base --install` (hostname, git, timezone, swap, etc.)
- **Step 3 - Services**: `./ali django --install`, `./ali redis --install`, `./ali nginx --install` (deploy specific services)

#### Production Setup
- **Ali CLI**: `./ali security --install --prod`, `./ali django --install --prod`, `./ali redis --install --prod`

#### Development Tools
- **Bootstrap**: `./bootstrap.sh` - Sets up .venv with all development tools
- **Ali CLI**: `./ali security --install` - Simplified Ansible commands (90% shorter)
- **Ali Dev Commands**: `./ali dev syntax`, `./ali dev validate`, `./ali dev lint`, `./ali dev test`
- **Authentication test**: `./ali dev test` - Test server authentication flow
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
./ali security
```

#### Method 2: Environment Variable
Set the sudo password via environment variable:

```bash
# Set sudo password for the session
export ANSIBLE_BECOME_PASS=secure123

# Or provide it directly with the command
ANSIBLE_BECOME_PASS=secure123 ./ali security
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
./ali security --install

# 2. Deploy base configuration
./ali base --install

# 3. Deploy services
./ali psql --install    # PostgreSQL database
./ali django --install  # Django web application
./ali redis --install   # Redis cache
./ali nginx --install   # Nginx load balancer
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
- ✅ **Verbose**: `./ali ... -v` (detailed debugging)
- ✅ **Always Shown**: Changed tasks, failed tasks, unreachable hosts
- ✅ **Hidden by Default**: Successful unchanged tasks, skipped tasks

### Ali Recipe Examples

```bash
# Ali CLI - Simplified Commands (Recommended)
# Help and Discovery (default action)
./ali security                  # Show security help and configuration options
./ali base                      # Show base setup help and variables
./ali psql                      # Show PostgreSQL help and configuration

# Step 1: Security setup
./ali security --install

# Step 2: Core setup  
./ali base --install

# Step 3: Service deployment
./ali psql --install
./ali django --install
./ali redis --install
./ali nginx --install
./ali openvpn --install

# Production deployment
./ali security --install --prod
./ali django --install --prod

# Dry runs and testing
./ali redis --install --check
./ali nginx --install -- --tags ssl

# Individual components and tags
./ali base --install -- --tags ssh
./ali base --install -- --tags firewall  
./ali django --install -- --tags nginx

# Development and validation
./ali dev validate                  # Comprehensive validation (with fallback)
./ali dev syntax                    # Quick syntax check
./ali dev test                      # Authentication flow test
./ali dev lint                      # Ansible linting
./ali dev spell                     # Spell checking

# Advanced dev commands (if needed)
./dev/validate.py                   # Direct validation script
./dev/syntax-check.sh              # Direct syntax check script
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

### Core Ali Commands
- **Show recipe help**: `./ali [recipe-name]` (security, base, psql, django, etc.)
- **Execute recipes**: `./ali [recipe-name] --install` (requires explicit flag for safety)
- **Test authentication flow**: `./ali dev test`
- **Clean output (changes only)**: Configured in `ansible.cfg` with `display_skipped_hosts = no`
- **Alternative output formats**:
  - `ANSIBLE_STDOUT_CALLBACK=minimal ./ali ... --install` (compact format)
  - `ANSIBLE_STDOUT_CALLBACK=oneline ./ali ... --install` (one line per task)
  - Standard verbose: `./ali ... --install -v` (detailed debugging)

### Ali Recipe Examples
```bash
# Help and configuration (default action)
./ali security                  # Show security help and options
./ali base                      # Show base configuration help
./ali psql                      # Show PostgreSQL help and variables

# Recipe execution (requires --install flag)
./ali security --install        # Security setup (root SSH keys + admin user, firewall, port change)
./ali openvpn --install         # VPN server setup (OpenVPN with Docker)
./ali django --install          # Web server setup (Django with Nginx/Apache/Supervisor)
./ali psql --install            # Database server setup (PostgreSQL, PostGIS, PgBouncer)
./ali postgis --install         # PostgreSQL with PostGIS extensions
./ali redis --install           # Cache server setup (Redis)
./ali nginx --install           # Load balancer setup (Nginx with SSL)
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
          ssh_port: 22022
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