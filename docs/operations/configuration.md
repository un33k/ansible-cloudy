# Configuration Guide

Complete guide to configuring Ansible Cloudy with vault files and inventory management.

## Configuration Overview

Ansible Cloudy uses a layered configuration system:

1. **Defaults** - Base values in `/cloudy/defaults/`
2. **Inventory** - Server and group definitions
3. **Vault** - Sensitive credentials and overrides
4. **Command Line** - Runtime parameters

Priority (highest to lowest):
1. Command-line arguments
2. Vault variables
3. Inventory variables  
4. Default values

## Vault Configuration

### Understanding Vault Files

Vault files contain sensitive credentials and configuration overrides. They are:
- Never committed to version control
- Environment-specific
- Simple YAML format (no encryption needed for open source)

### Vault File Structure

```yaml
# .vault/production.yml
---
# === AUTHENTICATION CREDENTIALS ===
vault_root_password: "secure_root_password"
vault_admin_password: "secure_admin_password"

# === CONNECTION CONFIGURATION ===
vault_ansible_user: "root"              # User for connections
vault_initial_ssh_port: 22              # Port before security setup
vault_ssh_port: 22022                   # Port after security setup

# === OPTIONAL GRUNT USER ===
vault_grunt_user: ""                    # Empty = don't create user
vault_grunt_password: ""                # Required if user defined

# === GLOBAL CONFIGURATION ===
vault_git_user_full_name: "DevOps Team"
vault_git_user_email: "devops@company.com"
vault_timezone: "America/New_York"
vault_locale: "en_US.UTF-8"

# === SERVICE CREDENTIALS ===
vault_postgres_password: "secure_db_password"
vault_redis_password: "secure_cache_password"
vault_mysql_root_password: "secure_mysql_password"
vault_vpn_passphrase: "secure_vpn_passphrase"

# === SERVICE PORTS ===
vault_postgresql_port: 5432             # PostgreSQL port
vault_pgbouncer_port: 6432              # PgBouncer port
vault_redis_port: 6379                  # Redis port
vault_nginx_http_port: 80               # HTTP port
vault_nginx_https_port: 443             # HTTPS port
```

### Creating Vault Files

```bash
# Copy template
cp .vault/prod.yml.example .vault/production.yml

# Edit with your values
vim .vault/production.yml

# Set restrictive permissions
chmod 600 .vault/production.yml
```

### Using Vault Files

```bash
# Automatic loading (for matching environment)
cli security --install --prod  # Loads .vault/prod.yml if exists

# Explicit vault file
cli security --install -e .vault/production.yml

# Multiple vault files
cli psql --install -e .vault/base.yml -e .vault/db-specific.yml
```

## Inventory Configuration

### Inventory Structure

```yaml
# cloudy/inventory/prod.yml
---
all:
  # No defaults here - all defaults in cloudy/defaults/
  
  children:
    # Groups for different server types
    web_servers:
      hosts:
        web-01:
          ansible_host: 10.0.1.10
        web-02:
          ansible_host: 10.0.1.11
    
    database_servers:
      hosts:
        db-01:
          ansible_host: 10.0.2.10
          
    cache_servers:
      hosts:
        cache-01:
          ansible_host: 10.0.3.10
```

### Important: No Defaults in Inventory

Never use `default()` in inventory files:

```yaml
# ❌ WRONG - Don't do this
ansible_user: "{{ vault_ansible_user | default('root') }}"

# ✅ CORRECT - Reference variable directly
ansible_user: "{{ vault_ansible_user }}"
```

All defaults belong in `/cloudy/defaults/` files.

### Host Configuration

```yaml
hosts:
  web-server-01:
    ansible_host: 192.168.1.100
    hostname: web01.example.com
    
    # PostgreSQL databases to create
    postgresql_databases:
      - name: app_db
        owner: app_user
      - name: analytics_db
        owner: analytics_user
    
    # PostgreSQL users to create
    postgresql_users:
      - name: app_user
        password: "{{ vault_app_db_password }}"
        database: app_db
      - name: analytics_user
        password: "{{ vault_analytics_db_password }}"
        database: analytics_db
```

### Group Variables

```yaml
# cloudy/inventory/group_vars/web_servers.yml
---
# Web server specific configuration
nginx_worker_processes: 4
nginx_worker_connections: 1024

# Application settings
app_port: 8000
enable_ssl: true
```

## Environment Management

### Built-in Environments

Ansible Cloudy includes three environments:

1. **Development** (`dev`)
   - Default environment
   - Relaxed security
   - Verbose logging
   
2. **Production** (`prod`)
   - Hardened security
   - Optimized performance
   - Minimal logging
   
3. **CI/CD** (`ci`)
   - Automated testing
   - Fast deployment
   - Temporary resources

### Using Environments

```bash
# Development (default)
cli security --install
cli security --install --dev

# Production
cli security --install --prod

# CI/CD
cli security --install --ci
```

### Custom Environments

Create your own:

```bash
# Create custom inventory
cp cloudy/inventory/prod.yml cloudy/inventory/staging.yml

# Create matching vault
cp .vault/prod.yml.example .vault/staging.yml

# Use custom environment
cli security --install -i cloudy/inventory/staging.yml -e .vault/staging.yml
```

## Variable Precedence

Understanding variable precedence is crucial:

```yaml
# 1. Command line (highest priority)
cli psql --install --port 5433

# 2. Extra vars file
cli psql --install -e .vault/overrides.yml

# 3. Vault variables
vault_postgresql_port: 5432

# 4. Inventory host vars
postgresql_port: 5432

# 5. Inventory group vars
postgresql_port: 5432

# 6. Defaults (lowest priority)
postgresql_port_default: 5432
```

## Security Best Practices

### Vault Security

1. **Never commit vault files**
   ```bash
   # Add to .gitignore
   .vault/*.yml
   !.vault/*.example
   ```

2. **Use strong passwords**
   ```bash
   # Generate secure passwords
   openssl rand -base64 32
   ```

3. **Separate environments**
   ```bash
   .vault/dev.yml      # Development only
   .vault/prod.yml     # Production only
   .vault/personal.yml # Never share
   ```

4. **Restrict permissions**
   ```bash
   chmod 600 .vault/*.yml
   ```

### Connection Security

1. **SSH Keys Required**
   - After security setup, only SSH keys work
   - No password authentication
   - Keys must be in place before running

2. **Port Management**
   - Initial connection on port 22
   - Security setup changes to 22022
   - Firewall blocks port 22 after setup

3. **User Management**
   - Root user for all operations
   - Optional grunt user for services only
   - No shared accounts

## Common Configuration Patterns

### Multi-Tier Application

```yaml
# .vault/production.yml
vault_postgres_password: "{{ lookup('password', '/dev/null length=32') }}"
vault_redis_password: "{{ lookup('password', '/dev/null length=32') }}"
vault_app_secret_key: "{{ lookup('password', '/dev/null length=64') }}"

# Web tier specific
vault_web_workers: 4
vault_web_threads: 2

# Database tier specific
vault_db_max_connections: 200
vault_db_shared_buffers: "2GB"
```

### High Availability Setup

```yaml
# cloudy/inventory/prod.yml
all:
  children:
    load_balancers:
      hosts:
        lb-01:
          ansible_host: 10.0.0.10
          keepalived_priority: 100
        lb-02:
          ansible_host: 10.0.0.11
          keepalived_priority: 90
    
    database_servers:
      hosts:
        db-primary:
          ansible_host: 10.0.1.10
          postgresql_role: primary
        db-replica:
          ansible_host: 10.0.1.11
          postgresql_role: replica
          postgresql_primary_host: db-primary
```

### Development Environment

```yaml
# .vault/dev.yml
# Simple passwords for development only
vault_root_password: "devpass123"
vault_postgres_password: "devpass123"
vault_redis_password: "devpass123"

# Development settings
vault_debug_mode: true
vault_log_level: "debug"
```

## Troubleshooting Configuration

### Variable Not Found

```bash
# Debug variable resolution
ansible-inventory -i cloudy/inventory/prod.yml --host myserver --vars
```

### Wrong Environment Loaded

```bash
# Explicitly specify environment
cli security --install -i cloudy/inventory/prod.yml -e .vault/prod.yml
```

### Connection Issues

Check variable precedence:
1. Is vault file loaded?
2. Is inventory correct?
3. Are defaults defined?

### Debug Mode

```bash
# Show variable values
cli psql --install --check -v

# Maximum verbosity
cli psql --install --check -vvv
```

## Best Practices

1. **Keep vault files simple** - Only overrides, not full config
2. **Use meaningful names** - `vault_app_db_password` not `password1`
3. **Document requirements** - Comment required variables
4. **Test with check mode** - Always use `--check` first
5. **Version control templates** - Commit `.example` files
6. **Separate concerns** - Don't mix environments
7. **Regular rotation** - Update passwords periodically

## Next Steps

- Explore [Available Commands](commands.md)
- Learn about [Deployment Recipes](recipes.md)
- Read [Variable Reference](../reference/variables.md)