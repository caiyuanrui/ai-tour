# 2026-06-12 — Agent Architectures

Course: Agents
Topic: Agent Architectures
Stage: Day 4 — Code-as-Action Architectures
Confidence: 0.65 → 0.75

## Today's Question

Beyond the ReAct pattern (text-based Thought/Action/Observation), how do modern agent architectures use **code execution** as a primary action space? What architectural patterns emerge when agents generate and execute programmatic actions instead of discrete tool calls?

## Main Paper

### Metadata

- Title: CodeAct: Your LLM Agent Acts Better when Generating Code
- Authors: Xingyao Wang, Yangyi Chen, Lifan Yuan, Yizhe Zhang, Yunzhu Li, Hao Peng, Heng Ji
- Year: 2024
- Venue: ICML 2024
- Link: https://arxiv.org/abs/2402.01030

### Why this paper?

All prior architecture notes focused on text-based reasoning-action patterns: ReAct interleaves natural language Thought/Action/Observation, ToT explores reasoning branches in text, Reflexion uses verbal self-reflection. CodeAct represents a fundamentally different architectural choice — instead of emitting structured JSON/text actions, the agent generates executable Python code as its universal action representation. This is important because it changes the architecture at the action interface layer, which is one of the most active design spaces in 2025-2026 agent systems.

### Core Problem

LLM agents are typically prompted to produce actions by generating JSON or text in pre-defined formats. This approach has two limitations:

1. **Constrained action space**: The agent can only call pre-defined tools/functions. It cannot compose them, loop, conditionally branch, or adapt its action representation on the fly.
2. **Restricted flexibility**: Multi-step workflows require many turns (one action per turn), wasting context and latency. The agent cannot "collapse" a sequence of operations into a single execution.

### Main Idea

Use **executable Python code** as a unified action space for LLM agents. CodeAct:

- Accepts code as agent actions (not JSON/text)
- Executes code in a Python interpreter
- Feeds execution output (stdout, stderr, exceptions) back as observations
- Allows the agent to dynamically revise, compose, or generate new code based on runtime feedback

The key architectural shift: **code is both the action and the plan**. Instead of "I need to call tool A, then tool B, then tool C" across multiple turns, the agent writes a single Python program that calls A, passes output to B, and processes C's result.

### Technical Details

**CodeAct Loop:**

```
Observation → [LLM generates Python code] → Execute → 
  stdout/stderr/exception → [LLM generates next code or natural language] → ...
```

- **Action space**: Any Python code (imports, API calls, data processing, file I/O, ML training loops)
- **Observation space**: Execution results (text output, error traces, variable values)
- **Termination condition**: Agent emits a natural language response (signaling completion)

**CodeActInstruct Dataset:**
- 7k multi-turn interactions collected using CodeAct
- Used to fine-tune CodeActAgent (Llama2, Mistral)
- Integrates with Python interpreter and can autonomously self-debug

**CodeActAgent capabilities:**
- Uses existing Python libraries for sophisticated tasks (e.g., model training)
- Autonomously self-debugs by reading error traces and generating fixes
- Can dynamically import and compose tools

### Results

- On API-Bank (tool-use benchmark): CodeAct outperforms JSON/text action formats on **17 LLMs**
- Up to **20% higher success rate** than alternatives
- CodeActAgent (fine-tuned) maintains general language capability while improving agent-oriented task performance

### Limitations

- Depends on a Python interpreter being available (security/sandboxing concerns)
- Code generation quality depends on LLM's coding ability — weaker coders produce worse agents
- Error recovery is limited to what the LLM can debug from tracebacks
- Not all tasks benefit from code-as-action (e.g., simple API calls may be overkill)
- Security: arbitrary code execution requires robust sandboxing

### Relation to Topic (Agent Architectures)

CodeAct introduces a **code-native architecture** that is distinct from the text-based ReAct lineage. This matters for the architecture map because:

- It shows that **action representation format** is an architectural design choice, not a given
- Code-as-action enables **composition** (import, loop, condition) as a first-class capability
- The architecture is **interpreter-mediated**: an external runtime (Python interpreter) sits between the LLM and the environment, executing actions and returning results
- This anticipates the "harness" perspective where the infrastructure around the LLM is as important as the model itself

### Modern perspective (2026)

CodeAct's insight — that code is a better action space than JSON — has been absorbed into most modern agent frameworks. Hermes Agent, OpenHands, Claude Code, and others all use code execution as a primary action modality. The 2026 survey "Agent Systems with Harness Engineering" formalizes this as the **Action Interface** layer within the broader harness architecture. The open question today is less "should agents use code?" and more **"how should the code execution environment be designed for safety, debugging, and long-running tasks?"**

## Related Papers

### Paper 1: SWE-agent — Agent-Computer Interfaces Enable Automated Software Engineering

- Authors: John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press
- Year: 2024
- Venue: NeurIPS 2024
- Link: https://arxiv.org/abs/2405.15793

**Contribution:** Introduces the concept of **Agent-Computer Interface (ACI)** — a custom interface designed specifically for LM agents, analogous to how IDEs help human developers. The SWE-agent system achieves 12.5% pass@1 on SWE-bench (state-of-the-art at time of publication).

**Relation to CodeAct:** Where CodeAct uses raw Python code as a universal action space, SWE-agent goes further: it designs specialized interfaces for each environment (bash, file editor, browser) rather than a single code interpreter. The ACI concept argues that **different environments need different action interfaces** — code is good for computation, but repository navigation needs structured file browsing commands. Together they show the action interface design space is rich and consequential.

**Should it be deep-read later?** Yes — especially the ACI design principles. The insight that LM agents are a new category of end users with their own needs (different from human users) is foundational.

### Paper 2: Agent Systems with Harness Engineering — A Systematic Survey

- Authors: Xinyu Tang, Han Peng, Guoxin Chen, Yuze Shi, Zitao Su, Peiyu Liu, Wayne Xin Zhao, Yawen Li, Zhe Xue
- Year: 2026
- Link: https://openreview.net/pdf?id=nM5tDHrQsx

**Contribution:** Formalizes **harness engineering** as the joint optimization of scaffold (workflow, memory, skills, multi-agent) and model (context engineering, agentic training). Proposes a three-layer evolution: Action Interface → Workflow Infrastructure → User-Centric Persistence.

**Relation to CodeAct:** Places CodeAct at the **Action Interface layer** — the first layer of harness evolution. The survey shows that action interface design (CodeAct, SWE-agent) is just one component; modern architectures also need workflow infrastructure (task planning, error recovery) and user-centric persistence (memory, cross-session continuity). This contextualizes CodeAct as an important but partial contribution to the full agent architecture stack.

**Should it be deep-read later?** Yes — this survey is essential for understanding the full architecture landscape. It shifts focus from "what agents can do" to "how infrastructure enables them to do it."

## Current Understanding

The agent architecture map now has a clearer branching structure:

**Text-based action architectures (already covered):**
- ReAct (Yao 2023) — Thought/Action/Observation interleaving, context window as memory
- Reflexion (Shinn 2023) — adds verbal self-reflection after failures
- ToT (Yao 2023) — tree-structured reasoning with breadth-first search
- GoT (Besta 2024) — graph-structured reasoning with non-linear dependencies

**Code-native action architectures (today's addition):**
- CodeAct (Wang 2024) — Python code as universal action space
- SWE-agent (Yang 2024) — environment-specific ACIs instead of universal code

**Harness engineering (meta-perspective):**
- The infrastructure stack (harness) is a first-class architectural concern
- Three layers: Action Interface → Workflow → Persistence
- CodeAct and SWE-agent operate at the Action Interface layer

Key insight: **Architecture design is not just about reasoning patterns (ReAct vs ToT) but also about action representation (code vs JSON vs structured interfaces).** These dimensions are orthogonal — one could build a CodeAct variant with tree-structured reasoning.

## Key Concepts

- Code-native action space: Using executable code instead of structured text as agent actions
- Interpreted execution loop: LLM → code → interpreter → observation → LLM
- Action composition: Code enables import, composition, and chaining of operations
- Agent-Computer Interface (ACI): Interface designed specifically for LM agents, not humans
- Harness engineering: Formal study of the scaffold infrastructure around foundation models
- Action Interface layer: The first layer of harness that connects model to environment

## Open Questions

- Is code-native always better than text-native for agent actions, or does it depend on task modality?
- How should the code interpreter be sandboxed without limiting agent capability?
- Can a single universal action space (CodeAct's Python) cover all needs, or do we need multiple environment-specific ACIs (SWE-agent's approach)?
- What happens to the ReAct pattern when the action is code — is explicit "thinking" still needed between code executions?
- How does code-as-action scale to multi-agent settings where different agents might use different code environments?
- **New question from today:** Is the harness itself an architecture to study separately from the agent's reasoning pattern? The Tang 2026 survey suggests yes, but most current literature conflates them.

## Possible Thesis Ideas

- **Adaptive action-format selection**: Build an architecture that dynamically switches between text-based tool calls, code execution, and structured interfaces based on task difficulty and environment constraints. This would unify the ReAct lineage and the CodeAct lineage.
- **CodeAct + reflection**: Extend CodeAct with a reflection module that analyzes execution traces (not just error messages) to improve code generation across turns — essentially combining verbal reflection (Reflexion) with code-native execution.
- **Multi-agent CodeAct**: Design a multi-agent system where sub-agents communicate via shared code modules rather than natural language, potentially reducing ambiguity in inter-agent handoffs.

## Next Step

Stay on Agent Architectures for one more day (Day 5). The confidence is approaching 0.75 but is not yet at the 0.80 advance threshold. The next session should explore the **workflow infrastructure layer** — task decomposition and planning within architectures (e.g., LLM+P, AdaPlanner, or related workflow orchestration papers) — to round out the architecture picture before advancing to Tool Use.
