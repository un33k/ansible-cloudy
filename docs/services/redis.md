# Redis Cache Service

Redis is an open-source, in-memory data structure store used as a database, cache, message broker, and streaming engine.

## Overview

The Redis service in Ansible Cloudy provides:
- Latest stable Redis version (7.x)
- Memory management and limits
- Persistence options (RDB/AOF)
- Password authentication
- SSL/TLS support
- Automated backups
- Performance monitoring
- Cluster support (optional)

## Installation

### Basic Installation

```bash
# Install Redis with defaults
cli redis --install
```

### Custom Installation

```bash
# Install with custom port and memory
cli redis --install --port 6380 --memory 512

# Install with password authentication
cli redis --install --password "secure_password"

# Install with all options
cli redis --install --port 6380 --memory 1024 --password "secure" --interface 0.0.0.0
```

## Configuration

### Required Variables

Add to your vault file (`.vault/production.yml`):

```yaml
# Redis Configuration
vault_redis_password: "secure_password"  # Required for production
```

### Optional Variables

```yaml
# Connection Settings
vault_redis_port: 6379                  # Default port
vault_redis_bind: "127.0.0.1"           # Bind address
vault_redis_timeout: 0                  # Client idle timeout (0 = disabled)

# Memory Settings
vault_redis_memory_mb: 512              # Max memory in MB
vault_redis_maxmemory_policy: "allkeys-lru"  # Eviction policy

# Persistence Settings
vault_redis_save: "900 1 300 10 60 10000"   # RDB save points
vault_redis_appendonly: "no"                 # AOF persistence
vault_redis_appendfsync: "everysec"          # AOF sync policy

# Security Settings
vault_redis_requirepass: "secure_password"   # Authentication password
vault_redis_protected_mode: "yes"            # Protected mode
```

## Memory Management

### Configure Memory Limit

```bash
# Set memory limit
cli redis --set-memory 1024  # 1GB

# Check current memory usage
cli redis --memory-stats
```

### Eviction Policies

Configure how Redis handles memory when limit is reached:

```yaml
vault_redis_maxmemory_policy: "allkeys-lru"  # Options:
# - noeviction: Return errors when memory limit reached
# - allkeys-lru: Evict least recently used keys
# - volatile-lru: Evict LRU keys with expire set
# - allkeys-random: Evict random keys
# - volatile-random: Evict random keys with expire
# - volatile-ttl: Evict keys with shortest TTL
```

## Persistence Options

### RDB Snapshots

```yaml
# Configure RDB save points
vault_redis_save: "900 1 300 10 60 10000"
# Format: "seconds changes"
# - 900 1: Save after 900 sec if at least 1 key changed
# - 300 10: Save after 300 sec if at least 10 keys changed
# - 60 10000: Save after 60 sec if at least 10000 keys changed
```

### AOF (Append Only File)

```yaml
# Enable AOF
vault_redis_appendonly: "yes"

# AOF sync policies
vault_redis_appendfsync: "everysec"  # Options:
# - always: Sync after every write (safest, slowest)
# - everysec: Sync every second (balanced)
# - no: Let OS handle syncing (fastest, least safe)
```

## Redis Operations

### Key Management

```bash
# Set a key
cli redis --set mykey "myvalue"

# Get a key
cli redis --get mykey

# Delete keys
cli redis --delete key1 key2 key3

# Check if key exists
cli redis --exists mykey

# Set key with expiration
cli redis --setex mykey 3600 "expires in 1 hour"
```

### Data Types

```bash
# Strings
cli redis --set user:1:name "John Doe"
cli redis --get user:1:name

# Lists
cli redis --lpush queue:jobs "job1"
cli redis --rpop queue:jobs

# Sets
cli redis --sadd tags "python" "redis" "cache"
cli redis --smembers tags

# Hashes
cli redis --hset user:1 name "John" email "john@example.com"
cli redis --hget user:1 name
cli redis --hgetall user:1

# Sorted Sets
cli redis --zadd leaderboard 100 "player1" 95 "player2"
cli redis --zrange leaderboard 0 -1 WITHSCORES
```

### Monitoring

```bash
# Real-time statistics
cli redis --monitor

# Get server info
cli redis --info

# Check memory usage
cli redis --memory-stats

# List all keys (careful in production!)
cli redis --keys "*"

# Get slow queries log
cli redis --slowlog
```

## Security

### Password Authentication

```bash
# Set password
cli redis --set-password "new_secure_password"

# Test authentication
cli redis --auth-test
```

### SSL/TLS Configuration

```bash
# Enable SSL
cli redis --enable-ssl

# Generate certificates
cli redis --generate-certs

# Configure SSL in vault
vault_redis_tls_port: 6380
vault_redis_tls_cert_file: "/etc/redis/certs/redis.crt"
vault_redis_tls_key_file: "/etc/redis/certs/redis.key"
vault_redis_tls_ca_cert_file: "/etc/redis/certs/ca.crt"
```

### Access Control Lists (ACL)

```bash
# Create user with specific permissions
cli redis --add-user readonly_user --password pass123 --acl "+get +mget -set"

# List users
cli redis --list-users

# Delete user
cli redis --delete-user readonly_user
```

## Backup and Recovery

### Automated Backups

```bash
# Enable automated backups
cli redis --enable-backups

# Configure backup schedule
cli redis --backup-schedule "0 3 * * *"  # Daily at 3 AM
```

### Manual Backup

```bash
# Create backup
cli redis --backup

# Backup to specific location
cli redis --backup --output /backup/redis/manual-backup.rdb
```

### Restore

```bash
# Restore from backup
cli redis --restore /backup/redis/backup.rdb

# Restore with data merge
cli redis --restore backup.rdb --merge
```

## Performance Tuning

### System Configuration

```bash
# Apply Redis-optimized kernel settings
cli redis --optimize-kernel

# Disable transparent huge pages
cli redis --disable-thp
```

### Redis Configuration

```yaml
# Performance settings
vault_redis_tcp_backlog: 511            # TCP listen backlog
vault_redis_tcp_keepalive: 300          # TCP keepalive
vault_redis_databases: 16                # Number of databases
vault_redis_hz: 10                       # Background task frequency

# Slow log
vault_redis_slowlog_log_slower_than: 10000  # Microseconds
vault_redis_slowlog_max_len: 128            # Max slow log entries
```

## Redis Cluster

### Setup Cluster

```bash
# Deploy Redis cluster (6 nodes minimum)
cli redis-cluster --install --nodes 6

# Add node to cluster
cli redis-cluster --add-node new-server:6379

# Remove node
cli redis-cluster --remove-node node-id
```

### Cluster Operations

```bash
# Check cluster status
cli redis-cluster --status

# Rebalance slots
cli redis-cluster --rebalance

# Failover
cli redis-cluster --failover
```

## Use Cases

### Session Storage

```python
# Python example with redis-py
import redis

r = redis.Redis(host='localhost', port=6379, password='secure_password')

# Store session
session_data = {
    'user_id': 123,
    'username': 'john_doe',
    'roles': ['user', 'admin']
}
r.setex(f"session:{session_id}", 3600, json.dumps(session_data))

# Retrieve session
session = json.loads(r.get(f"session:{session_id}"))
```

### Caching

```javascript
// Node.js example
const redis = require('redis');
const client = redis.createClient({
    host: 'localhost',
    port: 6379,
    password: 'secure_password'
});

// Cache function result
async function getCachedData(key, fetchFunction) {
    const cached = await client.get(key);
    if (cached) return JSON.parse(cached);
    
    const data = await fetchFunction();
    await client.setex(key, 3600, JSON.stringify(data));
    return data;
}
```

### Pub/Sub Messaging

```bash
# Publisher
cli redis --publish channel:news "Breaking news!"

# Subscriber (in another terminal)
cli redis --subscribe channel:news
```

### Rate Limiting

```lua
-- Lua script for rate limiting
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local current = redis.call('INCR', key)

if current == 1 then
    redis.call('EXPIRE', key, window)
end

if current > limit then
    return 0
else
    return 1
end
```

## Monitoring and Alerts

### Metrics to Monitor

1. **Memory Usage**
   ```bash
   cli redis --metric memory
   ```

2. **Connection Count**
   ```bash
   cli redis --metric connections
   ```

3. **Commands Per Second**
   ```bash
   cli redis --metric ops
   ```

4. **Hit Rate**
   ```bash
   cli redis --metric hitrate
   ```

### Alert Configuration

```yaml
# Alert thresholds
vault_redis_alert_memory_threshold: 90     # Alert when memory > 90%
vault_redis_alert_connection_limit: 1000  # Alert when connections > 1000
vault_redis_alert_slowlog_threshold: 10   # Alert when slow queries > 10/min
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if Redis is running
   systemctl status redis
   
   # Check bind address
   cli redis --show-config | grep bind
   
   # Check firewall
   cli redis --check-firewall
   ```

2. **Authentication Failed**
   ```bash
   # Reset password
   cli redis --reset-password
   
   # Test authentication
   cli redis --auth-test
   ```

3. **Out of Memory**
   ```bash
   # Check memory usage
   cli redis --memory-stats
   
   # Increase memory limit
   cli redis --set-memory 2048
   
   # Change eviction policy
   cli redis --set-eviction allkeys-lru
   ```

4. **Slow Performance**
   ```bash
   # Check slow log
   cli redis --slowlog
   
   # Monitor commands
   cli redis --monitor
   
   # Analyze latency
   cli redis --latency
   ```

### Debug Mode

```bash
# Enable debug logging
cli redis --debug

# View Redis logs
cli redis --logs

# Live log monitoring
cli redis --tail-logs
```

## Best Practices

1. **Memory Management**
   - Set appropriate memory limits
   - Choose correct eviction policy
   - Monitor memory fragmentation

2. **Persistence**
   - Use RDB for backups
   - Use AOF for durability
   - Balance performance vs safety

3. **Security**
   - Always use passwords in production
   - Enable protected mode
   - Use SSL for remote connections
   - Implement ACLs for fine-grained control

4. **Performance**
   - Use pipelining for bulk operations
   - Avoid KEYS command in production
   - Use appropriate data structures
   - Enable compression for large values

5. **Monitoring**
   - Track key metrics
   - Set up alerts
   - Monitor slow queries
   - Check client connections

## Integration Examples

### Django Cache

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': 'secure_password',
        }
    }
}
```

### Flask Session

```python
from flask import Flask
from flask_session import Session
import redis

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(
    host='localhost',
    port=6379,
    password='secure_password'
)
Session(app)
```

### Laravel Cache

```php
// config/database.php
'redis' => [
    'default' => [
        'host' => env('REDIS_HOST', '127.0.0.1'),
        'password' => env('REDIS_PASSWORD', 'secure_password'),
        'port' => env('REDIS_PORT', 6379),
        'database' => 0,
    ],
],
```

## Advanced Features

### Redis Modules

```bash
# Install RedisJSON
cli redis --install-module redisjson

# Install RedisSearch
cli redis --install-module redisearch

# Install RedisTimeSeries
cli redis --install-module redistimeseries
```

### Lua Scripting

```bash
# Load Lua script
cli redis --load-script /path/to/script.lua

# Execute script
cli redis --eval-script script_sha key1 key2 arg1 arg2
```

### Streams

```bash
# Add to stream
cli redis --xadd mystream "*" field1 value1 field2 value2

# Read from stream
cli redis --xread COUNT 10 STREAMS mystream 0

# Create consumer group
cli redis --xgroup-create mystream mygroup 0
```