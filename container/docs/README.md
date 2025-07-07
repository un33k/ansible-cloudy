# Container Module Documentation

## Overview

The container module provides Docker container runtime management and deployment capabilities through the CLI. It integrates with existing Ansible infrastructure to provide a consistent interface for container operations.

## Features

- **Docker Installation**: Install Docker CE with a single command
- **Container Deployment**: Deploy docker-compose stacks
- **User Management**: Add users to docker group
- **Pre-configured Stacks**: Ready-to-deploy templates for common applications

## Usage

### Installing Docker

```bash
# Install Docker CE
cli docker --install

# Install Docker and configure daemon
cli docker --install --configure
```

### Managing Docker Users

```bash
# Add user to docker group
cli docker --add-user username
```

### Deploying Container Stacks

```bash
# Deploy n8n with Portainer stack
cli docker --deploy-compose /path/to/container/templates/n8n-portainer-stack.yml

# Deploy standalone Portainer
cli docker --deploy-compose /path/to/container/templates/portainer-standalone.yml --compose-name portainer
```

## Available Templates

### 1. n8n + Portainer Stack (`n8n-portainer-stack.yml`)

Complete workflow automation platform with:
- PostgreSQL 17 with pgvector extension
- Redis for queue management
- n8n main app and scalable workers
- Portainer for Docker management
- Nginx Proxy Manager for SSL/reverse proxy

### 2. Standalone Portainer (`portainer-standalone.yml`)

Simple Portainer deployment for Docker container management.

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp container/templates/.env.example container/deployments/.env
# Edit container/deployments/.env with your values
```

### Required Configuration:
- Domain names for services
- Strong passwords for all services
- Encryption keys (generate with `openssl rand -hex 32`)

## Directory Structure

```
container/
├── templates/          # Docker Compose templates
├── deployments/        # Active deployments (gitignored)
└── docs/              # Documentation
```

## Post-Deployment Steps

### For n8n Stack:

1. **Configure Nginx Proxy Manager**:
   - Access NPM at `http://your-server:81`
   - Default login: `admin@example.com` / `changeme`
   - Add proxy hosts for n8n and Portainer
   - Enable SSL with Let's Encrypt

2. **Access Services**:
   - n8n: `https://n8n.yourdomain.com`
   - Portainer: `https://admin.yourdomain.com`
   - NPM: `http://your-server:81`

3. **Scale Workers**:
   ```bash
   cd /opt/docker-compose/n8n-stack
   docker-compose up -d --scale n8n-worker=3
   ```

### For Standalone Portainer:

1. Create admin password file:
   ```bash
   echo "your-secure-password" > portainer_admin_password.txt
   ```

2. Access Portainer at `http://your-server:9000`

## Backup Recommendations

1. **Database Backups**:
   ```bash
   # Add to crontab for hourly backups
   0 * * * * docker exec postgres_container pg_dumpall -U n8n > /data/dump/psql/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql
   ```

2. **Volume Backups**:
   - `/data/postgres` - PostgreSQL data
   - `/data/n8n` - n8n workflows and credentials
   - `/data/portainer/data` - Portainer configuration

## Security Notes

1. **Change All Default Passwords**: Update all passwords in `.env` before deployment
2. **Firewall Configuration**: Only expose necessary ports (80, 443, 81)
3. **SSL/TLS**: Always use HTTPS for production deployments
4. **Network Isolation**: Services use internal networks by default

## Troubleshooting

### Check Service Status
```bash
cd /opt/docker-compose/<stack-name>
docker-compose ps
docker-compose logs <service-name>
```

### Common Issues

1. **Port Conflicts**: Ensure ports 80, 443, 81 are not in use
2. **Permission Errors**: Run Docker commands with appropriate privileges
3. **Memory Issues**: Ensure sufficient RAM for all services (minimum 4GB recommended)

## Integration with CLI

The Docker module integrates seamlessly with the CLI infrastructure:

```bash
# Development environment
cli docker --install --dev

# Production environment  
cli docker --install --prod

# With custom inventory
cli docker --install -i /path/to/inventory.yml
```