# Ansible Cloudy - Development Tools & CLI Implementation

This directory contains the **Claudia CLI** implementation and essential development tools for **Ansible Cloudy**.

## 🏗️ Architecture Overview

The `dev/` directory houses two main components:

### **Claudia CLI Implementation** (`dev/claudia/`)
Sophisticated Python-based CLI with intelligent auto-discovery and universal parameter mapping.

### **Development Tools** (`dev/*.py`, `dev/*.sh`)
Comprehensive validation and testing tools for maintaining code quality.

## 🚀 Quick Start

```bash
# From the project root directory
cd ansible-cloudy/

# Setup development environment
./bootstrap.sh
source .venv/bin/activate

# Comprehensive validation
./claudia dev validate

# Quick syntax check
./claudia dev syntax

# Test authentication flow
./claudia dev test
```

## 🧠 Claudia CLI Implementation

### **Architecture Components**

#### **`claudia/cli/main.py`** - Command Router
- **Entry Point**: Main CLI coordinator and argument parser
- **Service Routing**: Dispatches commands to service-specific operations
- **Help System**: Coordinates context-aware help display
- **Development Integration**: Routes to dev tools for validation and testing

#### **`claudia/operations/`** - Service Operations
- **`base_service.py`**: Abstract base class for all service operations
- **`postgresql.py`**: PostgreSQL operations with 17+ granular commands
- **`redis.py`**: Redis configuration with memory, port, password management
- **`nginx.py`**: Nginx load balancer with domain and SSL management
- **`recipes.py`**: Recipe discovery and execution management

#### **`claudia/discovery/service_scanner.py`** - Auto-Discovery
- **Service Detection**: Scans filesystem for available services and operations
- **Dynamic Mapping**: Maps directory structure to CLI commands
- **Metadata Extraction**: Parses Claudia-Operation headers from task files
- **Help Generation**: Automatically generates help from discovered metadata

#### **`claudia/execution/ansible.py`** - Execution Engine
- **AnsibleRunner**: Executes Ansible automation with proper context
- **SmartSecurityRunner**: Handles intelligent server security and connection management
- **Task Execution**: Runs individual Ansible tasks for granular operations

#### **`claudia/utils/`** - Support Systems
- **`config.py`**: Project configuration and path management
- **`colors.py`**: Consistent terminal color output
- **`connection_manager.py`**: Smart connection detection and validation
- **`dev_tools.py`**: Development validation and testing tools

### **Key Features**

#### **Auto-Discovery System**
```python
# Services automatically discovered from filesystem
./claudia redis      # Found via cloudy/playbooks/recipes/cache/redis.yml
./claudia psql       # Found via cloudy/playbooks/recipes/db/psql.yml
./claudia nginx      # Found via cloudy/playbooks/recipes/lb/nginx.yml
```

#### **Universal Parameter Mapping**
```python
# Intuitive CLI parameters mapped to Ansible variables
./claudia redis --install --port 6380 --memory 512
# Becomes: redis_port=6380, redis_memory_mb=512

./claudia nginx --install --domain example.com --ssl
# Becomes: nginx_domain=example.com, nginx_ssl_enabled=true
```

#### **Granular Operations**
```python
# Service-specific operations without full recipe installation
./claudia psql --adduser myuser --password secret123
./claudia redis --configure-port 6379
./claudia nginx --setup-ssl example.com
```

## 🛠️ Development Tools

### **`./claudia dev validate`** - Comprehensive Validation Suite
**What it validates:**
- ✅ Project directory structure and organization
- ✅ YAML syntax for all playbooks, tasks, and inventory files
- ✅ Ansible configuration and template files
- ✅ Task file structure and recipe dependencies
- ✅ Service discovery and CLI integration
- ✅ Documentation consistency and spell checking

### **`./claudia dev syntax`** - Quick Syntax Validation
**What it checks:**
- ✅ Ansible playbook syntax for all recipes
- ✅ YAML structure validation
- ✅ Basic file accessibility and permissions

### **`./claudia dev test`** - Authentication Flow Testing
**What it tests:**
- ✅ Server connection validation
- ✅ Two-phase authentication workflow
- ✅ SSH key and password authentication
- ✅ Inventory configuration validation

### **`./claudia dev lint`** - Code Quality Validation
**What it analyzes:**
- ✅ Ansible-lint rules and best practices
- ✅ YAML formatting and style consistency
- ✅ Python code quality (for CLI implementation)

### **`./claudia dev spell`** - Documentation Spell Checking
**What it validates:**
- ✅ Documentation files (*.md) spell checking
- ✅ Technical dictionary with 480+ terms
- ✅ Consistent terminology across documentation

## 🔧 Development Workflow

### **Adding New Services**

To add a new service to Ansible Cloudy, follow this pattern:

#### 1. **Create Ansible Tasks** (`cloudy/tasks/`)
```bash
# Example: Adding MySQL support
cloudy/tasks/db/mysql/
├── install.yml
├── create-user.yml
├── create-database.yml
└── configure-port.yml
```

#### 2. **Create Service Recipe** (`cloudy/playbooks/recipes/`)
```yaml
# cloudy/playbooks/recipes/db/mysql.yml
- name: Deploy MySQL Database Server
  hosts: generic_servers
  become: true
  tasks:
    - include_tasks: ../../tasks/db/mysql/install.yml
```

#### 3. **Create CLI Operations** (`dev/claudia/operations/`)
```python
# dev/claudia/operations/mysql.py
class MySQLOperations(BaseServiceOperations):
    def get_parameter_mappings(self):
        return {
            '--port': 'mysql_port',
            '--root-password': 'mysql_root_password'
        }
```

#### 4. **Test Integration**
```bash
./claudia dev validate     # Validate all components
./claudia mysql            # Verify auto-discovery
./claudia mysql --help     # Check parameter mapping
```

### **Development Standards**

#### **Code Quality Requirements**
- **File Size**: Maximum 200 LOC per file (target 100 LOC)
- **Single Responsibility**: Each file handles one specific function
- **Documentation**: Clear docstrings and comments for complex logic
- **Error Handling**: Graceful failures with actionable error messages

#### **Testing Requirements**
- **Syntax Validation**: All files must pass syntax checks
- **Integration Testing**: Services must integrate properly with CLI
- **Documentation**: All new features must be documented
- **Backward Compatibility**: Changes must not break existing workflows

## 📋 Development Workflow Usage

### **Pre-Development Validation**
```bash
# Always validate before making changes
./claudia dev validate
```

### **During Development**
```bash
# Quick syntax checking while developing
./claudia dev syntax

# Test specific services
./claudia [service] --check  # Dry run validation
```

### **Pre-Commit Validation**
```bash
# Comprehensive validation before committing
./claudia dev validate
./claudia dev spell          # Documentation spell check
./claudia dev lint           # Code quality validation
```

### **CI/CD Integration**
```bash
# Bootstrap environment and run full validation
./bootstrap.sh -y && source .venv/bin/activate
./claudia dev syntax && ./claudia dev validate
```

## ⚙️ Configuration Files

Development tools are configured via:

- **`dev/.cspell.json`** - Spell checking with 480+ technical terms
- **`dev/.ansible-lint.yml`** - Ansible linting rules and best practices
- **`dev/.yamlint.yml`** - YAML formatting and syntax standards

## 🔧 Environment Requirements

### **Recommended Setup**
```bash
# Use bootstrap for complete environment
./bootstrap.sh
source .venv/bin/activate
```

**Provides:**
- Python 3.11+ virtual environment
- Ansible 6.0+ with all required modules
- Development tools (ansible-lint, yamllint, flake8)
- Spell checking tools with technical dictionary

### **Manual Requirements**
- **Python 3.8+** for CLI implementation
- **Ansible 2.9+** for automation execution
- **PyYAML, jsonschema, passlib** for Python dependencies

## 🚨 Troubleshooting

### **Environment Issues**
```bash
# "Command not found" errors
source .venv/bin/activate

# Missing dependencies
./bootstrap.sh

# Permission issues
chmod +x claudia dev/*.py dev/*.sh
```

### **Validation Failures**
```bash
# Syntax errors in recipes
./claudia dev syntax

# YAML formatting issues
./claudia dev lint

# Missing or incorrect file structure
./claudia dev validate
```

### **CLI Development Issues**
```bash
# Service not discovered
./claudia --list-services

# Parameter mapping not working
./claudia [service] --help

# Connection validation failing
./claudia dev test
```

## 🎯 Best Practices

### **Development Workflow**
1. **Environment Setup**: Use `./bootstrap.sh` for consistent development environment
2. **Validation First**: Run `./claudia dev validate` before making changes
3. **Incremental Testing**: Use `./claudia dev syntax` for quick feedback during development
4. **Documentation**: Update documentation for all new features and services
5. **Integration Testing**: Verify CLI integration with `./claudia [service] --help`

### **Code Quality**
- Keep all files under 200 LOC for maintainability
- Follow single responsibility principle for all modules
- Use consistent error handling and user-friendly messages
- Document all CLI parameters and operations in service classes