# Directory Structure

Detailed explanation of the Ansible Cloudy project structure.

## Project Root

```
ansible-cloudy/
├── .vault/                 # Sensitive credentials (git-ignored)
├── cloudy/                 # Core Ansible implementation
├── dev/                    # Development tools and utilities
├── docs/                   # Project documentation
├── test/                   # Test suites
├── .venv/                  # Python virtual environment
├── bootstrap.sh           # Environment setup script
├── README.md              # Project introduction
└── requirements.txt       # Python dependencies
```

## Core Ansible Directory (`/cloudy/`)

### Configuration Files

```
cloudy/
├── ansible.cfg            # Ansible runtime configuration
└── defaults/              # Default variable definitions
    ├── all.yml           # Global defaults
    ├── nginx.yml         # Nginx service defaults
    ├── nodejs.yml        # Node.js defaults
    ├── openvpn.yml       # OpenVPN defaults
    ├── pgbouncer.yml     # PgBouncer defaults
    ├── postgis.yml       # PostGIS defaults
    ├── postgresql.yml    # PostgreSQL defaults
    ├── redis.yml         # Redis defaults
    ├── security.yml      # Security defaults
    ├── system.yml        # System defaults
    └── vault.yml         # Vault variable defaults
```

### Inventory Files

```
cloudy/inventory/
├── dev.yml               # Development environment
├── prod.yml              # Production environment
├── ci.yml                # CI/CD environment
├── group_vars/           # Group-specific variables
│   ├── all.yml
│   ├── database_servers.yml
│   └── web_servers.yml
└── host_vars/            # Host-specific variables
    └── example.yml
```

### Playbooks and Recipes

```
cloudy/playbooks/recipes/
├── core/                 # Core system recipes
│   ├── base.yml         # Base system configuration
│   ├── security.yml     # Security setup
│   ├── security-production.yml
│   └── security-verify.yml
├── db/                   # Database recipes
│   ├── psql.yml         # PostgreSQL
│   ├── psql-production.yml
│   ├── postgis.yml      # PostGIS extension
│   └── pgvector.yml     # pgvector extension
├── cache/                # Caching recipes
│   ├── redis.yml
│   └── redis-production.yml
├── lb/                   # Load balancer recipes
│   ├── nginx.yml
│   └── nginx-production.yml
├── www/                  # Web application recipes
│   ├── django.yml       # Django deployment
│   └── nodejs.yml       # Node.js deployment
├── services/             # Additional services
│   └── pgbouncer.yml    # Connection pooling
├── vpn/                  # VPN services
│   └── openvpn.yml      # OpenVPN server
└── standalone/           # All-in-one deployments
    └── all-in-one.yml   # Complete stack
```

### Task Files

```
cloudy/tasks/
├── sys/                  # System operations
│   ├── core/            # Core system tasks
│   ├── ssh/             # SSH configuration
│   ├── firewall/        # Firewall management
│   ├── user/            # User management
│   ├── kernel/          # Kernel tuning
│   ├── swap/            # Swap configuration
│   ├── security/        # Security hardening
│   ├── audit/           # Audit logging
│   └── utilities/       # System utilities
├── db/                   # Database tasks
│   ├── postgresql/      # PostgreSQL operations
│   └── postgis/         # PostGIS operations
├── web/                  # Web server tasks
│   ├── nginx/           # Nginx configuration
│   ├── django/          # Django setup
│   ├── nodejs/          # Node.js setup
│   └── python/          # Python environment
├── services/             # Service tasks
│   ├── redis/           # Redis operations
│   ├── pgbouncer/       # PgBouncer setup
│   └── openvpn/         # OpenVPN management
├── cache/                # Cache-specific tasks
│   └── redis/           # Redis configuration
├── lb/                   # Load balancer tasks
│   └── nginx/           # Nginx LB config
└── monitoring/           # Monitoring setup
    └── setup-basic.yml  # Basic monitoring
```

### Templates

```
cloudy/templates/
├── nginx/                # Nginx configurations
├── postgresql/           # PostgreSQL configs
├── redis/                # Redis configurations
├── pgbouncer/           # PgBouncer configs
├── supervisor/          # Supervisor configs
└── systemd/             # Systemd service files
```

## Development Directory (`/dev/`)

### CLI

```
dev/cli/
├── cli/                  # CLI interface
│   ├── main.py          # Entry point
│   ├── argument_parser.py
│   ├── command_router.py
│   ├── dev_commands.py
│   └── help_system.py
├── operations/           # Service operations
│   ├── postgresql/      # PostgreSQL handler
│   ├── redis.py         # Redis handler
│   ├── nginx.py         # Nginx handler
│   ├── nodejs.py        # Node.js handler
│   ├── pgvector.py      # pgvector handler
│   ├── standalone.py    # Standalone handler
│   └── recipes.py       # Recipe handler
├── discovery/            # Auto-discovery
│   └── service_scanner.py
├── execution/            # Ansible execution
│   ├── ansible/         # Ansible wrappers
│   └── dependency_manager.py
├── utils/                # Utilities
│   ├── colors.py        # Terminal colors
│   ├── config.py        # Configuration
│   └── dev_tools/       # Development tools
└── tests/                # Unit tests
```

### Development Tools

```
dev/
├── validate.py           # Comprehensive validation
├── syntax-check.sh      # Quick syntax check
├── test-auth.yml        # Authentication test
├── .ansible-lint.yml    # Ansible lint config
├── .yamlint.yml         # YAML lint config
├── .flake8              # Python lint config
└── .cspell.json         # Spell check config
```

## Test Directory (`/test/`)

```
test/
├── e2e/                  # End-to-end tests
│   ├── docker-compose.yml
│   ├── Dockerfile.ubuntu
│   ├── Dockerfile.debian
│   ├── run-e2e-tests.sh
│   ├── scenarios/       # Test scenarios
│   ├── inventory/       # Test inventories
│   └── vault/           # Test credentials
└── ci/                   # CI/CD tests
    └── smoke-test.sh
```

## Documentation (`/docs/`)

```
docs/
├── README.md            # Documentation index
├── getting-started/     # New user guides
│   ├── quickstart.md
│   ├── installation.md
│   └── first-deployment.md
├── architecture/        # System design
│   ├── overview.md
│   ├── authentication-flow.md
│   └── directory-structure.md
├── development/         # Developer guides
│   ├── guide.md
│   ├── testing.md
│   ├── contributing.md
│   └── cli-cli.md
├── operations/          # User guides
│   ├── commands.md
│   ├── recipes.md
│   └── configuration.md
└── reference/           # Reference docs
    ├── variables.md
    ├── changelog.md
    └── troubleshooting.md
```

## Vault Directory (`/.vault/`)

```
.vault/
├── README.md            # Vault usage guide
├── dev.yml.example      # Development template
├── prod.yml.example     # Production template
├── ci.yml.example       # CI/CD template
└── *.yml                # Your vault files (git-ignored)
```

## File Naming Conventions

### Task Files
- **Action-based**: `install.yml`, `configure.yml`, `remove.yml`
- **Resource-based**: `create-user.yml`, `setup-firewall.yml`
- **Hyphenated**: Use hyphens, not underscores

### Variable Files
- **Service name**: `postgresql.yml`, `redis.yml`
- **Lowercase**: Always lowercase
- **Descriptive**: Clear purpose from filename

### Templates
- **Original name**: `nginx.conf.j2`, `postgresql.conf.j2`
- **Jinja2 extension**: Always use `.j2` suffix

## Best Practices

1. **Keep files small**: Target 100-200 lines per file
2. **Single responsibility**: Each file does one thing
3. **Clear naming**: File name describes content
4. **Consistent structure**: Follow existing patterns
5. **Document complex logic**: Add comments for clarity

## Adding New Components

### New Service
1. Create defaults: `/cloudy/defaults/myservice.yml`
2. Create tasks: `/cloudy/tasks/services/myservice/`
3. Create recipe: `/cloudy/playbooks/recipes/services/myservice.yml`
4. Add handler: `/dev/cli/operations/myservice.py`
5. Create templates: `/cloudy/templates/myservice/`

### New Feature
1. Identify category (sys, db, web, etc.)
2. Create task file in appropriate directory
3. Add to relevant recipe
4. Update documentation
5. Add tests

## Security Considerations

- **Never commit**: `.vault/` directory contents
- **Use vault**: All passwords in vault files
- **Git ignore**: Sensitive files and directories
- **Templates**: No hardcoded credentials
- **Defaults**: Safe, non-sensitive defaults only