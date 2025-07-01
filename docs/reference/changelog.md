# Changelog

All notable changes to Ansible Cloudy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-01

### Added

#### New Deployment Flavors
- **PostgreSQL with pgvector** - AI/ML ready database with vector embeddings support
  - Support for up to 16,000 dimensions
  - IVFFlat and HNSW index types
  - Example schemas and usage documentation
  - CLI: `cli pgvector --install --dimensions 1536`

- **Node.js Application Deployment** - Full-featured Node.js application hosting
  - PM2 process management with cluster mode
  - Zero-downtime deployments
  - Automatic restarts and memory limits
  - Nginx reverse proxy integration
  - CLI: `cli nodejs --install --app-repo <url> --pm2-instances 4`

- **Standalone All-in-One Server** - Complete stack on single server
  - Combines PostgreSQL, Redis, Nginx, and application layer
  - Supports both Django and Node.js applications
  - Automatic resource optimization based on available RAM
  - CLI: `cli standalone --install --app-type django --domain example.com`

- **PgBouncer Connection Pooling** - Database optimization
  - Transaction pooling for web applications
  - Distributed architecture (runs on web servers)
  - Configurable ports and pool sizes
  - CLI: `cli pgbouncer --install --pool-size 30`

#### Production Hardening
- **Kernel Security** - Comprehensive sysctl hardening
  - ASLR (Address Space Layout Randomization) enabled
  - Secure shared memory configuration
  - Network stack hardening
  - SYN flood protection

- **SSH Hardening** - Enterprise-grade SSH security
  - Modern cipher suites only
  - Rate limiting and connection throttling
  - Disabled weak protocols
  - Failed authentication tracking

- **Audit Logging** - Complete audit trail
  - auditd configuration for security events
  - Automatic log rotation
  - Centralized logging support

- **DDoS Protection** - Built-in protection mechanisms
  - Nginx rate limiting zones
  - Connection throttling
  - Request size limits
  - Slow request protection

- **Automatic Security Updates** - Unattended upgrades
  - Security patches automatically applied
  - Configurable maintenance windows
  - Smart reboot scheduling

#### Enhanced Services
- **PostgreSQL Production Configuration**
  - Dynamic memory tuning based on available RAM
  - Optimized connection settings
  - Automated backup scripts
  - WAL archiving configuration

- **Redis Production Setup**
  - Persistence enabled (AOF + RDB)
  - Memory limits and eviction policies
  - Security hardening (rename dangerous commands)
  - Backup automation

- **Nginx Production Features**
  - Security headers (HSTS, X-Frame-Options, etc.)
  - Gzip compression optimization
  - Static file caching
  - Health check endpoints

### Enhanced
- **Claudia CLI Auto-discovery** - Improved service detection
  - Automatic recognition of new services
  - Operation discovery from task files
  - Intelligent parameter mapping

- **Resource-aware Configuration** - Smart defaults
  - Memory allocation based on system RAM
  - CPU-aware worker processes
  - Disk space monitoring

### Security
- **Two-phase Authentication Model** - Enhanced security flow
  - Phase 1: Root + password for initial setup
  - Phase 2: Root + SSH keys for all operations
  - Optional admin user only for service processes

### Documentation
- Comprehensive production deployment guides
- Security best practices documentation
- Performance tuning guidelines
- Troubleshooting guides for all services

## [1.0.0] - 2024-12-15

### Initial Release
- Core infrastructure automation with Claudia CLI
- Basic service deployments (PostgreSQL, Redis, Nginx, Django)
- Two-phase security model
- Auto-discovery of services and operations
- Universal parameter support
- Granular operations for service management