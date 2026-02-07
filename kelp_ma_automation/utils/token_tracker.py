"""
Token Tracker Utility
Tracks LLM token usage across all pipeline operations.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Single LLM call token usage."""
    task: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def cost_estimate(self) -> float:
        """Estimate cost in USD (assuming phi4-mini rates ~$0.0001/1K tokens)."""
        return self.total_tokens * 0.0001 / 1000


class TokenTracker:
    """
    Singleton tracker for all LLM token usage in pipeline.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.usage_log: List[TokenUsage] = []
        self.current_run: str = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def reset(self):
        """Reset tracker for new run."""
        self.usage_log = []
        self.current_run = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def track(self, task: str, model: str, 
              prompt_tokens: int, completion_tokens: int):
        """Track a single LLM call."""
        usage = TokenUsage(
            task=task,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )
        self.usage_log.append(usage)
        
        logger.info(f"[TOKENS] {task}: {usage.total_tokens} tokens "
                    f"(prompt={prompt_tokens}, completion={completion_tokens})")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (~4 chars per token for English)."""
        return len(text) // 4
    
    def track_from_response(self, task: str, model: str, 
                            prompt: str, response: str):
        """Track using text lengths when API doesn't return counts."""
        prompt_tokens = self.estimate_tokens(prompt)
        completion_tokens = self.estimate_tokens(response)
        self.track(task, model, prompt_tokens, completion_tokens)
    
    @property
    def total_tokens(self) -> int:
        return sum(u.total_tokens for u in self.usage_log)
    
    @property
    def total_prompt_tokens(self) -> int:
        return sum(u.prompt_tokens for u in self.usage_log)
    
    @property
    def total_completion_tokens(self) -> int:
        return sum(u.completion_tokens for u in self.usage_log)
    
    def get_summary(self) -> Dict:
        """Get usage summary."""
        tasks = {}
        for u in self.usage_log:
            if u.task not in tasks:
                tasks[u.task] = {'calls': 0, 'tokens': 0}
            tasks[u.task]['calls'] += 1
            tasks[u.task]['tokens'] += u.total_tokens
        
        return {
            'run_id': self.current_run,
            'total_calls': len(self.usage_log),
            'total_tokens': self.total_tokens,
            'prompt_tokens': self.total_prompt_tokens,
            'completion_tokens': self.total_completion_tokens,
            'estimated_cost_usd': sum(u.cost_estimate for u in self.usage_log),
            'by_task': tasks
        }
    
    def print_summary(self):
        """Print formatted usage summary."""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("LLM TOKEN USAGE SUMMARY")
        print("=" * 60)
        print(f"Run ID: {summary['run_id']}")
        print(f"Total LLM Calls: {summary['total_calls']}")
        print(f"Total Tokens: {summary['total_tokens']:,}")
        print(f"  - Prompt Tokens: {summary['prompt_tokens']:,}")
        print(f"  - Completion Tokens: {summary['completion_tokens']:,}")
        usd_cost = summary['estimated_cost_usd']
        inr_cost = usd_cost * 83.5
        print(f"Estimated Cost: ${usd_cost:.4f} (₹{inr_cost:.2f} INR)")
        print("\nBy Task:")
        for task, info in summary['by_task'].items():
            print(f"  {task}: {info['calls']} calls, {info['tokens']:,} tokens")
        print("=" * 60 + "\n")
    
    def save_to_file(self, filepath: str):
        """Save usage log to JSON file."""
        summary = self.get_summary()
        summary['estimated_cost_inr'] = summary['estimated_cost_usd'] * 83.5
        data = {
            'summary': summary,
            'detailed_log': [
                {
                    'task': u.task,
                    'model': u.model,
                    'prompt_tokens': u.prompt_tokens,
                    'completion_tokens': u.completion_tokens,
                    'total_tokens': u.total_tokens,
                    'timestamp': u.timestamp
                }
                for u in self.usage_log
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Token usage saved to: {filepath}")


# Global instance
token_tracker = TokenTracker()


if __name__ == "__main__":
    # Test
    tracker = TokenTracker()
    tracker.track("domain_classification", "phi4-mini:latest", 500, 100)
    tracker.track("text_shortening", "phi4-mini:latest", 200, 50)
    tracker.track("text_shortening", "phi4-mini:latest", 180, 45)
    tracker.track("hook_generation", "phi4-mini:latest", 400, 120)
    
    tracker.print_summary()
