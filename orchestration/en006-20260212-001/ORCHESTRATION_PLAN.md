# EN-006 Platform Expansion: Orchestration Plan

> **Document ID:** EN006-ORCH-PLAN
> **Project:** jerry-statusline (ECW Status Line)
> **Workflow ID:** `en006-20260212-001`
> **Status:** ACTIVE
> **Version:** 1.0
> **Created:** 2026-02-12
> **Last Updated:** 2026-02-12

---

## L0: Workflow Overview

This orchestration coordinates the implementation of EN-006 (Platform Expansion) for the ECW Status Line project. It combines NASA Systems Engineering (requirements + risk + V&V) with problem-solving (RED/GREEN/REFACTOR test-driven development + adversarial critique) in a cross-pollinated dual-pipeline workflow.

**Scope:** 2 tasks across 2 hours effort:
- **TASK-001:** Add upgrade path documentation (1h) - DOCS
- **TASK-002:** Add schema version checking (1h) - CODE

**Quality target:** Weighted rubric score >= 0.92 across correctness (0.25), completeness (0.20), robustness (0.25), maintainability (0.15), documentation (0.15). Maximum 3 adversarial critique iterations.

**Strategy:** RED/GREEN/REFACTOR pattern for the code task (TASK-002), adversarial critique cycle for the documentation task (TASK-001). Both tasks are related to forward compatibility and are batched together.

---

## L1: Technical Plan

### Workflow Identification

| Field | Value | Source |
|-------|-------|--------|
| Workflow ID | `en006-20260212-001` | auto |
| ID Format | `{purpose}-{YYYYMMDD}-{NNN}` | semantic-date-seq |
| Base Path | `orchestration/en006-20260212-001/` | Dynamic |

**Artifact Output Locations:**
- Implementation Pipeline: `orchestration/en006-20260212-001/impl/`
- NASA-SE Pipeline: `orchestration/en006-20260212-001/nse/`
- Cross-pollination: `orchestration/en006-20260212-001/cross-pollination/`

### Workflow Diagram (ASCII)

```
    PIPELINE A (impl)                           PIPELINE B (nse)
    =================                           ================

┌──────────────────────────┐            ┌──────────────────────────┐
│ PHASE 1: RED             │            │ PHASE 1: Req + Risk      │
│ ──────────────────────── │            │ ──────────────────────── │
│ • ps-tdd-red             │            │ • nse-requirements       │
│   Write failing tests:   │            │ • nse-risk               │
│   - Schema version check │            │   (parallel, background) │
│   - Version mismatch warn│            │ STATUS: PENDING          │
│   - Backward compat      │            │                          │
│ STATUS: PENDING          │            │                          │
└────────────┬─────────────┘            └────────────┬─────────────┘
             │                                       │
             ▼                                       ▼
    ╔══════════════════════════════════════════════════════════════╗
    ║                      SYNC BARRIER 1                          ║
    ║  ┌────────────────────────────────────────────────────────┐  ║
    ║  │ impl→nse: Test requirements for V&V scope              │  ║
    ║  │ nse→impl: Requirements + Risk findings for tests       │  ║
    ║  └────────────────────────────────────────────────────────┘  ║
    ║  STATUS: PENDING                                             ║
    ╚══════════════════════════════════════════════════════════════╝
             │                                       │
             ▼                                       ▼
┌──────────────────────────┐            ┌──────────────────────────┐
│ PHASE 2: GREEN + REFACTOR│            │ PHASE 2: V&V Planning    │
│ ──────────────────────── │            │ ──────────────────────── │
│ GREEN:                   │            │ • nse-verification       │
│ • ps-tdd-green           │            │   Create VCRM based on   │
│   Implement schema ver   │            │   requirements +         │
│   checking code          │            │   test coverage          │
│   Write upgrade docs     │            │ STATUS: BLOCKED          │
│                          │            │                          │
│ REFACTOR:                │            │                          │
│ • ps-tdd-refactor        │            │                          │
│   Clean up, keep tests   │            │                          │
│   passing                │            │                          │
│ STATUS: BLOCKED          │            │                          │
└────────────┬─────────────┘            └────────────┬─────────────┘
             │                                       │
             ▼                                       ▼
    ╔══════════════════════════════════════════════════════════════╗
    ║                      SYNC BARRIER 2                          ║
    ║  ┌────────────────────────────────────────────────────────┐  ║
    ║  │ impl→nse: Implementation + tests for V&V execution     │  ║
    ║  │ nse→impl: VCRM test cases for final validation        │  ║
    ║  └────────────────────────────────────────────────────────┘  ║
    ║  STATUS: PENDING                                             ║
    ╚══════════════════════════════════════════════════════════════╝
             │                                       │
             ▼                                       ▼
┌──────────────────────────┐            ┌──────────────────────────┐
│ PHASE 3: Adversarial     │            │ PHASE 3: V&V Execution   │
│ ──────────────────────── │            │ ──────────────────────── │
│ FAN-OUT (5 critics):     │            │ • nse-verification       │
│ • ps-critic (red team)   │            │   Execute VCRM test      │
│ • ps-critic (blue team)  │            │   cases, verify all      │
│ • ps-critic (devil's     │            │   requirements met       │
│   advocate)              │            │ STATUS: BLOCKED          │
│ • ps-critic (steelman)   │            │                          │
│ • ps-critic (strawman)   │            │                          │
│ FAN-IN: Score synthesis  │            │                          │
│ STATUS: BLOCKED          │            │                          │
└────────────┬─────────────┘            └────────────┬─────────────┘
             │                                       │
             ▼                                       ▼
    ╔══════════════════════════════════════════════════════════════╗
    ║                      SYNC BARRIER 3                          ║
    ║  ┌────────────────────────────────────────────────────────┐  ║
    ║  │ impl→nse: Critique results for V&V confirmation        │  ║
    ║  │ nse→impl: V&V findings for final revision              │  ║
    ║  └────────────────────────────────────────────────────────┘  ║
    ║  STATUS: PENDING                                             ║
    ╚══════════════════════════════════════════════════════════════╝
             │                                       │
             ▼                                       ▼
┌──────────────────────────┐            ┌──────────────────────────┐
│ PHASE 4: Final Revision  │            │ PHASE 4: V&V Sign-Off    │
│ ──────────────────────── │            │ ──────────────────────── │
│ • ps-tdd-revision        │            │ • nse-verification       │
│   Apply critique/V&V     │            │   Final confirmation     │
│   feedback               │            │ STATUS: BLOCKED          │
│ • Loop to Phase 3 if     │            │                          │
│   score < 0.92           │            │                          │
│   (max 3 iterations)     │            │                          │
│ STATUS: BLOCKED          │            │                          │
└──────────────────────────┘            └──────────────────────────┘
```

### Pipeline Definitions

#### Pipeline A: Implementation (impl)

| Phase | Name | Purpose | Agents | Execution |
|-------|------|---------|--------|-----------|
| 1 | RED | Write failing tests for schema version checking | ps-tdd-red | Sequential |
| 2 | GREEN + REFACTOR | Implement code + docs, refactor | ps-tdd-green, ps-tdd-refactor | Sequential |
| 3 | Adversarial Critique | 5 critics score deliverables | ps-critic x5 | Fan-Out (background) |
| 4 | Final Revision | Fix issues, re-critique if needed | ps-tdd-revision | Sequential (loop) |

#### Pipeline B: NASA-SE (nse)

| Phase | Name | Purpose | Agents | Execution |
|-------|------|---------|--------|-----------|
| 1 | Requirements + Risk | Define requirements, assess risks | nse-requirements, nse-risk | Parallel (background) |
| 2 | V&V Planning | Create VCRM based on requirements | nse-verification | Sequential |
| 3 | V&V Execution | Execute VCRM test cases | nse-verification | Sequential |
| 4 | V&V Sign-Off | Confirm all criteria satisfied | nse-verification | Sequential |

### Work Items

#### TASK-001: Add Upgrade Path Documentation (1h) - DOCS

- **Gap:** G-022 (Upgrade path documentation)
- **Strategy:** Adversarial critique cycle
- **Target:** GETTING_STARTED.md - add section on upgrade instructions
- **Content:**
  - Version migration instructions (v1.x → v2.x)
  - Config file migration guidance
  - State file compatibility notes
  - Breaking change checklist
- **Acceptance:** Upgrade instructions in GETTING_STARTED.md

#### TASK-002: Add Schema Version Checking (1h) - CODE

- **Gap:** (implicit - forward compatibility support)
- **Strategy:** RED/GREEN/REFACTOR
- **RED:** Write tests that validate:
  - Schema version field exists in config/state structures
  - Version mismatch produces user-friendly warning
  - Unversioned configs load with backward compatibility
  - Version comparison logic works correctly
- **GREEN:** Implement:
  - Add `schema_version` field to DEFAULT_CONFIG and state file
  - Add version check on config load (compare against expected)
  - Warning message when version mismatch detected
  - Graceful fallback for unversioned configs (treat as v1.0)
- **REFACTOR:** Clean up version handling, ensure no regressions
- **Acceptance:** Schema version field in config/state, mismatch detection with warning, backward compat

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
1. Creator implements changes (RED/GREEN/REFACTOR)
2. 5 critics score independently (background, parallel)
3. Synthesize scores, compute weighted rubric
4. If score >= 0.92: APPROVE, proceed to V&V
5. If score < 0.92: Creator fixes, repeat (max 3 iterations)

---

## L2: Implementation Details

### Dynamic Path Configuration

```
orchestration/en006-20260212-001/
├── impl/
│   ├── phase-1-red/
│   │   └── ps-tdd-red/
│   │       └── ps-tdd-red-tests.md
│   ├── phase-2-green-refactor/
│   │   ├── ps-tdd-green/
│   │   │   └── ps-tdd-green-implementation.md
│   │   └── ps-tdd-refactor/
│   │       └── ps-tdd-refactor-cleanup.md
│   ├── phase-3-critique/
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
│   └── phase-4-revision/
│       └── ps-tdd-revision/
│           └── ps-tdd-revision-fixes.md
├── nse/
│   ├── phase-1-requirements/
│   │   ├── nse-requirements/
│   │   │   └── nse-requirements-analysis.md
│   │   └── nse-risk/
│   │       └── nse-risk-assessment.md
│   ├── phase-2-vv-planning/
│   │   └── nse-verification/
│   │       └── vcrm-test-plan.md
│   ├── phase-3-vv-execution/
│   │   └── nse-verification/
│   │       └── vcrm-execution-report.md
│   └── phase-4-signoff/
│       └── nse-verification/
│           └── nse-verification-signoff.md
├── cross-pollination/
│   ├── barrier-1/
│   │   ├── impl-to-nse/
│   │   │   └── handoff.md
│   │   └── nse-to-impl/
│   │       └── handoff.md
│   ├── barrier-2/
│   │   ├── impl-to-nse/
│   │   │   └── handoff.md
│   │   └── nse-to-impl/
│   │       └── handoff.md
│   └── barrier-3/
│       ├── impl-to-nse/
│       │   └── handoff.md
│       └── nse-to-impl/
│           └── handoff.md
└── synthesis/
    └── en006-20260212-001-final.md
```

### Recovery Strategies

| Failure Mode | Recovery Strategy |
|-------------|-------------------|
| Tests fail to write correctly (RED) | Re-invoke ps-tdd-red with specific requirements |
| Implementation doesn't pass tests (GREEN) | Re-invoke ps-tdd-green, debug failing tests |
| Critic agents fail | Re-invoke failed critics only |
| Score < 0.92 after 3 iterations | Escalate to user for decision |
| nse-requirements finds new gaps | Add to EN-006 or defer |
| V&V rejects deliverables | Loop back to Phase 3 critique |
| Session interrupted | Resume from ORCHESTRATION.yaml state |

### Execution Constraints

| Constraint | Value | Rationale |
|-----------|-------|-----------|
| Max concurrent agents | 5 | Critic fan-out |
| Max adversarial iterations | 3 | User requirement |
| Target quality score | >= 0.92 | User requirement |
| Agent nesting | 1 level max | P-003 compliance |
| File persistence | Required | P-002 compliance |
| Test execution | After each phase | TDD validation |

---

## Risk Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Schema version breaks existing configs | Medium | High | Treat missing version as v1.0, never reject |
| Upgrade docs become stale quickly | Low | Medium | Keep instructions version-agnostic where possible |
| Version mismatch warning too noisy | Low | Low | Only warn once per session, use debug_log |
| Config migration path unclear | Medium | Medium | Provide concrete before/after examples |

---

## Next Actions

1. Execute Phase 1: nse-requirements + nse-risk (parallel background agents)
2. Execute Phase 1: ps-tdd-red writes failing tests for schema version checking (RED)
3. Wait for all Phase 1 agents to complete
4. Execute Barrier 1 cross-pollination
5. Execute Phase 2: ps-tdd-green implements code + docs (GREEN)
6. Execute Phase 2: ps-tdd-refactor cleans up implementation (REFACTOR)
7. Execute Phase 2: nse-verification creates VCRM
8. Execute Barrier 2 cross-pollination
9. Execute Phase 3: 5 adversarial critics (parallel background agents)
10. Execute Phase 3: nse-verification executes VCRM

---

## Disclaimer

This orchestration plan was generated by the orch-planner agent (v2.1.0) following the proven dual-pipeline cross-pollinated pattern from EN-005. Human review recommended before execution.
