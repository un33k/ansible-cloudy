# Cleanup Steps - Bottom to Top Approach

## Overview
This document tracks the systematic cleanup of MySQL, pgbouncer, and memcached from the ansible-cloudy codebase, working from the bottom layer (tasks) up to the top layer (CLI).

## Layer 1: Tasks Cleanup (Bottom Layer)
### MySQL Tasks to Remove
- [x] `/cloudy/tasks/db/mysql/create-database.yml`
- [x] `/cloudy/tasks/db/mysql/create-user.yml`
- [x] `/cloudy/tasks/db/mysql/get-latest-version.yml`
- [x] `/cloudy/tasks/db/mysql/grant-privileges.yml`
- [x] `/cloudy/tasks/db/mysql/install-client.yml`
- [x] `/cloudy/tasks/db/mysql/install-server.yml`
- [x] `/cloudy/tasks/db/mysql/set-root-password.yml`
- [x] Remove empty `/cloudy/tasks/db/mysql/` directory

### PgBouncer Tasks to Remove
- [x] `/cloudy/tasks/db/pgbouncer/configure.yml`
- [x] `/cloudy/tasks/db/pgbouncer/install.yml`
- [x] `/cloudy/tasks/db/pgbouncer/set-user-password.yml`
- [x] Remove empty `/cloudy/tasks/db/pgbouncer/` directory

### Memcached Tasks to Remove
- [x] `/cloudy/tasks/services/memcached/configure-memory.yml`
- [x] `/cloudy/tasks/services/memcached/configure-port.yml`
- [x] `/cloudy/tasks/services/memcached/install-dev.yml`
- [x] `/cloudy/tasks/services/memcached/install.yml`
- [x] Remove empty `/cloudy/tasks/services/memcached/` directory

## Layer 2: Templates Cleanup
### PgBouncer Templates to Remove
- [x] `/cloudy/templates/pgbouncer.ini.j2`
- [x] `/cloudy/templates/pgbouncer-default.j2`

## Layer 3: Playbooks/Recipes Cleanup
### References to Update
- [x] `/cloudy/playbooks/recipes/db/postgis.yml` - Remove pgbouncer reference

## Layer 4: Inventory & Configuration Cleanup
### Inventory Files to Update
- [x] `/cloudy/inventory/group_vars/database_servers.yml` - Remove MySQL variables (lines 23-26)
- [x] `/cloudy/inventory/ci.yml` - Remove `vault_mysql_root_password`
- [x] `/cloudy/inventory/prod.yml` - Remove `vault_mysql_root_password`

### Vault Examples to Update
- [x] `/.vault/ci.yml.example` - Remove `vault_mysql_root_password`
- [x] `/.vault/dev.yml.example` - Remove `vault_mysql_root_password`
- [x] `/.vault/prod.yml.example` - Remove `vault_mysql_root_password`
- [x] `/.vault/README.md` - Remove MySQL password reference

## Layer 5: CLI Cleanup
### Dependency Manager Update
- [x] `/dev/cli/execution/dependency_manager.py` - Remove mysql and memcached from dependency mappings

### Service Discovery
- [x] Verify no service modules exist for mysql, pgbouncer, memcached (already confirmed none exist)

## Layer 6: Documentation Cleanup
### Main Documentation
- [x] `/CLAUDE.md` - Remove MySQL examples
- [x] `/README.md` - Remove MySQL references
- [x] `/FLOW.md` - Already updated (MySQL removed)

### Developer Documentation
- [x] `/docs/CONTRIBUTING.md` - Keep as educational example
- [x] `/docs/DEVELOPMENT.md` - Keep as educational example
- [x] `/docs/USAGE.md` - Remove service references

## Layer 7: Final Verification
### Testing & Validation
- [x] Run `./cli --list` to verify removed services don't appear
- [x] Search codebase for any remaining references: `grep -r "mysql\|pgbouncer\|memcached"`
- [x] Test security and base playbooks still work
- [x] Test remaining services (psql, redis, nginx, etc.) work correctly

## Execution Order
1. **Start with Tasks** (Layer 1) - Remove the foundation
2. **Templates** (Layer 2) - Remove configuration templates
3. **Playbooks** (Layer 3) - Update any references
4. **Configuration** (Layer 4) - Clean inventory and vault files
5. **CLI** (Layer 5) - Update dependency manager
6. **Documentation** (Layer 6) - Update all docs
7. **Verification** (Layer 7) - Test everything works

## Progress Tracking
- Total files to modify/remove: ~30
- Layers completed: 7/7
- Current layer: Completed all layers