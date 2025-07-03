# Ansible Cloudy - Complete Usage Guide

Comprehensive guide for using **Ansible Cloudy** with the **CLI** for infrastructure automation and server management.

## Table of Contents
- [CLI Command Reference](#cli-cli-command-reference)
- [Prerequisites & Setup](#prerequisites--setup)
- [Configuration Guide](#configuration-guide)
- [Server Deployment Workflows](#server-deployment-workflows)
- [Advanced Usage Patterns](#advanced-usage-patterns)
- [Troubleshooting & Support](#troubleshooting--support)

## CLI Command Reference

Complete reference for the **CLI** - an intelligent command-line interface with auto-discovery and universal parameter support.

### 🧠 Intelligent CLI Features
- **Auto-Discovery**: Services automatically discovered from filesystem
- **Universal Parameters**: Intuitive CLI with `--port`, `--domain`, `--ssl` instead of complex Ansible variables
- **Granular Operations**: Service-specific tasks without full recipe installation
- **Smart Help System**: Context-aware help for every service and operation
- **Clean Output**: Shows only changes and failures by default

### 🎯 Core Services

#### Infrastructure Foundation
```bash
# SSH Hardening (Run FIRST on fresh servers)
cli harden                    # Show hardening help
cli harden --install         # Atomic SSH hardening (changes port, disables passwords)

# Security Setup (Standard)
cli security                  # Show help and configuration options
cli security --install       # Standard security setup (grunt user, firewall, fail2ban)

# Security Setup (Production Hardened)
cli security --install --production-hardening  # Enterprise-grade security with:
                                              # - Production SSH hardening
                                              # - Kernel security parameters
                                              # - System auditing (auditd)
                                              # - Automatic security updates
                                              # - Secure file permissions

# Base Configuration  
cli base                      # Show help and available variables
cli base --install           # Execute base setup (hostname, git, timezone, swap)
```

#### Database Services with Universal Parameters
```bash
# PostgreSQL with intuitive parameters
cli psql                                    # Show help and all parameters
cli psql --install                         # Standard PostgreSQL installation
cli psql --install --port 5544 --pgis      # Custom port with PostGIS extensions

# Granular database operations (no recipe installation)
cli psql --adduser myapp --password secret123    # Add user
cli psql --adddb myapp_db --owner myapp          # Add database
cli psql --list-users                            # List all users
cli psql --list-databases                        # List all databases
```

#### Cache Services with Smart Configuration
```bash
# Redis with universal parameters
cli redis                                         # Show help and parameters
cli redis --install                              # Standard Redis installation
cli redis --install --port 6380 --memory 512 --password secret  # Custom configuration

# Granular Redis operations
cli redis --configure-port 6379                  # Change port
cli redis --set-password newpass                 # Update password
cli redis --restart                              # Restart service
```

#### Web Services with Domain Management
```bash
# Nginx with SSL and domain support
cli nginx                                         # Show help and SSL options
cli nginx --install                              # Standard Nginx installation
cli nginx --install --domain example.com --ssl   # Nginx with SSL domain

# Granular web operations
cli nginx --setup-ssl example.com                # Setup SSL for domain
cli nginx --add-domain api.example.com           # Add new domain

# Django web applications
cli django                                        # Show deployment options
cli django --install                             # Django web server
cli django --install --prod                      # Production deployment
```

#### VPN Services
```bash
# OpenVPN with Docker
cli openvpn                                       # Show VPN configuration help
cli openvpn --install                            # Deploy OpenVPN server
```

#### AI/ML Database Services
```bash
# PostgreSQL with pgvector for embeddings
cli pgvector                                      # Show pgvector configuration
cli pgvector --install                           # Install with defaults (1536 dimensions)
cli pgvector --install --dimensions 768 --index-type hnsw  # Custom dimensions and HNSW index
cli pgvector --install --prod --create-examples  # Production with example schemas
```

#### Node.js Application Deployment
```bash
# Node.js with PM2 process manager
cli nodejs                                        # Show Node.js deployment options
cli nodejs --install                             # Deploy sample Node.js app
cli nodejs --install --app-repo https://github.com/user/app.git  # Deploy from Git
cli nodejs --install --prod --domain api.example.com --ssl --pm2-instances 4  # Production deployment
```

#### All-in-One Standalone Server
```bash
# Complete stack on single server
cli standalone                                    # Show standalone options
cli standalone --install                         # Deploy complete Django stack
cli standalone --install --app-type nodejs      # Deploy complete Node.js stack
cli standalone --install --domain example.com --ssl --production  # Production deployment
```

#### Database Connection Pooling
```bash
# PgBouncer for optimal database connections
cli pgbouncer                                     # Show PgBouncer configuration
cli pgbouncer --install                          # Install with defaults
cli pgbouncer --install --port 6433 --pool-size 30  # Custom configuration

# Granular PgBouncer operations
cli pgbouncer --configure-port 6433              # Change port
cli pgbouncer --set-pool-size 50                # Update pool size
cli pgbouncer --restart                          # Restart service
```

#### Simple Vault Configuration
```bash
# Copy vault template for your environment
cp .vault/dev.yml.example .vault/my-dev.yml

# Edit with your real credentials
vim .vault/my-dev.yml

# Use with CLI commands
cli psql --install -- -e @.vault/my-dev.yml
```

### 🛠️ Development & Validation Commands

```bash
# Comprehensive development tools
cli dev validate      # Full validation suite (YAML, Ansible, structure)
cli dev syntax        # Quick syntax checking for all playbooks
cli dev lint          # Ansible-lint validation with rules
cli dev test          # Authentication flow testing
cli dev spell         # Spell check documentation with technical dictionary

# Service discovery and help
cli --list-services   # Show all available services and operations
cli --help            # Complete CLI usage guide
```

### ⚙️ Universal Options

Available with any service command:

```bash
# Core Operations
--install               # Execute the service recipe (required for installations)
--check, --dry-run      # Run in check mode without making changes
--prod, --production    # Use production inventory (default: dev/test)
--verbose, -v           # Enable verbose Ansible output

# Legacy Ansible Support
-- [ansible-args]       # Pass additional arguments to ansible-playbook

# Help and Discovery
--help, -h              # Show service-specific help and parameters
--list                  # List available operations for the service

# Backward Compatibility
-- [ansible-args]       # Pass additional arguments (legacy ansible-playbook syntax - not recommended)
```

### 🎨 Usage Examples

#### Help and Discovery (Default Action)
```bash
cli security         # Show security help and configuration options
cli django           # Show Django help and deployment variables
cli redis             # Show Redis help and memory configuration
```

#### Recipe Execution (Requires --install Flag)
```bash
cli security --install          # Execute security setup on test environment
cli django --install --prod     # Execute Django deployment on production  
cli redis --install --check     # Dry run Redis installation
```

#### Development Workflow
```bash
cli dev syntax       # Quick validation
cli dev validate     # Full validation  
cli dev spell        # Check spelling
cli dev test         # Test auth flow
```

#### Advanced Usage  
```bash
cli nginx --install --ssl                      # Execute nginx with SSL configuration
cli django --install --prod --verbose          # Production execution with debug output
cli security --install --check                 # Dry run security setup
```

#### Discovery Commands
```bash
cli --list           # Show all recipes
cli dev              # Show all dev commands  
cli --help           # Show complete usage
```

### 📊 Command Summary

| **Category** | **Commands** | **Count** |
|-------------|-------------|-----------|
| **Core** | security, base | 2 |
| **Database** | psql, postgis, pgvector | 3 |
| **Web** | django, nodejs, nginx | 3 |
| **Services** | redis, openvpn, pgbouncer | 3 |
| **Standalone** | standalone | 1 |
| **Development** | validate, syntax, lint, test, spell | 5 |
| **Total** | | **17 commands** |

## Prerequisites & Setup

### Quick Environment Setup (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd ansible-cloudy/

# Bootstrap environment - creates .venv with all development tools
./bootstrap.sh

# Activate development environment
source .venv/bin/activate

# After activation, use 'cli' (short alias) or 'cli' (full name)
# Both commands are identical - 'cli' saves keystrokes for frequent use

# Verify installation
cli dev syntax  # or cli dev syntax
cli --help      # or cli --help
```

**What bootstrap.sh provides:**
- Python virtual environment with proper isolation
- Ansible and all linting tools (ansible-lint, yamllint, flake8)
- Development dependencies (PyYAML, jsonschema, passlib)
- Spell checking tools with technical dictionary (480+ terms)

### Manual Setup (Alternative)
```bash
# Install Ansible and dependencies
pip install ansible ansible-lint yamllint pyyaml passlib

# Verify installation
ansible --version
cli dev syntax
```

### SSH Key Requirements
```bash
# Generate SSH key pair (if not already present)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa

# Verify key exists and has proper permissions
ls -la ~/.ssh/id_rsa*
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### Server Requirements
- **Fresh Ubuntu/Debian server** (20.04+ recommended)
- **Root access** with password for initial setup
- **Network connectivity** to server from your machine
- **Minimum resources**: 1GB RAM, 10GB disk space
- **Open ports**: 22 (SSH) initially, 22022 (custom SSH) after setup

## Configuration Guide

### 1. Understanding the Two-Phase Authentication Model

Ansible Cloudy uses a sophisticated two-phase authentication approach:

**Phase 1 - Initial Security Setup** (Root + Password):
- Connection: Root user with password authentication
- Purpose: Install SSH keys, create grunt user, secure server
- Command: `cli security --install`

**Phase 2 - Service Operations** (Admin + SSH Keys):
- Connection: Grunt user with SSH key authentication
- Purpose: All service installations and configurations  
- Commands: `cli base --install`, `cli psql --install`, etc.

### 2. Inventory Configuration

#### For Fresh Servers (Initial Setup)
Edit `cloudy/inventory/dev.yml`:
```yaml
all:
  vars:
    # Phase 1: Fresh server configuration (root + password)
    ansible_user: root
    ansible_ssh_pass: your_root_password  # or use vault_root_password
    ansible_port: 22
    ansible_host_key_checking: false
    
  children:
    generic_servers:
      hosts:
        my-server:
          ansible_host: 192.168.1.100
          hostname: my-server.example.com
          grunt_user: admin
          grunt_password: secure_grunt_password  # or use vault_grunt_password
```

#### After Security Setup (Production Use)
Update inventory after running `cli security --install`:
```yaml
all:
  vars:
    # Phase 2: Secured server configuration (admin + SSH keys)
    ansible_user: admin
    ansible_port: 22022
    ansible_ssh_private_key_file: ~/.ssh/id_rsa
    ansible_host_key_checking: false
    
  children:
    generic_servers:
      hosts:
        my-server:
          ansible_host: 192.168.1.100
          hostname: my-server.example.com
```

### 3. Simple Vault Setup (Recommended for Production)

For production deployments, use simple vault files for sensitive credentials:

```bash
# Copy vault template for your environment
cp .vault/prod.yml.example .vault/my-prod.yml

# Edit with your real credentials
vim .vault/my-prod.yml
```

Example vault content:
```yaml
---
# Root credentials for initial setup
vault_root_password: "secure_root_password_123"

# Grunt user configuration
vault_grunt_user: "admin"
vault_grunt_password: "secure_grunt_password_456"
vault_ssh_port: 22022

# Global server configuration
vault_git_user_full_name: "Your Full Name"
vault_git_user_email: "your.email@example.com"
vault_timezone: "America/New_York"

# Service-specific credentials
vault_postgres_password: "database_password_789"
vault_redis_password: "redis_password_def"
```

Use vault variables in inventory:
```yaml
all:
  vars:
    ansible_user: "{{ vault_grunt_user | default('admin') }}"
    ansible_ssh_pass: "{{ vault_grunt_password }}"
    ansible_port: "{{ vault_ssh_port | default(22022) }}"
```

### 4. Connection Testing

```bash
# Test initial connection (fresh server)
cli dev test

# Test specific inventory configuration
ansible -i cloudy/inventory/dev.yml my-server -m ping

# Test authentication flow with vault
cli security --install -- -e @.vault/my-dev.yml
```

## Server Deployment Workflows

### Complete Server Foundation
Sets up secure SSH, user management, and firewall.

#### Standard Security (Development/Staging)
```bash
# Three-step process for new servers
cli harden --install      # SSH hardening (port change, disable passwords)
cli security --install    # Security setup (grunt user, firewall, fail2ban)
cli base --install        # Base configuration (hostname, git, timezone)
```

**What it does:**
- ✅ Changes SSH port to 22022
- ✅ Disables password authentication
- ✅ Creates optional grunt user with SSH keys
- ✅ Configures UFW firewall 
- ✅ Installs fail2ban
- ✅ Sets up sudo access

#### Production Security (Enterprise Hardening)
```bash
# Three-step process with maximum security
cli harden --install                          # SSH hardening first
cli security --install --production-hardening # Enterprise security
cli base --install                            # Base configuration
```

**Additional production features:**
- ✅ Everything from standard security PLUS:
- ✅ Production SSH hardening (modern ciphers, MACs, KEX algorithms)
- ✅ Kernel security parameters (ASLR, SYN flood protection)
- ✅ System auditing with auditd (comprehensive audit logging)
- ✅ Automatic security updates (unattended upgrades)
- ✅ Secure file permissions on sensitive files
- ✅ Security compliance report generation
- ✅ DDoS protection and rate limiting

### VPN Server
Deploys OpenVPN using Docker containers.

```bash
# Deploy VPN server (includes foundation setup)
cli openvpn --install
```

**What it includes:**
- ✅ Generic server foundation
- ✅ Docker installation
- ✅ OpenVPN container setup
- ✅ Client certificate management
- ✅ Firewall rules for VPN traffic

### Web Server
Complete web application stack.

```bash
# Deploy web server
cli django --install
```

**What it includes:**
- ✅ Generic server foundation
- ✅ Nginx web server
- ✅ Apache configuration
- ✅ Supervisor process management
- ✅ SSL certificate support

### Database Server
PostgreSQL with spatial extensions.

```bash
# Deploy database server
cli psql --install --pgis
```

**What it includes:**
- ✅ Generic server foundation
- ✅ PostgreSQL installation
- ✅ PostGIS spatial extensions
- ✅ Database user management

### Cache Server
Redis caching solution.

```bash
# Deploy cache server
cli redis --install
```

**What it includes:**
- ✅ Generic server foundation
- ✅ Redis installation
- ✅ Memory optimization
- ✅ Persistence configuration

### Load Balancer
Nginx load balancer with SSL.

```bash
# Deploy load balancer
cli nginx --install --ssl
```

**What it includes:**
- ✅ Generic server foundation
- ✅ Nginx load balancer
- ✅ SSL termination
- ✅ Backend server configuration

## Output Control

### Default Output (Clean)
Shows only changes and failures:
```bash
cli security --install
```

### Compact Output
Single line per task:
```bash
ANSIBLE_STDOUT_CALLBACK=minimal cli security --install
```

### One-Line Output
Extremely compact:
```bash
ANSIBLE_STDOUT_CALLBACK=oneline cli security --install
```

### Verbose Output
Full debugging information:
```bash
cli security --install -v
```

### Ultra-Verbose Output
Maximum detail:
```bash
cli security --install -vvv
```

## Common Scenarios

### Scenario 1: Complete Web Application Stack

```bash
# 1. Start with fresh server, deploy foundation
cli security --install   # Create grunt user, SSH keys, firewall
cli base --install       # Base configuration

# 2. Update inventory to use grunt user on port 22022
# Edit inventory: ansible_user: admin, ansible_port: 22022

# 3. Deploy database layer
cli psql --install --pgis

# 4. Deploy web application layer
cli django --install

# 5. Optional: Deploy load balancer
cli nginx --install --ssl
```

### Scenario 2: VPN-Only Server

```bash
# Single command deployment (includes security setup)
cli openvpn --install

# Inventory automatically updated for grunt user access
```

### Scenario 3: Cache-Only Server

```bash
# Deploy Redis cache server with custom configuration
cli redis --install --port 6380 --memory 512

# Or with production settings
cli redis --install --prod --memory 1024
```

### Scenario 4: Multi-Server Environment

Create separate inventory files:

**inventory/production-web.yml:**
```yaml
all:
  vars:
    ansible_user: admin
    ansible_ssh_pass: grunt_password
    ansible_port: 22022
    
  children:
    web_servers:
      hosts:
        web1:
          ansible_host: 10.0.1.10
        web2:
          ansible_host: 10.0.1.11
```

**inventory/production-db.yml:**
```yaml
all:
  vars:
    ansible_user: admin
    ansible_ssh_pass: grunt_password
    ansible_port: 22022
    
  children:
    database_servers:
      hosts:
        db1:
          ansible_host: 10.0.2.10
```

Deploy:
```bash
# Deploy web servers
cli django --install --prod

# Deploy database servers  
cli psql --install --prod --pgis
```

## Troubleshooting

### Connection Issues

**Problem:** `UNREACHABLE! => ssh: connect to host X port Y: Connection refused`

**Solutions:**
1. Check server is running: `ping server_ip`
2. Verify SSH port: `nmap -p 22,22022 server_ip`
3. Check inventory configuration matches server state
4. For fresh servers, use `ansible_user: root` and `ansible_port: 22`
5. After setup, use `ansible_user: admin` and `ansible_port: 22022`

### Authentication Issues

**Problem:** `Permission denied (publickey,password)`

**Solutions:**
1. Verify password in inventory is correct
2. Check SSH key exists: `ls ~/.ssh/id_rsa*`
3. For fresh servers, ensure `ansible_user: root`
4. After setup, ensure `ansible_user: admin`

### Firewall Issues

**Problem:** SSH connection timeout after port change

**Solutions:**
1. The recipes automatically configure UFW firewall
2. Port 22022 is opened before SSH port change
3. If locked out, reset server to fresh state and retry

### Task Failures

**Problem:** Tasks fail during execution

**Solutions:**
1. Run with verbose output: `cli [service] --install -v`
2. Check specific task error messages in output
3. Verify server has sufficient resources (disk, memory)
4. Check internet connectivity for package downloads

### Output Too Verbose

**Problem:** Too much output information

**Solutions:**
1. Use default clean output (configured in `ansible.cfg`)
2. Try minimal callback: `ANSIBLE_STDOUT_CALLBACK=minimal cli [service] --install`
3. Focus on changed tasks only (default behavior)

### Re-running Commands

**Best Practice:** CLI commands are idempotent - safe to re-run.

```bash
# Re-run safely - only changes will be applied
cli security --install
```

### Testing Before Production

**Always test with dry runs first:**
```bash
# Test with dry run mode
cli security --install --check

# Test authentication flow
cli dev test

# If successful, proceed with actual installation
cli security --install
```

## Advanced Usage

### Custom Configuration Variables

Add custom variables to inventory:
```yaml
all:
  vars:
    custom_domain: myapp.com
    ssl_cert_email: admin@myapp.com
    
  children:
    web_servers:
      hosts:
        web1:
          ansible_host: 10.0.1.10
          app_name: myapp-production
```

### Granular Operations

Use specific operations for targeted changes:
```bash
# PostgreSQL specific operations
cli psql --adduser myapp --password secret123
cli psql --configure-port 5544

# Redis specific operations  
cli redis --configure-port 6380
cli redis --set-password newpass

# Nginx specific operations
cli nginx --setup-ssl example.com
cli nginx --add-domain api.example.com
```

### Dry Run Mode

Test without making changes:
```bash
# Check what would change
cli security --install --check
cli psql --install --check --port 5544
```

This guide covers the most common usage patterns. For detailed command reference, see `CLAUDE.md`.