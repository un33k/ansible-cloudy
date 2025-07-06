# N8N Workflow Automation

N8N is a powerful workflow automation tool that provides a visual interface for creating complex automation workflows.

## Overview

The N8N service in Ansible Cloudy deploys a production-ready N8N instance with:
- PostgreSQL database backend
- Redis for queue management
- SSL/TLS encryption
- Automated backups
- Resource monitoring

## Prerequisites

Before installing N8N, ensure you have:
- Security setup completed (`cli security --install`)
- Base configuration completed (`cli base --install`)
- PostgreSQL installed (`cli psql --install`)
- Redis installed (`cli redis --install`)
- Nginx installed (`cli nginx --install`)

## Installation

### Basic Installation

```bash
# Install N8N with default configuration
cli n8n --install
```

### Custom Installation

```bash
# Install with custom domain and port
cli n8n --install --domain workflow.example.com --port 5678

# Install with custom webhook URL
cli n8n --install --webhook-url https://n8n.example.com/webhook
```

## Configuration

### Required Variables

Add these to your vault file (`.vault/production.yml`):

```yaml
# N8N Configuration
vault_n8n_encryption_key: "your-32-char-encryption-key"  # Required
vault_n8n_webhook_url: "https://n8n.example.com"        # Required for webhooks
vault_n8n_domain: "n8n.example.com"                     # Required for SSL

# Database Configuration (if not using default)
vault_n8n_db_name: "n8n"                                # Default: n8n
vault_n8n_db_user: "n8n"                                # Default: n8n
vault_n8n_db_password: "secure_password"                # Required
```

### Optional Variables

```yaml
# Performance Tuning
vault_n8n_executions_process: "main"                    # or "own" for separate process
vault_n8n_executions_timeout: 3600                      # Timeout in seconds
vault_n8n_executions_data_save_on_error: "all"         # Save data on error
vault_n8n_executions_data_save_on_success: "all"       # Save data on success
vault_n8n_executions_data_save_manual_executions: true # Save manual executions

# Security
vault_n8n_basic_auth_active: true                      # Enable basic auth
vault_n8n_basic_auth_user: "admin"                     # Basic auth username
vault_n8n_basic_auth_password: "secure_password"       # Basic auth password
```

## Usage

### Access N8N

After installation, access N8N at:
- HTTP: `http://your-server-ip:5678`
- HTTPS: `https://your-domain.com` (if SSL configured)

### First-Time Setup

1. Navigate to the N8N URL
2. Create your first user account
3. Start creating workflows!

### CLI Operations

```bash
# Check N8N status
cli n8n --status

# Restart N8N
cli n8n --restart

# View logs
cli n8n --logs

# Backup N8N data
cli n8n --backup

# Update N8N
cli n8n --update
```

## Architecture

N8N is deployed using Docker with the following architecture:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Nginx    │────▶│     N8N     │────▶│ PostgreSQL  │
│   (Proxy)   │     │  (Docker)   │     │ (Database)  │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │    Redis    │
                    │   (Queue)   │
                    └─────────────┘
```

## Backup and Recovery

### Automated Backups

N8N data is automatically backed up daily at 3 AM to `/backup/n8n/`.

### Manual Backup

```bash
# Create manual backup
cli n8n --backup

# Restore from backup
cli n8n --restore /backup/n8n/backup-2024-01-01.tar.gz
```

## Monitoring

### Health Checks

N8N provides health check endpoints:
- `/healthz` - Basic health check
- `/metrics` - Prometheus metrics (if enabled)

### Resource Usage

Monitor N8N resource usage:

```bash
# Check Docker container stats
docker stats n8n

# View system resources
cli n8n --resources
```

## Troubleshooting

### Common Issues

1. **N8N not starting**
   ```bash
   # Check logs
   docker logs n8n
   
   # Check if ports are in use
   ss -tulpn | grep 5678
   ```

2. **Database connection issues**
   ```bash
   # Test PostgreSQL connection
   cli psql --test-connection
   
   # Check N8N environment
   docker exec n8n env | grep DB
   ```

3. **Webhook issues**
   - Ensure `vault_n8n_webhook_url` is correctly set
   - Check Nginx proxy configuration
   - Verify SSL certificates if using HTTPS

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Run with debug logging
cli n8n --install -- -e "n8n_log_level=debug"
```

## Security Considerations

1. **Encryption Key**: Always use a strong 32-character encryption key
2. **Basic Auth**: Enable basic authentication for additional security
3. **SSL/TLS**: Always use SSL in production environments
4. **Firewall**: Ensure only necessary ports are open
5. **Updates**: Regularly update N8N to the latest version

## Performance Tuning

### For High-Volume Workflows

```yaml
# Optimize for performance
vault_n8n_executions_process: "own"              # Separate execution process
vault_n8n_executions_timeout: 7200               # 2-hour timeout
vault_n8n_executions_data_save_on_error: "none" # Don't save error data
vault_n8n_executions_data_save_on_success: "none" # Don't save success data
```

### Database Optimization

```bash
# Optimize PostgreSQL for N8N
cli psql --optimize-for n8n
```

## Integration Examples

### Webhook Integration

```javascript
// Example webhook trigger
{
  "webhookUrl": "https://n8n.example.com/webhook/abc123",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "event": "user.created",
    "data": {
      "userId": "123",
      "email": "user@example.com"
    }
  }
}
```

### API Integration

N8N provides a REST API for programmatic access:

```bash
# Get all workflows
curl -X GET https://n8n.example.com/api/v1/workflows \
  -H "Authorization: Bearer YOUR_API_KEY"

# Execute workflow
curl -X POST https://n8n.example.com/api/v1/workflows/1/execute \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"data": {"key": "value"}}'
```

## Best Practices

1. **Workflow Organization**: Use folders to organize workflows by function
2. **Error Handling**: Always implement error handling in workflows
3. **Testing**: Test workflows in a development environment first
4. **Version Control**: Export and version control critical workflows
5. **Monitoring**: Set up alerts for failed executions
6. **Documentation**: Document complex workflows for team members

## Support

For issues or questions:
1. Check the [N8N documentation](https://docs.n8n.io/)
2. Review logs with `cli n8n --logs`
3. Check the Ansible Cloudy troubleshooting guide
4. Open an issue on the Ansible Cloudy repository