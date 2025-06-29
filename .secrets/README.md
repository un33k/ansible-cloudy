# Vault Configuration Directory

This directory contains Ansible Vault files with sensitive credentials and configuration.

## Vault Access Control Strategy

**Different teams get different vault passwords for security isolation:**

### Environment-Specific Access

1. **Development Team** → Only has `dev.yml` vault password
   - Can decrypt/edit development secrets
   - Cannot access CI/staging or production vaults
   - Used for local development and testing

2. **CI/CD System** → Only has `ci.yml` vault password  
   - Automated deployments to CI/staging environment
   - Stored in CI/CD secrets management (GitHub Actions, Jenkins, etc.)
   - Cannot access production secrets

3. **DevOps/SRE Team** → Has `prod.yml` vault password
   - Production deployments and emergency access
   - Highly restricted, audit-logged access
   - Separate from development credentials

### Access Pattern Examples

**For Developers:**
```bash
# Set dev vault password
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass-dev

# They can work with dev environment
./claudia django --install  # Uses dev.yml vault

# But cannot access production (fails - no prod vault password)
./claudia django --install --prod  # ❌ Access denied
```

**For CI/CD System:**
```bash
# CI server has ci vault password in secure environment
export ANSIBLE_VAULT_PASSWORD_FILE=/secure/ci-vault-pass

# CI can deploy to staging
./claudia django --install --ci  # Uses ci.yml vault

# But cannot deploy to production
./claudia django --install --prod  # ❌ Access denied
```

**For Production Deployments:**
```bash
# Only DevOps team has this password
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass-prod  

# Production deployments
./claudia django --install --prod  # Uses prod.yml vault
```

### Security Benefits

- **Separation of Concerns**: Each team/system only has access to appropriate environments
- **Least Privilege Access**: No one has more access than needed
- **Audit Trail**: Production vault access is limited and tracked
- **Breach Containment**: Compromise of dev credentials doesn't affect production

## File Structure

```
.secrets/
├── README.md                    # This file
├── vault.yml.template           # Template for creating new vault files
├── dev.yml                     # Development environment vault (encrypted)
├── ci.yml                      # CI/CD environment vault (encrypted)
└── prod.yml                    # Production environment vault (encrypted)
```

## How Vault Loading Works

Ansible automatically loads vault variables using the standard `group_vars` structure:

- **Development**: `cloudy/inventory/group_vars/all/vault.yml` → symlinks to `.secrets/dev.yml`
- **Staging**: Create `cloudy/inventory/group_vars/all/vault_staging.yml` → symlinks to `.secrets/staging.yml`
- **Production**: Create `cloudy/inventory/group_vars/all/vault_prod.yml` → symlinks to `.secrets/production.yml`

## Environment Setup

### Development Environment
```bash
# 1. Create your dev vault from template
cp .secrets/vault.yml.template .secrets/dev.yml

# 2. Edit with your development credentials
vim .secrets/dev.yml

# 3. Encrypt the vault file
ansible-vault encrypt .secrets/dev.yml

# 4. Vault is automatically loaded via symlink
ansible-playbook -i cloudy/inventory/dev.yml [your-playbook] --ask-vault-pass
```

### CI/CD Environment
```bash
# 1. Create your CI vault from template
cp .secrets/vault.yml.template .secrets/ci.yml

# 2. Edit with your CI credentials
vim .secrets/ci.yml

# 3. Encrypt the vault file
ansible-vault encrypt .secrets/ci.yml

# 4. Create symlink for CI inventory
ln -s ../../../../.secrets/ci.yml cloudy/inventory/group_vars/all/vault_ci.yml

# 5. Use CI inventory
ansible-playbook -i cloudy/inventory/ci.yml [your-playbook] --ask-vault-pass
```

### Production Environment
```bash
# 1. Create your production vault from template
cp .secrets/vault.yml.template .secrets/prod.yml

# 2. Edit with your production credentials (use strong passwords!)
vim .secrets/prod.yml

# 3. Encrypt the vault file
ansible-vault encrypt .secrets/prod.yml

# 4. Create symlink for production inventory
ln -s ../../../../.secrets/prod.yml cloudy/inventory/group_vars/all/vault_prod.yml

# 5. Use production inventory
ansible-playbook -i cloudy/inventory/prod.yml [your-playbook] --ask-vault-pass
```

## Vault Variables

All vault variables use the `vault_` prefix and have fallback defaults in inventory files:

- `vault_admin_user` → fallback: `admin`
- `vault_ssh_port` → fallback: `22022`
- `vault_git_user_full_name` → fallback: `John Doe`
- `vault_timezone` → fallback: `America/New_York`

## Security Notes

- ✅ **Encrypted at rest**: All vault files should be encrypted with `ansible-vault encrypt`
- ✅ **Safe to commit**: Encrypted vault files are safe to commit to git
- ✅ **Environment separation**: Separate vault files for dev/staging/production
- ⚠️ **Password protection**: Always use `--ask-vault-pass` or set `ANSIBLE_VAULT_PASSWORD_FILE`

## Vault Password Setup (Required for Seamless Workflow)

Set up the `ANSIBLE_VAULT_PASSWORD_FILE` environment variable to avoid manual password prompts:

```bash
# 1. Create vault password file (secure location)
echo "your_vault_password" > ~/.ansible-vault-pass
chmod 600 ~/.ansible-vault-pass

# 2. Set environment variable (add to ~/.bashrc or ~/.zshrc)
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass

# 3. Reload your shell or run:
source ~/.bashrc  # or ~/.zshrc
```

**Security Notes**: 
- ✅ Use a strong, unique password for your vault
- ✅ File should have restricted permissions (600)
- ✅ Store in your home directory, NOT in the project
- ⚠️ Add the export to your shell profile for persistence

## Simple Security Workflow (Recommended)

The git hooks provide clear security guidance:

```bash
# 1. Edit vault files directly (unencrypted for fast development)
vim .secrets/dev.yml

# 2. Commit changes normally (warns but allows unencrypted files)
git add .secrets/dev.yml
git commit -m "Update vault configuration"

# 3. Encrypt before pushing (using Claudia CLI)
./claudia vault encrypt --all

# 4. Commit encrypted files and push safely
git add .secrets/
git commit -m "Encrypt vault files"
git push origin main
```

**Security Features:**
- ✅ **Pre-commit**: Warns about unencrypted files (allows commits)
- ✅ **Pre-push**: Blocks push if vault files are unencrypted
- ✅ **Clear guidance**: Shows exact Claudia commands to fix issues
- 🎯 **Simple**: No complex automation to break

## Claudia Vault Commands

```bash
# Main vault operations
./claudia vault create                # Create new vault file
./claudia vault edit                  # Edit vault file (decrypts, opens editor, re-encrypts)
./claudia vault view                  # View encrypted vault contents
./claudia vault encrypt --all         # Encrypt all vault files in .secrets/
./claudia vault decrypt --all         # Decrypt all vault files for editing
./claudia vault rekey                 # Change vault password

# File-specific operations
./claudia vault edit --file dev       # Edit specific vault file
./claudia vault encrypt --file dev    # Encrypt specific vault file
./claudia vault decrypt --file dev    # Decrypt specific vault file
```

## Manual Ansible Vault Commands (Alternative)

```bash
# Direct ansible-vault usage
ansible-vault edit .secrets/dev.yml    # Edit encrypted vault
ansible-vault view .secrets/dev.yml    # View encrypted vault
ansible-vault encrypt .secrets/dev.yml # Encrypt file
ansible-vault decrypt .secrets/dev.yml # Decrypt file
```

## Git Hook Installation

```bash
# Install the smart workflow hooks
./.githooks/install-hooks.sh
```