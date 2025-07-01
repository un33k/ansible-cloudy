# Contributing to Ansible Cloudy

Welcome to **Ansible Cloudy**! This guide will help you contribute effectively to our intelligent infrastructure automation project featuring the **Claudia CLI**.

## 🚀 Quick Start for Contributors

### Prerequisites

```bash
# Clone the repository
git clone <repository-url>
cd ansible-cloudy/

# Bootstrap environment (Recommended) - Sets up .venv with all development tools
./bootstrap.sh
source .venv/bin/activate

# Verify installation
cli dev syntax
```

**What bootstrap.sh provides:**
- Python virtual environment with proper isolation
- Ansible and all linting tools (ansible-lint, yamllint, flake8)
- Development dependencies (PyYAML, jsonschema, etc.)
- Spell checking tools with technical dictionary

### Development Workflow

1. **Understand the Architecture**: Familiarize yourself with the Claudia CLI system
   ```bash
   cli --help                    # View all available services
   cli security                  # View service-specific help
   cli dev                       # View development commands
   ```

2. **Run Pre-Development Validation**: Always validate before making changes
   ```bash
   cli dev syntax               # Quick syntax check
   cli dev validate             # Comprehensive validation suite
   cli dev spell                # Spell check documentation
   ```

3. **Make Changes**: Follow project architecture and conventions
   - **Ansible Tasks**: Add to `cloudy/tasks/` with single responsibility
   - **Service Operations**: Add to `dev/claudia/operations/` for CLI functionality
   - **Recipes**: Add to `cloudy/playbooks/recipes/` for high-level workflows
   - **Documentation**: Update relevant .md files

4. **Test Changes**: Comprehensive validation
   ```bash
   cli dev syntax               # Quick syntax validation
   cli dev validate             # Full validation suite
   cli dev lint                 # Ansible linting (if available)
   cli dev test                 # Authentication flow testing
   cli [service] --check        # Dry run specific services
   ```

5. **Commit Changes**: Follow semantic commit conventions
   ```bash
   git add .
   git commit -m "feat: add Redis password configuration support"
   git push
   ```

### Pre-commit Validation

Before committing, run the development tools:

```bash
# Quick validation (recommended)
cli dev syntax

# Full validation (comprehensive)
cli dev validate
cli dev spell
cli dev lint      # If ansible-lint installed
```

### Running GitHub Actions Locally

You can run the same tests that GitHub Actions runs using **act**:

```bash
# Install act (requires Docker)
brew install act              # macOS
# or download from: https://github.com/nektos/act

# Start Docker first
open -a Docker               # macOS
sudo systemctl start docker  # Linux

# Run the workflow locally
act -W .github/workflows/test.yml

# Run with verbose output
act -W .github/workflows/test.yml -v

# List available workflows
act -l
```

**Requirements:**
- **Docker must be installed and running** for act to work
- Act runs workflows in Docker containers to simulate GitHub's environment

**Alternative (no Docker required):**
Run the workflow steps manually:
```bash
# This runs the same validation as GitHub Actions
./bootstrap.sh -y && source .venv/bin/activate
cli dev syntax
cli dev lint
cli dev validate
cli dev test -- --syntax-check
cli security --check
cli django --check
```

### Testing Changes

Test your recipes safely with check mode:

```bash
# Test specific recipes (dry run)
cli security --check    # Test security recipe
cli django --check      # Test django recipe

# Test authentication flow
cli dev test
```

## 📁 Project Architecture

Understanding the Ansible Cloudy architecture is crucial for effective contributions:

### Core Components

```
ansible-cloudy/
├── cli                    # Main CLI entry point (bash wrapper)
├── bootstrap.sh              # Development environment setup
├── cloudy/                   # Ansible automation core
│   ├── playbooks/recipes/    # High-level service deployment
│   ├── tasks/                # Granular, reusable Ansible tasks
│   ├── templates/            # Jinja2 configuration templates
│   ├── inventory/            # Server inventory configurations
│   └── ansible.cfg           # Ansible configuration
├── dev/                      # Development tools and CLI implementation
│   ├── claudia/             # Python CLI implementation
│   │   ├── cli/             # Command parsing and routing
│   │   ├── operations/      # Service-specific operations
│   │   ├── discovery/       # Auto-discovery system
│   │   ├── execution/       # Ansible execution engine
│   │   └── utils/           # Configuration and utilities
│   └── validate.py          # Development validation tools
└── docs/                    # Project documentation
    ├── CONTRIBUTING.md      # Development guidelines
    ├── USAGE.md            # Complete usage guide
    ├── IMPLEMENTATION_PLAN.md  # Technical implementation details
    └── DEVELOPMENT.md      # Development tools and CLI implementation guide
```

### Key Architecture Principles

1. **Auto-Discovery**: Services are automatically discovered from filesystem structure
2. **Universal Parameters**: CLI parameters map intuitively to Ansible variables
3. **Modular Design**: Each component has single responsibility, files under 200 LOC
4. **Layered Architecture**: CLI → Operations → Discovery → Execution
5. **Smart Security**: Two-phase authentication with connection validation

## 🎯 Contribution Guidelines

### Adding New Services

When adding a new service to Ansible Cloudy, follow this systematic approach:

#### 1. Ansible Tasks (Backend Logic)
Create granular task files in `cloudy/tasks/`:
```bash
# Example: Adding MySQL support
cloudy/tasks/db/mysql/
├── install.yml              # Main installation
├── create-user.yml          # User management
├── create-database.yml      # Database management
├── set-root-password.yml    # Security configuration
└── configure-port.yml       # Port configuration
```

#### 2. Service Recipe (High-Level Workflow)
Create recipe in `cloudy/playbooks/recipes/`:
```yaml
# cloudy/playbooks/recipes/db/mysql.yml
---
- name: Deploy MySQL Database Server
  hosts: generic_servers
  become: true
  
  tasks:
    - include_tasks: ../../tasks/db/mysql/install.yml
    - include_tasks: ../../tasks/db/mysql/set-root-password.yml
    - include_tasks: ../../tasks/sys/firewall/allow-port.yml
      vars:
        port: "{{ mysql_port | default(3306) }}"
```

#### 3. CLI Operations (Frontend Interface)
Create operations class in `dev/claudia/operations/`:
```python
# dev/claudia/operations/mysql.py
class MySQLOperations(BaseServiceOperations):
    def __init__(self):
        super().__init__("mysql", "db")
        
    def get_parameter_mappings(self):
        return {
            '--port': 'mysql_port',
            '--root-password': 'mysql_root_password',
            '--memory': 'mysql_memory_mb'
        }
    
    def get_supported_operations(self):
        return ['install', 'adduser', 'adddb', 'configure-port']
```

### Task File Standards

**✅ Best Practices:**
- Single responsibility per task file
- Descriptive task names explaining purpose
- Proper error handling with `register` and `when`
- Use variables instead of hardcoded values
- Include Claudia-Operation headers for auto-discovery
- Keep files under 200 LOC

**Example Task with Claudia Integration:**
```yaml
---
# Claudia-Operation: configure-port
# Claudia-Description: Change MySQL port configuration
# Claudia-Parameters: --port (required)

- name: Update MySQL port configuration
  lineinfile:
    path: /etc/mysql/mysql.conf.d/mysqld.cnf
    regexp: '^port\s*='
    line: "port = {{ mysql_port }}"
    backup: true
  register: mysql_port_config
  
- name: Restart MySQL to apply port change
  systemd:
    name: mysql
    state: restarted
  when: mysql_port_config is changed
  
- name: Verify MySQL is running on new port
  wait_for:
    port: "{{ mysql_port }}"
    timeout: 30
```

### Recipe Files

**✅ DO:**
- Compose recipes from existing tasks when possible
- Include comprehensive pre_tasks and post_tasks sections
- Use meaningful variable names and defaults
- Provide clear documentation in comments
- Include tags for selective execution

**❌ DON'T:**
- Duplicate task logic in recipes
- Use deprecated `include` statements (use `include_tasks`)
- Skip variable validation
- Create recipes without proper error handling

**Example Recipe Structure:**
```yaml
---
- name: Example Server Setup Recipe
  hosts: example_servers
  gather_facts: true
  become: true
  
  vars:
    setup_firewall: true
    setup_ssl: false
    
  pre_tasks:
    - name: Display setup information
      debug:
        msg: |
          🚀 Starting Example Server Setup
          Target: {{ inventory_hostname }}
          
  tasks:
    - name: Include foundation tasks
      include_tasks: ../../tasks/sys/core/init.yml
      tags: [foundation]
      
  post_tasks:
    - name: Display completion summary
      debug:
        msg: "🎉 ✅ Example server setup completed!"
```

### Inventory Configuration

**✅ DO:**
- Use descriptive group names
- Provide sensible defaults in group_vars
- Document required variables
- Use consistent naming conventions

**Example Inventory:**
```yaml
all:
  vars:
    ansible_user: admin
    ansible_port: 22022
    
  children:
    web_servers:
      hosts:
        web1:
          ansible_host: 10.0.1.10
          domain_name: app.example.com
```

## 🧪 Testing

### Running Tests

```bash
# Full test suite via Claudia CLI
cli dev validate

# Individual validations
cli dev syntax
cli dev lint
```

### Test Categories

1. **Syntax Validation**: YAML and Ansible syntax checks
2. **Dependency Validation**: Ensure all included tasks exist
3. **Structure Validation**: Verify proper file organization
4. **Inventory Validation**: Check inventory configuration
5. **Template Validation**: Validate Jinja2 templates

### Adding New Tests

When adding new functionality:

1. Add test cases to `test-runner.sh`
2. Update `create-missing-tasks.sh` if adding new dependencies
3. Include example usage in documentation
4. Test in check mode before implementation

## 🔧 Development Tools

### Useful Scripts

- `./test-runner.sh` - Comprehensive test suite
- `./create-missing-tasks.sh` - Create missing task dependencies
- `./validate-yaml.py` - YAML structure validation

### IDE Configuration

**VS Code Extensions:**
- Ansible (Red Hat)
- YAML (Red Hat)
- Jinja (wholroyd)

**Settings:**
```json
{
  "ansible.python.interpreterPath": "/usr/bin/python3",
  "yaml.schemas": {
    "https://raw.githubusercontent.com/ansible/ansible/devel/lib/ansible/modules/": "*.yml"
  }
}
```

## 📝 Documentation Standards

### Task Documentation

```yaml
# Task Purpose and Context
# Based on: original-implementation-reference (if applicable)
# Usage: include_tasks: path/to/task.yml

---
- name: Clear, descriptive task name
  module:
    parameter: value
```

### Recipe Documentation

```yaml
# Recipe: Purpose and Scope
# Based on: original-implementation-reference (if applicable)
# Usage: cli [service] --install

---
- name: Descriptive Recipe Name
  hosts: target_group
```

## 🚦 Code Review Process

### Before Submitting

1. ✅ All tests pass (`./test-runner.sh`)
2. ✅ Code follows project conventions
3. ✅ Documentation is updated
4. ✅ No hardcoded values or secrets
5. ✅ Error handling is implemented

### Review Checklist

- [ ] Task files follow single responsibility principle
- [ ] Recipes compose existing tasks appropriately
- [ ] Variables are properly defined and documented
- [ ] Error handling covers failure scenarios
- [ ] Tests validate the new functionality
- [ ] Documentation explains usage and purpose

## 🐛 Troubleshooting

### Common Issues

**Syntax Errors:**
```bash
# Check YAML syntax and Ansible validation
cli dev syntax

# Comprehensive validation
cli dev validate
```

**Missing Dependencies:**
```bash
# Auto-create missing task files
./create-missing-tasks.sh
```

**Inventory Issues:**
```bash
# Validate inventory
ansible-inventory -i inventory/file.yml --list
```

### Getting Help

1. Check existing documentation in `USAGE.md` and `CLAUDE.md`
2. Run the test suite to identify specific issues
3. Review similar implementations in the codebase
4. Open an issue with detailed error information

## 🎉 Recognition

Contributors who follow these guidelines and make meaningful improvements will be recognized in:

- Project README
- Release notes
- Contributor documentation

Thank you for helping make Ansible Cloudy an amazing infrastructure automation tool! 🚀