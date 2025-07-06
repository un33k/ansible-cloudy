# CLAUDE CODE DEVELOPMENT GUIDE

This repository is optimized for development with Claude Code. This guide provides quick reference for AI-assisted development.

## 🚀 Quick Start

1. **Before Any Code Changes:**
   - Read `/docs/development/04-development/optimization-principles.md`
   - Check existing patterns with `cli search [pattern]`
   - Score your approach (must be ≥ 7/10)

2. **Key Commands:**
   ```bash
   # IMPORTANT: Always activate Python venv first
   source .venv/bin/activate
   
   # Always use CLI (not direct python commands unless debugging)
   cli security --install            # SSH hardening + security setup
   cli base --install               # Base system configuration
   cli [service] --install          # Service installation
   
   # Optional: Change SSH port after everything is set up
   cli ssh --new-port 2222
   ```

3. **Development Workflow:**
   - Extend existing code (don't create new files)
   - Use LEVER principles (Locate, Extend, Validate, Enhance, Reduce)
   - Target 30-50% code reduction from initial approach

## 📁 Project Structure

```
ansible-cloudy/
├── cloudy/           # Ansible playbooks and roles
├── dev/cli/          # CLI implementation
├── docs/development/ # Development documentation
└── .claude/          # Claude Code settings
```

## 🔧 Key Principles

1. **Architecture Standards:**
   - Files under 200 LOC (target 100 LOC)
   - Single responsibility per module
   - Auto-discovery over configuration
   - NEVER hardcode values - always use variables from vault/config

2. **Security Model:**
   - Phase 1: Security (SSH hardening, firewall, fail2ban)
   - Phase 2: Base (system configuration)
   - Phase 3: Services (application deployment)
   - Optional: Port change with harden command

3. **Testing Requirements:**
   - Run `cli [command] --check` before `--install`
   - Verify with `npm run lint` and `npm run typecheck`
   - Test both dev and production scenarios

## 🎯 Optimization Targets

- **Code Reduction:** 87% (proven in production)
- **Time Savings:** 90% (days → hours)
- **Performance:** 5x improvement
- **Reuse Rate:** >60% of existing code

## 📚 Essential Reading

1. **Optimization Framework:** `/docs/development/04-development/optimization-principles.md`
2. **LEVER Methodology:** `/docs/development/04-development/lever-methodology.md`
3. **Extended Thinking:** `/docs/development/04-development/extended-thinking.md`
4. **Tool Usage:** `/docs/development/04-development/tool-usage-guide.md`

## 🛠️ Claude Code Configuration

Settings are in `.claude/settings.json` with hooks for:
- Pre-write optimization reminders
- Automated principle checking
- Code quality validation

## 🔄 Common Workflows

### Adding a New Service
1. Search for similar services: `cli search service`
2. Extend existing playbook structure
3. Follow naming conventions
4. Test with `--check` first

### Debugging Issues
1. Use extended thinking: "think harder about this issue"
2. Check logs systematically
3. Verify variable naming in inventories
4. Test in isolation with `--dev`

### Creating PRs
1. Ensure all tests pass
2. Run production hardening checks
3. Document architectural decisions
4. Use conventional commits

## 💡 Pro Tips

- **Always** check existing code before creating new files
- **Batch** related changes in single commits
- **Document** why, not just what
- **Test** incrementally, not just at the end
- **Reuse** patterns from similar implementations

## 🚨 Important Reminders

- Never commit secrets or credentials
- Always use vault variables for sensitive data
- Test production scenarios in CI
- Maintain backward compatibility
- Follow security best practices

---

For detailed implementation guidelines, see the documentation in `/docs/development/`.