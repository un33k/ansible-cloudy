# Claude Code Tool Usage Guide

This guide provides best practices for using Claude Code's tools effectively in the ansible-cloudy project.

## 🛠️ Available Tools

### 📖 Read
**Purpose:** Read file contents and understand code structure

**Best Practices:**
- Always read before editing
- Use line limits for large files
- Read related files for context
- Check file existence before operations

**Examples:**
```bash
# Read entire file
Read file_path="/path/to/file.py"

# Read specific lines
Read file_path="/path/to/file.py" offset=100 limit=50
```

### ✏️ Edit
**Purpose:** Make precise single-line or block replacements

**Best Practices:**
- Read file first to get exact content
- Include enough context for uniqueness
- Preserve exact indentation
- Verify changes after editing

**Common Pitfalls:**
- Missing whitespace in old_string
- Not including enough context
- Forgetting line number prefixes

### 📝 MultiEdit
**Purpose:** Make multiple edits to a single file efficiently

**Best Practices:**
- Group related changes
- Order edits logically
- Consider sequential impacts
- Use for refactoring

**Example Structure:**
```python
edits=[
    {"old_string": "import old", "new_string": "import new"},
    {"old_string": "old.method()", "new_string": "new.method()"}
]
```

### 🔍 Grep
**Purpose:** Search file contents using regex patterns

**Best Practices:**
- Use specific patterns
- Include file filters
- Combine with Glob for comprehensive search
- Use Task for complex searches

**Examples:**
```bash
# Search for function definitions
Grep pattern="def\s+\w+.*security" include="*.py"

# Find TODO comments
Grep pattern="TODO|FIXME" include="*.yml"
```

### 🌐 Glob
**Purpose:** Find files by name patterns

**Best Practices:**
- Use wildcards effectively
- Specify base directory
- Combine with Grep for content search
- Sort by modification time

**Examples:**
```bash
# Find all playbooks
Glob pattern="**/*.yml" path="/cloudy/playbooks"

# Find Python test files
Glob pattern="**/test_*.py"
```

### 📂 LS
**Purpose:** List directory contents

**Best Practices:**
- Use absolute paths
- Apply ignore patterns
- Verify directories before operations
- Check structure before creating files

**Examples:**
```bash
# List directory with ignores
LS path="/absolute/path" ignore=["*.pyc", "__pycache__"]
```

### 💻 Bash
**Purpose:** Execute shell commands

**Best Practices:**
- Quote paths with spaces
- Use absolute paths
- Avoid search commands (use Grep/Glob)
- Batch parallel operations
- Set appropriate timeouts

**Examples:**
```bash
# Run multiple git commands in parallel
Bash command="git status"
Bash command="git diff"
Bash command="git log --oneline -5"
```

### 🤖 Task
**Purpose:** Launch agent for complex multi-step operations

**When to Use:**
- Complex searches across many files
- Multi-phase investigations
- Exploratory analysis
- Pattern discovery

**When NOT to Use:**
- Simple file reads
- Specific file edits
- Known file locations
- Single operations

### 📔 NotebookRead/Edit
**Purpose:** Work with Jupyter notebooks

**Best Practices:**
- Read cells before editing
- Maintain cell types
- Preserve outputs when appropriate
- Update markdown documentation

### 🌐 WebFetch
**Purpose:** Fetch and analyze web content

**Best Practices:**
- Provide specific prompts
- Use for documentation lookup
- Cache results mentally
- Extract key information

### 📋 TodoRead/Write
**Purpose:** Manage task lists and track progress

**Best Practices:**
- Use proactively for complex tasks
- Update status in real-time
- Break down large tasks
- Mark completed immediately

**Task States:**
- `pending`: Not started
- `in_progress`: Currently working (only one at a time)
- `completed`: Finished successfully

## 🎯 Tool Selection Strategy

### For Searching:
```
Specific file? → Read
File pattern? → Glob
Content pattern? → Grep
Complex search? → Task
```

### For Editing:
```
Single change? → Edit
Multiple changes? → MultiEdit
New file? → Write
Notebook? → NotebookEdit
```

### For Analysis:
```
Directory structure? → LS
Command output? → Bash
Web documentation? → WebFetch
Complex investigation? → Task
```

## 🚀 Performance Optimization

### Batch Operations
**Do:**
```python
# Good - Parallel execution
Bash command="npm test"
Bash command="npm run lint"
Bash command="npm run build"
```

**Don't:**
```python
# Bad - Sequential execution
Bash command="npm test && npm run lint && npm run build"
```

### Search Efficiency
**Do:**
```python
# Good - Specific search
Grep pattern="class.*Security" include="*.py"
```

**Don't:**
```python
# Bad - Too broad
Grep pattern=".*"
```

### File Operations
**Do:**
```python
# Good - Read once, edit multiple
content = Read file_path="/path/to/file"
MultiEdit file_path="/path/to/file" edits=[...]
```

**Don't:**
```python
# Bad - Multiple reads
Read file_path="/path/to/file"
Edit file_path="/path/to/file" ...
Read file_path="/path/to/file"
Edit file_path="/path/to/file" ...
```

## 📊 Tool Usage Metrics

Track your tool efficiency:
- Searches per task
- Edits per file
- Commands per operation
- Cache hit rate
- Task completion time

## 💡 Pro Tips

1. **Plan Before Executing**
   - List needed operations
   - Order for efficiency
   - Batch similar tasks

2. **Use Right Tool for Job**
   - Don't use Bash for file reading
   - Don't use Task for simple operations
   - Don't create files unnecessarily

3. **Verify Before Acting**
   - Check file existence
   - Verify directory structure
   - Confirm patterns match

4. **Document Tool Chains**
   - Record successful patterns
   - Note tool combinations
   - Share with team

## 🔧 Troubleshooting

### Common Issues:

1. **Edit Fails - String Not Found**
   - Solution: Read file first, copy exact content

2. **Glob Returns Nothing**
   - Solution: Verify path exists, check pattern

3. **Bash Command Timeout**
   - Solution: Increase timeout, simplify command

4. **Task Confusion**
   - Solution: Provide clearer, more specific prompt

Remember: The key to efficient tool usage is choosing the right tool for each job and combining them effectively!