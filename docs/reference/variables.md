# Variable Reference

Complete reference of all configurable variables in Ansible Cloudy.

## Variable Naming Convention

All variables follow a consistent naming pattern:

- **Vault variables**: `vault_*` - User-provided sensitive values
- **Default variables**: `*_default` - System defaults
- **Service variables**: `<service>_*` - Service-specific settings

## Global Variables

### Authentication & Connection

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_root_user` | `root` | Root user for SSH connections | No |
| `vault_root_password` | - | Root password for initial connection | Yes (Harden only) |
| `vault_root_ssh_private_key_file` | `~/.ssh/id_rsa` | Root user SSH private key path | No |
| `vault_root_ssh_password_authentication` | `false` | Allow password auth for root | No |
| `vault_ssh_port_initial` | `22` | SSH port before hardening | No |
| `vault_ssh_port_final` | `22022` | SSH port after hardening | No |
| `vault_ssh_host_key_checking` | `false` | SSH host key checking | No |
| `vault_ssh_common_args` | `-o StrictHostKeyChecking=no` | Common SSH arguments | No |

### Optional Grunt User

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_grunt_user` | - | Service user name (empty = skip) | No |
| `vault_grunt_password` | - | Service user password | If user defined |
| `vault_grunt_groups` | `admin,www-data` | Groups for grunt user | No |
| `vault_grunt_ssh_private_key_file` | `~/.ssh/id_rsa` | Grunt user SSH key | No |

### System Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_hostname` | - | Server hostname | No |
| `vault_timezone` | `America/New_York` | System timezone | No |
| `vault_locale` | `en_US.UTF-8` | System locale | No |
| `vault_git_user_full_name` | `System Administrator` | Git user name | No |
| `vault_git_user_email` | `admin@example.com` | Git user email | No |

## PostgreSQL Variables

### Basic Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_postgres_password` | - | PostgreSQL superuser password | Yes |
| `vault_postgresql_port` | `5432` | PostgreSQL port | No |
| `vault_postgresql_version` | `15` | PostgreSQL major version | No |
| `vault_postgresql_listen_addresses` | `localhost` | Listen addresses | No |
| `vault_postgresql_max_connections` | `100` | Maximum connections | No |

### Performance Tuning

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_postgresql_shared_buffers` | 25% of RAM | Shared memory buffers | No |
| `vault_postgresql_effective_cache_size` | 75% of RAM | Effective cache size | No |
| `vault_postgresql_work_mem` | `4MB` | Work memory | No |
| `vault_postgresql_maintenance_work_mem` | `64MB` | Maintenance work memory | No |
| `vault_postgresql_wal_buffers` | `16MB` | WAL buffers | No |

### Backup Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_postgresql_backup_enabled` | `true` | Enable backups | No |
| `vault_postgresql_backup_schedule` | `0 2 * * *` | Backup cron schedule | No |
| `vault_postgresql_backup_retention` | `7` | Days to keep backups | No |
| `vault_postgresql_backup_directory` | `/var/backups/postgresql` | Backup location | No |

## Redis Variables

### Basic Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_redis_password` | - | Redis password (empty = none) | No |
| `vault_redis_port` | `6379` | Redis port | No |
| `vault_redis_bind` | `127.0.0.1` | Bind address | No |
| `vault_redis_memory_mb` | `512` | Memory limit in MB | No |
| `vault_redis_maxmemory_policy` | `allkeys-lru` | Eviction policy | No |

### Persistence

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_redis_persistence_enabled` | `true` | Enable persistence | No |
| `vault_redis_appendonly` | `yes` | AOF persistence | No |
| `vault_redis_appendfsync` | `everysec` | AOF sync policy | No |
| `vault_redis_save` | Multiple | RDB save points | No |

## Nginx Variables

### Basic Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_nginx_http_port` | `80` | HTTP port | No |
| `vault_nginx_https_port` | `443` | HTTPS port | No |
| `vault_nginx_worker_processes` | `auto` | Worker processes | No |
| `vault_nginx_worker_connections` | `1024` | Connections per worker | No |

### SSL Configuration

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_nginx_ssl_certificate` | - | SSL certificate path | If SSL enabled |
| `vault_nginx_ssl_certificate_key` | - | SSL key path | If SSL enabled |
| `vault_nginx_ssl_protocols` | `TLSv1.2 TLSv1.3` | SSL protocols | No |
| `vault_nginx_ssl_ciphers` | Secure list | SSL cipher suite | No |

### Load Balancing

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_nginx_upstream_servers` | - | Backend servers | For LB |
| `vault_nginx_load_balance_method` | `least_conn` | LB algorithm | No |
| `vault_nginx_keepalive` | `32` | Keepalive connections | No |

## PgBouncer Variables

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_pgbouncer_port` | `6432` | PgBouncer port | No |
| `vault_pgbouncer_pool_mode` | `transaction` | Pool mode | No |
| `vault_pgbouncer_default_pool_size` | `25` | Default pool size | No |
| `vault_pgbouncer_max_client_conn` | `100` | Max client connections | No |
| `vault_pgbouncer_auth_type` | `md5` | Authentication type | No |

## Node.js Variables

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_nodejs_version` | `18` | Node.js major version | No |
| `vault_nodejs_port` | `3000` | Application port | No |
| `vault_nodejs_app_name` | `app` | PM2 app name | No |
| `vault_nodejs_instances` | `max` | PM2 instances | No |
| `vault_nodejs_env` | `production` | Node environment | No |

## Security Variables

### Firewall

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_firewall_allowed_ports` | `[22, 80, 443]` | Allowed ports | No |
| `vault_firewall_allowed_networks` | `[]` | Allowed networks | No |
| `vault_firewall_ssh_rate_limit` | `6/minute` | SSH rate limit | No |

### SSH Hardening

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_ssh_permit_root_login` | `prohibit-password` | Root login policy | No |
| `vault_ssh_password_authentication` | `no` | Password auth | No |
| `vault_ssh_max_auth_tries` | `3` | Max auth attempts | No |
| `vault_ssh_client_alive_interval` | `300` | Keepalive interval | No |

## Application Variables

### Django

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_django_secret_key` | - | Django secret key | Yes |
| `vault_django_debug` | `false` | Debug mode | No |
| `vault_django_allowed_hosts` | `['*']` | Allowed hosts | No |
| `vault_django_database_name` | `django_db` | Database name | No |
| `vault_django_database_user` | `django_user` | Database user | No |

### Standalone Deployment

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_app_type` | `django` | App type (django/nodejs) | No |
| `vault_domain` | Server IP | Domain name | No |
| `vault_enable_ssl` | `true` | Enable SSL | No |
| `vault_app_name` | `webapp` | Application name | No |
| `vault_app_port` | `8000`/`3000` | Application port | No |

## Environment-Specific Variables

### Production Mode

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_production_mode` | `false` | Enable production hardening | No |
| `vault_enable_monitoring` | `true` | Enable monitoring | No |
| `vault_enable_audit` | `true` | Enable audit logging | No |
| `vault_enable_fail2ban` | `true` | Enable fail2ban | No |

### Development Mode

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `vault_debug_mode` | `false` | Enable debug logging | No |
| `vault_verbose_logging` | `false` | Verbose logs | No |
| `vault_skip_security_hardening` | `false` | Skip hardening | No |

## Variable Usage Examples

### Basic Vault File

```yaml
# .vault/production.yml
---
# Required for initial connection
vault_root_password: "secure_root_password"

# Service passwords
vault_postgres_password: "secure_pg_password"
vault_redis_password: "secure_redis_password"

# Optional overrides
vault_postgresql_port: 5433
vault_redis_memory_mb: 2048
vault_nginx_worker_processes: 8
```

### Advanced Configuration

```yaml
# Production with custom settings
vault_production_mode: true
vault_postgresql_shared_buffers: "4GB"
vault_postgresql_max_connections: 500
vault_redis_maxmemory_policy: "volatile-lru"
vault_nginx_ssl_protocols: "TLSv1.3"
```

### Multi-Environment Setup

```yaml
# .vault/staging.yml
vault_root_password: "staging_password"
vault_debug_mode: true
vault_verbose_logging: true

# .vault/production.yml
vault_root_password: "prod_password"
vault_production_mode: true
vault_enable_monitoring: true
```

## Best Practices

1. **Required variables** - Always set required variables in vault
2. **Sensitive data** - Never put passwords in inventory
3. **Environment isolation** - Separate vault files per environment
4. **Documentation** - Document custom variables
5. **Validation** - Test with `--check` mode first
6. **Defaults** - Rely on defaults when possible

## Variable Debugging

```bash
# Show all variables for a host
ansible-inventory -i inventory/prod.yml --host myserver --vars

# Debug specific variable
ansible -i inventory/prod.yml myserver -m debug -a "var=vault_postgresql_port"

# Test variable resolution
cli psql --install --check -v
```