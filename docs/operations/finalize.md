# Server Finalization Guide

The finalize operation completes server setup by applying system upgrades and managing system reboots.

## Overview

The finalize step should be run after all services are installed. It performs:
- System package upgrades (security patches and updates)
- Reboot management (skipped by default to prevent disruption)
- Final validation of all services

## When to Use

Run finalize:
- After completing all service installations
- Before putting a server into production
- To apply accumulated system updates
- During scheduled maintenance windows

## Basic Usage

```bash
# Standard finalization (upgrades only, no reboot)
cli finalize --install

# Finalize with reboot if needed
cli finalize --install --reboot

# Skip system upgrades (not recommended)
cli finalize --install --skip-upgrade

# Force reboot even if not required
cli finalize --install --force-reboot
```

## SSH Port Management

SSH port changes have been separated into a dedicated command for better control:

```bash
# Change SSH port (simple)
cli ssh --new-port 3333

# Change SSH port (explicit)
cli ssh --old-port 22 --new-port 3333
```

See the [SSH Port Management](#ssh-port-management-1) section below for details.

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
- Kernel updates
- Core library updates

## Reboot Management

### Default Behavior

**By default, reboots are skipped** even if required. This prevents unexpected disconnections during automated deployments.

When a reboot is required but skipped, you'll see:
```
⚠️  IMPORTANT: Reboot is required but was skipped.
Run 'cli finalize --install --reboot' to perform the reboot.
```

### Reboot Options

- **No flag**: Skip reboot (default)
- `--reboot`: Allow reboot if required
- `--force-reboot`: Always reboot

## Examples by Scenario

### Production Server Finalization

```bash
# Step 1: Apply updates without reboot
cli finalize --install

# Step 2: Schedule maintenance window
# Step 3: Apply updates with reboot
cli finalize --install --reboot
```

### Development Server Quick Setup

```bash
# Just upgrades, no reboot needed
cli finalize --install
```

### Immediate Production Deployment

```bash
# Full finalization with automatic reboot if needed
cli finalize --install --reboot --prod
```

### Maintenance Window

```bash
# Force reboot during scheduled maintenance
cli finalize --install --force-reboot
```

## SSH Port Management

### Changing SSH Port

SSH port changes are now handled by the dedicated `cli ssh` command:

```bash
# Change to port 3333 (reads current port from vault)
cli ssh --new-port 3333

# Explicit port change
cli ssh --old-port 22 --new-port 3333
```

### Important Notes

1. **Connection will drop** - This is normal behavior
2. **Update your vault** - After changing ports, update `vault_ssh_port` in `.vault/*.yml`
3. **UFW is updated automatically** - New port is added before old port is removed

### Port Change Workflow

1. Add new port to UFW firewall
2. Update SSH configuration
3. Restart SSH service (connection drops)
4. Manually update vault/inventory files

## Validation

After finalization, the system performs:

1. **System Check**: Verifies all services are running
2. **Update Status**: Shows what was upgraded
3. **Reboot Status**: Indicates if reboot was performed or skipped

## Troubleshooting

### System Needs Reboot But Wasn't Rebooted

If you see the reboot warning:

```bash
# Option 1: Run finalize with reboot
cli finalize --install --reboot

# Option 2: Manual reboot
sudo reboot
```

### Cannot Connect After SSH Port Change

If you lose connection after port change:

1. **Update vault file**:
   ```yaml
   vault_ssh_port: 3333  # Your new port
   ```

2. **Test connection**:
   ```bash
   ssh -p 3333 user@server
   ```

3. **If still failing, check via console**:
   ```bash
   systemctl status ssh
   ss -tlnp | grep sshd
   ufw status numbered
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

## Best Practices

1. **Test First**: Always test finalization in development before production
2. **Backup**: Ensure backups exist before major changes
3. **Maintenance Window**: Schedule production finalizations during maintenance windows
4. **Separate Operations**: Use `cli ssh` for port changes, `cli finalize` for upgrades
5. **Monitor**: Watch system logs during the process

## Integration with Services

Finalize works seamlessly after any service installation:

```bash
# Example: Complete PostgreSQL deployment
cli security --install
cli base --install
cli psql --install --pgis
cli finalize --install

# Example: Full web stack
cli security --install
cli base --install
cli nginx --install
cli django --install
cli redis --install
cli finalize --install --reboot
```

## Security Benefits

Running finalize provides:

1. **Latest Security Patches**: All CVEs addressed
2. **Clean System**: Ensures all services start fresh
3. **Verified State**: Confirms all components working correctly

For additional security through port changes:
```bash
# Change SSH port after finalization
cli ssh --new-port 3333
```

## Summary

The finalize operation is the final step in server deployment, ensuring:
- System is fully updated
- Reboot management is under your control
- All services are running correctly
- Server is production-ready

Always run finalize before considering a server deployment complete. Use `cli ssh` separately for SSH port management when needed.