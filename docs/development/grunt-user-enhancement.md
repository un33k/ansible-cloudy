# Grunt User Enhancement Documentation

## Overview
This document describes the enhancements made to the grunt user management system in Ansible Cloudy.

## Changes Made

### 1. Enhanced Group Memberships
Updated the default groups for the grunt user:
- **Location:** `cloudy/defaults/security.yml` (as `grunt_groups_string_default`)
- **Previous groups:** `sudo,adm,systemd-journal`
- **New groups:** `sudo,adm,systemd-journal,www-data,docker,ssl-cert`
- **Override:** Set `vault_grunt_groups_string` in vault files

This allows the grunt user to:
- Manage web server files (www-data)
- Run Docker containers (docker)
- Access SSL certificates (ssl-cert)

### 2. Group Creation in Security Playbook
Added group creation tasks in `cloudy/playbooks/recipes/core/security.yml` before grunt user creation:
```yaml
- name: Create required groups for grunt user
  group:
    name: "{{ item }}"
    state: present
  loop:
    - www-data
    - docker
    - ssl-cert
  when: vault_grunt_user is defined
  tags: [users, grunt, groups]
```

### 3. Enhanced User Creation
Split user creation and group management into separate tasks:
- `cloudy/tasks/sys/user/add-user.yml` - Creates/updates user without groups
- `cloudy/tasks/sys/user/set-groups.yml` - Sets exact group membership
- Uses `append: false` for exact group membership
- Sets user to ONLY the groups specified (removes from all others)

### 4. Password Generation
Enhanced `cloudy/tasks/sys/user/change-password.yml` to:
- Generate random 20-character passwords when not provided
- Display generated passwords with security warning
- Use secure password generation with letters, digits, and punctuation

### 5. Docker Installation in Base
Added Docker installation to `cloudy/playbooks/recipes/core/base.yml`:
- Installs Docker Engine and all components
- Adds grunt user to docker group post-installation
- Ensures Docker service is enabled and started

### 6. Docker Installation Task
Updated `cloudy/tasks/sys/docker/install.yml` to be a proper includable task file with:
- Docker CE, CLI, containerd, buildx, and compose plugins
- Proper daemon configuration with log rotation
- Group creation and service management

## Security Considerations

### Group Memberships
- **sudo**: Administrative access (already existed)
- **adm**: System log access (already existed)
- **systemd-journal**: Journal log access (already existed)
- **www-data**: Web server file access (new)
- **docker**: Container management (new)
- **ssl-cert**: SSL certificate access (new)

### Risk Mitigation
1. The grunt user is optional - only created when `vault_grunt_user` is defined
2. Services should still use dedicated service accounts when possible
3. The docker group provides root-equivalent access to Docker daemon
4. All automation continues to run as root with SSH key authentication

## Usage

### Creating/Updating Grunt User

#### Scenario A: Grunt User Doesn't Exist
1. Define in vault file (`.vault/secrets.yml`):
```yaml
vault_grunt_user: "grunt"
vault_grunt_password: "SecurePassword123!"  # Optional - generated if not provided
```

2. Run security playbook:
```bash
cli security --install
```

Result:
- Creates user with exact groups: sudo,adm,systemd-journal,www-data,docker,ssl-cert
- Sets password (provided or generated)
- User has ONLY the specified groups

#### Scenario B: Grunt User Already Exists
1. Update vault file with new password or groups:
```yaml
vault_grunt_user: "grunt"
vault_grunt_password: "NewPassword456!"  # Optional - only updates if provided
vault_grunt_groups: "sudo,adm,docker"  # User will be REMOVED from www-data, ssl-cert, etc.
```

2. Run security playbook:
```bash
cli security --install
```

Result:
- Updates password if provided (keeps existing if not)
- Sets exact group membership (removes from any groups not listed)
- Example: If user was in "wheel" group, they'll be removed from it

### Verifying Setup
After installation:
- Check user groups: `id grunt`
- Verify exact groups match vault_grunt_groups
- Verify Docker access: `sudo -u grunt docker ps`
- Check service directories ownership

## Service Integration
Services automatically detect and use grunt user when available:
- Django, Node.js apps run under grunt
- Service directories created with proper ownership
- Logs and runtime directories accessible to grunt

## Notes
- The Docker group is created in security playbook before Docker installation
- This ensures grunt user has proper group membership when Docker is installed later
- Using `append: false` ensures exact group membership control
- If vault_grunt_groups changes, the user will be updated to match exactly
- All changes maintain backward compatibility - existing deployments continue to work

## Important Behavior
- **Exact Group Membership**: The user will have ONLY the groups listed in vault_grunt_groups
- **Group Removal**: If a user is in groups not listed (e.g., wheel), they'll be removed
- **Primary Group**: The user's primary group is preserved (typically same as username)
- **No admin group**: We use 'adm' not 'admin' as it's the standard Ubuntu/Debian group
- **Separate Tasks**: User creation and group assignment are separate for better error handling

## Implementation Details
The grunt user management is implemented in two phases:
1. **User Creation**: Creates the user account with default settings
2. **Group Assignment**: Sets exact group membership using a separate task

This approach avoids issues with variable passing through include_tasks and ensures reliable group management.