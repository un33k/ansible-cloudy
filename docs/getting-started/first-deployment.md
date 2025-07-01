# First Deployment Guide

A step-by-step guide to deploying your first server with Ansible Cloudy.

## Overview

This guide walks you through deploying a complete web application stack:
1. Secure the server
2. Install PostgreSQL database
3. Deploy Redis cache
4. Set up Nginx web server
5. Configure your application

## Prerequisites

- Ansible Cloudy installed and activated
- A fresh Ubuntu/Debian server
- Root SSH access or password
- Basic familiarity with command line

## Step 1: Prepare Your Configuration

### Create Vault File

```bash
# Copy the example
cp .vault/dev.yml.example .vault/production.yml

# Edit with your values
vim .vault/production.yml
```

Essential vault variables:
```yaml
# Authentication
vault_root_password: "your_root_password"
vault_admin_password: "secure_admin_password"

# Optional: Create a service user (leave empty to skip)
vault_grunt_user: ""  # or "deploy" to create user

# Service passwords
vault_postgres_password: "secure_db_password"
vault_redis_password: "secure_cache_password"
```

### Update Inventory

Edit `cloudy/inventory/prod.yml`:

```yaml
all:
  hosts:
    web-server-01:
      ansible_host: 192.168.1.100
      hostname: app.example.com
```

## Step 2: Initial Security Setup

This is the most critical step - securing your server:

```bash
# Run security setup (uses root password from vault)
cli security --install --prod
```

What this does:
- Creates SSH keys for root access
- Configures firewall (UFW)
- Changes SSH port to 22022
- Optionally creates grunt user (if defined in vault)
- Hardens SSH configuration
- Disables root password authentication

After this step, all connections use SSH keys on port 22022.

## Step 3: Base System Configuration

Configure the base system:

```bash
# Install base configuration
cli base --install --prod
```

This configures:
- System hostname
- Timezone and locale
- Git configuration
- Essential packages
- Swap file (if needed)
- System optimization

## Step 4: Install PostgreSQL

Deploy PostgreSQL database:

```bash
# Install PostgreSQL with default settings
cli psql --install --prod

# Or with custom configuration
cli psql --install --prod --port 5433 --version 15
```

Verify installation:
```bash
# Check PostgreSQL status
ssh root@192.168.1.100 -p 22022 "systemctl status postgresql"
```

## Step 5: Install Redis

Deploy Redis cache:

```bash
# Install Redis with default settings
cli redis --install --prod

# Or with custom configuration
cli redis --install --prod --port 6380 --memory 1024 --password
```

## Step 6: Install Web Server

Deploy Nginx:

```bash
# Install Nginx
cli nginx --install --prod --domain app.example.com --ssl
```

This sets up:
- Nginx web server
- SSL certificates (Let's Encrypt)
- DDoS protection
- Optimized configuration

## Step 7: Deploy Your Application

### For Django Applications

```bash
# Deploy Django with all components
cli django --install --prod
```

### For Node.js Applications

```bash
# Deploy Node.js with PM2
cli nodejs --install --prod
```

### For Custom Applications

Use the modular tasks to build custom deployments.

## Verification Steps

### 1. Check Service Status

```bash
# Connect to your server
ssh root@192.168.1.100 -p 22022

# Check services
systemctl status postgresql
systemctl status redis
systemctl status nginx
```

### 2. Test Database Connection

```bash
# On the server
sudo -u postgres psql -c "SELECT version();"
```

### 3. Test Redis

```bash
# Test Redis connection
redis-cli ping
```

### 4. Check Nginx

```bash
# Test Nginx configuration
nginx -t

# Check if site is accessible
curl -I http://app.example.com
```

## Common Issues and Solutions

### SSH Connection Failed

If you can't connect after security setup:

1. **Wrong port**: Remember to use `-p 22022`
2. **Firewall blocking**: Check cloud provider firewall rules
3. **Key issues**: Ensure your SSH key exists at `~/.ssh/id_rsa`

### Service Won't Start

Check logs:
```bash
# PostgreSQL logs
journalctl -u postgresql -n 50

# Redis logs
journalctl -u redis -n 50

# Nginx logs
journalctl -u nginx -n 50
```

### Permission Issues

If using grunt user and getting permission errors:
```bash
# Ensure user is in correct groups
usermod -a -G postgres,redis,www-data grunt
```

## Next Steps

1. **Configure Backups**: Set up automated PostgreSQL backups
2. **Monitor Services**: Install monitoring tools
3. **Security Hardening**: Review and enhance security settings
4. **Load Testing**: Test your application under load
5. **Documentation**: Document your specific configuration

## Production Checklist

Before going live:

- [ ] Change all default passwords
- [ ] Configure firewall rules for your application
- [ ] Set up SSL certificates
- [ ] Configure backups
- [ ] Set up monitoring
- [ ] Test disaster recovery
- [ ] Document the deployment
- [ ] Create runbooks for common tasks

## Getting Help

- Run `cli [service] --help` for command help
- Check logs with `journalctl -u [service]`
- Review configuration in `/etc/[service]/`
- See [Troubleshooting Guide](../reference/troubleshooting.md)