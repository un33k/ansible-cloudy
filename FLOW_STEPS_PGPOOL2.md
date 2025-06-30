# PgPool2 Implementation Steps

## Overview
This document outlines the implementation of PgPool2 connection pooling for PostgreSQL in ansible-cloudy, based on best practices from python-cloudy.

## Implementation Layers

### Layer 1: Task Files (Foundation)
Create modular task files for PgPool2 operations:

#### Installation Tasks
- [x] `/cloudy/tasks/db/pgpool2/install.yml` - Install pgpool2 package
- [x] `/cloudy/tasks/db/pgpool2/install-dependencies.yml` - Install required dependencies (included in install.yml)

#### Configuration Tasks
- [x] `/cloudy/tasks/db/pgpool2/configure.yml` - Main configuration task
- [x] `/cloudy/tasks/db/pgpool2/configure-backends.yml` - Configure PostgreSQL backends
- [x] `/cloudy/tasks/db/pgpool2/configure-pooling.yml` - Set connection pool parameters (included in configure.yml)
- [x] `/cloudy/tasks/db/pgpool2/configure-auth.yml` - Setup authentication (included in configure.yml)

#### Service Management Tasks
- [x] `/cloudy/tasks/db/pgpool2/start.yml` - Start pgpool2 service
- [ ] `/cloudy/tasks/db/pgpool2/stop.yml` - Stop pgpool2 service (optional)
- [x] `/cloudy/tasks/db/pgpool2/restart.yml` - Restart pgpool2 service
- [x] `/cloudy/tasks/db/pgpool2/enable.yml` - Enable service on boot (included in configure.yml)

#### Validation Tasks
- [ ] `/cloudy/tasks/db/pgpool2/validate-config.yml` - Validate configuration (optional)
- [x] `/cloudy/tasks/db/pgpool2/health-check.yml` - Check pgpool2 health

### Layer 2: Templates
Create Jinja2 templates for configuration files:

- [x] `/cloudy/templates/pgpool2/pgpool.conf.j2` - Main configuration
- [x] `/cloudy/templates/pgpool2/pool_hba.conf.j2` - Authentication rules
- [ ] `/cloudy/templates/pgpool2/pool_passwd.j2` - User passwords (optional)

### Layer 3: Variable Definitions
Define default variables and vault integration:

#### Group Variables
- [ ] Add pgpool2 variables to `/cloudy/inventory/group_vars/database_servers.yml`
- [ ] Define connection pool settings, ports, backends

#### Vault Variables
- [ ] Update vault examples to include pgpool2 settings
- [ ] Add `vault_pgpool2_port`, `vault_pgpool2_max_connections`

### Layer 4: Playbook Integration
Update existing playbooks to support pgpool2:

- [x] Update `/cloudy/playbooks/recipes/db/postgis.yml` to include pgpool2 option
- [x] Create `/cloudy/playbooks/recipes/db/pgpool2.yml` standalone recipe

### Layer 5: Firewall Rules
Add firewall management for pgpool2:

- [x] Create `/cloudy/tasks/sys/firewall/allow-pgpool2.yml` (using allow-port.yml)
- [ ] Update security configurations

### Layer 6: Claudia CLI Integration
Add pgpool2 support to Claudia:

- [ ] Create `/dev/claudia/operations/pgpool2.py` service module
- [x] Add pgpool2 to dependency manager
- [ ] Support parameters: `--port`, `--backends`, `--max-connections`

### Layer 7: Documentation
Update documentation:

- [ ] Update FLOW.md to include pgpool2 in architecture
- [ ] Add pgpool2 examples to CLAUDE.md
- [ ] Document connection pooling best practices

## Configuration Approach

### Default Configuration
Based on python-cloudy best practices:
```yaml
# Connection Settings
pgpool2_port: 5432          # Default PostgreSQL port
pgpool2_backend_port: 5433  # Actual PostgreSQL port
pgpool2_backend_host: localhost

# Pool Settings
pgpool2_num_init_children: 32
pgpool2_max_pool: 4
pgpool2_child_life_time: 300
pgpool2_connection_life_time: 0
pgpool2_client_idle_limit: 0

# Load Balancing
pgpool2_load_balance_mode: off
pgpool2_replication_mode: off
pgpool2_master_slave_mode: off

# Health Checks
pgpool2_health_check_period: 0
pgpool2_health_check_timeout: 20
```

### Architecture Pattern
```
Client App → PgPool2 (5432) → PostgreSQL (5433)
```

### Key Features to Implement
1. **Simple Connection Pooling**: Focus on connection reuse
2. **Transparent Proxy**: Apps connect to pgpool2 as if it's PostgreSQL
3. **Configurable Ports**: Support custom ports via vault
4. **Service Management**: Proper start/stop/restart handling
5. **Health Monitoring**: Basic health checks
6. **Secure Defaults**: Conservative pool settings

## Testing Strategy
1. Install pgpool2 on test server
2. Configure with PostgreSQL backend
3. Test connection pooling
4. Verify performance improvements
5. Test failover scenarios (if applicable)

## Migration Path
For existing PostgreSQL installations:
1. Install pgpool2 alongside PostgreSQL
2. Configure PostgreSQL on alternate port (5433)
3. Configure pgpool2 on standard port (5432)
4. Update application connection strings (if needed)
5. Monitor connection pooling effectiveness