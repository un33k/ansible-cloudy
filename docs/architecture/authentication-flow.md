# Infrastructure Automation Flow

## Overview
This project provides automated configuration and deployment for Linux servers, with a security-first approach and support for multiple server flavors/roles.

## Core Security Flow
Every server MUST follow this security hardening sequence:

1. **Initial Connection**: Connect as root with password
2. **SSH Key Deployment**: Push SSH public key to root user
3. **Disable Root Password**: Root access via SSH keys only
4. **Optional Grunt User**: 
   - If defined in vault, create grunt user with:
     - Password authentication
     - SSH key authentication
     - Sudo privileges
   - If grunt user already exists:
     - Reset password to vault-defined value
     - Update SSH keys to vault-defined keys
5. **Ongoing Management**: All remote configuration uses root via SSH keys

## Base Configuration Flow
After security hardening, ALL servers receive base configuration:

1. **Run Security Playbook**: Mandatory security hardening
2. **Run Base Playbook**: Core system configuration
3. **Select Server Flavor**: Deploy specific role configuration

## Server Flavors

### 1. Database Server
- **PostgreSQL**: `psql --install`
  - Optional extensions: `--pgis` (PostGIS), `--pgvector` (pgvector)
  - Custom port configurable via vault settings

### 2. Cache Server
- **Redis**: `redis --install`
  - Custom port configurable via vault settings
  - Persistence options (RDB/AOF)
  - Master-slave replication support
  - Password authentication
  - Excellent TypeScript/Python client support

### 2.5. Connection Pooler (Web Server Component)
- **PgBouncer**: Installed on web servers for local pooling
  - Lightweight (~2MB memory footprint)
  - Transaction pooling mode for web applications
  - Reduces database connections by 10x
  - Configurable port (default: 6432)
  - MD5 authentication support
  - Zero application changes needed (drop-in replacement)

### 3. Load Balancer
- **Nginx**: `nginx --install`
  - SSL termination with Let's Encrypt
  - Auto-renewal configured for certificates
  - Custom port configurable via vault settings
  - Security hardened configuration:
    - Hide server version and tokens
    - Secure headers (HSTS, X-Frame-Options, etc.)
    - Rate limiting
    - Request size limits
  - Preserves client headers to backend:
    - X-Real-IP
    - X-Forwarded-For
    - X-Forwarded-Proto
    - X-Forwarded-Host
    - Host header passthrough
  - Handles traffic distribution to web servers

### 4. Web Server
**Options:**
- **TypeScript/Node.js**: Modern TypeScript applications
  - Express.js, NestJS, or custom frameworks
  - PM2 process manager
  - Development and production modes
- **Python/Django**: Python web applications
  - Django with Gunicorn/uWSGI
  - Celery support for async tasks
  - Development and production modes

**Connection Pooling:**
- PgBouncer installed locally on each web server
- Reduces database connections by 10x
- Transaction pooling for maximum efficiency

**Architecture Example:**
```
User → Load Balancer (SSL) → Web Server → PgBouncer (localhost) → Database (PostgreSQL)
                              (Django)     (local connection pooling)
```

### 5. Generic Server
- Receives security + base configuration
- Ready for custom deployments
- Clean slate for any application

### 6. Standalone Server (All-in-One)
**Components on single server:**
- Local PostgreSQL (with dependencies)
- Web application:
  - Django + dependencies OR
  - Node.js/TypeScript + dependencies
- Redis cache layer

### 7. VPN Server
**Options:**
- **V2Ray**: Modern VPN protocol
  - Zero DNS leak configuration
  - Custom port configurable via vault settings
- **OpenVPN**: Traditional VPN solution
  - Zero DNS leak configuration
  - Custom port configurable via vault settings

## Deployment Sequence

### Standard Multi-Server Deployment:
1. **Security Phase**: Run security playbook on all servers
2. **Base Phase**: Run base playbook on all servers
3. **Specialization Phase**: Deploy specific flavors:
   - Database servers first (PostgreSQL)
   - Cache server second (Redis)
   - Web servers third (TypeScript/Python)
   - Load balancers last (Nginx with SSL)

### Standalone Deployment:
1. **Security Phase**: Run security playbook
2. **Base Phase**: Run base playbook
3. **All-in-One Phase**: Deploy all components:
   - PostgreSQL
   - Redis cache
   - Web application (TypeScript or Python)
   - Local reverse proxy if needed

## Port Configuration

All services support custom port configuration via vault files (`./vault/*.yml`):

```yaml
# Example vault configuration
vault_ssh_port: 2222
vault_postgres_port: 5432
vault_redis_port: 6379
vault_redis_password: "secure_redis_password"
vault_nginx_http_port: 80
vault_nginx_https_port: 443
vault_openvpn_port: 1194
vault_v2ray_port: 10086
```

## Key Principles

1. **Security First**: No server deployment without security hardening
2. **SSH Key Only**: Root automation exclusively via SSH keys
3. **Modular Design**: Each flavor is independent and composable
4. **Idempotent**: Playbooks can be run multiple times safely
5. **Flexible Architecture**: Support for various deployment patterns
6. **Custom Ports**: All services configurable via vault settings
7. **SSL by Default**: Load balancers auto-configure Let's Encrypt SSL
8. **Zero DNS Leak**: VPN servers configured for complete privacy

## Connection Flow for Web Applications

### With Connection Pooling (PgBouncer):
```
Internet → Load Balancer (Nginx with SSL/Let's Encrypt)
         → Web Server 1 + PgBouncer → 
         → Web Server 2 + PgBouncer → PostgreSQL (configurable port)
         → Web Server N + PgBouncer →

Each web server has local PgBouncer (localhost:6432)
```

### Direct Connection:
```
Internet → Load Balancer (Nginx with SSL/Let's Encrypt)
         → Web Servers (Django/Node.js)
         → Database (PostgreSQL on vault-defined port)
```

## Notes
- All servers start with the same security baseline
- Grunt user is optional but recommended for emergency access
- Grunt user credentials are managed via vault - existing users get updated passwords/keys
- Root remains accessible via SSH keys for automation
- Each flavor can be deployed independently after base setup
- All service ports are configurable via vault files
- SSL certificates are auto-provisioned and renewed via Let's Encrypt
- VPN servers include DNS leak protection by default