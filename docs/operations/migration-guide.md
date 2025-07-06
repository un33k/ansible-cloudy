# Ansible Cloudy Migration Guide

This guide helps you migrate from older versions of Ansible Cloudy or from other infrastructure automation tools.

## Version Migration

### From Ansible Cloudy 1.x to 2.x

#### Breaking Changes

1. **Variable Naming Convention**
   - Old: `default_*` prefix for defaults
   - New: `*_default` suffix for defaults
   
   ```yaml
   # Old
   default_locale: "en_US.UTF-8"
   default_timezone: "UTC"
   
   # New
   locale_default: "en_US.UTF-8"
   timezone_default: "UTC"
   ```

2. **Vault Variables**
   - Removed: `vault_admin_password` (no longer exists)
   - Removed: `vault_ansible_user` (use `vault_root_user`)
   - Changed: `vault_admin_user` → `vault_grunt_user`
   - Changed: `vault_grunt_groups` → `vault_grunt_groups_string`

3. **Default Filter Usage**
   - All inline `default()` filters have been removed
   - Defaults now come from centralized files in `cloudy/defaults/`
   
   ```yaml
   # Old
   port: "{{ redis_port | default(6379) }}"
   
   # New (with centralized default)
   port: "{{ vault_redis_port | default(vault_redis_port_default) }}"
   ```

4. **Service Names**
   - PostgreSQL service remains `psql` (not `postgresql`)
   - All services use consistent naming in CLI

#### Migration Steps

1. **Update Vault Files**
   ```bash
   # Backup existing vault files
   cp -r .vault .vault.backup
   
   # Update variable names
   sed -i 's/vault_admin_user/vault_grunt_user/g' .vault/*.yml
   sed -i 's/vault_admin_password/vault_grunt_password/g' .vault/*.yml
   sed -i 's/vault_ansible_user/vault_root_user/g' .vault/*.yml
   ```

2. **Update Custom Playbooks**
   - Replace `default()` filters with references to `*_default` variables
   - Update variable names to match new convention

3. **Test Migration**
   ```bash
   # Run validation
   cli dev validate
   
   # Test with check mode
   cli security --install --check
   cli base --install --check
   ```

### From Cloudy-Old (Python) to Ansible Cloudy

#### Key Differences

1. **Architecture**
   - Old: Python-based with function calls
   - New: Ansible-based with declarative playbooks

2. **Command Structure**
   - Old: `cloudy sys.user.add --username john`
   - New: `cli psql --adduser john`

3. **Configuration**
   - Old: Python config files
   - New: YAML vault files

#### Migration Path

1. **Export Existing Configuration**
   ```bash
   # From cloudy-old, export current settings
   cloudy config.export > old-config.json
   ```

2. **Convert to Vault Format**
   ```python
   # convert_config.py
   import json
   import yaml
   
   with open('old-config.json') as f:
       old_config = json.load(f)
   
   vault_config = {
       'vault_root_user': old_config.get('root_user', 'root'),
       'vault_root_password': old_config.get('root_password'),
       'vault_grunt_user': old_config.get('service_user', ''),
       'vault_postgres_password': old_config.get('db_password'),
       # Add more mappings
   }
   
   with open('.vault/migrated.yml', 'w') as f:
       yaml.dump(vault_config, f)
   ```

3. **Migrate Services**
   ```bash
   # Install services in order
   cli security --install
   cli base --install
   cli psql --install
   cli redis --install
   cli nginx --install
   ```

## Tool Migration

### From Puppet

1. **Convert Manifests to Playbooks**
   - Puppet classes → Ansible roles
   - Puppet resources → Ansible tasks
   - Hiera data → Vault variables

2. **Example Conversion**
   ```puppet
   # Puppet manifest
   class postgresql {
     package { 'postgresql':
       ensure => installed,
     }
     service { 'postgresql':
       ensure => running,
       enable => true,
     }
   }
   ```
   
   ```yaml
   # Ansible playbook
   - name: Install PostgreSQL
     apt:
       name: postgresql
       state: present
   
   - name: Start PostgreSQL
     systemd:
       name: postgresql
       state: started
       enabled: true
   ```

### From Chef

1. **Convert Cookbooks to Roles**
   - Chef recipes → Ansible tasks
   - Chef attributes → Ansible variables
   - Data bags → Vault files

2. **Attribute Mapping**
   ```ruby
   # Chef attributes
   default['postgresql']['port'] = 5432
   default['postgresql']['max_connections'] = 100
   ```
   
   ```yaml
   # Ansible defaults
   vault_postgresql_port_default: 5432
   pg_max_connections_default: 100
   ```

### From Terraform

While Terraform focuses on infrastructure provisioning, Ansible Cloudy handles configuration management. They can work together:

1. **Use Terraform for Infrastructure**
   ```hcl
   # Create servers with Terraform
   resource "aws_instance" "web" {
     ami           = "ami-0c55b159cbfafe1f0"
     instance_type = "t2.micro"
     
     tags = {
       Name = "web-server"
       Role = "web"
     }
   }
   ```

2. **Use Ansible Cloudy for Configuration**
   ```yaml
   # Configure servers with Ansible Cloudy
   cli security --install --host {{ terraform_output.web.public_ip }}
   cli base --install --host {{ terraform_output.web.public_ip }}
   cli nginx --install --host {{ terraform_output.web.public_ip }}
   ```

## Database Migration

### PostgreSQL Data Migration

1. **Backup Source Database**
   ```bash
   # On old server
   pg_dumpall -h old-server -U postgres > full_backup.sql
   ```

2. **Restore to New Server**
   ```bash
   # Install PostgreSQL with Ansible Cloudy
   cli psql --install
   
   # Restore data
   psql -h localhost -U postgres < full_backup.sql
   ```

3. **Migrate Specific Databases**
   ```bash
   # Backup specific database
   pg_dump -h old-server -U postgres myapp > myapp.sql
   
   # Create database and restore
   cli psql --adddb myapp --owner myapp_user
   psql -h localhost -U postgres myapp < myapp.sql
   ```

### Redis Data Migration

1. **Create Backup**
   ```bash
   # On old server
   redis-cli --rdb /tmp/redis-backup.rdb
   ```

2. **Restore Data**
   ```bash
   # Install Redis
   cli redis --install
   
   # Stop Redis and restore
   systemctl stop redis
   cp /tmp/redis-backup.rdb /var/lib/redis/dump.rdb
   chown redis:redis /var/lib/redis/dump.rdb
   systemctl start redis
   ```

## Configuration Migration

### SSH Keys

1. **Preserve Existing Keys**
   ```bash
   # Backup SSH keys before migration
   tar -czf ssh-keys-backup.tar.gz ~/.ssh/
   ```

2. **Update Vault Configuration**
   ```yaml
   vault_root_ssh_private_key_file: "~/.ssh/id_rsa"
   vault_grunt_ssh_private_key_file: "~/.ssh/id_rsa"
   ```

### SSL Certificates

1. **Backup Certificates**
   ```bash
   # Backup existing certificates
   tar -czf ssl-backup.tar.gz /etc/letsencrypt/
   ```

2. **Restore After Migration**
   ```bash
   # Install Nginx
   cli nginx --install
   
   # Restore certificates
   tar -xzf ssl-backup.tar.gz -C /
   
   # Update Nginx configuration
   cli nginx --setup-ssl example.com
   ```

## Common Migration Issues

### Issue: Variable Not Found

**Problem**: `vault_admin_password is undefined`

**Solution**: This variable no longer exists. Remove references or update to use `vault_grunt_password`.

### Issue: Port Conflicts

**Problem**: Service fails to start due to port conflict

**Solution**: 
```bash
# Check what's using the port
ss -tulpn | grep :5432

# Use custom port
cli psql --install --port 5433
```

### Issue: Authentication Failures

**Problem**: Cannot authenticate after migration

**Solution**:
```bash
# Reset passwords
cli psql --reset-password postgres
cli redis --reset-password
```

### Issue: Missing Dependencies

**Problem**: Service installation fails due to missing dependencies

**Solution**:
```bash
# Ensure proper installation order
cli security --install  # First
cli base --install      # Second
cli psql --install      # Then services
```

## Validation Checklist

After migration, verify:

- [ ] SSH access works with configured port
- [ ] Grunt user can sudo without password
- [ ] Firewall rules are correctly applied
- [ ] All services are running
- [ ] Databases are accessible
- [ ] Backups are working
- [ ] Monitoring is active
- [ ] SSL certificates are valid
- [ ] Application can connect to services

## Rollback Plan

If migration fails:

1. **Restore from Backup**
   ```bash
   # Restore system backup
   # (Depends on your backup solution)
   ```

2. **Revert Configuration**
   ```bash
   # Use backup vault files
   rm -rf .vault
   mv .vault.backup .vault
   ```

3. **Clean Installation**
   ```bash
   # Start fresh
   cli security --install --force
   cli base --install --force
   ```

## Getting Help

If you encounter issues during migration:

1. Check logs: `cli [service] --logs`
2. Run validation: `cli dev validate`
3. Enable debug mode: `cli [service] --install --debug`
4. Open an issue on GitHub with migration details