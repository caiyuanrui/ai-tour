# 2026-07-11 — Failure Analysis: P3 Design Assumptions & Validation Gaps

Course: Research Lab
Topic: Failure Analysis
Stage: Systematic postmortem of three design-level failures from the P3 prototype cycle
Confidence: 0.0 -> 0.75

## Today's Question

What design-level failures occurred during the P3 (Practical Token-Budget-Controlled ReAct Agent) prototype cycle, what do they reveal about assumption-based engineering, and how should the thesis approach change?

## Failure 1: Instruction Length ≈ Task Complexity (EffortRouter always-ECONOMY Bug)

### What was expected

The EffortRouter's complexity scoring would use per-step features — instruction word count, tool keywords, precision/exploration markers — to correctly classify tasks into ECONOMY (≤2K tokens/step), STANDARD (≤8K), or DEEP (≤32K).

### What actually happened

All demo tasks scored ≤2 on the complexity scale (scale: 0-12). Instructions like "Search for papers on adaptive token control" and "Analyze performance metrics" are concise (≤10 words) but describe multi-step research activities. The router routed 8/8 steps to ECONOMY.

### Root cause analysis

**Bad assumption at the architectural level:** The designer conflated *instruction length* with *task complexity*. In the ReAct framework, instructions are naturally concise because the agent's behavior is determined by the *outcome* of tool calls, not the length of the instruction. A single line like "find the source code and analyze it" describes potentially 10+ tool calls.

**Why it happened:** The complexity scoring was designed based on how humans describe difficulty (longer descriptions = harder), not on how agents actually experience complexity. In agent systems:
- Instructions are brief by convention (one goal per step)
- Complexity is *emergent* across steps — a 30-step chain of simple-seeming instructions can be harder than a 2-step chain of verbose instructions
- Tool output size is the actual complexity signal because it proxies for how much information the LLM must process

**Systemic pattern:** This is a case of **proxy variable failure** — using a correlated-but-causally-wrong signal as the decision feature. The root cause is designing routing features from the *human's* perspective (how hard does this sound?) rather than the *agent's* perspective (how much state and computation does this step require?).

### Fix applied

StatefulEffortRouter was built in the experiment-log session (2026-07-04). It tracks:
- Accumulated step count (0-4 points)
- Total tool output chars observed (0-5 points)
- Total tool calls across episode (0-3 points)

This correctly escalates: 2 ECONOMY, 4 STANDARD, 2 DEEP instead of 8/8 ECONOMY.

### What should change going forward

1. **Never use per-step instruction length as a primary complexity signal** — it's a known bad proxy in the literature (see: tool token economics, observation purification theory).
2. **Always prototype routing with a stateful dimension** — even a simple step counter improves routing dramatically.
3. **Feature design must be grounded in the agent's observation space**, not in human intuitions about task difficulty.

## Failure 2: Missing Graceful Degradation (Budget Exhaustion Mid-Task)

### What was expected

The BudgetController would emit budget signals (OK → WARNING at 75% → HARD_STOP at 100% → OVER_BUDGET) and the agent would know how to respond.

### What actually happened

The controller correctly tracks budget and emits signals, but when HARD_STOP fires mid-task, **nothing happens** — the agent has no fallback behavior. The code sets `is_active = False` but the ReAct loop doesn't read this flag, so the agent continues full-steam until the task completes or crashes.

### Root cause analysis

**Design assumption:** The prototype assumed the agent would "just know" to stop when budget is exhausted. In reality, stopping mid-task is non-trivial — the agent must:
1. Decide what to save (partial results? best attempt?)
2. Notify the user without being confusing
3. Optionally request more budget
4. Handle the psychological failure of not completing

**Why this is hard to fix:** The ReAct loop pattern (Think → Act → Observe) is a while-loop with no concept of early termination. Adding graceful degradation requires:
- A termination boundary step (not mid-tool-call)
- A summary sub-agent to produce partial results
- A user communication protocol ("Budget exhausted. Showing best attempt. Request more?")
- This is architecturally different from simple token tracking

**Systemic pattern:** **Interface incompleteness** — emitting a signal without defining what consumes it. The BudgetController produces output (signals) but no component was designed as the signal consumer. This is the same class of problem as "throwing an exception that nobody catches."

### Fix suggested

Implement a `DegradationAgent` wrapper:
```
BudgetController → DegradationAgent → ReActLoop
```
When budget hits HARD_STOP:
1. Pause at the next Think step (not mid-Observe)
2. Run summary of work done so far
3. Present to user with requote option
4. If no budget added → save partial results and exit cleanly

### What should change going forward

**Every budget/control signal must have an explicit consumer.** The architecture should specify:
- Who emits the signal
- Who listens for the signal
- What actions the listener takes for each signal level
- What happens if no listener responds

## Failure 3: Simulated-Only Validation (No Real API Testing Across the Entire P3 Cycle)

### What was expected

The purifier (87.9% compression benchmark) and stateful router (correct escalation) would perform equivalently on real API calls.

### What actually happened

**Neither the purifier nor the router was ever tested against a real LLM API.** Every benchmark used simulated tool outputs and hypothetical routing scenarios. The 87.9% compression number is real *for the input types tested*, but:
- The 120KB JSON outlier drives most of the compression — without it, average drops to ~26%
- The stateful router was tested against a fabricated 8-step episode, not real agent logs
- The 23.1% token savings in the demo are based on simulated token counts, not measured API billing

### Root cause analysis

**Engineering bias toward simulation:** Building a prototype that runs in isolation is faster and easier than connecting to real APIs. The P3 cycle had 3 sessions (project-planning → implementation-notes → experiment-log) and none made real API calls.

**Why this matters:** Three critical unknowns cannot be answered without real API testing:
1. **Token savings → cost savings mapping:** API billing counts tokens differently (prompt tokens are cheaper than completion tokens, caching gives free tokens). 87.9% compression in character count doesn't translate to 87.9% token savings.
2. **Latency impact:** Purifying observations adds processing time (JSON parsing, regex). On a fast local system this is negligible, but in production the overhead accumulates.
3. **Content preservation risk:** The purifier aggressively removes structural content. On real, messy tool outputs, it might strip critical information that structured test inputs don't capture.

### Systemic pattern

**Simulation overconfidence** — the bias where clean, synthetic tests produce impressive numbers that don't survive contact with reality. This is especially dangerous in agent systems where real-world tool outputs are messy, multimodal, and inconsistent.

### What should change going forward

**Before any component is declared "production-ready," it must pass a real API test.** The purifier should be tested against actual Hermes agent tool calls from a real session. The router should be tested against replay logs from real agent runs.

## Failure 4: Purification Asymmetry Blindness (Compression Metric Inflation)

### What was expected

The overall 87.9% compression is representative of typical tool output compression.

### What actually happened

The 87.9% is heavily driven by one input type (large JSON at 120KB, compressed 96.7%). Without this outlier, the average compression across the other 7 types is only ~26%:

| Tool type | Original | Purified | Ratio |
|-----------|----------|----------|-------|
| 7 non-JSON types combined | 10,206 | 8,295 | 81.3% (only 18.7% compression) |

For text-heavy agent tasks (coding, terminal, error reading), the purifier provides near-zero benefit.

### Root cause analysis

**Reporting bias:** The benchmark was designed to showcase the purifier's strength (structured JSON) rather than test it where it's weak (text output, source code). The 87.9% number became the headline, while the much more modest 18.7% for non-JSON types was buried in the detailed table.

**Why this matters:** In a real agent workload (e.g., software engineering agent), most tool outputs are text: source code listings, terminal output, error messages. These types see minimal compression. The overall savings on a mixed workload would be far below 87.9%.

### What should change going forward

**Always report compression statistics broken down by tool output type**, not as a single aggregate. Report median (not mean) compression across types. The headline number should be the median, not the mean.

## Current Understanding

The P3 prototype cycle has been enormously productive — a working purifier, a fixed stateful router, cost tracking, and clear experimental validation. But it has also revealed a consistent failure pattern: **simulated validation overconfidence** combined with **design assumptions not grounded in agent runtime reality**.

The four failures share a common root: building features that make sense *intellectually* and *on paper* but don't survive the transition to real agent execution. The path forward is clear:

1. **Real API testing is the gate** — no component is production-ready without a real API validation pass
2. **Stateful signals beat per-step heuristics** — acknowledge that agent complexity is emergent, not local
3. **Every signal needs a consumer** — architecture must be explicit about who responds to control signals
4. **Report the median, not just the mean** — single aggregate metrics hide distribution problems

## Key Concepts

- **Proxy variable failure:** Using a correlated but causally wrong signal (instruction length → complexity) as a routing feature
- **Interface incompleteness:** Emitting signals without defining their consumers (budget signals with no degradation handler)
- **Simulation overconfidence:** Clean synthetic benchmarks that don't survive real API contact
- **Metric aggregation blindness:** A single headline number (87.9%) that hides a bimodal distribution (96.7% vs 18.7%)
- **Agent complexity emergence:** Task difficulty in agents is determined by accumulated step state, not per-instruction features

## Open Questions

1. **How much of the 87.9% compression survives real API billing?** Need to compare character-level compression vs. token-level savings using an actual LLM API.
2. **What is the optimal graceful degradation strategy?** Summary + requote? Auto-switch to cheaper model? User notification only?
3. **Do other agent runtimes (LangGraph, AutoGen, CrewAI) have the same effort-tracking assumptions?** Or is this unique to ReAct-style custom implementations?
4. **Can simulation overconfidence be systematically prevented?** A pre-release checklist for agent components?

## Possible Thesis Ideas

1. **Failure patterns in agent system design:** A taxonomy of common design assumptions that break in real agent deployments — similar to Gilb's "software engineering failure patterns" but specific to LLM agents. Could become a measurement study or a design methodology paper.

2. **Stateful effort routing as a formal framework:** The stateful complexity tracking fix could be formalized into a general-purpose routing framework with well-defined signals, thresholds, and adaptation rules. Extends naturally from ReAct to any tool-use agent architecture.

3. **Graceful degradation for token-budgeted agents:** A complete architecture for how agents should handle resource exhaustion — partial result preservation, user communication protocols, budget request patterns. This is an open problem.

## Next Step

Advance to **Project Planning** for a new refinement cycle. The key input to project-planning is the real API validation gap — the next thesis refinement should prioritize a concrete plan to run the P3 components against real Hermes agent logs and real API calls. The failure taxonomy (Failure 1-4) should inform the thesis framing.
