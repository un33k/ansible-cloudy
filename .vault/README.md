# Vault Configuration Directory

This directory contains configuration templates for different environments.

## Quick Start

1. **Copy the template for your environment:**
   ```bash
   cp .vault/dev.yml.example .vault/my-dev.yml
   ```

2. **Edit with your real credentials:**
   ```bash
   vim .vault/my-dev.yml
   ```

3. **Use in playbooks:**
   ```bash
   ./claudia psql --install -- -e @.vault/my-dev.yml
   ```

## Environment Templates

- `dev.yml.example` - Development environment template
- `prod.yml.example` - Production environment template  
- `ci.yml.example` - CI/CD environment template

## Variable Organization

All vault variables use the `vault_*` prefix for clear organization:

- `vault_root_password` - Initial root password
- `vault_admin_password` - Admin user password
- `vault_admin_user` - Admin username
- `vault_ssh_port` - Custom SSH port
- Service-specific passwords (postgres, mysql, redis, etc.)

## Usage Patterns

### With Claudia CLI
```bash
./claudia psql --install -- -e @.vault/my-dev.yml
```

### Direct Ansible
```bash
ansible-playbook -i inventory/dev.yml -e @.vault/my-dev.yml playbooks/recipes/db/psql.yml
```

### Multiple Environments
```bash
# Development
./claudia psql --install -- -e @.vault/dev-local.yml

# Production  
./claudia psql --install --prod -- -e @.vault/prod-secrets.yml
```

## Security Notes

- Add your vault files to `.gitignore`
- Use strong, unique passwords for each environment
- Consider using a password manager
- Regularly rotate credentials
- Keep production credentials separate from dev/test