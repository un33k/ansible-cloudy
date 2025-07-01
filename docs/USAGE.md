# Ansible Cloudy - Complete Usage Guide

Comprehensive guide for using **Ansible Cloudy** with the **Claudia CLI** for infrastructure automation and server management.

## Table of Contents
- [Claudia CLI Command Reference](#claudia-cli-command-reference)
- [Prerequisites & Setup](#prerequisites--setup)
- [Configuration Guide](#configuration-guide)
- [Server Deployment Workflows](#server-deployment-workflows)
- [Advanced Usage Patterns](#advanced-usage-patterns)
- [Troubleshooting & Support](#troubleshooting--support)

## Claudia CLI Command Reference

Complete reference for the **Claudia CLI** - an intelligent command-line interface with auto-discovery and universal parameter support.

### 🧠 Intelligent CLI Features
- **Auto-Discovery**: Services automatically discovered from filesystem
- **Universal Parameters**: Intuitive CLI with `--port`, `--domain`, `--ssl` instead of complex Ansible variables
- **Granular Operations**: Service-specific tasks without full recipe installation
- **Smart Help System**: Context-aware help for every service and operation
- **Clean Output**: Shows only changes and failures by default

### 🎯 Core Services

#### Infrastructure Foundation
```bash
# Security Setup (Two-phase authentication model)
./claudia security                  # Show help and configuration options
./claudia security --install       # Execute security setup (SSH keys, grunt user, firewall)

# Base Configuration  
./claudia base                      # Show help and available variables
./claudia base --install           # Execute base setup (hostname, git, timezone, swap)
```

#### Database Services with Universal Parameters
```bash
# PostgreSQL with intuitive parameters
./claudia psql                                    # Show help and all parameters
./claudia psql --install                         # Standard PostgreSQL installation
./claudia psql --install --port 5544 --pgis      # Custom port with PostGIS extensions

# Granular database operations (no recipe installation)
./claudia psql --adduser myapp --password secret123    # Add user
./claudia psql --adddb myapp_db --owner myapp          # Add database
./claudia psql --list-users                            # List all users
./claudia psql --list-databases                        # List all databases
```

#### Cache Services with Smart Configuration
```bash
# Redis with universal parameters
./claudia redis                                         # Show help and parameters
./claudia redis --install                              # Standard Redis installation
./claudia redis --install --port 6380 --memory 512 --password secret  # Custom configuration

# Granular Redis operations
./claudia redis --configure-port 6379                  # Change port
./claudia redis --set-password newpass                 # Update password
./claudia redis --restart                              # Restart service
```

#### Web Services with Domain Management
```bash
# Nginx with SSL and domain support
./claudia nginx                                         # Show help and SSL options
./claudia nginx --install                              # Standard Nginx installation
./claudia nginx --install --domain example.com --ssl   # Nginx with SSL domain

# Granular web operations
./claudia nginx --setup-ssl example.com                # Setup SSL for domain
./claudia nginx --add-domain api.example.com           # Add new domain

# Django web applications
./claudia django                                        # Show deployment options
./claudia django --install                             # Django web server
./claudia django --install --prod                      # Production deployment
```

#### VPN Services
```bash
# OpenVPN with Docker
./claudia openvpn                                       # Show VPN configuration help
./claudia openvpn --install                            # Deploy OpenVPN server
```

#### AI/ML Database Services
```bash
# PostgreSQL with pgvector for embeddings
./claudia pgvector                                      # Show pgvector configuration
./claudia pgvector --install                           # Install with defaults (1536 dimensions)
./claudia pgvector --install --dimensions 768 --index-type hnsw  # Custom dimensions and HNSW index
./claudia pgvector --install --prod --create-examples  # Production with example schemas
```

#### Node.js Application Deployment
```bash
# Node.js with PM2 process manager
./claudia nodejs                                        # Show Node.js deployment options
./claudia nodejs --install                             # Deploy sample Node.js app
./claudia nodejs --install --app-repo https://github.com/user/app.git  # Deploy from Git
./claudia nodejs --install --prod --domain api.example.com --ssl --pm2-instances 4  # Production deployment
```

#### All-in-One Standalone Server
```bash
# Complete stack on single server
./claudia standalone                                    # Show standalone options
./claudia standalone --install                         # Deploy complete Django stack
./claudia standalone --install --app-type nodejs      # Deploy complete Node.js stack
./claudia standalone --install --domain example.com --ssl --production  # Production deployment
```

#### Database Connection Pooling
```bash
# PgBouncer for optimal database connections
./claudia pgbouncer                                     # Show PgBouncer configuration
./claudia pgbouncer --install                          # Install with defaults
./claudia pgbouncer --install --port 6433 --pool-size 30  # Custom configuration

# Granular PgBouncer operations
./claudia pgbouncer --configure-port 6433              # Change port
./claudia pgbouncer --set-pool-size 50                # Update pool size
./claudia pgbouncer --restart                          # Restart service
```

#### Simple Vault Configuration
```bash
# Copy vault template for your environment
cp .vault/dev.yml.example .vault/my-dev.yml

# Edit with your real credentials
vim .vault/my-dev.yml

# Use with Claudia commands
./claudia psql --install -- -e @.vault/my-dev.yml
```

### 🛠️ Development & Validation Commands

```bash
# Comprehensive development tools
./claudia dev validate      # Full validation suite (YAML, Ansible, structure)
./claudia dev syntax        # Quick syntax checking for all playbooks
./claudia dev lint          # Ansible-lint validation with rules
./claudia dev test          # Authentication flow testing
./claudia dev spell         # Spell check documentation with technical dictionary

# Service discovery and help
./claudia --list-services   # Show all available services and operations
./claudia --help            # Complete CLI usage guide
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
./claudia security         # Show security help and configuration options
./claudia django           # Show Django help and deployment variables
./claudia redis             # Show Redis help and memory configuration
```

#### Recipe Execution (Requires --install Flag)
```bash
./claudia security --install          # Execute security setup on test environment
./claudia django --install --prod     # Execute Django deployment on production  
./claudia redis --install --check     # Dry run Redis installation
```

#### Development Workflow
```bash
./claudia dev syntax       # Quick validation
./claudia dev validate     # Full validation  
./claudia dev spell        # Check spelling
./claudia dev test         # Test auth flow
```

#### Advanced Usage  
```bash
./claudia nginx --install --ssl                      # Execute nginx with SSL configuration
./claudia django --install --prod --verbose          # Production execution with debug output
./claudia security --install --check                 # Dry run security setup
```

#### Discovery Commands
```bash
./claudia --list           # Show all recipes
./claudia dev              # Show all dev commands  
./claudia --help           # Show complete usage
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

# Verify installation
./claudia dev syntax
./claudia --help
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
./claudia dev syntax
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
- Command: `./claudia security --install`

**Phase 2 - Service Operations** (Admin + SSH Keys):
- Connection: Grunt user with SSH key authentication
- Purpose: All service installations and configurations  
- Commands: `./claudia base --install`, `./claudia psql --install`, etc.

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
Update inventory after running `./claudia security --install`:
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
./claudia dev test

# Test specific inventory configuration
ansible -i cloudy/inventory/dev.yml my-server -m ping

# Test authentication flow with vault
./claudia security --install -- -e @.vault/my-dev.yml
```

## Server Deployment Workflows

### Complete Server Foundation
Sets up secure SSH, user management, and firewall.

```bash
# Deploy secure foundation (two-step process)
./claudia security --install    # Security setup (SSH keys, grunt user, firewall)
./claudia base --install        # Base configuration (hostname, git, timezone)
```

**What it does:**
- ✅ Creates grunt user with SSH key access
- ✅ Configures UFW firewall 
- ✅ Changes SSH port to 22022
- ✅ Disables root login
- ✅ Sets up sudo access

### VPN Server
Deploys OpenVPN using Docker containers.

```bash
# Deploy VPN server (includes foundation setup)
./claudia openvpn --install
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
./claudia django --install
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
./claudia psql --install --pgis
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
./claudia redis --install
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
./claudia nginx --install --ssl
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
./claudia security --install
```

### Compact Output
Single line per task:
```bash
ANSIBLE_STDOUT_CALLBACK=minimal ./claudia security --install
```

### One-Line Output
Extremely compact:
```bash
ANSIBLE_STDOUT_CALLBACK=oneline ./claudia security --install
```

### Verbose Output
Full debugging information:
```bash
./claudia security --install -v
```

### Ultra-Verbose Output
Maximum detail:
```bash
./claudia security --install -vvv
```

## Common Scenarios

### Scenario 1: Complete Web Application Stack

```bash
# 1. Start with fresh server, deploy foundation
./claudia security --install   # Create grunt user, SSH keys, firewall
./claudia base --install       # Base configuration

# 2. Update inventory to use grunt user on port 22022
# Edit inventory: ansible_user: admin, ansible_port: 22022

# 3. Deploy database layer
./claudia psql --install --pgis

# 4. Deploy web application layer
./claudia django --install

# 5. Optional: Deploy load balancer
./claudia nginx --install --ssl
```

### Scenario 2: VPN-Only Server

```bash
# Single command deployment (includes security setup)
./claudia openvpn --install

# Inventory automatically updated for grunt user access
```

### Scenario 3: Cache-Only Server

```bash
# Deploy Redis cache server with custom configuration
./claudia redis --install --port 6380 --memory 512

# Or with production settings
./claudia redis --install --prod --memory 1024
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
./claudia django --install --prod

# Deploy database servers  
./claudia psql --install --prod --pgis
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
1. Run with verbose output: `./claudia [service] --install -v`
2. Check specific task error messages in output
3. Verify server has sufficient resources (disk, memory)
4. Check internet connectivity for package downloads

### Output Too Verbose

**Problem:** Too much output information

**Solutions:**
1. Use default clean output (configured in `ansible.cfg`)
2. Try minimal callback: `ANSIBLE_STDOUT_CALLBACK=minimal ./claudia [service] --install`
3. Focus on changed tasks only (default behavior)

### Re-running Commands

**Best Practice:** Claudia commands are idempotent - safe to re-run.

```bash
# Re-run safely - only changes will be applied
./claudia security --install
```

### Testing Before Production

**Always test with dry runs first:**
```bash
# Test with dry run mode
./claudia security --install --check

# Test authentication flow
./claudia dev test

# If successful, proceed with actual installation
./claudia security --install
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
./claudia psql --adduser myapp --password secret123
./claudia psql --configure-port 5544

# Redis specific operations  
./claudia redis --configure-port 6380
./claudia redis --set-password newpass

# Nginx specific operations
./claudia nginx --setup-ssl example.com
./claudia nginx --add-domain api.example.com
```

### Dry Run Mode

Test without making changes:
```bash
# Check what would change
./claudia security --install --check
./claudia psql --install --check --port 5544
```

This guide covers the most common usage patterns. For detailed command reference, see `CLAUDE.md`.