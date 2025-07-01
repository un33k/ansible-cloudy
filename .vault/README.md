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
   ./cli psql --install -- -e @.vault/my-dev.yml
   ```

## Environment Templates

- `dev.yml.example` - Development environment template
- `prod.yml.example` - Production environment template  
- `ci.yml.example` - CI/CD environment template

## Variable Organization

All vault variables use the `vault_*` prefix for clear organization:

- `vault_root_password` - Initial root password
- `vault_grunt_password` - Grunt user password
- `vault_grunt_user` - Grunt username
- `vault_ssh_port` - Custom SSH port
- Service-specific passwords (postgres, redis, etc.)

## Usage Patterns

### With Claudia CLI
```bash
./cli psql --install -- -e @.vault/my-dev.yml
```

### Direct Ansible
```bash
ansible-playbook -i inventory/dev.yml -e @.vault/my-dev.yml playbooks/recipes/db/psql.yml
```

### Multiple Environments
```bash
# Development
./cli psql --install -- -e @.vault/dev-local.yml

# Production  
./cli psql --install --prod -- -e @.vault/prod-secrets.yml
```

## Security Notes

- ✅ **Git Safety**: All `.vault/*.yml` files are automatically ignored by git
- ✅ **Templates Only**: Only `.example` files and `README.md` are tracked in git
- 🔒 **Real Credentials**: Never commit actual `.vault/*.yml` files with real passwords
- 🔑 **Strong Passwords**: Use strong, unique passwords for each environment
- 💼 **Password Manager**: Consider using a password manager for credential storage
- 🔄 **Regular Rotation**: Regularly rotate credentials, especially for production
- 🏢 **Environment Separation**: Keep production credentials completely separate from dev/test

## Git Ignore Rules

The following files are tracked in git:
- ✅ `.vault/*.example` - Template files
- ✅ `.vault/README.md` - This documentation

The following files are automatically ignored:
- 🚫 `.vault/*.yml` - All actual vault files with real credentials
- 🚫 `.vault/dev.yml`, `.vault/prod.yml`, etc.

This ensures your real credentials are never accidentally committed to git.