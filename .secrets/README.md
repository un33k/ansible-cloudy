# Vault Configuration Directory

This directory contains **example vault files** and templates for open source usage. No real secrets are stored here.

## Vault Access Control Strategy

**Hierarchical access model based on team roles and responsibilities:**

### Role-Based Access Levels

1. **Junior Developers** → `dev.yml` vault password only
   - Local development environment access
   - Can test and iterate on features safely
   - Cannot deploy to shared environments

2. **Senior Developers** → `dev.yml` + `ci.yml` vault passwords
   - Can debug CI/staging deployment issues
   - Can test integration scenarios
   - Still cannot access production secrets
   - Trusted with staging environment troubleshooting

3. **QA/Testing Team** → `ci.yml` vault password only
   - Can access staging environment for testing
   - Can validate deployments before production
   - Cannot access development or production secrets

4. **CI/CD Systems** → `ci.yml` vault password only
   - Automated deployments to CI/staging environment
   - Stored in CI/CD secrets management (GitHub Actions, Jenkins, etc.)
   - Cannot access development or production secrets

5. **DevOps/SRE Team** → All vault passwords (`dev.yml` + `ci.yml` + `prod.yml`)
   - Full environment access for operational needs
   - Production deployments and emergency access
   - Highly restricted, audit-logged access
   - Responsible for security and infrastructure

### Multi-Vault Setup for Senior Developers

**Configure multiple vault passwords:**
```bash
# Create separate password files for each environment
echo "dev_vault_password" > ~/.ansible-vault-pass-dev
echo "ci_vault_password" > ~/.ansible-vault-pass-ci
echo "prod_vault_password" > ~/.ansible-vault-pass-prod

# Secure the files
chmod 600 ~/.ansible-vault-pass-*

# Add to shell profile (.bashrc/.zshrc)
export ANSIBLE_VAULT_PASSWORD_FILE_DEV=~/.ansible-vault-pass-dev
export ANSIBLE_VAULT_PASSWORD_FILE_CI=~/.ansible-vault-pass-ci
export ANSIBLE_VAULT_PASSWORD_FILE_PROD=~/.ansible-vault-pass-prod
```

### Access Pattern Examples

**Junior Developer (dev only):**
```bash
# Set dev vault password
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass-dev

# Can work with dev environment
./claudia django --install  # Uses dev.yml vault

# Cannot access other environments
./claudia django --install --ci   # ❌ Access denied
./claudia django --install --prod # ❌ Access denied
```

**Senior Developer (dev + ci):**
```bash
# Switch between environments as needed
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass-dev
./claudia django --install  # Development deployment

export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass-ci  
./claudia django --install --ci  # Debug CI issues

# Still cannot access production
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass-prod  # They don't have this
./claudia django --install --prod # ❌ Access denied
```

**QA Team (ci only):**
```bash
# Set CI vault password for staging testing
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass-ci

# Can test on staging environment
./claudia django --install --ci  # Staging deployment

# Cannot access dev or production
./claudia django --install      # ❌ Access denied (no dev password)
./claudia django --install --prod # ❌ Access denied (no prod password)
```

**DevOps Team (full access):**
```bash
# Can switch between any environment as needed
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass-dev
./claudia django --install  # Development

export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass-ci
./claudia django --install --ci  # Staging

export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible-vault-pass-prod
./claudia django --install --prod  # Production
```

### Security Benefits

- **Hierarchical Access**: Role-based permissions match team responsibilities  
- **Least Privilege**: Each person gets minimum access needed for their role
- **Flexible Debugging**: Senior devs can troubleshoot CI without prod access
- **Audit Trail**: Production vault access limited to DevOps team only
- **Breach Containment**: Compromise of dev/ci credentials doesn't affect production
- **Clear Escalation**: Junior → Senior → DevOps access progression

### Security Guidelines

**Password Distribution:**
- **Junior Devs**: Get `dev.yml` password during onboarding
- **Senior Devs**: Get `dev.yml` + `ci.yml` after 6+ months and team lead approval  
- **QA Team**: Get `ci.yml` password for staging testing responsibilities
- **DevOps**: Get all passwords, with mandatory 2FA and audit logging

**Access Management:**
- Rotate passwords when team members leave
- Regular access reviews (quarterly)
- Log all production vault usage
- Use environment variables, never hardcode passwords
- Separate password files per environment

**Common Scenarios:**

1. **"CI deployment failed, need to debug"**
   - Senior dev uses `ci.yml` password to investigate
   - Can replicate CI environment locally
   - Cannot accidentally affect production

2. **"Need to test integration between services"**  
   - Senior dev deploys to staging with `ci.yml`
   - QA team validates on staging with `ci.yml`
   - Production remains isolated

3. **"Production emergency"**
   - Only DevOps team has `prod.yml` password
   - Emergency access is logged and audited
   - Clear escalation from dev → ci → prod environments

## Open Source File Structure

```
.secrets/
├── README.md                    # This file
├── vault.yml.template           # Base template for creating vaults
├── dev.yml.example             # Development environment example (unencrypted)
├── ci.yml.example              # CI/CD environment example (unencrypted)
└── prod.yml.example            # Production environment example (unencrypted)

# User's real vault files (gitignored):
my-dev.vault.yml                # User's actual dev vault (encrypted)
staging-vault.yml               # User's actual staging vault (encrypted)
production-secrets.vault.yml    # User's actual prod vault (encrypted)
```

## Open Source Usage Workflow

**For open source projects, users create their own vault files:**

### 1. Copy Example to Real Vault
```bash
# Copy the appropriate example file
cp .secrets/dev.yml.example my-dev.vault.yml
cp .secrets/prod.yml.example my-production.vault.yml
```

### 2. Edit with Real Credentials
```bash
# Replace example values with your actual credentials
vim my-dev.vault.yml
```

### 3. Encrypt Your Vault
```bash
# Encrypt your real vault file
./claudia vault --encrypt --file my-dev.vault.yml
```

### 4. Use with Ansible
```bash
# Use in playbooks with vault password
ansible-playbook -i inventory/dev.yml --ask-vault-pass playbook.yml
```

**Benefits of this approach:**
- ✅ No real secrets in the repository
- ✅ Clear examples for contributors
- ✅ Users control their own vault files
- ✅ Vault CLI still provides encryption utilities
- ✅ Gitignored patterns protect user's real vaults

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