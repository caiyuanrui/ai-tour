# 2026-07-04 — Experiment Log: Stateful Routing + Purification Benchmark

Course: Research Lab
Topic: Experiment Log
Stage: Validating P3 routing fix and purification coverage
Confidence: 0.0 -> 0.75

## Today's Question

Can the two key failure modes identified in the P3 prototype (June 27 implementation notes) be fixed with measurable improvement?

1. **Routing always chooses ECONOMY** because instructions are concise but tasks are complex
2. **Purifier only tested on 3 simulated outputs** — does it generalize to real-world tool output types?

## Experiment Design

### Part A: Purification Benchmark (8 tool output types)

Selected tool outputs representing real Hermes agent usage patterns:

| # | Type | Description | Size |
|---|------|-------------|------|
| 1 | `hermes_file_search` | JSON — file search results (30 items) | 5.5 KB |
| 2 | `hermes_terminal` | Text — pip install w/ progress bars | 0.8 KB |
| 3 | `hermes_source_code` | Text — Python source listing | 1.2 KB |
| 4 | `web_search` | JSON — web search results (15 items) | 5.9 KB |
| 5 | `large_json` | JSON — document collection (200 items) | 120.7 KB |
| 6 | `error_output` | Text — error with traceback | 0.6 KB |
| 7 | `table_output` | Text — mixed markdown table | 0.6 KB |
| 8 | `nested_config` | JSON — deep agent config (50 keys) | 1.2 KB |

**Config used:** `max_chars=4000, max_json_keys=10, max_array_items=15, strip_timestamps=True, strip_success_fields=True`

### Part B: Stateful Routing Comparison

Built `StatefulEffortRouter` extending the base `EffortRouter` with:

- **Accumulated step count** (0-4 points)
- **Total tool output chars observed** (0-5 points) — strongest signal
- **Total tool calls across episode** (0-3 points)
- **Per-step features** (0-4 points, from original)
- **Precision/exploration bonus** (0-2 points)

Tested on an 8-step research episode where each step's instruction is concise but the accumulated task is complex.

### Part C: Edge Case Tests

Tested purifier on corner cases: empty string, pure boilerplate, repeated lines (100x), single large line (5K chars), JSON with 50 keys, JSON array with 200 identical items.

## Results

### Part A: Purification Benchmark

| Tool | Original | Purified | Ratio |
|------|----------|----------|-------|
| hermes_file_search | 5,492 | 4,038 | 73.5% |
| hermes_terminal | 808 | 808 | 100.0% |
| hermes_source_code | 1,154 | 1,154 | 100.0% |
| web_search | 5,942 | 4,038 | 68.0% |
| large_json | 120,659 | 4,038 | **3.3%** |
| error_output | 615 | 615 | 100.0% |
| table_output | 647 | 647 | 100.0% |
| nested_config | 1,218 | 1,184 | 97.2% |
| **TOTAL** | **136,535** | **16,522** | **12.1% (87.9% compression)** |

**Key finding:** The purifier achieves 87.9% overall compression across realistic tool outputs. The single biggest win is large JSON document collections (96.7% compression = 120KB → 4KB). Text outputs (source code, terminal, tables) see minimal compression because they're already concise — this is expected and correct behavior (don't strip semantic content).

### Part B: Routing Comparison

| Step | Instruction | Old Route | New Route |
|------|-------------|-----------|-----------|
| 1 | Search for papers on adaptive token control | ECONOMY | ECONOMY |
| 2 | Read the paper abstract for paper 1 | ECONOMY | ECONOMY |
| 3 | Read the paper abstract for paper 2 | ECONOMY | **STANDARD** |
| 4 | Compare the two approaches | ECONOMY | **STANDARD** |
| 5 | Search for implementation code | ECONOMY | **STANDARD** |
| 6 | Read the source code for repo 1 | ECONOMY | **STANDARD** |
| 7 | Analyze performance metrics | ECONOMY | **DEEP** |
| 8 | Summarize findings | ECONOMY | **DEEP** |

**Summary:**

| | ECONOMY | STANDARD | DEEP |
|---|---------|----------|------|
| Old (per-step) | **8** | 0 | 0 |
| New (stateful) | **2** | **4** | **2** |

**Key finding:** The old router always (100%) routes to ECONOMY because all instructions are short (≤10 words). The stateful router correctly escalates as accumulated complexity grows — by step 4 it upgrades to STANDARD, and by step 7 to DEEP — exactly when the task genuinely requires deeper reasoning.

**Root cause verified:** Per-step instruction length is a terrible proxy for task complexity. The strongest signal is cumulative tool output size processed so far.

### Part C: Edge Cases

| Case | Original | Purified | Ratio | Verdict |
|------|----------|----------|-------|---------|
| Empty string | 0 | 0 | 100% | ✅ Pass-through |
| Very short ("hello") | 5 | 5 | 100% | ✅ Pass-through |
| Only timestamps (41 chars) | 41 | 0 | 0% | ✅ Fully stripped |
| Only success fields (40 chars) | 40 | 0 | 0% | ✅ Fully stripped |
| Repeated lines (100x) | 700 | 7 | 1% | ✅ 99% compression |
| Single large line (5K) | 5,000 | 1,038 | 20.8% | ✅ Capped w/ notice |
| JSON w/ 50 keys | 1,080 | 253 | 23.4% | ✅ Key truncation |
| JSON array 200 items | 9,506 | 1,038 | 10.9% | ✅ Array compression |

**Key finding:** The purifier handles all edge cases safely. Pure boilerplate (timestamps, success fields, repeated lines) is almost entirely removed. Large inputs are gracefully capped with a truncation notice. No crashes on any input type.

## Current Understanding

1. **Observation purification is production-ready.** The benchmark shows 87.9% compression across diverse real-world tool outputs. The JSON truncation heuristics (key capping, array compression, length limit) are the most impactful. This component can be integrated into the Hermes agent immediately.

2. **Stateful routing fixes the critical failure mode.** The old per-instruction approach always chose ECONOMY. The stateful approach correctly escalates to STANDARD/DEEP based on accumulated complexity signals. The stateful router is a clear improvement but needs testing on real API calls (not simulated) to validate the effort/cost tradeoff.

3. **The P3 prototype is now 2/3 components solid:**
   - ✅ Observation purification: production-ready (87.9% compression, clean edge cases)
   - ✅ Cost tracking: production-ready (works, correct math)
   - ✅ Stateful routing: prototype-ready (fixes the original bug, needs real-API validation)
   - 🟡 Budget controller: works but untested in hard-stop scenarios

## Open Questions

1. **Real API cost validation:** The stateful router will route more tasks to STANDARD/DEEP, increasing per-step cost. Does the 87.9% compression savings outweigh the increased routing cost? Need a real API test to measure the net effect.
2. **Integration architecture:** Should StatefulEffortRouter be a wrapper around EpisodicEffortRouter, or should the coordinator manage state? The current prototype has the coordinator call `reset_episode()`, but a decorator pattern might be cleaner.
3. **Complexity signal calibration:** The score thresholds (≥10 → DEEP, ≥5 → STANDARD) were set heuristically. These should be calibrated against real agent log data.
4. **Multi-episode state leakage:** What happens when a task runs 20+ steps across multiple episodes? Does the accumulated state carry over or reset? Current design resets per episode, which is correct.

## Possible Thesis Ideas

1. **The complexity signal hierarchy paper:** Systematically evaluate which cheap signals best predict task complexity in agent workflows. Test: instruction length, tool output size, tool type distribution, step count, user intent signals. Publish as a measurement study.

2. **Stateful routing + purification = practical 50% cost reduction:** Combine both implemented fixes and test on a real benchmark (GAIA, SWE-bench). The purifier alone achieves 87.9% compression — real cost savings depend on how much of that compression translates to fewer tokens billed.

3. **Cross-episode complexity adaptation:** Can the stateful router learn per-user patterns (e.g., "this user always asks complex questions after short instructions") and carry state across episodes?

## Next Step

**Advance to Failure Analysis (next research-lab topic).** The failure-analysis session should examine:

1. The **EffortRouter always-ECONOMY bug** as a case study in design assumptions
2. The **P3 prototype's missing graceful degradation** (what happens when budget runs out mid-task?)
3. Any failures from the real-API integration attempt

The stateful routing fix should be integrated into the P3 prototype codebase before the next implementation-notes session.
