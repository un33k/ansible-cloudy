# Let's Encrypt Docker Implementation Plan

## Overview

This document outlines the implementation strategy for automated SSL/TLS certificate management using Let's Encrypt in our Docker-based infrastructure. The solution addresses the chicken-and-egg problem of domain validation while supporting multiple domains across various containerized services.

## Current State

- **Infrastructure**: Docker-based services with nginx reverse proxy
- **Domains**: 
  - admin.neekware.com (Portainer)
  - auto.neekware.com (n8n) 
  - app.neekware.com (Next.js)
- **Current SSL**: Self-signed certificates
- **Certificate Location**: `/data/docker/nginx/certs/`

## Solution Comparison

### 1. Certbot Standalone Container
**Pros:**
- Lightweight, focused solution
- Direct integration with existing nginx
- Full control over certificate management
- Minimal overhead

**Cons:**
- Requires custom automation scripts
- Manual domain management
- More configuration needed

### 2. SWAG (Secure Web Application Gateway)
**Pros:**
- All-in-one solution (nginx + certbot + fail2ban)
- Pre-configured for many applications
- Built-in DNS plugin support
- Automatic renewal

**Cons:**
- Replaces existing nginx setup
- Heavier resource usage
- Less flexibility for custom configs

### 3. Traefik
**Pros:**
- Native Docker integration
- Automatic service discovery
- Built-in Let's Encrypt support
- Modern, cloud-native design

**Cons:**
- Complete paradigm shift from nginx
- Steeper learning curve
- Would require significant refactoring

### 4. Nginx Proxy Manager
**Pros:**
- Web UI for certificate management
- Built on familiar nginx
- Easy domain management
- Built-in Let's Encrypt support

**Cons:**
- Another service to maintain
- Potential conflicts with existing nginx
- Less infrastructure-as-code friendly

## Recommended Approach: Hybrid Certbot Solution

Based on our existing infrastructure and requirements, I recommend a **Certbot Container with DNS-01 Challenge** approach that:

1. Maintains our existing nginx configuration
2. Provides automated certificate management
3. Supports pre-deployment certificate generation
4. Handles multiple domains efficiently

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Host                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │  Certbot        │         │  Nginx          │           │
│  │  Container      │◄────────┤  Container      │           │
│  │                 │ shares  │                 │           │
│  │ - DNS-01       │ certs   │ - Reverse Proxy │           │
│  │ - Auto Renew   │         │ - SSL Termination│          │
│  └────────┬────────┘         └────────┬────────┘           │
│           │                            │                     │
│           └──────────┬─────────────────┘                    │
│                      │                                       │
│         ┌────────────▼─────────────┐                        │
│         │ /data/docker/nginx/certs │                        │
│         │  (Shared Volume)         │                        │
│         └──────────────────────────┘                        │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Portainer   │  │    n8n      │  │   Next.js   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Infrastructure Preparation (Current State)
- ✅ Docker and nginx containers deployed
- ✅ Services accessible via self-signed certificates
- ✅ Domain configuration in place

### Phase 2: Certbot Container Implementation
1. Create certbot container recipe
2. Configure DNS plugin support
3. Set up certificate volume sharing
4. Implement domain configuration management

### Phase 3: DNS Validation Setup
1. Configure DNS API credentials (Cloudflare recommended)
2. Test DNS-01 challenge in staging mode
3. Validate domain ownership
4. Document DNS requirements

### Phase 4: Production Deployment
1. Generate production certificates
2. Update nginx configurations
3. Implement automatic renewal
4. Set up monitoring

## Technical Implementation Details

### 1. Certbot Container Recipe
**File**: `cloudy/playbooks/recipes/container/certbot.yml`

```yaml
# Key features:
- DNS-01 challenge support (no live server required)
- Multiple domain management from vault
- Automatic renewal via cron
- Staging/production mode toggle
- Certificate status reporting
```

### 2. Docker Compose Template
**File**: `cloudy/templates/container/certbot/docker-compose.yml.j2`

```yaml
services:
  certbot:
    image: certbot/dns-cloudflare:latest
    container_name: certbot
    volumes:
      - /data/docker/nginx/certs:/etc/letsencrypt
      - /data/docker/certbot/logs:/var/log/letsencrypt
    environment:
      - CERTBOT_EMAIL={{ vault_letsencrypt_email }}
    command: renew
```

### 3. Enhanced Nginx Configuration
**Updates**: Modify nginx site templates to handle dual certificate mode

```nginx
# Intelligent SSL configuration
ssl_certificate /etc/nginx/certs/{{ domain }}/fullchain.pem;
ssl_certificate_key /etc/nginx/certs/{{ domain }}/privkey.pem;

# Fallback to self-signed if Let's Encrypt cert doesn't exist
include /etc/nginx/certs/ssl-fallback.conf;
```

### 4. CLI Commands

```bash
# Certificate management commands
cli docker --compose certbot              # Deploy certbot container
cli docker --certbot-request <domain>     # Request new certificate
cli docker --certbot-renew               # Force renewal check
cli docker --certbot-status              # Show all certificates
cli docker --certbot-revoke <domain>     # Revoke certificate
```

### 5. Vault Configuration Structure

```yaml
# Certificate configuration
vault_letsencrypt_email: "admin@neekware.com"
vault_letsencrypt_staging: false  # Use staging for testing
vault_letsencrypt_dns_provider: "cloudflare"
vault_letsencrypt_dns_credentials: "{{ vault_cloudflare_api_token }}"

# Domain configurations
vault_letsencrypt_domains:
  - name: "admin.neekware.com"
    service: "portainer"
    sans: []  # Subject Alternative Names
  - name: "auto.neekware.com"
    service: "n8n"
    sans: []
  - name: "app.neekware.com"
    service: "nextjs"
    sans: ["www.app.neekware.com"]
```

## Solving the Chicken-and-Egg Problem

### Strategy 1: DNS-01 Challenge (Recommended)
- **Advantage**: No live server required
- **Process**:
  1. Add DNS TXT records via API
  2. Let's Encrypt validates DNS ownership
  3. Certificate issued without HTTP access
  4. Deploy certificate before service goes live

### Strategy 2: Hybrid Deployment
1. **Initial Setup**: Deploy with self-signed certificates
2. **DNS Propagation**: Add A records, wait for propagation
3. **Certificate Request**: Use HTTP-01 with existing nginx
4. **Certificate Switch**: Reload nginx with new certificates

### Strategy 3: Pre-deployment Certificates
1. **Local Validation**: Use certbot with manual DNS mode
2. **Generate Certificates**: Before server deployment
3. **Deploy with Certs**: Include certificates in initial setup

## Certificate Lifecycle Management

### Automatic Renewal
- Certbot container runs renewal check daily
- Certificates renewed 30 days before expiration
- Nginx automatically reloaded after renewal
- Email notifications for renewal status

### Monitoring and Alerts
```yaml
# Certificate expiry monitoring
- Check certificate validity daily
- Alert if expiry < 14 days
- Log all renewal attempts
- Health check endpoint for monitoring systems
```

## Migration Path

### Step 1: Deploy Certbot Container
```bash
cli docker --compose certbot
```

### Step 2: Configure DNS Provider
```bash
# Add DNS API credentials to vault
# Test with staging certificates first
cli docker --certbot-request admin.neekware.com --staging
```

### Step 3: Validate Staging Certificates
```bash
# Check certificate status
cli docker --certbot-status

# Test nginx configuration
docker exec nginx nginx -t
```

### Step 4: Production Certificates
```bash
# Request production certificates
cli docker --certbot-request admin.neekware.com
cli docker --certbot-request auto.neekware.com
cli docker --certbot-request app.neekware.com
```

### Step 5: Update Nginx Configuration
```bash
# Nginx will automatically use new certificates
docker exec nginx nginx -s reload
```

## Troubleshooting Guide

### Common Issues

1. **DNS Propagation Delays**
   - Solution: Wait 5-10 minutes after DNS changes
   - Use DNS propagation checker tools

2. **Rate Limiting**
   - Solution: Use staging environment for testing
   - Production: 50 certificates per registered domain per week

3. **Certificate Not Loading**
   - Check file permissions
   - Verify nginx configuration syntax
   - Ensure volume mounts are correct

4. **Renewal Failures**
   - Check DNS API credentials
   - Verify domain ownership
   - Review certbot logs

### Debug Commands
```bash
# Check certificate details
docker exec certbot certbot certificates

# View renewal configuration
docker exec certbot cat /etc/letsencrypt/renewal/domain.com.conf

# Test renewal
docker exec certbot certbot renew --dry-run

# Check nginx SSL configuration
docker exec nginx nginx -T | grep ssl
```

## Security Considerations

1. **API Credentials**: Store DNS API tokens in vault
2. **Certificate Permissions**: Restrict to nginx user only
3. **Backup Strategy**: Regular backup of `/etc/letsencrypt`
4. **Revocation Plan**: Document certificate revocation process

## Future Enhancements

1. **Wildcard Certificates**: `*.neekware.com` for simplified management
2. **Certificate Transparency Monitoring**: Track certificate issuance
3. **Multi-provider Support**: Fallback DNS providers
4. **Web UI Integration**: Certificate management in Portainer

## Conclusion

This implementation provides a robust, automated SSL certificate management system that:
- Integrates seamlessly with existing Docker infrastructure
- Solves the chicken-and-egg DNS validation problem
- Supports unlimited domains with automatic renewal
- Maintains high security standards
- Provides clear operational procedures

The phased approach ensures minimal disruption while providing a path to full automation.