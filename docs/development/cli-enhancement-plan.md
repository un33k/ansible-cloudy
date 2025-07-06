# CLI Enhancement Plan for Distributed Architecture

## Current Issues

### 1. Naming Inconsistency
- `django` - Actually installs full web server stack (Apache/Gunicorn, PostgreSQL, PostGIS, PgBouncer)
- `psql` - Just PostgreSQL (not the full stack)
- `nodejs` - Full Node.js application server with PM2 and optional Nginx
- `standalone` - Complete all-in-one stack

### 2. Unclear Categories
- "Database Services" mixes actual databases (psql) with extensions (postgis, pgvector) and utilities (pgbouncer)
- "Web & Cache Services" groups unrelated things (Django framework, Nginx server, Redis cache)

### 3. Confusion about Scope
- Some commands install just the service (redis, nginx)
- Others install complete stacks (django, nodejs, standalone)

## Distributed Architecture Patterns

### Deployment Scenarios

1. **Database Server**
   - `security` + `base` + `psql` = Basic PostgreSQL server
   - Can add `postgis` and/or `pgvector` as extensions
   - Dedicated to database operations only

2. **Application Server** (e.g., Django)
   - `security` + `base` + `django` = Application server
   - Points to remote database server
   - No local database

3. **Load Balancer/Proxy Server**
   - `security` + `base` + `nginx` = Reverse proxy
   - Routes traffic to application servers
   - No application code

4. **Cache Server**
   - `security` + `base` + `redis` = Cache server
   - Provides caching for application servers

5. **All-in-One Server** (Standalone only)
   - Everything on one box for development/small deployments
   - Two flavors: Django-based or Node.js-based

## Proposed CLI Enhancement

### 1. Rename Services to Reflect Their True Purpose

#### Foundation (Required for all servers):
- `security` - Security hardening (keep as is)
- `base` - Base system configuration (keep as is)
- `finalize` - System finalization (keep as is)
- `ssh` - SSH port management (keep as is)

#### Database Layer:
- `postgresql` (rename from `psql`) - PostgreSQL database server
- `postgis` - PostGIS extension for PostgreSQL (requires postgresql)
- `pgvector` - pgvector extension for PostgreSQL (requires postgresql)

#### Application Layer:
- `django-app` (rename from `django`) - Django application server (no DB)
- `nodejs-app` (rename from `nodejs`) - Node.js application server (no DB)

#### Infrastructure Layer:
- `nginx-proxy` (rename from `nginx`) - Nginx as reverse proxy/load balancer
- `redis-cache` (rename from `redis`) - Redis cache server
- `pgbouncer` - Connection pooler (typically on app servers)

#### All-in-One:
- `standalone-django` - Complete Django stack on single server
- `standalone-nodejs` - Complete Node.js stack on single server

### 2. Fix Recipe Implementations

#### A. Split current `django.yml` into:
1. `django-app.yml` - Only Django/Python/Gunicorn setup, expects remote DB
2. `standalone-django.yml` - Current implementation (all-in-one)

#### B. Split current `nodejs.yml` into:
1. `nodejs-app.yml` - Only Node.js/PM2 setup, expects remote services
2. `standalone-nodejs.yml` - Current implementation with local services

### 3. Add Connection Configuration

Add CLI parameters for distributed setup:
```bash
# Database server
cli postgresql --install

# Application server pointing to database
cli django-app --install --db-host 10.0.1.10 --db-port 5432

# Cache server
cli redis-cache --install

# Load balancer pointing to app servers
cli nginx-proxy --install --backends "10.0.2.10:8000,10.0.2.11:8000"
```

### 4. Improve Service Descriptions

```
Foundation Services:
  security          Security hardening (required first)
  base              Base system configuration (required second)

Database Services:
  postgresql        PostgreSQL database server
  postgis           Add PostGIS spatial extension to PostgreSQL
  pgvector          Add pgvector AI/ML extension to PostgreSQL

Application Services:
  django-app        Django application server (connects to remote DB)
  nodejs-app        Node.js application server (connects to remote services)
  
Infrastructure Services:
  nginx-proxy       Nginx reverse proxy/load balancer
  redis-cache       Redis in-memory cache server
  pgbouncer         PostgreSQL connection pooler

All-in-One Stacks:
  standalone-django Complete Django stack on single server
  standalone-nodejs Complete Node.js stack on single server
```

### 5. Add Deployment Guides

Create quick deployment patterns in help:

```
Common Deployment Patterns:

1. Three-Tier Web Application:
   DB Server:    cli security && cli base && cli postgresql
   App Server:   cli security && cli base && cli django-app --db-host <db-ip>
   Proxy:        cli security && cli base && cli nginx-proxy --backends <app-ips>

2. Database Cluster with Extensions:
   cli security && cli base && cli postgresql && cli postgis && cli pgvector

3. Development/Small Deployment:
   cli security && cli base && cli standalone-django --domain myapp.com
```

### 6. Add Service Dependencies Validation

Before installing a service, check dependencies:
- `postgis` checks if `postgresql` is installed
- `pgvector` checks if `postgresql` is installed  
- `django-app` warns if no `--db-host` provided
- `nginx-proxy` warns if no `--backends` provided

### 7. Update Inventory Group Names

Align inventory groups with service roles:
```yaml
all:
  children:
    database_servers:    # postgresql, postgis, pgvector
    app_servers:         # django-app, nodejs-app
    cache_servers:       # redis-cache
    proxy_servers:       # nginx-proxy
    standalone_servers:  # standalone-*
```

### 8. Add Service Scope Indicators

Add a scope indicator to help users understand what they're installing:
- [Component] - Single service only
- [Stack] - Complete application stack
- [Extension] - Add-on to existing service

Example output:
```
Database Services:
  postgresql         [Component] PostgreSQL database server
  postgis            [Extension] PostgreSQL with PostGIS spatial extension  
  pgvector           [Extension] PostgreSQL with pgvector for AI embeddings

Application Stacks:
  standalone-django  [Stack] Complete Django web application environment
  standalone-nodejs  [Stack] Complete Node.js application environment
```

### 9. Add Interactive Mode

Add `cli --interactive` that asks users:
1. What are you trying to deploy? (Web app, Database, Cache, etc.)
2. What technology? (Django, Node.js, Custom, etc.)
3. What components do you need? (Database, Cache, SSL, etc.)

Then suggest the appropriate command.

## Implementation Steps

1. Create alias mappings for backward compatibility
2. Update service descriptions in service_scanner.py
3. Reorganize the --list output with new categories
4. Add scope indicators to service listings
5. Update documentation with clearer explanations
6. Add interactive mode for beginners
7. Create a migration guide for the naming changes
8. Split existing recipes into distributed and standalone versions
9. Add connection parameter support to CLI operations
10. Implement dependency checking

## Benefits

This structure makes it crystal clear:
- What each service does
- Where it should be deployed
- What it depends on
- How services connect in a distributed architecture
- The difference between single-service and full-stack deployments