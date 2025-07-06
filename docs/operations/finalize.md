# Server Finalization Guide

The finalize operation completes server setup by applying system upgrades, optionally changing the SSH port, and rebooting if necessary.

## Overview

The finalize step should be run after all services are installed. It performs:
- System package upgrades (security patches and updates)
- Optional SSH port change for additional security
- System reboot if required by upgrades or port changes
- Final validation of all services

## When to Use

Run finalize:
- After completing all service installations
- Before putting a server into production
- When you want to change the SSH port after initial setup
- To apply accumulated system updates

## Basic Usage

```bash
# Standard finalization with upgrades
cli finalize --install

# Finalize and change SSH port to hardened default (22022)
cli finalize --install --change-port

# Finalize with custom SSH port
cli finalize --install --change-port --to-port 2222

# Skip system upgrades (not recommended)
cli finalize --install --skip-upgrade

# Force reboot even if not required
cli finalize --install --force-reboot

# Never reboot (manual reboot required)
cli finalize --install --no-reboot
```

## SSH Port Change Considerations

### Important Notes

1. **Connection Update**: When the SSH port changes, the system will:
   - Update SSH configuration
   - Add the new port to firewall rules
   - Reboot the system
   - Remove the old port from firewall after successful reconnection
   - Update ansible connection to use the new port

2. **Inventory Update Required**: After changing the SSH port, update your inventory files:
   ```yaml
   # inventory/prod.yml
   all:
     vars:
       ansible_port: 22022  # Update to your new port
   ```

3. **Client Configuration**: Update your SSH client config:
   ```bash
   # ~/.ssh/config
   Host myserver
     HostName server.example.com
     Port 22022  # New port
     User grunt
   ```

### Port Change Workflow

1. **Current State**: System validates current SSH port
2. **Configuration**: Updates `/etc/ssh/sshd_config` with new port
3. **Firewall**: Adds new port to UFW allow rules
4. **Validation**: Tests SSH configuration syntax
5. **Reboot**: System reboots to apply changes
6. **Reconnection**: Ansible reconnects on new port
7. **Cleanup**: Old port removed from firewall rules
8. **Verification**: Final validation on new port

## Upgrade Process

### What Gets Upgraded

- Security patches
- System libraries
- Installed packages
- Kernel updates (if available)

### Upgrade Safety

The finalize process uses:
- `apt upgrade`: Standard package upgrades
- `aptitude safe-upgrade`: Conservative upgrade approach
- No automatic removal of packages
- No distribution upgrades

### Reboot Detection

System automatically detects if reboot is required by checking:
- `/var/run/reboot-required` file
- SSH configuration changes
- Kernel updates

## Examples by Scenario

### Production Server Finalization

```bash
# Full finalization with port hardening
cli finalize --install --change-port

# This will:
# 1. Apply all security updates
# 2. Change SSH port to 22022
# 3. Reboot the system
# 4. Validate all services
```

### Development Server Quick Setup

```bash
# Just upgrades, no port change
cli finalize --install

# Keeps SSH on port 22 for convenience
```

### Staged Deployment

```bash
# Step 1: Apply updates without reboot
cli finalize --install --no-reboot

# Step 2: Schedule maintenance window
# Step 3: Manual reboot
sudo reboot

# Step 4: Verify services
cli security --verify
```

### Custom Security Port

```bash
# Use organization-specific port
cli finalize --install --change-port --to-port 52022

# Very high port for obscurity
```

## Validation

After finalization, the system performs:

1. **Connection Test**: Verifies SSH on new port
2. **Service Check**: Ensures SSH daemon is running
3. **Port Verification**: Confirms correct port binding
4. **Service Restart Check**: Uses `needrestart` to identify services needing restart

## Troubleshooting

### Cannot Connect After Port Change

If you lose connection after port change:

1. **Console Access**: Use provider's console (AWS, DigitalOcean, etc.)
2. **Check SSH Status**:
   ```bash
   systemctl status ssh
   ss -tlnp | grep sshd
   ```
3. **Check Firewall**:
   ```bash
   ufw status numbered
   ```
4. **Revert if Needed**:
   ```bash
   # Via console
   sed -i 's/Port 22022/Port 22/' /etc/ssh/sshd_config
   systemctl restart ssh
   ufw allow 22/tcp
   ```

### Upgrades Fail

If system upgrades fail:

1. **Check Disk Space**:
   ```bash
   df -h
   ```
2. **Fix Package Issues**:
   ```bash
   apt --fix-broken install
   apt autoremove
   ```
3. **Clear Package Cache**:
   ```bash
   apt clean
   ```

### Reboot Hangs

If system doesn't come back after reboot:

1. Wait full timeout (5 minutes)
2. Check provider console for boot issues
3. May need manual intervention for:
   - Kernel panics
   - Filesystem checks
   - Network configuration issues

## Best Practices

1. **Test First**: Always test finalization in development before production
2. **Backup**: Ensure backups exist before major changes
3. **Maintenance Window**: Schedule production finalizations during maintenance windows
4. **Monitor**: Watch system logs during the process
5. **Document**: Record the new SSH port in your documentation
6. **Access**: Ensure you have console access before port changes

## Integration with Services

Finalize works seamlessly after any service installation:

```bash
# Example: Complete PostgreSQL deployment
cli security --install
cli base --install
cli psql --install --pgis
cli finalize --install --change-port

# Example: Full web stack
cli security --install
cli base --install
cli nginx --install
cli django --install
cli redis --install
cli finalize --install --change-port
```

## Security Benefits

Running finalize provides:

1. **Latest Security Patches**: All CVEs addressed
2. **Port Obscurity**: Non-standard SSH port reduces automated attacks
3. **Clean System**: Ensures all services start fresh
4. **Verified State**: Confirms all components working correctly

## Summary

The finalize operation is the final step in server deployment, ensuring:
- System is fully updated
- Security is maximized with optional port change
- All services are running correctly
- Server is production-ready

Always run finalize before considering a server deployment complete.