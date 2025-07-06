# Variable Naming Convention Guide

## Overview
This document describes the standardized variable naming convention for Ansible Cloudy to eliminate the use of `default()` filters throughout the codebase.

## Core Principles

### 1. Default Values
- **Variables WITH defaults**: Must end with `_default` suffix
- **Variables WITHOUT defaults**: Come directly from vault files
- **No default_ prefix**: All variables use suffix notation

### 2. Variable Resolution Order
1. **Inventory/host vars** (highest priority)
2. **Vault files** (.vault/*.yml)
3. **Default files** (cloudy/defaults/*.yml)
4. **Playbook vars** (lowest priority)

## Naming Conventions

### Variables That MUST Come From Vault (No Defaults)
These variables have no defaults and must be explicitly set:
- `vault_root_user` - Root username
- `vault_root_password` - Root password
- `vault_grunt_user` - Grunt username (empty = skip creation)
- `vault_grunt_password` - Grunt password (empty = generate)
- `vault_postgres_password` - PostgreSQL password
- `vault_redis_password` - Redis password
- `vault_mysql_root_password` - MySQL root password
- `vault_vpn_passphrase` - VPN passphrase

### Variables With Defaults
All variables that have default values use the `_default` suffix:

#### System Defaults (all.yml)
```yaml
# Before: default_locale
# After:  locale_default

locale_default: "en_US.UTF-8"
timezone_default: "UTC"
shell_default: "/bin/bash"
```

#### Security Defaults (security.yml)
```yaml
ssh_port_default: 22
ssh_permit_root_login_default: "prohibit-password"
fail2ban_bantime_default: 3600
grunt_groups_string_default: "sudo,adm,systemd-journal,www-data,docker,ssl-cert"
```

#### Service Defaults
```yaml
# PostgreSQL
pg_port_default: 5432
pg_listen_addresses_default: "localhost"

# Redis
redis_port_default: 6379
redis_bind_default: "127.0.0.1"

# Nginx
nginx_http_port_default: 80
nginx_worker_processes_default: "auto"
```

## Usage Examples

### Before (with default() filter)
```yaml
- name: Configure service
  template:
    src: config.j2
    dest: /etc/service/config
  vars:
    port: "{{ service_port | default(8080) }}"
    workers: "{{ worker_count | default('auto') }}"
```

### After (using defaults)
```yaml
# In cloudy/defaults/service.yml
service_port_default: 8080
worker_count_default: "auto"

# In task/playbook
- name: Configure service
  template:
    src: config.j2
    dest: /etc/service/config
  vars:
    port: "{{ service_port | default(service_port_default) }}"
    workers: "{{ worker_count | default(worker_count_default) }}"
```

## Variable Precedence for Service Ports

Service ports follow a special pattern to allow vault overrides:

1. **User sets in vault**: `vault_redis_port: 6380` in .vault/*.yml
2. **Playbook uses**: `{{ vault_redis_port | default(vault_redis_port_default) }}`
3. **Default comes from**: `vault_redis_port_default: 6379` in defaults/vault.yml

### Important: Port variables are centralized in vault.yml

All service port defaults MUST be defined in `defaults/vault.yml` with the pattern `vault_<service>_port_default`. Do NOT duplicate port definitions in service-specific default files.

Example:
```yaml
# In defaults/vault.yml
vault_postgresql_port_default: 5432
vault_redis_port_default: 6379
vault_nginx_http_port_default: 80

# In playbooks/recipes/cache/redis.yml
vars:
  redis_port: "{{ vault_redis_port | default(vault_redis_port_default) }}"

# In .vault/prod.yml (user override)
vault_redis_port: 6380  # This overrides the default
```

This ensures:
1. All port defaults are in one place (vault.yml)
2. Users can override by setting `vault_<service>_port` in their vault files
3. No duplicate definitions across different default files

## Important Note on default() Filter

The `default()` filter MUST be used for variable fallbacks:
- **Correct**: `{{ variable | default(variable_default) }}`
- **Incorrect**: `{{ variable | variable_default }}` (This will cause runtime errors)

While the simpler syntax might look cleaner, Jinja2 requires the explicit `default()` filter to handle undefined variables properly.

## Migration Checklist

When migrating existing code:

1. **Identify all default() usage**: `grep -r "default(" .`
2. **Check if variable should have a default**:
   - Passwords, secrets → No default
   - Ports, settings → Add to defaults/*.yml with _default suffix
3. **Update the code**:
   - Remove inline defaults
   - Reference default variables
4. **Test thoroughly**:
   - Ensure defaults are loaded
   - Verify precedence works correctly

## Best Practices

1. **Group related defaults** in appropriate files:
   - System settings → system.yml
   - Security settings → security.yml
   - Service-specific → service.yml

2. **Document defaults clearly**:
   ```yaml
   # === SECTION DEFAULTS ===
   variable_default: "value"  # Description of what this controls
   ```

3. **Keep defaults reasonable**:
   - Use industry-standard ports
   - Follow security best practices
   - Consider production use cases

4. **Validate required variables**:
   ```yaml
   - name: Validate required variables
     fail:
       msg: "vault_postgres_password is required"
     when: vault_postgres_password is not defined
   ```

## Common Patterns

### Service Ports
```yaml
# In defaults/vault.yml
vault_postgresql_port_default: 5432
vault_redis_port_default: 6379
vault_nginx_http_port_default: 80

# In playbook
postgresql_port: "{{ vault_postgresql_port | default(vault_postgresql_port_default) }}"
```

### Feature Flags
```yaml
# In defaults/security.yml
ssh_password_authentication_default: "no"
fail2ban_enabled_default: "yes"

# In task
when: ssh_password_authentication | default(ssh_password_authentication_default) == "yes"
```

### Configuration Values
```yaml
# In defaults/system.yml
system_swap_size_mb_default: 2048
system_timezone_default: "UTC"

# In template
swap_size: {{ system_swap_size | default(system_swap_size_mb_default) }}
```

## Summary

The key benefits of this approach:
- **No inline defaults**: All defaults are centralized
- **Clear variable sources**: Easy to see what comes from vault vs defaults
- **Consistent naming**: `_default` suffix makes defaults obvious
- **Better security**: Required secrets have no defaults
- **Easier maintenance**: Change defaults in one place

Remember: If a variable has a default value, it MUST end with `_default`!