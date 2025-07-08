#!/usr/bin/env python
"""Optimize Claude configuration files by removing redundancy and improving performance."""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Set


class ClaudeConfigOptimizer:
    """Optimizes Claude configuration files."""
    
    def __init__(self, claude_dir: Path = Path(".claude")):
        """Initialize optimizer with claude directory path."""
        self.claude_dir = claude_dir
        self.settings_path = claude_dir / "settings.json"
        self.local_settings_path = claude_dir / "settings.local.json"
        
    def deduplicate_permissions(self, permissions: List[str]) -> List[str]:
        """Remove duplicate permissions and organize them logically."""
        # Convert to set to remove exact duplicates
        unique_perms = set(permissions)
        
        # Group by pattern type
        groups = {
            'cli': [],
            'python': [],
            'ansible': [],
            'git': [],
            'docker': [],
            'file_ops': [],
            'scripts': [],
            'other': []
        }
        
        for perm in sorted(unique_perms):
            if 'cli' in perm.lower():
                groups['cli'].append(perm)
            elif 'python' in perm.lower():
                groups['python'].append(perm)
            elif 'ansible' in perm.lower():
                groups['ansible'].append(perm)
            elif 'git' in perm.lower():
                groups['git'].append(perm)
            elif 'docker' in perm.lower():
                groups['docker'].append(perm)
            elif any(op in perm.lower() for op in ['ls', 'find', 'grep', 'cat', 'touch', 'mkdir', 'mv', 'cp', 'rm', 'chmod']):
                groups['file_ops'].append(perm)
            elif './scripts/' in perm or 'bootstrap.sh' in perm:
                groups['scripts'].append(perm)
            else:
                groups['other'].append(perm)
        
        # Combine groups in logical order
        result = []
        for group in ['cli', 'python', 'ansible', 'scripts', 'git', 'docker', 'file_ops', 'other']:
            result.extend(sorted(groups[group]))
        
        return result
    
    def merge_hooks(self, base_hooks: Dict, local_hooks: Dict) -> Dict:
        """Merge hooks from base and local settings, avoiding duplicates."""
        merged = {}
        
        # Process each hook type
        for hook_type in set(base_hooks.keys()) | set(local_hooks.keys()):
            base_list = base_hooks.get(hook_type, [])
            local_list = local_hooks.get(hook_type, [])
            
            # Create a set of unique hook commands
            seen_commands = set()
            merged_list = []
            
            # Process all hooks, local first (higher priority)
            for hook in local_list + base_list:
                command = hook.get('hooks', [{}])[0].get('command', '')
                if command and command not in seen_commands:
                    seen_commands.add(command)
                    merged_list.append(hook)
            
            if merged_list:
                merged[hook_type] = merged_list
        
        return merged
    
    def optimize_configs(self) -> Dict[str, Any]:
        """Load and optimize configuration files."""
        # Load base settings
        base_settings = {}
        if self.settings_path.exists():
            with open(self.settings_path) as f:
                base_settings = json.load(f)
        
        # Load local settings
        local_settings = {}
        if self.local_settings_path.exists():
            with open(self.local_settings_path) as f:
                local_settings = json.load(f)
        
        # Optimize permissions
        all_permissions = (
            base_settings.get('permissions', {}).get('allow', []) +
            local_settings.get('permissions', {}).get('allow', [])
        )
        optimized_permissions = self.deduplicate_permissions(all_permissions)
        
        # Merge hooks
        merged_hooks = self.merge_hooks(
            base_settings.get('hooks', {}),
            local_settings.get('hooks', {})
        )
        
        return {
            'permissions': optimized_permissions,
            'hooks': merged_hooks,
            'stats': {
                'original_permission_count': len(all_permissions),
                'optimized_permission_count': len(optimized_permissions),
                'reduction_percentage': round((1 - len(optimized_permissions) / len(all_permissions)) * 100, 1)
            }
        }
    
    def generate_report(self, optimization_result: Dict[str, Any]) -> str:
        """Generate a report of the optimization."""
        stats = optimization_result['stats']
        report = [
            "# Claude Configuration Optimization Report",
            "",
            "## Permission Optimization",
            f"- Original permissions: {stats['original_permission_count']}",
            f"- Optimized permissions: {stats['optimized_permission_count']}",
            f"- Reduction: {stats['reduction_percentage']}%",
            "",
            "## Hook Consolidation",
            f"- Hook types: {len(optimization_result['hooks'])}",
            ""
        ]
        
        for hook_type, hooks in optimization_result['hooks'].items():
            report.append(f"### {hook_type}")
            for hook in hooks:
                command = hook.get('hooks', [{}])[0].get('command', 'N/A')
                report.append(f"- {command}")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main entry point."""
    optimizer = ClaudeConfigOptimizer()
    result = optimizer.optimize_configs()
    
    # Print report
    print(optimizer.generate_report(result))
    
    # Save optimized permissions back to local settings
    local_settings_path = Path(".claude/settings.local.json")
    if local_settings_path.exists():
        with open(local_settings_path) as f:
            settings = json.load(f)
        
        settings['permissions']['allow'] = result['permissions']
        
        with open(local_settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print("\n✅ Optimized permissions saved to settings.local.json")


if __name__ == "__main__":
    main()