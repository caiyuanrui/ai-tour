#!/usr/bin/env python3
"""
Demo: Token-Budget-Controlled ReAct Agent (P3)

Simulates three ReAct episodes with varying task complexity:
1. Simple lookup (economy) — weather check
2. Moderate task (standard) — data analysis
3. Complex task (deep) — multi-step research

Each episode demonstrates: purification, routing, budget enforcement.
"""

import sys
import os

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.budget_controller import TokenBudgetConfig, BudgetLevel
from src.observation_purifier import PurificationConfig
from src.effort_router import EffortLevel
from src.agent_coordinator import TokenBudgetAgentCoordinator, CoordinatorConfig


def simulate_large_json_output(n_items: int = 100) -> str:
    """Generate a large JSON tool output for testing purification."""
    import json
    items = [
        {
            "id": i,
            "name": f"file_{i}.txt",
            "size_kb": i * 10,
            "created_at": f"2026-06-27T10:{i:02d}:00Z",
            "status": "ok",
            "checksum": f"abc{i:08x}",
            "metadata": {
                "owner": "research",
                "permissions": "read-only",
                "version": i % 5,
            }
        }
        for i in range(n_items)
    ]
    return json.dumps(items, indent=2)


def simulate_tool_output(tool: str) -> str:
    """Generate realistic tool outputs for testing."""
    outputs = {
        "weather": (
            '{"location": "San Francisco", "temperature_c": 18, '
            '"condition": "partly cloudy", "humidity": 0.72, '
            '"wind_kph": 15, "forecast": [{"day": "Mon", "high": 20, "low": 14}, '
            '{"day": "Tue", "high": 22, "low": 15}], '
            '"alerts": [], "status": "ok"}'
        ),
        "search": (
            'Search results for "transformer attention optimization 2026":\n\n'
            '1. FlashAttention-3: 2x speedup on H100 GPUs\n'
            '   Link: https://arxiv.org/abs/2601.12345\n\n'
            '2. MLA: Multi-head Latent Attention for KV cache reduction\n'
            '   Link: https://arxiv.org/abs/2602.54321\n\n'
            '3. Ring Attention with block-sparse masks\n'
            '   Link: https://arxiv.org/abs/2603.98765\n'
            'status: success'
        ),
        "database_query": (
            'Query: SELECT * FROM experiments WHERE date > "2026-06-01" LIMIT 50\n'
            'Total rows: 50\n'
            'Execution time: 0.034s\n'
            'Rows:\n' + '\n'.join(
                f'  {{"id": {i}, "name": "exp_{i}", "value": {i * 1.5:.2f}, '
                f'"timestamp": "2026-06-{10 + i % 20:02d}T08:00:00Z"}}'
                for i in range(50)
            )
        ),
        "code_review": (
            'def analyze_data(data):\n'
            '    """Analyze experimental data with statistical methods."""\n'
            '    import numpy as np\n'
            '    arr = np.array(data)\n'
            '    results = {\n'
            '        "mean": float(np.mean(arr)),\n'
            '        "std": float(np.std(arr)),\n'
            '        "median": float(np.median(arr)),\n'
            '        "q25": float(np.percentile(arr, 25)),\n'
            '        "q75": float(np.percentile(arr, 75)),\n'
            '        "skew": float(np.mean(((arr - np.mean(arr)) / np.std(arr)) ** 3)),\n'
            '        "kurtosis": float(np.mean(((arr - np.mean(arr)) / np.std(arr)) ** 4)) - 3,\n'
            '        "outliers": int(np.sum(np.abs(arr - np.mean(arr)) > 2 * np.std(arr))),\n'
            '        "timestamp": "2026-06-27T12:00:00Z",\n'
            '        "status": "ok",\n'
            '    }\n'
            '    return results\n'
        ),
        "large_json": simulate_large_json_output(100),
    }
    return outputs.get(tool, f"Unknown tool: {tool}")


def run_demo_episode(
    coordinator: TokenBudgetAgentCoordinator,
    task: str,
    steps: list[list[tuple[str, str]]],
    prompt_tokens_per_step: int = 500,
    completion_tokens_per_step: int = 200,
) -> dict:
    """Run a simulated episode through the coordinator."""
    print(f"\n{'='*70}")
    print(f"  EPISODE: {task}")
    print(f"{'='*70}")
    
    # Start
    start_info = coordinator.start_episode(task)
    print(f"  Initial routing: {start_info['effort_level'].value} "
          f"(budget: {start_info['effort_budget']} tokens)")
    
    # Process steps
    purifier_total_before = 0
    purifier_total_after = 0
    
    for i, (instruction, observations) in enumerate(steps):
        print(f"\n  --- Step {i+1} ---")
        result = coordinator.process_step(
            instruction=instruction,
            observations=observations,
            num_tools=len(observations),
            prompt_tokens=prompt_tokens_per_step,
            completion_tokens=completion_tokens_per_step,
        )
        
        pur = result["purification"]
        purifier_total_before += pur["total_original_chars"]
        purifier_total_after += pur["total_purified_chars"]
        
        print(f"  Effort: {result['effort_level'].value} "
              f"(conf: {result['effort_confidence']:.0%})")
        print(f"  Budget signal: {result['budget_signal'].value}")
        print(f"  Purification: {pur['tools_processed']} tools, "
              f"{pur['total_original_chars']} → {pur['total_purified_chars']} chars "
              f"({pur['compression_ratio']:.1%})")
        print(f"  Cumulative: {result['cumulative_tokens']} tokens "
              f"(${result['estimated_cost']:.6f})")
        
        if result['budget_signal'].value in ('HARD_STOP', 'OVER_BUDGET'):
            print(f"  ⛔ Budget exhausted! Forcing finalize.")
            break
    
    # End episode
    result = coordinator.end_episode(
        success=True,
        notes=f"Demo episode: {task}",
    )
    
    print(f"\n  ✅ Episode complete:")
    print(f"     Tokens: {result.total_tokens} "
          f"(saved {result.tokens_saved_vs_baseline} vs baseline)")
    print(f"     Cost: ${result.estimated_cost_usd:.6f} "
          f"(saved ${result.cost_saved_vs_baseline:.6f})")
    print(f"     Steps: {result.total_steps}, "
          f"Effort changes: {result.effort_level_changes}")
    
    return result


def main():
    print("=" * 70)
    print("  Token-Budget-Controlled ReAct Agent — Demo")
    print("  Prototype P3 — Practical Token Budget Control")
    print("=" * 70)
    
    # Configure with gpt-4o-mini (cheapest useful provider)
    config = CoordinatorConfig(
        budget=TokenBudgetConfig(
            budget_tokens=16_000,
            level=BudgetLevel.STANDARD,
            provider="gpt-4o-mini",
        ),
        purification=PurificationConfig(
            max_chars=2_000,
            max_array_items=5,
            strip_timestamps=True,
            strip_success_fields=True,
        ),
    )
    
    coordinator = TokenBudgetAgentCoordinator(config)
    
    # --- EPISODE 1: Simple lookup (economy) ---
    run_demo_episode(
        coordinator,
        "What's the weather in San Francisco today?",
        steps=[
            (
                "I need to check the weather for San Francisco.",
                [("weather", simulate_tool_output("weather"))],
            ),
        ],
        prompt_tokens_per_step=300,
        completion_tokens_per_step=100,
    )
    
    # --- EPISODE 2: Data analysis (standard) ---
    run_demo_episode(
        coordinator,
        "Query the database for recent experiments and analyze their results.",
        steps=[
            (
                "Let me query the experiments database for recent entries.",
                [("database_query", simulate_tool_output("database_query"))],
            ),
            (
                "Now let me analyze the statistical properties of the data.",
                [("code_review", simulate_tool_output("code_review"))],
            ),
        ],
        prompt_tokens_per_step=800,
        completion_tokens_per_step=400,
    )
    
    # --- EPISODE 3: Complex research (deep) ---
    run_demo_episode(
        coordinator,
        "Research the latest advances in transformer attention optimization, "
        "search for papers, analyze code implementations, and summarize findings. "
        "Focus on KV cache reduction techniques from 2025-2026.",
        steps=[
            (
                "Search for recent papers on attention optimization.",
                [("search", simulate_tool_output("search"))],
            ),
            (
                "Review the code implementation of FlashAttention-3.",
                [("code_review", simulate_tool_output("code_review"))],
            ),
            (
                "Query the database for related experimental results.",
                [
                    ("database_query", simulate_tool_output("database_query")),
                    ("large_json", simulate_tool_output("large_json")),
                ],
            ),
        ],
        prompt_tokens_per_step=1500,
        completion_tokens_per_step=800,
    )
    
    # --- Summary report ---
    print(f"\n\n{'='*70}")
    print("  AGGREGATE REPORT")
    print(f"{'='*70}")
    print(coordinator.cost_tracker.report())
    
    # Compression efficiency across all episodes
    print(f"\n  Purification Efficiency:")
    print(f"    Filters: timestamp stripping, success field removal,")
    print(f"    deduplication, JSON array truncation, length capping")
    print(f"\n  Effort Routing Decision Tree:")
    print(f"    1. Budget < 25% → ECONOMY")
    print(f"    2. Budget 25-60% → STANDARD")
    print(f"    3. Budget > 60% → DEEP (conserving)")
    print(f"    Contingency: budget > 90% → ECONOMY override")
    
    print(f"\n  ✅ Demo complete. Prototype ready for integration.")


if __name__ == "__main__":
    main()
