# Claudia: Self-Discovering Infrastructure Management CLI

**Project Name**: Claudia (Claude-inspired Infrastructure Assistant)  
**Tagline**: "Intelligent Infrastructure Management Made Intuitive"

## Vision: Transform Ali into Claudia - Self-Discovering Infrastructure CLI

**Current State**: Ali with basic recipe execution (`./ali psql --install`)  
**Target State**: Claudia with complete auto-discovering infrastructure operations

### Phase 1: Full Migration to Claudia Architecture

**New Directory Structure:**
```
dev/claudia/
├── cli/
│   ├── main.py              # Main CLI entry point
│   ├── parser.py            # Enhanced argument parsing
│   └── help.py              # Dynamic help generation
├── operations/
│   ├── recipes.py           # Recipe operations (--install)
│   ├── postgresql.py        # PostgreSQL operations
│   ├── redis.py             # Redis operations (future)
│   └── base.py              # System operations (future)
├── discovery/
│   ├── service_scanner.py   # Auto-discover services from recipes/tasks
│   ├── operation_builder.py # Build operations from task files
│   └── metadata_parser.py   # Parse task metadata for parameters
├── mapping/
│   ├── params.py            # Parameter mapping engine
│   ├── validation.py        # Parameter validation
│   └── auto_mapping.py      # Automatic parameter discovery
├── execution/
│   ├── ansible.py           # Ansible execution wrapper
│   └── task_runner.py       # Individual task execution
└── utils/
    ├── colors.py            # Output formatting
    └── config.py            # Configuration
```

**Entry Point:**
- `./claudia` (clean start, no Ali legacy)
- Remove `dev/ali/` directory entirely
- Update main script to point to Claudia

### Phase 2: Auto-Discovery Engine

**Service Discovery:**
- Automatically scan `/recipes/` for new services (e.g., `ai/ollama.yml`)
- Scan `/tasks/` directories for available operations
- Parse task file headers for operation metadata
- Build service operations dynamically

**Example Auto-Discovery for Ollama:**
```
When this structure exists:
cloudy/recipes/ai/ollama.yml              # Recipe
cloudy/tasks/ai/ollama/install.yml         # Install operation
cloudy/tasks/ai/ollama/create-model.yml    # Create model operation
cloudy/tasks/ai/ollama/list-models.yml     # List models operation
cloudy/tasks/ai/ollama/delete-model.yml    # Delete model operation

Claudia automatically provides:
./claudia ollama --install                 # Recipe execution
./claudia ollama --create-model llama2     # Model creation
./claudia ollama --list-models             # List models
./claudia ollama --delete-model oldmodel   # Delete model
./claudia ollama --help                    # Auto-generated help
```

### Phase 3: Metadata-Driven Operations

**Task File Metadata Standard:**
```yaml
# Granular Task: Create PostgreSQL User
# Claudia-Operation: adduser
# Claudia-Params: username:str, password:str, database:str?
# Claudia-Usage: ./claudia psql --adduser foo --password 1234 --database mydb
# Usage: ansible-playbook tasks/db/postgresql/create-user.yml -e "username=foo password=1234"

---
- name: Create PostgreSQL user
  vars:
    username: "{{ username | mandatory }}"
    password: "{{ password | mandatory }}"
    database: "{{ database | default('template1') }}"
```

**Auto-Parameter Mapping:**
- `Claudia-Params: username:str, password:str, database:str?` → `--username NAME --password PASS --database DB`
- `username:str` → Required string parameter
- `password:str` → Required string parameter
- `database:str?` → Optional string parameter with default

### Phase 4: Parameter Mapping Engine

**Claudia Parameters → Ansible Variables:**
```bash
# PostgreSQL Examples
./claudia psql --port 5544                 # database_port: 5544
./claudia psql --pgis                      # setup_postgis: true
./claudia psql --adduser foo --password 1234   # username: foo, password: 1234

# Auto-discovered Ollama Examples
./claudia ollama --create-model llama2      # model_name: llama2
./claudia ollama --create-model llama2 --gpu # model_name: llama2, use_gpu: true
./claudia ollama --delete-model oldmodel    # model_name: oldmodel
```

### Phase 5: Self-Expanding Command Interface

**Recipe Operations:**
```bash
./claudia psql --install --port 5544 --pgis    # PostgreSQL with custom config
./claudia ollama --install --gpu-support       # Auto-discovered Ollama install
./claudia redis --install --memory 512         # Redis with memory limit
```

**Granular Operations (Auto-discovered):**
```bash
# PostgreSQL (existing tasks become auto-operations)
./claudia psql --adduser foo --password 1234
./claudia psql --delete-user foo
./claudia psql --list-users
./claudia psql --adddb myapp --owner myuser
./claudia psql --delete-db oldapp
./claudia psql --change-password myuser --password newpass123

# Ollama (auto-discovered from tasks)
./claudia ollama --create-model llama2 --gpu
./claudia ollama --list-models
./claudia ollama --delete-model oldmodel
./claudia ollama --chat --model llama2

# Redis (future auto-discovery)
./claudia redis --set-memory 1024
./claudia redis --get-info
./claudia redis --flush-all
```

### Phase 6: Intelligent Auto-Help System

**Dynamic Help Generation:**
```bash
./claudia --help                           # Shows all discovered services
./claudia ollama --help                    # Shows all Ollama operations
./claudia --list-services                  # Shows available services
./claudia --version                        # Claudia version info
```

**Claudia Branding in Help:**
```
Claudia (Claude-inspired Infrastructure Assistant)
Intelligent Infrastructure Management Made Intuitive

Usage: ./claudia <service> [operation] [options]

Auto-discovered services:
  psql        PostgreSQL database operations
  redis       Redis cache operations  
  ollama      AI model management (auto-discovered)
  nginx       Web server management
```

### Phase 7: Implementation Steps

1. **Create CLAUDIA_ENHANCE.md** with complete plan ✅
2. **Migrate Ali → Claudia** (rename directories, update imports)
3. **Implement service discovery engine** that scans recipes/tasks
4. **Create metadata parsing system** for task file headers
5. **Build automatic parameter mapping** from metadata
6. **Create PostgreSQL operations** as the reference implementation
7. **Test auto-discovery** by adding PostgreSQL operations
8. **Build dynamic help system** with Claudia branding
9. **Update main entry script** to point to Claudia
10. **Update documentation** with Claudia references

### Phase 8: Future Service Addition Workflow

**Adding New Service (e.g., Ollama):**
1. Create `/recipes/ai/ollama.yml` with standard recipe structure
2. Create `/tasks/ai/ollama/` directory with operation tasks
3. Add Claudia metadata headers to each task file
4. Run `./claudia --refresh` (optional, auto-discovery on startup)
5. Service automatically available: `./claudia ollama --help`

**Zero Configuration Required:**
- No code changes to Claudia core
- No registration steps
- Automatic parameter mapping
- Auto-generated help
- Immediate availability

### Phase 9: Claudia Metadata Standards

**Required Metadata Headers:**
- `# Claudia-Operation: operation-name` - Defines the CLI operation name
- `# Claudia-Params: param1:type, param2:type?` - Parameter definitions
- `# Claudia-Usage: ./claudia service --operation-name param1 value` - Usage example

**Parameter Types:**
- `str` - String parameter (required)
- `str?` - Optional string parameter
- `bool` - Boolean flag
- `int` - Integer parameter
- `path` - File path parameter

### Target User Experience

**Before (Manual Configuration):**
- Add service manually to Ali code
- Define parameters explicitly
- Write help text manually
- Test and debug integration

**After (Claudia Auto-Discovery):**
- Create tasks with Claudia metadata headers
- Claudia automatically discovers service
- Parameters auto-mapped from metadata
- Help auto-generated with Claudia branding
- Immediately available and functional

**Example Future Addition:**
```bash
# After adding Ollama tasks with Claudia metadata:
./claudia ollama --help                     # Auto-generated help
./claudia ollama --install --gpu-support    # Auto-discovered install
./claudia ollama --create-model llama2 --gpu # Auto-discovered operation
./claudia --list-services                   # Shows Ollama automatically
```

**Claudia Philosophy:**
> "Every infrastructure operation should be as simple as a conversation. 
> Claudia discovers what you can do and makes it intuitive to do it."

---

This enhancement transforms Ali into Claudia - a truly intelligent, self-discovering infrastructure management CLI that honors its AI-inspired origins while providing unparalleled extensibility and ease of use.