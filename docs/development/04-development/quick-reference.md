# Claude Code Quick Reference Card

## 🚀 Essential Commands

### CLI Operations
```bash
# Development workflow
cli harden --check --dev          # Dry run SSH hardening
cli harden --install --dev        # Apply SSH hardening
cli security --check --dev        # Dry run security
cli security --install --dev      # Apply security
cli base --install --dev          # Install base packages

# Production workflow  
cli security --install --prod --production-hardening

# Service operations
cli nginx --install
cli postgresql --install
cli redis --install
```

### Common Search Patterns
```python
# Find similar implementations
Grep pattern="class.*Service" include="*.py"
Glob pattern="**/security*.yml"

# Find TODO items
Grep pattern="TODO|FIXME|HACK" include="*.py"

# Find variable usage
Grep pattern="vault_.*_user" include="*.yml"
```

## 📏 Code Standards

### File Size Limits
- **Maximum:** 200 lines
- **Target:** 100 lines
- **Functions:** <20 lines
- **Classes:** Single responsibility

### Naming Conventions
```python
# Files
security-production.yml     # Kebab-case for Ansible
smart_security.py          # Snake_case for Python

# Variables
vault_grunt_user           # Vault prefix for secrets
admin_user                 # Clear, descriptive names

# Functions
def validate_connection()  # Verb_noun pattern
def get_inventory_vars()   # Explicit action
```

## 🔄 LEVER Checklist

Before coding:
- [ ] **L**ocated similar code?
- [ ] **E**xtending existing?
- [ ] **V**alidated compatibility?
- [ ] **E**nhancing performance?
- [ ] **R**educing complexity?

## 🎯 Optimization Metrics

| Metric | Target | Formula |
|--------|--------|---------|
| Code Reduction | 30-50% | (Initial - Final) / Initial |
| Reuse Rate | >60% | Extended / Total LOC |
| Test Coverage | >80% | Tested / Total Functions |
| Performance | No regression | Benchmark comparison |

## 🛠️ Tool Decision Tree

```
Need to read a file?
├─ Specific file → Read
└─ Unknown location → Grep/Glob

Need to edit code?
├─ Single change → Edit
├─ Multiple changes → MultiEdit
└─ New file (last resort) → Write

Need to search?
├─ File names → Glob
├─ File contents → Grep
└─ Complex search → Task

Need to run commands?
├─ Single command → Bash
├─ Multiple commands → Batch Bash calls
└─ Avoid: find, grep, cat commands
```

## 📋 Pre-Flight Checklist

### Before Implementation
1. Read optimization principles
2. Search for patterns
3. Score approach (≥7/10)
4. Plan with TodoWrite

### During Implementation
1. Extend don't create
2. Test incrementally  
3. Document decisions
4. Update todos

### After Implementation
1. Run all tests
2. Check performance
3. Update documentation
4. Clean up code

## 🚨 Red Flags

**Stop and reconsider if:**
- Creating multiple new files
- Duplicating existing logic
- Score below 7/10
- No similar patterns found
- Breaking existing tests

## 💡 Power User Tips

### Efficient Searching
```python
# Search multiple patterns at once
Task: "Find all security-related playbooks and their grunt user configurations"

# Batch file reads
Read file1.yml
Read file2.yml  
Read file3.yml
```

### Smart Editing
```python
# Use MultiEdit for refactoring
MultiEdit file_path="/path/to/file" edits=[
    {"old_string": "old_var", "new_string": "new_var", "replace_all": true},
    {"old_string": "# TODO", "new_string": "# DONE"}
]
```

### Performance Testing
```bash
# Always benchmark
time cli security --check --dev
time cli security --install --dev
```

## 🔗 Quick Links

- **Optimization:** `/docs/development/04-development/optimization-principles.md`
- **LEVER:** `/docs/development/04-development/lever-methodology.md`
- **Extended Thinking:** `/docs/development/04-development/extended-thinking.md`
- **Tools:** `/docs/development/04-development/tool-usage-guide.md`

## 📝 Commit Message Format

```
type: Subject line (50 chars max)

- Bullet point details
- What changed and why
- Reference issue numbers

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

Remember: Less code, more impact! 🚀