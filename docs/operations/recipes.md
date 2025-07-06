# Deployment Recipes

Complete guide to all available deployment recipes in Ansible Cloudy.

## Overview

Recipes are high-level deployment playbooks that orchestrate multiple tasks to deploy complete services. They are designed to be production-ready, secure, and idempotent.

## Core Recipes

### Security Setup

**Purpose**: Initial server security configuration

```bash
cli security --install
```

Features:
- SSH key installation
- Firewall configuration (UFW)
- SSH port change (22 → 2222)
- Optional grunt user creation
- Root password authentication disabled
- Security hardening

Options:
- `--prod`: Production hardening
- `--check`: Dry run mode

### Base Configuration

**Purpose**: Basic system setup

```bash
cli base --install
```

Features:
- Hostname configuration
- Timezone and locale setup
- Git configuration
- Essential packages
- Swap file setup
- System optimization

## Database Recipes

### PostgreSQL

**Purpose**: PostgreSQL database server

```bash
cli psql --install
```

Features:
- Latest PostgreSQL version
- Optimized configuration
- Automatic tuning
- Database/user creation
- Backup configuration

Options:
- `--port 5433`: Custom port
- `--version 15`: Specific version
- `--pgis`: Include PostGIS

### PostGIS

**Purpose**: PostgreSQL with PostGIS extension

```bash
cli postgis --install
```

Features:
- PostgreSQL + PostGIS
- Spatial database support
- GIS functionality
- All PostgreSQL features

### pgvector

**Purpose**: PostgreSQL with pgvector for AI/ML

```bash
cli pgvector --install
```

Features:
- Vector similarity search
- AI/ML embeddings storage
- Optimized for vector operations
- HNSW and IVFFlat indexes

Options:
- `--dimensions 1536`: Vector dimensions
- `--index-type hnsw`: Index type

## Caching Recipes

### Redis

**Purpose**: Redis cache server

```bash
cli redis --install
```

Features:
- Memory optimization
- Persistence options
- Password authentication
- Custom configuration

Options:
- `--port 6380`: Custom port
- `--memory 1024`: Memory limit (MB)
- `--password`: Enable authentication

### Redis Production

**Purpose**: Hardened Redis for production

```bash
cli redis --install --prod
```

Additional features:
- AOF persistence
- RDB snapshots
- Memory policies
- Security hardening
- Monitoring setup

## Web Server Recipes

### Nginx Load Balancer

**Purpose**: Nginx as load balancer/reverse proxy

```bash
cli nginx --install
```

Features:
- Load balancing
- SSL/TLS support
- DDoS protection
- Caching
- Compression

Options:
- `--domain example.com`: Domain name
- `--ssl`: Enable HTTPS
- `--backends "10.0.0.1:8080,10.0.0.2:8080"`: Backend servers

### Django Application

**Purpose**: Complete Django deployment

```bash
cli django --install
```

Features:
- Python environment
- Gunicorn/uWSGI
- Nginx integration
- Static file serving
- Database configuration
- Supervisor setup

### Node.js Application

**Purpose**: Node.js with PM2

```bash
cli nodejs --install
```

Features:
- Node.js latest/LTS
- PM2 process manager
- Nginx reverse proxy
- Auto-restart
- Clustering support

Options:
- `--version 18`: Node.js version
- `--port 3000`: Application port

## Service Recipes

### PgBouncer

**Purpose**: PostgreSQL connection pooling

```bash
cli pgbouncer --install
```

Features:
- Connection pooling
- Transaction pooling mode
- Authentication
- Monitoring
- High performance

Options:
- `--port 6432`: Listen port
- `--pool-size 25`: Connection pool size

### OpenVPN

**Purpose**: VPN server with Docker

```bash
cli openvpn --install
```

Features:
- Docker-based deployment
- Client management
- Certificate generation
- Firewall rules
- Easy client creation

## Standalone Recipe

### All-in-One Server

**Purpose**: Complete stack on single server

```bash
cli standalone --install
```

Includes:
- PostgreSQL database
- Redis cache
- Nginx web server
- Application (Django/Node.js)
- Monitoring
- Security hardening

Options:
- `--app-type django`: Application type
- `--domain example.com`: Domain name
- `--enable-ssl`: HTTPS setup

## Recipe Combinations

### Web Application Stack

```bash
# 1. Secure the server
cli security --install --prod

# 2. Base configuration
cli base --install --prod

# 3. Database
cli psql --install --prod

# 4. Cache
cli redis --install --prod

# 5. Web application
cli django --install --prod

# 6. Load balancer
cli nginx --install --prod --domain example.com --ssl
```

### Microservices Infrastructure

```bash
# Database servers
cli psql --install --prod -H db-01
cli psql --install --prod -H db-02

# Cache servers
cli redis --install --prod -H cache-01
cli redis --install --prod -H cache-02

# Application servers
cli nodejs --install --prod -H app-01
cli nodejs --install --prod -H app-02

# Load balancer
cli nginx --install --prod -H lb-01 --backends "app-01:3000,app-02:3000"
```

## Production Considerations

### Environment Selection

```bash
# Development (default)
cli [recipe] --install

# Production
cli [recipe] --install --prod

# CI/CD
cli [recipe] --install --ci
```

### Custom Configuration

```bash
# With custom inventory
cli [recipe] --install -i inventory/custom.yml

# With vault overrides
cli [recipe] --install -e .vault/prod-secrets.yml

# Target specific host
cli [recipe] --install -H 192.168.1.100
```

### Dry Run Mode

Always test with `--check` first:

```bash
cli [recipe] --install --check
```

## Recipe Development

### Creating Custom Recipes

1. Create playbook in `/cloudy/playbooks/recipes/`
2. Include necessary tasks
3. Define variables with defaults
4. Add tags for selective execution
5. Document in recipe header

Example structure:
```yaml
---
# Recipe: My Custom Service
# Purpose: Deploy custom application
# Usage: cli myservice --install

- name: My Custom Service Setup
  hosts: service_targets
  vars_files:
    - "../../../defaults/all.yml"
    - "../../../defaults/myservice.yml"
  
  tasks:
    - include_tasks: "../../../tasks/myservice/install.yml"
      tags: [install]
    
    - include_tasks: "../../../tasks/myservice/configure.yml"
      tags: [configure]
```

### Recipe Best Practices

1. **Idempotency**: Can run multiple times safely
2. **Error handling**: Graceful failure modes
3. **Validation**: Check prerequisites
4. **Documentation**: Clear usage instructions
5. **Tags**: Enable partial execution
6. **Variables**: Sensible defaults

## Troubleshooting Recipes

### Common Issues

1. **Connection failures**: Check SSH keys and ports
2. **Permission denied**: Verify user permissions
3. **Package conflicts**: Check OS compatibility
4. **Port conflicts**: Ensure ports are available
5. **Memory issues**: Check system resources

### Debug Mode

```bash
# Verbose output
cli [recipe] --install -v

# Very verbose
cli [recipe] --install -vvv
```

### Logs

Check service logs:
```bash
journalctl -u postgresql
journalctl -u redis
journalctl -u nginx
```

## Next Steps

- Learn about [Configuration](configuration.md)
- Explore [Command Reference](commands.md)
- Read [Troubleshooting Guide](../reference/troubleshooting.md)