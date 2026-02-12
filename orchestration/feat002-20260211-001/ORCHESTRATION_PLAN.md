# FEAT-002 High-Priority Improvements: Orchestration Plan

> **Document ID:** FEAT002-ORCH-PLAN
> **Project:** jerry-statusline (ECW Status Line)
> **Workflow ID:** `feat002-20260211-001`
> **Status:** ACTIVE
> **Version:** 2.0
> **Created:** 2026-02-11
> **Last Updated:** 2026-02-11

---

## L0: Workflow Overview

This orchestration coordinates the implementation of FEAT-002 (High-Priority Improvements) for the ECW Status Line project. It combines NASA Systems Engineering (requirements + risk + V&V) with problem-solving (implementation + adversarial critique) in a cross-pollinated pipeline.

**Scope reduction:** Re-assessment against EN-002 deliverables reduced effort from 18h to ~4.75h. Seven of eleven tasks are already completed or partially completed by EN-002 work. Seven tasks remain across two enablers (EN-003: Code Hardening, EN-004: Documentation).

**Quality target:** Weighted rubric score >= 0.92 across correctness (0.25), completeness (0.20), robustness (0.25), maintainability (0.15), documentation (0.15). Maximum 3 adversarial critique iterations.

---

## L1: Technical Plan

### Workflow Identification

| Field | Value | Source |
|-------|-------|--------|
| Workflow ID | `feat002-20260211-001` | auto |
| ID Format | `{purpose}-{YYYYMMDD}-{NNN}` | semantic-date-seq |
| Base Path | `orchestration/feat002-20260211-001/` | Dynamic |

**Artifact Output Locations:**
- Implementation Pipeline: `orchestration/feat002-20260211-001/impl/`
- NASA-SE Pipeline: `orchestration/feat002-20260211-001/nse/`
- Cross-pollination: `orchestration/feat002-20260211-001/cross-pollination/`

### Workflow Diagram (ASCII)

```
    PIPELINE A (impl)                           PIPELINE B (nse)
    =================                           ================

┌──────────────────────────┐            ┌──────────────────────────┐
│ PHASE 1: Implementation  │            │ PHASE 1: Req + Risk      │
│ ──────────────────────── │            │ ──────────────────────── │
│ • MAIN CONTEXT creates   │            │ • nse-requirements       │
│   EN-003 code changes    │            │ • nse-risk               │
│   EN-004 documentation   │            │   (parallel, background) │
│ STATUS: PENDING          │            │ STATUS: PENDING          │
└────────────┬─────────────┘            └────────────┬─────────────┘
             │                                       │
             ▼                                       ▼
    ╔══════════════════════════════════════════════════════════════╗
    ║                      SYNC BARRIER 1                          ║
    ║  ┌────────────────────────────────────────────────────────┐  ║
    ║  │ impl→nse: Implementation draft for V&V scope           │  ║
    ║  │ nse→impl: Requirements + Risk findings for refinement  │  ║
    ║  └────────────────────────────────────────────────────────┘  ║
    ║  STATUS: PENDING                                             ║
    ╚══════════════════════════════════════════════════════════════╝
             │                                       │
             ▼                                       ▼
┌──────────────────────────┐            ┌──────────────────────────┐
│ PHASE 2: Adversarial     │            │ PHASE 2: V&V Execution   │
│ ──────────────────────── │            │ ──────────────────────── │
│ FAN-OUT (5 critics):     │            │ • nse-verification       │
│ • ps-critic (red team)   │            │   Verify requirements    │
│ • ps-critic (blue team)  │            │   against deliverables   │
│ • ps-critic (devil's     │            │ STATUS: BLOCKED          │
│   advocate)              │            │                          │
│ • ps-critic (steelman)   │            │                          │
│ • ps-critic (strawman)   │            │                          │
│ FAN-IN: Score synthesis  │            │                          │
│ STATUS: BLOCKED          │            │                          │
└────────────┬─────────────┘            └────────────┬─────────────┘
             │                                       │
             ▼                                       ▼
    ╔══════════════════════════════════════════════════════════════╗
    ║                      SYNC BARRIER 2                          ║
    ║  ┌────────────────────────────────────────────────────────┐  ║
    ║  │ impl→nse: Critique results for V&V confirmation        │  ║
    ║  │ nse→impl: V&V findings for final revision              │  ║
    ║  └────────────────────────────────────────────────────────┘  ║
    ║  STATUS: PENDING                                             ║
    ╚══════════════════════════════════════════════════════════════╝
             │                                       │
             ▼                                       ▼
┌──────────────────────────┐            ┌──────────────────────────┐
│ PHASE 3: Final Revision  │            │ PHASE 3: V&V Sign-Off    │
│ ──────────────────────── │            │ ──────────────────────── │
│ • MAIN CONTEXT fixes     │            │ • nse-verification       │
│   issues from B2         │            │   Final confirmation     │
│ • Loop to Phase 2 if     │            │ STATUS: BLOCKED          │
│   score < 0.92           │            │                          │
│   (max 3 iterations)     │            │                          │
│ STATUS: BLOCKED          │            │                          │
└──────────────────────────┘            └──────────────────────────┘
```

### Pipeline Definitions

#### Pipeline A: Implementation (impl)

| Phase | Name | Purpose | Agents | Execution |
|-------|------|---------|--------|-----------|
| 1 | Implementation | Create EN-003 code + EN-004 docs | MAIN CONTEXT | Sequential |
| 2 | Adversarial Critique | 5 critics score deliverables | ps-critic x5 | Fan-Out (background) |
| 3 | Final Revision | Fix issues, re-critique if needed | MAIN CONTEXT | Sequential (loop) |

#### Pipeline B: NASA-SE (nse)

| Phase | Name | Purpose | Agents | Execution |
|-------|------|---------|--------|-----------|
| 1 | Requirements + Risk | Define requirements, assess risks | nse-requirements, nse-risk | Parallel (background) |
| 2 | V&V Execution | Verify requirements met | nse-verification | Sequential |
| 3 | V&V Sign-Off | Confirm all criteria satisfied | nse-verification | Sequential |

### Remaining Work Items

#### EN-003: Code Hardening (Remaining: ~2.5h)

| Task | Gap | Description | Effort |
|------|-----|-------------|--------|
| TASK-001 | G-007 | Add `encoding='utf-8', errors='replace'` to subprocess.run() calls | 0.5h |
| TASK-003 | G-014 | Complete ASCII fallback (progress bar `#/-`, git status `+/*`, token indicators `>/<`) | 1.0h |
| TASK-004 | G-008 | Test VS Code terminal compatibility and document | 1.0h |

#### EN-004: Documentation Completion (Remaining: ~2.25h)

| Task | Gap | Description | Effort |
|------|-----|-------------|--------|
| TASK-003 | G-013 | Document Claude Code JSON schema dependency | 1.0h |
| TASK-005 | - | Clarify WSL vs native Windows guidance | 0.5h |
| TASK-006 | - | Add CI status badge to README.md | 0.25h |
| TASK-007 | - | Update version changelog | 0.5h |

### Adversarial Critique Protocol

**Weighted Rubric (target >= 0.92):**

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Correctness | 0.25 | Code works as intended, no regressions |
| Completeness | 0.20 | All gaps addressed, no missing work |
| Robustness | 0.25 | Edge cases handled, graceful degradation |
| Maintainability | 0.15 | Clean code, consistent patterns |
| Documentation | 0.15 | Accurate, complete, user-friendly |

**Critic Roles:**

| Role | Perspective | Focus |
|------|-------------|-------|
| Red Team | Adversarial attacker | Security, edge cases, failure modes |
| Blue Team | Defensive reviewer | Overall quality, defensive posture |
| Devil's Advocate | Contrary position | Challenge assumptions, question approach |
| Steelman | Best interpretation | Identify strengths, validate architecture |
| Strawman | Weakest link finder | Find the most vulnerable aspects |

**Iteration Protocol:**
1. Creator implements changes
2. 5 critics score independently (background, parallel)
3. Synthesize scores, compute weighted rubric
4. If score >= 0.92: APPROVE, proceed to V&V
5. If score < 0.92: Creator fixes, repeat (max 3 iterations)

---

## L2: Implementation Details

### Dynamic Path Configuration

```
orchestration/feat002-20260211-001/
├── impl/
│   ├── phase-1-implementation/
│   │   └── implementation-summary.md
│   ├── phase-2-critique/
│   │   ├── critic-red-team/
│   │   │   └── critic-red-team-review.md
│   │   ├── critic-blue-team/
│   │   │   └── critic-blue-team-review.md
│   │   ├── critic-devils-advocate/
│   │   │   └── critic-devils-advocate-review.md
│   │   ├── critic-steelman/
│   │   │   └── critic-steelman-review.md
│   │   └── critic-strawman/
│   │       └── critic-strawman-review.md
│   └── phase-3-revision/
│       └── revision-summary.md
├── nse/
│   ├── phase-1-requirements/
│   │   ├── nse-requirements/
│   │   │   └── nse-requirements-analysis.md
│   │   └── nse-risk/
│   │       └── nse-risk-assessment.md
│   ├── phase-2-vv/
│   │   └── nse-verification/
│   │       └── nse-verification-report.md
│   └── phase-3-signoff/
│       └── nse-verification/
│           └── nse-verification-signoff.md
├── cross-pollination/
│   ├── barrier-1/
│   │   ├── impl-to-nse/
│   │   │   └── handoff.md
│   │   └── nse-to-impl/
│   │       └── handoff.md
│   └── barrier-2/
│       ├── impl-to-nse/
│       │   └── handoff.md
│       └── nse-to-impl/
│           └── handoff.md
└── synthesis/
    └── feat002-20260211-001-final.md
```

### Recovery Strategies

| Failure Mode | Recovery Strategy |
|-------------|-------------------|
| Critic agents fail | Re-invoke failed critics only |
| Score < 0.92 after 3 iterations | Escalate to user for decision |
| nse-requirements finds new gaps | Add to EN-003/EN-004, extend scope |
| V&V rejects deliverables | Loop back to Phase 2 critique |
| Session interrupted | Resume from ORCHESTRATION.yaml state |

### Execution Constraints

| Constraint | Value | Rationale |
|-----------|-------|-----------|
| Max concurrent agents | 5 | Critic fan-out |
| Max adversarial iterations | 3 | User requirement |
| Target quality score | >= 0.92 | User requirement |
| Agent nesting | 1 level max | P-003 compliance |
| File persistence | Required | P-002 compliance |

---

## Risk Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| EN-002 overlap misjudged | Low | Medium | Verify each "DONE" claim against actual code |
| ASCII fallback incomplete | Medium | Medium | Test with `use_emoji: false` on all segments |
| VS Code terminal issues | Low | Low | VS Code uses xterm-256color, ANSI should work |
| JSON schema changes in Claude Code | Medium | High | Document observed schema, note volatility |
| Critics disagree significantly | Low | Medium | Weighted synthesis, majority rules |

---

## Next Actions

1. Execute Phase 1: nse-requirements + nse-risk (parallel background agents)
2. Execute Phase 1: MAIN CONTEXT implements EN-003 + EN-004 code/docs
3. Wait for all Phase 1 agents to complete
4. Execute Barrier 1 cross-pollination
5. Execute Phase 2: 5 adversarial critics (parallel background agents)

---

## Disclaimer

This orchestration plan was generated by the main context following the orch-planner agent specification (v2.1.0). Human review recommended before execution.
