# Ansible Cloudy Architecture

## Overview

Ansible Cloudy is a layered infrastructure automation framework built on top of Ansible. It provides a production-ready, secure, and modular approach to server deployment and management.

## Architecture Layers

```
┌─────────────────────────────────────────┐
│          Claudia CLI Interface          │  User Interface Layer
├─────────────────────────────────────────┤
│         Service Operations              │  Business Logic Layer
├─────────────────────────────────────────┤
│          Recipe Playbooks               │  Orchestration Layer
├─────────────────────────────────────────┤
│         Modular Task Files              │  Task Layer
├─────────────────────────────────────────┤
│        Templates & Defaults             │  Configuration Layer
├─────────────────────────────────────────┤
│           Ansible Core                  │  Execution Layer
└─────────────────────────────────────────┘
```

## Component Architecture

### 1. Claudia CLI (`/dev/claudia/`)

The intelligent command-line interface that provides:
- **Auto-discovery**: Automatically finds available services and operations
- **Smart routing**: Routes commands to appropriate handlers
- **Parameter mapping**: Converts user-friendly parameters to Ansible variables
- **Help system**: Context-aware help for all commands
- **Validation**: Pre-flight checks before execution

### 2. Service Operations (`/dev/claudia/operations/`)

Service-specific logic for:
- **PostgreSQL**: Database operations, user management, backups
- **Redis**: Cache configuration, memory management
- **Nginx**: Load balancer setup, SSL configuration
- **Node.js**: PM2 process management
- **Standalone**: All-in-one server deployments

### 3. Recipe Playbooks (`/cloudy/playbooks/recipes/`)

High-level orchestration playbooks organized by category:
- **core/**: Security and base system setup
- **db/**: Database deployments (PostgreSQL, PostGIS, pgvector)
- **cache/**: Caching solutions (Redis)
- **lb/**: Load balancers (Nginx)
- **www/**: Web applications (Django, Node.js)
- **services/**: Additional services (PgBouncer, OpenVPN)

### 4. Modular Tasks (`/cloudy/tasks/`)

Atomic, reusable task files:
- **sys/**: System operations (users, SSH, firewall)
- **db/**: Database management tasks
- **web/**: Web server configuration
- **services/**: Service-specific tasks
- **monitoring/**: Monitoring setup

### 5. Configuration Layer

- **Defaults** (`/cloudy/defaults/`): Default values for all variables
- **Templates** (`/cloudy/templates/`): Jinja2 templates for configuration files
- **Inventory** (`/cloudy/inventory/`): Server definitions and groupings
- **Vault** (`/.vault/`): Sensitive credentials and overrides

## Key Design Principles

### 1. Two-Phase Authentication

```
Phase 1: Initial Setup (Root + Password)
├── Connect as root with password
├── Install SSH keys
├── Configure firewall
└── Optionally create grunt user

Phase 2: All Operations (Root + SSH Keys)
├── Connect as root with SSH keys
├── No passwords in automation
├── Full system access
└── Secure by default
```

### 2. Modular Design

Each component is:
- **Self-contained**: Can be used independently
- **Idempotent**: Safe to run multiple times
- **Parameterized**: Highly configurable
- **Validated**: Input checking and error handling

### 3. Configuration Hierarchy

```
1. Command-line parameters (highest priority)
2. Vault variables
3. Inventory variables
4. Default values (lowest priority)
```

### 4. Security First

- SSH key authentication for all operations
- Firewall configured before network changes
- Passwords never stored in code
- Audit logging and monitoring

## Data Flow

```
User Command → Claudia CLI → Argument Parser → Service Handler
                                                      ↓
Ansible Core ← Recipe Playbook ← Task Selection ← Operation Logic
      ↓
Target Server ← SSH Connection ← Execution
      ↓
Results → User Feedback
```

## Directory Structure

```
ansible-cloudy/
├── .vault/                 # Sensitive credentials
├── cloudy/                 # Ansible implementation
│   ├── ansible.cfg        # Ansible configuration
│   ├── defaults/          # Default variables
│   ├── inventory/         # Server inventories
│   ├── playbooks/         # Recipe playbooks
│   ├── tasks/             # Modular tasks
│   └── templates/         # Config templates
├── dev/                    # Development tools
│   ├── claudia/           # CLI implementation
│   └── validate.py        # Validation tools
├── docs/                   # Documentation
├── test/                   # Test suites
└── bootstrap.sh           # Setup script
```

## Extension Points

### Adding New Services

1. Create service tasks in `/cloudy/tasks/[category]/[service]/`
2. Add recipe playbook in `/cloudy/playbooks/recipes/[category]/`
3. Create operation handler in `/dev/claudia/operations/`
4. Add defaults in `/cloudy/defaults/[service].yml`

### Custom Deployments

1. Use existing tasks as building blocks
2. Create custom recipes combining tasks
3. Override variables in vault files
4. Use tags for selective execution

## Performance Considerations

- **Parallel execution**: Multiple tasks run concurrently
- **Connection reuse**: SSH connections are persistent
- **Fact caching**: System facts cached between runs
- **Conditional execution**: Skip unnecessary tasks

## Security Architecture

- **Defense in depth**: Multiple security layers
- **Principle of least privilege**: Minimal permissions
- **Audit trail**: All actions logged
- **Encrypted communication**: SSH for all connections
- **No hardcoded secrets**: All credentials in vault

## Next Steps

- Learn about the [Authentication Flow](authentication-flow.md)
- Understand the [Directory Structure](directory-structure.md)
- Explore [Development Guide](../development/guide.md)