# Variable Naming Migration Guide

This guide helps you migrate from the old variable naming conventions to the new standardized naming.

## Overview

We've standardized all variable names to follow a consistent pattern:
- `service_setting` format (e.g., `postgresql_port`, `redis_memory_mb`)
- Service prefix matches the actual service name
- Clear, descriptive names without abbreviations

## Migration Table

### PostgreSQL Variables

| Old Variable Name | New Variable Name | Default Value |
|------------------|-------------------|---------------|
| `pg_version` | `postgresql_version` | `17` |
| `pg_port` | `postgresql_port` | `5432` |
| `database_port` | `postgresql_port` | `5432` |
| `vault_postgresql_port` | `postgresql_port` | `5432` |
| `pg_databases` | `postgresql_databases` | `[]` |
| `pg_users` | `postgresql_users` | `[]` |
| `pg_listen_addresses` | `postgresql_listen_addresses` | `localhost` |
| `pg_max_connections` | `postgresql_max_connections` | `100` |
| `pg_shared_buffers` | `postgresql_shared_buffers` | `256MB` |

### Redis Variables

| Old Variable Name | New Variable Name | Default Value |
|------------------|-------------------|---------------|
| `redis_memory` | `redis_memory_mb` | `0` (auto) |
| `redis_maxmemory` | `redis_memory_mb` | `0` (auto) |
| `memory` | `redis_memory_mb` | `0` (auto) |
| `divider` | `redis_memory_divider` | `8` |
| `port` | `redis_port` | `6379` |
| `interface` | `redis_interface` | `0.0.0.0` |
| `password` | `redis_password` | `''` |

### Nginx Variables

| Old Variable Name | New Variable Name | Default Value |
|------------------|-------------------|---------------|
| `domain_name` | `nginx_domain` | `{{ inventory_hostname }}` |
| `domain` | `nginx_domain` | `{{ inventory_hostname }}` |
| `protocol` | `nginx_protocol` | `https` |
| `proto` | `nginx_protocol` | `https` |
| `upstream_servers` | `nginx_upstream_servers` | `[]` |
| `backends` | `nginx_upstream_servers` | `[]` |
| `ssl_cert_dir` | `nginx_ssl_cert_dir` | `/etc/nginx/ssl` |
| `ssl_enabled` | `nginx_ssl_enabled` | `true` |

### PgBouncer Variables

| Old Variable Name | New Variable Name | Default Value |
|------------------|-------------------|---------------|
| `pgbouncer_listen_port` | `pgbouncer_port` | `6432` |
| `pgbouncer_listen_addr` | `pgbouncer_listen_address` | `127.0.0.1` |
| `pgbouncer_db_host` | `pgbouncer_backend_host` | `localhost` |
| `pgbouncer_database_host` | `pgbouncer_backend_host` | `localhost` |
| `pgbouncer_db_port` | `pgbouncer_backend_port` | `5432` |
| `pgbouncer_database_port` | `pgbouncer_backend_port` | `5432` |
| `pgbouncer_db_name` | `pgbouncer_default_database` | `postgres` |
| `pgbouncer_database_name` | `pgbouncer_default_database` | `postgres` |

## How to Migrate

### 1. Update Your Inventory Files

**Before:**
```yaml
database_servers:
  hosts:
    db1:
      pg_version: "16"
      pg_port: 5433
      redis_memory: 512
```

**After:**
```yaml
database_servers:
  hosts:
    db1:
      postgresql_version: "16"
      postgresql_port: 5433
      redis_memory_mb: 512
```

### 2. Update Your Vault Files

**Before:**
```yaml
vault_postgresql_port: 5432
vault_redis_password: "secret123"
```

**After:**
```yaml
# These still work but you can also use:
postgresql_port: 5432
redis_password: "secret123"
```

### 3. Update Claudia Commands

**Before:**
```bash
./cli psql --install -- -e "pg_port=5433"
./cli redis --install -- -e "redis_memory=512"
```

**After:**
```bash
# Now using universal parameters (recommended)
./cli psql --install --port 5433
./cli redis --install --memory 512

# Or with new variable names
./cli psql --install -- -e "postgresql_port=5433"
./cli redis --install -- -e "redis_memory_mb=512"
```

## Backward Compatibility

All playbooks include variable mappings for backward compatibility, so your existing configurations will continue to work. However, we recommend migrating to the new naming convention for:

1. **Consistency** - All variables follow the same pattern
2. **Clarity** - No more guessing what `pg_` stands for
3. **Maintainability** - Easier to find and update variables
4. **Future-proofing** - New features will use the standardized naming

## Timeline

- **Current**: Both old and new variable names are supported
- **Future**: Old variable names will be deprecated with warnings
- **Later**: Old variable names will be removed

We recommend migrating as soon as possible to avoid future issues.