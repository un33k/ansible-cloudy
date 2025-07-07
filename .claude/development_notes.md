# Ansible Cloudy Development Notes

## Version Status
- Current version: Pre-v1.1 (not yet released)
- Backward compatibility is NOT a concern for changes made before v1.1 release

## Architecture Decisions

### Service Installation Pattern (Implemented)
As of this change, we have two distinct installation patterns:

1. **Service-only commands** (`psql`, `nginx`, `redis`, etc.)
   - Install ONLY the specified service
   - NO automatic dependency installation (no security, no base)
   - For advanced users who already have secured/prepared servers
   - Example: `cli psql --install`

2. **Full server commands** (`psql-server`, `nginx-server`, etc.)
   - Complete server setup: security → base → service
   - For new server deployments
   - Ensures proper hardening and configuration
   - Example: `cli psql-server --install`

### Special Cases
- `pgbouncer`: Always standalone (no -server variant) as it's installed on existing web servers
- `django-server` and `nodejs-server`: Also install pgbouncer automatically
- Environment (dev/ci/prod) is orthogonal to this pattern and controlled by:
  - Default: dev
  - Flags: --dev, --ci, --prod
  - Vault configuration

### Rationale
This pattern provides clarity and flexibility:
- Clear user intent (service vs full server)
- No surprises for advanced users
- Safe defaults for new users
- Clean separation of concerns