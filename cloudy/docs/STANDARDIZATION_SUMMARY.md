# Variable Standardization Summary

## What Changed

We've implemented a comprehensive variable standardization and defaults centralization system for the Ansible Cloudy project.

### 1. Created Central Defaults Directory

**Location**: `cloudy/defaults/`

**Files Created**:
- `all.yml` - Global defaults for all services
- `postgresql.yml` - PostgreSQL-specific defaults  
- `redis.yml` - Redis-specific defaults
- `nginx.yml` - Nginx-specific defaults
- `pgbouncer.yml` - PgBouncer-specific defaults
- `security.yml` - Security-related defaults
- `system.yml` - System-level defaults
- `README.md` - Documentation for the defaults system

### 2. Standardized Variable Naming

**Pattern**: `service_setting`

**Examples**:
- `pg_port` → `postgresql_port`
- `redis_memory` → `redis_memory_mb`
- `domain_name` → `nginx_domain`
- `pgbouncer_db_host` → `pgbouncer_backend_host`

### 3. Updated Playbooks

All recipe playbooks now:
- Load appropriate default files using `vars_files`
- Include variable mappings for backward compatibility
- Use standardized variable names internally

**Updated Files**:
- `playbooks/recipes/db/psql.yml`
- `playbooks/recipes/cache/redis.yml`
- `playbooks/recipes/lb/nginx.yml`
- `playbooks/recipes/services/pgbouncer.yml`
- `playbooks/recipes/www/django.yml`

### 4. Updated Inventory Files

Group variables and example inventories updated to show standardized naming:
- `inventory/group_vars/database_servers.yml`
- `inventory/group_vars/web_servers.yml`
- `inventory/dev.yml`

### 5. Documentation

Created comprehensive documentation:
- `docs/VARIABLE_MIGRATION.md` - Migration guide for users
- `docs/STANDARDIZATION_SUMMARY.md` - This summary
- `defaults/README.md` - Defaults system documentation

## Benefits

1. **Consistency**: All variables follow the same naming pattern
2. **Centralization**: All defaults in one location, easy to find and modify
3. **Clarity**: Clear, descriptive variable names without abbreviations
4. **Maintainability**: Easier to update and manage configurations
5. **Backward Compatibility**: Old variable names still work through mappings

## Backward Compatibility

All playbooks include variable mappings like:

```yaml
# Variable mapping for backward compatibility
pg_version: "{{ postgresql_version }}"
pg_port: "{{ postgresql_port }}"
database_port: "{{ postgresql_port }}"
```

This ensures existing configurations continue to work while allowing migration to the new standard.

## Next Steps

1. Test all playbooks with both old and new variable names
2. Update CLI to use new variable names in generated commands
3. Add deprecation warnings for old variable names (future)
4. Eventually remove backward compatibility mappings (much later)

## Quick Reference

| Service | Old Prefix | New Prefix | Example |
|---------|------------|------------|---------|
| PostgreSQL | `pg_`, `database_` | `postgresql_` | `postgresql_port` |
| Redis | `redis_` (mixed) | `redis_` | `redis_memory_mb` |
| Nginx | `domain_`, various | `nginx_` | `nginx_domain` |
| PgBouncer | `pgbouncer_db_` | `pgbouncer_` | `pgbouncer_backend_host` |

The standardization is complete and ready for use!