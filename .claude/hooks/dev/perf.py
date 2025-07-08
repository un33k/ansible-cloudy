#!/usr/bin/env python
"""Performance monitoring hook for Claude tool usage."""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime


class PerformanceMonitor:
    """Monitors performance metrics for Claude tool usage."""
    
    def __init__(self, metrics_dir: str = "logs/metrics"):
        """Initialize the performance monitor."""
        # Use project root for logs directory
        project_root = Path(__file__).parent.parent.parent.parent
        self.metrics_dir = project_root / metrics_dir
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_path = self.metrics_dir / "perf.json"
        self.summary_path = self.metrics_dir / "perfs.json"
        
    def load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics from file."""
        if not self.metrics_path.exists():
            return {"sessions": [], "tool_stats": {}}
        
        try:
            with open(self.metrics_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"sessions": [], "tool_stats": {}}
    
    def save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to file."""
        try:
            with open(self.metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
        except IOError:
            pass
    
    def update_tool_stats(self, metrics: Dict[str, Any], tool_name: str, duration: float) -> None:
        """Update aggregated tool statistics."""
        if "tool_stats" not in metrics:
            metrics["tool_stats"] = {}
        
        if tool_name not in metrics["tool_stats"]:
            metrics["tool_stats"][tool_name] = {
                "count": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "min_duration": float('inf'),
                "max_duration": 0
            }
        
        stats = metrics["tool_stats"][tool_name]
        stats["count"] += 1
        stats["total_duration"] += duration
        stats["avg_duration"] = stats["total_duration"] / stats["count"]
        stats["min_duration"] = min(stats["min_duration"], duration)
        stats["max_duration"] = max(stats["max_duration"], duration)
    
    def generate_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary."""
        tool_stats = metrics.get("tool_stats", {})
        
        # Find slowest tools
        slowest_tools = sorted(
            [(name, stats["avg_duration"]) for name, stats in tool_stats.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Find most used tools
        most_used = sorted(
            [(name, stats["count"]) for name, stats in tool_stats.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_tools_tracked": len(tool_stats),
            "total_calls": sum(stats["count"] for stats in tool_stats.values()),
            "total_duration": sum(stats["total_duration"] for stats in tool_stats.values()),
            "slowest_tools": [{"name": name, "avg_ms": round(dur * 1000, 2)} for name, dur in slowest_tools],
            "most_used_tools": [{"name": name, "count": count} for name, count in most_used],
            "recommendations": self.generate_recommendations(tool_stats)
        }
    
    def generate_recommendations(self, tool_stats: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on metrics."""
        recommendations = []
        
        # Check for slow file operations
        slow_file_ops = [
            name for name, stats in tool_stats.items()
            if name in ["Read", "Write", "Edit", "MultiEdit"] and stats["avg_duration"] > 0.1
        ]
        if slow_file_ops:
            recommendations.append(f"Consider batching file operations: {', '.join(slow_file_ops)} are slower than expected")
        
        # Check for excessive tool usage
        high_usage_tools = [
            name for name, stats in tool_stats.items()
            if stats["count"] > 100
        ]
        if high_usage_tools:
            recommendations.append(f"High usage detected for: {', '.join(high_usage_tools)}. Consider using Task tool for batch operations")
        
        return recommendations
    
    def record_metric(self, input_data: Dict[str, Any]) -> None:
        """Record a performance metric."""
        tool_name = input_data.get("tool_name", "unknown")
        start_time = input_data.get("start_time", time.time())
        end_time = input_data.get("end_time", time.time())
        duration = end_time - start_time
        
        # Load existing metrics
        metrics = self.load_metrics()
        
        # Add session entry
        session_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "duration": duration,
            "input_size": len(json.dumps(input_data.get("tool_input", {})))
        }
        
        if "sessions" not in metrics:
            metrics["sessions"] = []
        metrics["sessions"].append(session_entry)
        
        # Keep only last 1000 entries
        metrics["sessions"] = metrics["sessions"][-1000:]
        
        # Update aggregated stats
        self.update_tool_stats(metrics, tool_name, duration)
        
        # Save metrics
        self.save_metrics(metrics)
        
        # Generate and save summary
        summary = self.generate_summary(metrics)
        try:
            with open(self.summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
        except IOError:
            pass


def main():
    """Main entry point."""
    try:
        # Read input
        input_data = json.load(sys.stdin)
        
        # Create monitor and record metric
        monitor = PerformanceMonitor()
        monitor.record_metric(input_data)
        
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()