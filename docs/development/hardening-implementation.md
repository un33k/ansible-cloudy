# SSH Hardening Implementation Summary

## Overview
This document summarizes the complete implementation of the atomic SSH hardening flow for Ansible Cloudy.

## Changes Made

### 1. New Harden Playbook
**File**: `cloudy/playbooks/recipes/core/harden.yml`
- Atomic SSH hardening that runs first
- Connects via password on initial port (default 22)
- Installs SSH keys
- Disables password authentication
- Changes port to final port (default 22022)
- Gracefully handles already-hardened servers

### 2. Updated Inventory Structure
**File**: `cloudy/inventory/dev.yml`
- Added `harden_targets` group (password auth on initial port)
- Updated `security_targets` group (SSH keys on final port)
- Updated `service_targets` group (SSH keys on final port)
- All groups properly use new vault variable names

### 3. Vault Variable Updates
**Files Updated**:
- `.vault/dev.yml` - Uses new variable names
- `cloudy/defaults/vault.yml` - Updated with new names and legacy mappings

**New Variable Names**:
- `vault_root_user` (was vault_ansible_user)
- `vault_root_password` 
- `vault_root_ssh_private_key_file` (was vault_ansible_ssh_private_key_file)
- `vault_ssh_port_initial` (was vault_initial_ssh_port)
- `vault_ssh_port_final` (was vault_ssh_port)
- `vault_grunt_user` (was vault_admin_user)
- `vault_grunt_password` (was vault_admin_password)

### 4. Updated Security Playbook
**File**: `cloudy/playbooks/recipes/core/security.yml`
- Removed SSH hardening tasks (now in harden.yml)
- Focuses on firewall, fail2ban, grunt user creation
- Expects SSH keys on final port

### 5. CLI Integration
**New Files**:
- `dev/cli/operations/harden.py` - Harden operation handler
- Updated `dev/cli/cli/command_router.py` - Added harden routing
- Updated `dev/cli/execution/dependency_manager.py` - Added harden to dependency chain

**Dependency Chain**: `harden → security → base → service`

### 6. Port Detection Updates
**File**: `dev/cli/execution/ansible/vault_loader.py`
- Updated to check for `vault_ssh_port_final` first, then fall back to `vault_ssh_port`

### 7. Validation Updates
**File**: `cloudy/tasks/sys/core/ensure-secure-connection.yml`
- Skip password/port validation for harden_targets group
- Updated error messages to reference new flow

## Usage Flow

### For Fresh Servers:
```bash
# 1. Harden SSH (password → SSH keys, port 22 → 22022)
cli harden --install

# 2. Security setup (firewall, fail2ban, grunt user)
cli security --install

# 3. Base configuration
cli base --install

# 4. Install services
cli psql --install
cli redis --install
# etc...
```

### For Already Hardened Servers:
- `cli harden --install` will gracefully timeout and skip
- Continue with security/base/services as normal

## Testing

### Test Scripts Created:
1. `test-simple.sh` - Basic syntax validation
2. `verify-variable-mapping.sh` - Verify all variables resolve correctly
3. `run-complete-test.sh` - Full Docker-based test of complete flow
4. `test/e2e/scenarios/00-harden-security-base.sh` - E2E test scenario

### Running Tests:
```bash
# Quick syntax check
./test-simple.sh

# Verify variables
./verify-variable-mapping.sh

# Full Docker test
./run-complete-test.sh
```

## Key Benefits

1. **Atomic Operations**: SSH hardening is isolated and can fail/timeout gracefully
2. **Clear Separation**: Password auth phase vs SSH key auth phase
3. **Vault-Driven**: All ports and settings come from vault variables
4. **Smart Detection**: System automatically detects which port to use
5. **Idempotent**: Safe to run multiple times

## Important Notes

- Initial port (vault_ssh_port_initial) is ONLY used by harden playbook
- All other playbooks use final port (vault_ssh_port_final)
- The system is smart enough to handle already-hardened servers
- Grunt user is optional - only created if vault_grunt_user is defined