# Troubleshooting Guide

Common issues and solutions for Ansible Cloudy deployments.

## Connection Issues

### SSH Connection Failed

**Symptom**: Cannot connect to server after security setup

**Common Causes**:
1. Wrong SSH port (changed from 22 to 2222)
2. Firewall blocking connection
3. SSH key not installed
4. Wrong user or authentication method

**Solutions**:

```bash
# Check if using correct port
ssh root@server -p 2222

# Verify SSH key exists
ls -la ~/.ssh/id_rsa

# Test with verbose output
ssh -vvv root@server -p 2222

# Check from different port if locked out
ssh root@server -p 22
```

### Authentication Failed

**Symptom**: "Permission denied" errors

**Solutions**:

```bash
# Ensure vault has correct password
grep vault_root_password .vault/dev.yml

# Try with password explicitly
sshpass -p 'your_password' ssh root@server

# Check if key-based auth is required
ssh -o PreferredAuthentications=publickey root@server -p 2222
```

### Unreachable Host

**Symptom**: "Host unreachable" errors

**Solutions**:

```bash
# Test basic connectivity
ping server_ip

# Check if port is open
nc -zv server_ip 2222

# Verify firewall rules on server
# (May need console access)
```

## Deployment Issues

### Variable Undefined Errors

**Symptom**: "undefined variable" during playbook execution

**Common Causes**:
1. Missing vault file
2. Variable not in vault
3. Wrong environment loaded

**Solutions**:

```bash
# Verify vault file exists
ls -la .vault/dev.yml

# Check variable is defined
grep variable_name .vault/dev.yml

# Explicitly load vault
cli security --install -e .vault/dev.yml

# Debug variable resolution
ansible-inventory -i inventory/dev.yml --host server --vars | grep variable_name
```

### Service Won't Start

**Symptom**: Service fails to start after installation

**PostgreSQL Issues**:

```bash
# Check PostgreSQL logs
journalctl -u postgresql -n 100

# Common issues:
# - Port already in use
sudo lsof -i :5432

# - Permission issues
ls -la /var/lib/postgresql/

# - Configuration errors
sudo -u postgres pg_ctl -D /var/lib/postgresql/15/main reload
```

**Redis Issues**:

```bash
# Check Redis logs
journalctl -u redis -n 100

# Common issues:
# - Memory limits
free -h

# - Port conflicts
sudo lsof -i :6379

# - Configuration syntax
redis-server --test-memory 1024
```

**Nginx Issues**:

```bash
# Test configuration
nginx -t

# Check error log
tail -f /var/log/nginx/error.log

# Common issues:
# - Port 80/443 in use
sudo lsof -i :80
sudo lsof -i :443

# - SSL certificate issues
ls -la /etc/letsencrypt/live/
```

### Package Installation Failures

**Symptom**: "Package not found" or "Unable to locate package"

**Solutions**:

```bash
# Update package cache
sudo apt update  # Debian/Ubuntu
sudo yum makecache  # RHEL/CentOS

# Check OS version compatibility
lsb_release -a
cat /etc/os-release

# Verify repository configuration
ls -la /etc/apt/sources.list.d/  # Debian/Ubuntu
ls -la /etc/yum.repos.d/  # RHEL/CentOS
```

## Configuration Issues

### Wrong Port After Setup

**Symptom**: Services accessible on wrong ports

**Solution**:

```bash
# Check actual port in use
sudo netstat -tlnp | grep postgres
sudo netstat -tlnp | grep redis
sudo netstat -tlnp | grep nginx

# Verify configuration
grep port /etc/postgresql/*/main/postgresql.conf
grep port /etc/redis/redis.conf
```

### SSL Certificate Problems

**Symptom**: HTTPS not working or certificate errors

**Solutions**:

```bash
# Check certificate status
sudo certbot certificates

# Test SSL configuration
openssl s_client -connect domain.com:443

# Renew certificates
sudo certbot renew --dry-run
sudo certbot renew

# Verify Nginx SSL config
grep -r ssl /etc/nginx/sites-enabled/
```

### Firewall Blocking Services

**Symptom**: Services running but not accessible

**Solutions**:

```bash
# Check UFW status
sudo ufw status verbose

# Allow required ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 2222/tcp

# Check iptables (if not using UFW)
sudo iptables -L -n -v
```

## Performance Issues

### High Memory Usage

**PostgreSQL Tuning**:

```bash
# Check current memory usage
free -h
ps aux | grep postgres

# Adjust shared_buffers
# Edit postgresql.conf
shared_buffers = 256MB  # Reduce if needed

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**Redis Memory Issues**:

```bash
# Check Redis memory
redis-cli info memory

# Set memory limit
redis-cli CONFIG SET maxmemory 512mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Persist configuration
redis-cli CONFIG REWRITE
```

### Slow Response Times

**Diagnosis Steps**:

```bash
# Check system load
uptime
top

# Check disk I/O
iostat -x 5

# Check network
netstat -i
ss -s

# PostgreSQL slow queries
tail -f /var/log/postgresql/postgresql-*.log
```

## Ansible-Specific Issues

### Playbook Hanging

**Symptom**: Playbook seems stuck

**Solutions**:

```bash
# Run with verbose output
cli service --install -vvv

# Use check mode first
cli service --install --check

# Increase timeout for slow operations
cli service --install -- -e ansible_command_timeout=300
```

### Module Failures

**Common Module Issues**:

```bash
# Python module missing
# Solution: Install on target
ssh root@server -p 2222 "apt install python3-psycopg2"

# Permission denied
# Solution: Check become privileges
cli service --install -- -K  # Ask for sudo password
```

## Recovery Procedures

### Locked Out of Server

**If you're completely locked out**:

1. **Use console access** (if available)
2. **Boot from rescue mode**
3. **Restore from backup**

**Prevention**:
```bash
# Always test on non-production first
cli security --install --check

# Keep console access available
# Don't close your current SSH session until verified
```

### Rollback Procedures

**PostgreSQL Rollback**:

```bash
# Stop service
sudo systemctl stop postgresql

# Restore from backup
pg_restore -d dbname backup_file

# Revert configuration
sudo cp /etc/postgresql/15/main/postgresql.conf.bak /etc/postgresql/15/main/postgresql.conf
sudo systemctl start postgresql
```

**General Service Rollback**:

```bash
# Most services keep backup configs
ls -la /etc/service/*.bak

# Restore and restart
sudo cp /etc/service/config.bak /etc/service/config
sudo systemctl restart service
```

## Debug Commands

### Useful Debugging Tools

```bash
# Check all services status
systemctl status postgresql redis nginx

# View recent logs
journalctl -xe

# Check disk space
df -h

# Check port usage
ss -tlnp

# Process list
ps auxf

# System resources
htop

# Network connections
netstat -an

# DNS resolution
nslookup domain.com
dig domain.com
```

### Ansible Debug Commands

```bash
# Test inventory
ansible all -i inventory/prod.yml -m ping

# Show host variables
ansible-inventory -i inventory/prod.yml --host server

# Run ad-hoc commands
ansible all -i inventory/prod.yml -m shell -a "uptime"

# Check facts
ansible all -i inventory/prod.yml -m setup
```

## Getting Help

### Log Locations

- **System logs**: `/var/log/syslog` or `/var/log/messages`
- **PostgreSQL**: `/var/log/postgresql/`
- **Redis**: `/var/log/redis/`
- **Nginx**: `/var/log/nginx/`
- **Application**: Check systemd: `journalctl -u appname`

### Support Resources

1. **Check existing documentation**
2. **Review ansible.log** (if enabled)
3. **Search error messages**
4. **Test in isolation**
5. **Use verbose mode** (`-v`, `-vv`, `-vvv`)

### Reporting Issues

When reporting issues, include:

1. **Command run**: Full command with parameters
2. **Error message**: Complete error output
3. **Environment**: OS, Ansible version
4. **Configuration**: Relevant vault/inventory sections
5. **Logs**: Related log entries

```bash
# Gather diagnostic info
cli --version
ansible --version
python --version
cat /etc/os-release
```