# Claude Configuration

This directory contains configuration files and hooks for Claude Code integration.

## Structure

```
.claude/
├── settings.json          # Base Claude settings
├── settings.local.json    # Project-specific settings
├── commands/              # Custom command templates
├── hooks/                 # Event hooks
│   └── dev/              # Development hooks
│       ├── pre.py        # Pre-tool validation
│       ├── post.py       # Post-tool logging
│       ├── notify.py     # User notifications
│       └── performance_monitor.py  # Performance tracking
└── scripts/              # Utility scripts
    └── optimize_claude_config.py  # Config optimization tool
```

## Hooks

### Pre-Tool Hook (`pre.py`)
- Validates dangerous commands (rm -rf, etc.)
- Blocks access to sensitive .env files
- Logs all tool usage

### Post-Tool Hook (`post.py`)
- Logs tool execution results
- Tracks tool usage patterns

### Notification Hook (`notify.py`)
- Provides TTS notifications when Claude needs input
- Supports multiple TTS providers (ElevenLabs, OpenAI, pyttsx3)

### Performance Monitor (`performance_monitor.py`)
- Tracks tool execution times
- Generates performance summaries
- Provides optimization recommendations

## Usage

### Optimize Configuration
```bash
python .claude/scripts/optimize_claude_config.py
```

### View Performance Metrics
```bash
cat logs/metrics/performance_summary.json | jq
```

### Custom Commands

Commands in the `commands/` directory provide quick templates for common tasks:
- `prime.md` - Load project context
- `principles.md` - Code review template
- `git_status.md` - Git status overview

## Environment Variables

- `ENGINEER_NAME` - Used in notifications (optional)
- `ELEVENLABS_API_KEY` - For ElevenLabs TTS
- `OPENAI_API_KEY` - For OpenAI TTS

## Best Practices

1. Keep permissions minimal and organized
2. Use hooks for validation and monitoring
3. Review performance metrics regularly
4. Update local settings rather than base settings
5. Document custom commands clearly