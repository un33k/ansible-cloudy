# PostgreSQL Database Service

PostgreSQL is a powerful, open-source relational database system with a strong reputation for reliability, feature robustness, and performance.

## Overview

The PostgreSQL service in Ansible Cloudy provides:
- Latest stable PostgreSQL version (17)
- Optional PostGIS spatial database extension
- Optional pgvector for AI/ML vector operations
- Automated backups
- Performance tuning
- Security hardening
- Connection pooling with PgBouncer

## Installation

### Basic Installation

```bash
# Install PostgreSQL with defaults
cli psql --install
```

### Advanced Installation

```bash
# Install with custom port
cli psql --install --port 5433

# Install with PostGIS extension
cli psql --install --pgis

# Install with pgvector extension
cli psql --install --pgvector

# Install with all extensions
cli psql --install --pgis --pgvector --port 5433
```

## Configuration

### Required Variables

Add to your vault file (`.vault/production.yml`):

```yaml
# PostgreSQL Configuration
vault_postgres_password: "secure_password"  # Required - superuser password
```

### Optional Variables

```yaml
# Custom Configuration
vault_postgresql_port: 5432                # Default port
vault_pg_version: "17"                     # PostgreSQL version
vault_pg_listen_addresses: "localhost"     # Listen addresses
vault_pg_max_connections: 100              # Max connections

# Performance Tuning
vault_pg_shared_buffers: "256MB"          # Shared memory buffers
vault_pg_work_mem: "4MB"                  # Work memory per operation
vault_pg_maintenance_work_mem: "64MB"     # Maintenance work memory
vault_pg_effective_cache_size: "4GB"      # Effective cache size

# Databases and Users
vault_pg_databases:                        # List of databases to create
  - name: myapp_production
    encoding: UTF8
    lc_collate: en_US.UTF-8
    lc_ctype: en_US.UTF-8
    
vault_pg_users:                           # List of users to create
  - name: myapp
    password: "app_password"
    role_attr_flags: CREATEDB,NOSUPERUSER
```

## Database Management

### User Management

```bash
# Add a new user
cli psql --adduser myapp --password secretpass

# Add user with specific privileges
cli psql --adduser readonly --password readpass --role "NOSUPERUSER,NOCREATEDB"

# List all users
cli psql --list-users

# Remove a user
cli psql --dropuser myapp
```

### Database Management

```bash
# Create a database
cli psql --adddb myapp_production --owner myapp

# Create database with custom encoding
cli psql --adddb myapp_dev --owner myapp --encoding UTF8

# List all databases
cli psql --list-databases

# Drop a database
cli psql --dropdb myapp_dev
```

### Backup Operations

```bash
# Backup specific database
cli psql --backup myapp_production

# Backup all databases
cli psql --backup-all

# Schedule automated backups
cli psql --schedule-backup --time "02:00"
```

### Restore Operations

```bash
# Restore from backup
cli psql --restore /backup/postgresql/myapp_production_2024-01-01.sql

# Restore with custom options
cli psql --restore backup.sql --clean --create
```

## PostGIS Extension

PostGIS adds geographic object support to PostgreSQL.

### Installation

```bash
# Install PostgreSQL with PostGIS
cli psql --install --pgis
```

### Enable PostGIS on Database

```bash
# Enable PostGIS on existing database
cli psql --enable-extension postgis --database myapp_production

# Create spatially-enabled database
cli psql --adddb spatial_db --owner myapp --extensions postgis
```

### PostGIS Usage Example

```sql
-- Create a spatial table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom GEOMETRY(Point, 4326)
);

-- Insert spatial data
INSERT INTO locations (name, geom) 
VALUES ('Office', ST_GeomFromText('POINT(-73.935242 40.730610)', 4326));

-- Spatial query
SELECT name, ST_Distance(geom::geography, 
    ST_GeomFromText('POINT(-73.935 40.731)', 4326)::geography) 
FROM locations;
```

## pgvector Extension

pgvector enables vector similarity search for AI/ML applications.

### Installation

```bash
# Install PostgreSQL with pgvector
cli psql --install --pgvector
```

### Enable pgvector

```bash
# Enable pgvector on database
cli psql --enable-extension vector --database myapp_production
```

### pgvector Usage Example

```sql
-- Create a table with vector column
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(384)
);

-- Create index for similarity search
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);

-- Insert vector data
INSERT INTO embeddings (content, embedding) 
VALUES ('Sample text', '[0.1, 0.2, 0.3, ...]');

-- Similarity search
SELECT content, embedding <=> '[0.1, 0.2, 0.3, ...]' AS distance
FROM embeddings
ORDER BY embedding <=> '[0.1, 0.2, 0.3, ...]'
LIMIT 5;
```

## Performance Tuning

### Automatic Tuning

```bash
# Apply recommended settings for your hardware
cli psql --tune-performance

# Tune for specific workload
cli psql --tune-performance --workload oltp  # or olap, mixed
```

### Manual Tuning

Key parameters to adjust in vault file:

```yaml
# Memory Settings (adjust based on available RAM)
vault_pg_shared_buffers: "4GB"          # 25% of RAM
vault_pg_effective_cache_size: "12GB"   # 75% of RAM
vault_pg_work_mem: "16MB"               # RAM / max_connections / 4
vault_pg_maintenance_work_mem: "1GB"    # RAM / 16

# Connection Settings
vault_pg_max_connections: 200           # Based on application needs
vault_pg_max_prepared_transactions: 0   # Set > 0 only if needed

# Checkpoint Settings
vault_pg_checkpoint_completion_target: 0.9
vault_pg_wal_buffers: "16MB"
vault_pg_checkpoint_segments: 32        # For write-heavy workloads
```

## Connection Pooling with PgBouncer

For high-traffic applications, use PgBouncer for connection pooling.

### Install PgBouncer

```bash
# Install on web servers
cli pgbouncer --install
```

### Configure Application

```yaml
# Application database configuration
database:
  host: localhost      # PgBouncer runs locally
  port: 6432          # PgBouncer port
  name: myapp_production
  user: myapp
  password: app_password
```

## Monitoring

### Basic Monitoring

```bash
# Check PostgreSQL status
cli psql --status

# View current connections
cli psql --connections

# Show running queries
cli psql --activity

# Database sizes
cli psql --sizes
```

### Performance Monitoring

```bash
# Enable query statistics
cli psql --enable-stats

# View slow queries
cli psql --slow-queries

# Analyze query performance
cli psql --explain "SELECT * FROM users WHERE email = 'test@example.com'"
```

## Security

### SSL/TLS Configuration

```bash
# Enable SSL
cli psql --enable-ssl

# Generate new certificates
cli psql --generate-certs
```

### Access Control

```yaml
# Configure pg_hba.conf through vault
vault_pg_hba_entries:
  - type: local
    database: all
    user: all
    method: peer
  - type: host
    database: all
    user: all
    address: 127.0.0.1/32
    method: md5
  - type: host
    database: all
    user: all
    address: 10.0.0.0/8
    method: md5
```

### Audit Logging

```bash
# Enable audit logging
cli psql --enable-audit

# View audit logs
cli psql --audit-logs
```

## Maintenance

### Routine Maintenance

```bash
# Run VACUUM on all databases
cli psql --vacuum

# Run ANALYZE to update statistics
cli psql --analyze

# Reindex databases
cli psql --reindex
```

### Automated Maintenance

Maintenance tasks are automatically scheduled:
- Daily: VACUUM and ANALYZE
- Weekly: Full VACUUM
- Monthly: REINDEX

## Troubleshooting

### Common Issues

1. **Connection refused**
   ```bash
   # Check if PostgreSQL is running
   systemctl status postgresql
   
   # Check listen addresses
   cli psql --show-config | grep listen
   ```

2. **Authentication failed**
   ```bash
   # Check pg_hba.conf
   cli psql --show-hba
   
   # Reset user password
   cli psql --reset-password myapp
   ```

3. **Performance issues**
   ```bash
   # Check slow queries
   cli psql --slow-queries
   
   # Analyze specific query
   cli psql --explain "YOUR QUERY HERE"
   
   # Check table statistics
   cli psql --table-stats mytable
   ```

### Debug Mode

```bash
# Enable debug logging
cli psql --debug

# View PostgreSQL logs
cli psql --logs

# Live log monitoring
cli psql --tail-logs
```

## Best Practices

1. **Regular Backups**: Always maintain regular backups
2. **Connection Pooling**: Use PgBouncer for applications with many connections
3. **Monitoring**: Set up monitoring for slow queries and disk usage
4. **Indexing**: Create appropriate indexes for your queries
5. **Partitioning**: Use table partitioning for large datasets
6. **VACUUM**: Ensure autovacuum is properly configured
7. **Security**: Use SSL and strong passwords in production
8. **Testing**: Test major changes in a staging environment first

## Migration Guide

### From Other Databases

```bash
# Migrate from MySQL
cli psql --migrate-from mysql --source-host old-server --source-db myapp

# Migrate from MongoDB
cli psql --migrate-from mongodb --source-uri "mongodb://old-server/myapp"
```

### Version Upgrades

```bash
# Check for available upgrades
cli psql --check-upgrade

# Perform upgrade
cli psql --upgrade --to-version 17
```

## Integration Examples

### Python (psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="myapp_production",
    user="myapp",
    password="app_password"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
```

### Node.js (pg)

```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'myapp_production',
  user: 'myapp',
  password: 'app_password',
});

const result = await pool.query('SELECT * FROM users');
```

### Django

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myapp_production',
        'USER': 'myapp',
        'PASSWORD': 'app_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Advanced Features

### Logical Replication

```bash
# Set up logical replication
cli psql --setup-replication --type logical --target replica-server
```

### Foreign Data Wrappers

```bash
# Connect to external database
cli psql --add-foreign-server mysql-server --type mysql
```

### Full Text Search

```sql
-- Create text search configuration
CREATE TEXT SEARCH CONFIGURATION english_stem (COPY = english);

-- Create search index
CREATE INDEX idx_fts ON documents USING gin(to_tsvector('english_stem', content));

-- Search documents
SELECT * FROM documents 
WHERE to_tsvector('english_stem', content) @@ to_tsquery('english_stem', 'search & terms');
```