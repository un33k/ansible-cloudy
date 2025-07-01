# Ansible Variable Defaults

This directory contains centralized default values for all Ansible variables used in the cloudy playbooks.

## Variable Naming Convention

All variables follow a standardized naming pattern:
- `service_setting` - e.g., `postgresql_port`, `redis_memory_mb`, `nginx_domain`
- Service prefix matches the service name (postgresql, redis, nginx, pgbouncer, etc.)
- Use underscores to separate words
- Be explicit and descriptive

## File Structure

- `all.yml` - Global defaults for all services (timezone, locale, paths, etc.)
- `postgresql.yml` - PostgreSQL-specific defaults
- `redis.yml` - Redis-specific defaults  
- `nginx.yml` - Nginx-specific defaults
- `pgbouncer.yml` - PgBouncer-specific defaults
- `security.yml` - Security-related defaults (SSH, firewall, etc.)
- `system.yml` - System-level defaults (packages, users, swap, etc.)

## Usage

These defaults are loaded automatically by playbooks using `vars_files`:

```yaml
vars_files:
  - "../../../defaults/all.yml"
  - "../../../defaults/postgresql.yml"
```

## Variable Precedence

Variables can be overridden at multiple levels (from lowest to highest precedence):
1. Default files (this directory)
2. Inventory group_vars
3. Inventory host_vars
4. Playbook vars
5. Command line with `-e` or Claudia CLI parameters

## Backward Compatibility

Many playbooks include variable mappings for backward compatibility:

```yaml
# Variable mapping for backward compatibility
pg_version: "{{ postgresql_version }}"
pg_port: "{{ postgresql_port }}"
```

These mappings allow old variable names to work while transitioning to the new standard.

## Vault Variables

Sensitive values should use vault variables with fallbacks:

```yaml
postgresql_password: "{{ vault_postgres_password | default('') }}"
redis_password: "{{ vault_redis_password | default('') }}"
```

## Adding New Defaults

When adding new services or variables:
1. Use the standardized naming convention
2. Add defaults to the appropriate file
3. Include helpful comments and examples
4. Update playbooks to load the defaults file
5. Add backward compatibility mappings if replacing old variables