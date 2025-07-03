# CLI Development Guide

Guide for extending and developing the CLI.

## Architecture Overview

The CLI is built with modularity and extensibility in mind:

```
User Input → Argument Parser → Command Router → Service Handler → Ansible Execution
                                                       ↓
                                              Operation Parameters
                                                       ↓
                                              Recipe/Task Selection
```

## Directory Structure

```
dev/cli/
├── cmd/                    # CLI interface layer
│   ├── main.py            # Entry point
│   ├── argument_parser.py # Command-line parsing
│   ├── command_router.py  # Routes to handlers
│   ├── dev_commands.py    # Development commands
│   └── help_system.py     # Help formatting
├── operations/            # Service handlers
│   ├── postgresql/        # PostgreSQL operations
│   ├── redis.py          # Redis operations
│   ├── nginx.py          # Nginx operations
│   └── recipes.py        # Generic recipe handler
├── discovery/             # Auto-discovery system
│   └── service_scanner.py # Finds services/operations
├── execution/             # Ansible execution layer
│   ├── ansible/          # Ansible wrappers
│   │   ├── runner.py     # Playbook execution
│   │   ├── port_manager.py # SSH port detection
│   │   └── vault_loader.py # Vault file handling
│   └── dependency_manager.py # Task dependencies
├── utils/                 # Shared utilities
│   ├── colors.py         # Terminal colors
│   ├── config.py         # Configuration management
│   └── dev_tools/        # Development utilities
└── tests/                # Unit tests
```

## Adding a New Service

### Step 1: Create the Operation Handler

Create `operations/myservice.py`:

```python
"""MyService operations handler"""

import sys
from pathlib import Path
from typing import List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.colors import Colors, info, error
from execution.ansible import AnsibleRunner
from .base import BaseOperation


class MyServiceOperations(BaseOperation):
    """Handle MyService operations"""
    
    def __init__(self, config):
        super().__init__(config)
        self.service_name = "myservice"
        self.recipe_category = "services"
    
    def handle_operation(self, args, ansible_args: List[str]) -> int:
        """Handle MyService operations"""
        
        # Handle help
        if hasattr(args, 'help') and args.help:
            self._show_service_help()
            return 0
        
        # Handle granular operations
        if hasattr(args, 'add_user') and args.add_user:
            return self._handle_add_user(args, ansible_args)
        
        # Handle installation
        if hasattr(args, 'install') and args.install:
            return self._handle_install(args, ansible_args)
        
        # Default: show help
        self._show_service_help()
        return 0
    
    def _handle_install(self, args, ansible_args: List[str]) -> int:
        """Handle service installation"""
        info("Installing MyService...")
        
        # Build parameters
        extra_vars = {}
        
        # Add service-specific parameters
        if hasattr(args, 'port') and args.port:
            extra_vars['myservice_port'] = args.port
        
        if hasattr(args, 'memory') and args.memory:
            extra_vars['myservice_memory_mb'] = args.memory
        
        # Run the playbook
        runner = AnsibleRunner(self.config)
        return runner.run_playbook(
            playbook_name=f"{self.recipe_category}/myservice",
            extra_vars=extra_vars,
            ansible_args=ansible_args,
            args=args
        )
    
    def _handle_add_user(self, args, ansible_args: List[str]) -> int:
        """Handle adding a user"""
        if not args.add_user or not args.password:
            error("Username and password required")
            return 1
        
        extra_vars = {
            'myservice_operation': 'add_user',
            'myservice_username': args.add_user,
            'myservice_password': args.password
        }
        
        # Run specific task
        runner = AnsibleRunner(self.config)
        return runner.run_task(
            task_file="services/myservice/add-user.yml",
            extra_vars=extra_vars,
            ansible_args=ansible_args,
            args=args
        )
    
    def _show_service_help(self):
        """Show MyService help"""
        print(f"""
{Colors.CYAN}MyService - Service Description{Colors.NC}

{Colors.YELLOW}USAGE:{Colors.NC}
    cli myservice [OPTIONS]
    cli myservice --install [OPTIONS]

{Colors.YELLOW}INSTALLATION OPTIONS:{Colors.NC}
    --port PORT          Service port (default: 8080)
    --memory MB          Memory limit in MB (default: 512)
    --enable-ssl         Enable SSL/TLS
    --config FILE        Custom config file

{Colors.YELLOW}OPERATIONS:{Colors.NC}
    --add-user USER      Add a new user
    --remove-user USER   Remove a user
    --list-users         List all users
    
{Colors.YELLOW}COMMON OPTIONS:{Colors.NC}
    --check              Dry run mode
    -v, --verbose        Verbose output
    -h, --help           Show this help

{Colors.YELLOW}EXAMPLES:{Colors.NC}
    # Install with defaults
    cli myservice --install
    
    # Install with custom port
    cli myservice --install --port 8090
    
    # Add a user
    cli myservice --add-user john --password secret123
    
    # List users
    cli myservice --list-users

{Colors.YELLOW}ENVIRONMENT VARIABLES:{Colors.NC}
    vault_myservice_port         Override default port
    vault_myservice_memory_mb    Override memory limit
    vault_myservice_password     Service password
""")
```

### Step 2: Register in Command Router

Edit `cli/command_router.py`:

```python
# Add to imports
from operations.myservice import MyServiceOperations

# Add to handle_service_operation method
elif service_name == "myservice":
    myservice_ops = MyServiceOperations(config)
    exit_code = myservice_ops.handle_operation(args, ansible_args)
    sys.exit(exit_code)
```

### Step 3: Add Argument Parsing

Edit `operations/myservice.py` to add argument parsing:

```python
@staticmethod
def add_arguments(parser):
    """Add MyService-specific arguments"""
    
    # Installation
    parser.add_argument(
        "--install", "--run",
        action="store_true",
        help="Install MyService"
    )
    
    # Service options
    parser.add_argument(
        "--port",
        type=int,
        help="Service port (default: 8080)"
    )
    
    parser.add_argument(
        "--memory",
        type=int,
        help="Memory limit in MB (default: 512)"
    )
    
    parser.add_argument(
        "--enable-ssl",
        action="store_true",
        help="Enable SSL/TLS"
    )
    
    # Operations
    parser.add_argument(
        "--add-user",
        metavar="USERNAME",
        help="Add a new user"
    )
    
    parser.add_argument(
        "--password",
        help="Password for user operations"
    )
    
    parser.add_argument(
        "--remove-user",
        metavar="USERNAME",
        help="Remove a user"
    )
    
    parser.add_argument(
        "--list-users",
        action="store_true",
        help="List all users"
    )
```

### Step 4: Create Ansible Components

Create the recipe in `cloudy/playbooks/recipes/services/myservice.yml`:

```yaml
---
# Recipe: MyService
# Purpose: Install and configure MyService
# Usage: cli myservice --install

- name: MyService Setup
  hosts: service_targets
  gather_facts: true
  become: true
  
  vars_files:
    - "../../../defaults/all.yml"
    - "../../../defaults/myservice.yml"
  
  vars:
    task_paths: "../../../tasks"
  
  pre_tasks:
    - name: Ensure secure connection
      include_tasks: "{{ task_paths }}/sys/core/ensure-secure-connection.yml"
      tags: [always]
  
  tasks:
    - name: Install MyService
      include_tasks: "{{ task_paths }}/services/myservice/install.yml"
      tags: [install]
    
    - name: Configure MyService
      include_tasks: "{{ task_paths }}/services/myservice/configure.yml"
      tags: [configure]
    
    - name: Start MyService
      include_tasks: "{{ task_paths }}/services/myservice/start.yml"
      tags: [start]
```

Create task files in `cloudy/tasks/services/myservice/`:
- `install.yml` - Installation tasks
- `configure.yml` - Configuration tasks  
- `add-user.yml` - User management
- `start.yml` - Service startup

Create defaults in `cloudy/defaults/myservice.yml`:

```yaml
---
# MyService defaults

# Service configuration
myservice_port_default: 8080
myservice_memory_mb_default: 512
myservice_user_default: "myservice"
myservice_group_default: "myservice"

# Paths
myservice_home_default: "/opt/myservice"
myservice_config_dir_default: "/etc/myservice"
myservice_log_dir_default: "/var/log/myservice"
myservice_data_dir_default: "/var/lib/myservice"

# Service settings
myservice_enable_ssl_default: false
myservice_max_connections_default: 100
myservice_timeout_default: 30
```

## Auto-Discovery System

The auto-discovery system automatically finds services and operations.

### How It Works

1. **Service Discovery**: Scans `/cloudy/playbooks/recipes/` for services
2. **Operation Discovery**: Scans task files for operations
3. **Metadata Parsing**: Reads headers for documentation

### Adding Discovery Metadata

In your task files, add headers:

```yaml
---
# Operation: Add User
# Purpose: Add a new user to MyService
# Usage: cli myservice --add-user USERNAME --password PASSWORD
# Parameters:
#   - myservice_username: Username to create (required)
#   - myservice_password: User password (required)
#   - myservice_role: User role (optional, default: user)
```

The scanner will automatically pick this up and make it available.

## Testing Your Service

### Unit Tests

Create `tests/test_myservice.py`:

```python
"""Test MyService operations"""

import pytest
from unittest.mock import Mock, patch
from operations.myservice import MyServiceOperations


class TestMyServiceOperations:
    """Test MyService operations"""
    
    def test_handle_install(self):
        """Test installation handling"""
        config = Mock()
        ops = MyServiceOperations(config)
        
        args = Mock()
        args.install = True
        args.port = 8090
        args.memory = 1024
        
        with patch('operations.myservice.AnsibleRunner') as mock_runner:
            mock_runner.return_value.run_playbook.return_value = 0
            
            result = ops.handle_operation(args, [])
            
            assert result == 0
            mock_runner.return_value.run_playbook.assert_called_once()
    
    def test_handle_add_user(self):
        """Test user addition"""
        config = Mock()
        ops = MyServiceOperations(config)
        
        args = Mock()
        args.install = False
        args.add_user = "testuser"
        args.password = "testpass"
        
        with patch('operations.myservice.AnsibleRunner') as mock_runner:
            mock_runner.return_value.run_task.return_value = 0
            
            result = ops.handle_operation(args, [])
            
            assert result == 0
```

### Integration Tests

Add to `test/e2e/scenarios/`:

```bash
#!/bin/bash
# Test MyService deployment

source "$(dirname "$0")/common.sh"

test_myservice_deployment() {
    log_info "Testing MyService deployment"
    
    # Install MyService
    run_cli "myservice" "--install" "--port" "8090"
    
    # Verify installation
    verify_service_running "myservice"
    verify_port_open 8090
    
    # Test operations
    run_cli "myservice" "--add-user" "testuser" "--password" "testpass"
    run_cli "myservice" "--list-users"
}

# Run tests
test_myservice_deployment
```

## Best Practices

### Code Organization

1. **Single Responsibility**: Each method does one thing
2. **Consistent Naming**: Follow existing patterns
3. **Error Handling**: Always handle failures gracefully
4. **Logging**: Use info() and error() for user feedback
5. **Documentation**: Add docstrings and comments

### Parameter Handling

```python
# Always validate required parameters
if not args.username:
    error("Username is required")
    return 1

# Use hasattr for optional parameters
if hasattr(args, 'port') and args.port:
    extra_vars['port'] = args.port

# Provide sensible defaults
port = getattr(args, 'port', 8080)
```

### Error Messages

```python
# Be specific and helpful
error(f"Port {args.port} is already in use. Try a different port.")

# Suggest solutions
error("Database connection failed. Check your credentials in vault file.")

# Use colors appropriately
info(f"{Colors.GREEN}✓{Colors.NC} Service installed successfully")
error(f"{Colors.RED}✗{Colors.NC} Installation failed")
```

## Advanced Features

### Custom Argument Types

```python
def port_type(value):
    """Validate port number"""
    ivalue = int(value)
    if ivalue < 1 or ivalue > 65535:
        raise argparse.ArgumentTypeError(
            f"Port must be between 1 and 65535"
        )
    return ivalue

parser.add_argument("--port", type=port_type)
```

### Dynamic Help

```python
def _show_dynamic_help(self):
    """Show help with discovered operations"""
    operations = self._discover_operations()
    
    print(f"{Colors.YELLOW}AVAILABLE OPERATIONS:{Colors.NC}")
    for op in operations:
        print(f"    --{op['name']:<20} {op['description']}")
```

### Progress Indicators

```python
from utils.progress import ProgressBar

def _handle_long_operation(self):
    """Handle operation with progress"""
    tasks = ["Installing", "Configuring", "Starting"]
    
    with ProgressBar(total=len(tasks)) as pb:
        for task in tasks:
            pb.update(task)
            # Do actual work
            time.sleep(1)
```

## Debugging

### Debug Mode

```python
# Add debug logging
if self.config.debug_mode:
    print(f"DEBUG: Running with vars: {extra_vars}")

# Use verbose flag
if args.verbose:
    ansible_args.append("-v")
```

### Testing Locally

```bash
# Run directly without installation
cd dev/cli
python -m cli.main myservice --help

# Test with mock data
ANSIBLE_STDOUT_CALLBACK=debug python -m cli.main myservice --install --check
```

## Contributing

1. **Follow PEP 8**: Use flake8 for linting
2. **Add tests**: Both unit and integration
3. **Update docs**: Document new features
4. **Use type hints**: For better IDE support
5. **Handle edge cases**: Validate inputs

## Next Steps

- Study existing operations for patterns
- Review the discovery system
- Understand the execution layer
- Add comprehensive tests
- Document your service