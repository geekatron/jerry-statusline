# EN-005 Edge Case Handling: Orchestration Plan

> **Document ID:** EN005-ORCH-PLAN
> **Project:** jerry-statusline (ECW Status Line)
> **Workflow ID:** `en005-20260211-001`
> **Status:** ACTIVE
> **Version:** 1.0
> **Created:** 2026-02-11
> **Last Updated:** 2026-02-11

---

## L0: Workflow Overview

This orchestration coordinates the implementation of EN-005 (Edge Case Handling) for the ECW Status Line project. It combines NASA Systems Engineering (requirements + risk + V&V) with problem-solving (RED/GREEN/REFACTOR test-driven development + adversarial critique) in a cross-pollinated dual-pipeline workflow.

**Scope:** 6 tasks across 8 hours effort, batched into 3 logical groups:
- **Batch A (Color/ANSI):** TASK-001 + TASK-006 (tightly coupled color control)
- **Batch B (Atomic Writes):** TASK-005 (independent, modifies save_state)
- **Batch C (Documentation):** TASK-002 + TASK-003 + TASK-004 (all modify GETTING_STARTED.md)

**Quality target:** Weighted rubric score >= 0.92 across correctness (0.25), completeness (0.20), robustness (0.25), maintainability (0.15), documentation (0.15). Maximum 3 adversarial critique iterations.

**Strategy:** RED/GREEN/REFACTOR pattern for code tasks (TASK-001, 003, 005, 006), adversarial critique cycle for documentation tasks (TASK-002, 004).

---

## L1: Technical Plan

### Workflow Identification

| Field | Value | Source |
|-------|-------|--------|
| Workflow ID | `en005-20260211-001` | auto |
| ID Format | `{purpose}-{YYYYMMDD}-{NNN}` | semantic-date-seq |
| Base Path | `orchestration/en005-20260211-001/` | Dynamic |

**Artifact Output Locations:**
- Implementation Pipeline: `orchestration/en005-20260211-001/impl/`
- NASA-SE Pipeline: `orchestration/en005-20260211-001/nse/`
- Cross-pollination: `orchestration/en005-20260211-001/cross-pollination/`

### Workflow Diagram (ASCII)

```
    PIPELINE A (impl)                           PIPELINE B (nse)
    =================                           ================

┌──────────────────────────┐            ┌──────────────────────────┐
│ PHASE 1: RED (Batch A)   │            │ PHASE 1: Req + Risk      │
│ ──────────────────────── │            │ ──────────────────────── │
│ • ps-tdd-red             │            │ • nse-requirements       │
│   Write failing tests:   │            │ • nse-risk               │
│   - NO_COLOR env var     │            │   (parallel, background) │
│   - use_color config     │            │ STATUS: PENDING          │
│   - integration test     │            │                          │
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
│   Implement Batch A code │            │   requirements +         │
│   Implement Batch B code │            │   test coverage          │
│   Write Batch C docs     │            │ STATUS: BLOCKED          │
│                          │            │                          │
│ REFACTOR:                │            │                          │
│ • ps-tdd-refactor        │            │                          │
│   Clean up impl, keep    │            │                          │
│   tests passing          │            │                          │
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
| 1 | RED (Batch A) | Write failing tests for color tasks | ps-tdd-red | Sequential |
| 2 | GREEN + REFACTOR | Implement all code + docs, refactor | ps-tdd-green, ps-tdd-refactor | Sequential |
| 3 | Adversarial Critique | 5 critics score deliverables | ps-critic x5 | Fan-Out (background) |
| 4 | Final Revision | Fix issues, re-critique if needed | ps-tdd-revision | Sequential (loop) |

#### Pipeline B: NASA-SE (nse)

| Phase | Name | Purpose | Agents | Execution |
|-------|------|---------|--------|-----------|
| 1 | Requirements + Risk | Define requirements, assess risks | nse-requirements, nse-risk | Parallel (background) |
| 2 | V&V Planning | Create VCRM based on requirements | nse-verification | Sequential |
| 3 | V&V Execution | Execute VCRM test cases | nse-verification | Sequential |
| 4 | V&V Sign-Off | Confirm all criteria satisfied | nse-verification | Sequential |

### Work Items and Batching

#### Batch A: Color/ANSI (2h total)

**TASK-006: Add use_color config toggle (1h) - Code**
- **Gap:** G-021 (ANSI color toggle config option)
- **Strategy:** RED/GREEN/REFACTOR
- **RED:** Write test that validates `use_color: false` disables ANSI codes
- **GREEN:** Add `use_color` to config schema at line 67, modify `ansi_color()` to check config
- **REFACTOR:** Clean up config flow, ensure emoji/color are independent controls
- **Acceptance:** Config option controls ANSI codes independent of NO_COLOR env var

**TASK-001: Implement NO_COLOR support (1h) - Code**
- **Gap:** G-016 (NO_COLOR environment variable not respected)
- **Strategy:** RED/GREEN/REFACTOR
- **RED:** Write test that validates `NO_COLOR=1` overrides all color output
- **GREEN:** Modify `ansi_color()` at line 302 to check `os.environ.get("NO_COLOR")` first, return "" if set
- **REFACTOR:** Ensure NO_COLOR takes precedence over use_color config
- **Acceptance:** `NO_COLOR=1` disables all ANSI escape codes regardless of config

**Integration Test:**
- Test matrix: `use_color=true/false` × `NO_COLOR=0/1` → 4 scenarios
- Expected: NO_COLOR=1 always wins, use_color=false disables when NO_COLOR unset

#### Batch B: Atomic Writes (2h total)

**TASK-005: Implement atomic state writes (2h) - Code**
- **Gap:** G-026 (Atomic state file writes)
- **Strategy:** RED/GREEN/REFACTOR
- **RED:** Write test that simulates concurrent writes and validates no corruption
- **GREEN:** Modify `save_state()` at line 277 to use `tempfile.NamedTemporaryFile` + `os.replace()`
- **REFACTOR:** Clean up error handling, preserve existing graceful degradation
- **Acceptance:** State file writes use atomic pattern (write temp, rename)

#### Batch C: Documentation (4h total)

**TASK-002: Document UNC path limitations (2h) - Docs**
- **Gap:** G-017 (UNC path handling on Windows)
- **Strategy:** Adversarial critique cycle
- **Target:** GETTING_STARTED.md - add section on Windows UNC paths
- **Content:** Document that `\\server\share` paths may not work, recommend mapped drives or WSL
- **Acceptance:** UNC paths documented with known limitations

**TASK-003: Make git timeout configurable (1h) - Code + Docs**
- **Gap:** G-018 (Large monorepo git timeout)
- **Strategy:** RED/GREEN/REFACTOR (code already exists, needs validation + docs)
- **Current State:** `git_timeout: 2` hardcoded at line 156
- **RED:** Write test that validates config.advanced.git_timeout is respected
- **GREEN:** Code already exists! Validate it works correctly
- **REFACTOR:** Add documentation to GETTING_STARTED.md explaining the config option
- **Acceptance:** `git.timeout` configurable in config file + documented

**TASK-004: Add SSH/tmux terminal docs (1h) - Docs**
- **Gap:** G-019 (SSH/tmux terminal documentation)
- **Strategy:** Adversarial critique cycle
- **Target:** GETTING_STARTED.md - add section on SSH/tmux terminal compatibility
- **Content:** Document TERM variable requirements, tmux -2 flag, SSH terminal forwarding
- **Acceptance:** SSH/tmux terminal compatibility documented

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

### RED/GREEN/REFACTOR Strategy

**Phase 1 (RED):** Write failing tests
- Focus on Batch A color tasks first (tight coupling)
- Tests should validate expected behavior before code exists
- Expected state: Tests fail because code not implemented

**Phase 2 (GREEN):** Make tests pass
- Implement minimum code to pass tests
- Batch A: NO_COLOR env var + use_color config
- Batch B: Atomic state writes (tempfile + os.replace)
- Batch C: Documentation (GETTING_STARTED.md)
- Expected state: All tests pass, code may be messy

**Phase 2 (REFACTOR):** Clean up while keeping tests green
- Improve code structure, naming, comments
- Ensure error handling is robust
- Verify all edge cases covered
- Expected state: Clean code, all tests pass

---

## L2: Implementation Details

### Dynamic Path Configuration

```
orchestration/en005-20260211-001/
├── impl/
│   ├── phase-1-red/
│   │   └── ps-tdd-red/
│   │       └── red-phase-tests.md
│   ├── phase-2-green-refactor/
│   │   ├── ps-tdd-green/
│   │   │   └── green-phase-implementation.md
│   │   └── ps-tdd-refactor/
│   │       └── refactor-phase-cleanup.md
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
│           └── revision-summary.md
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
    └── en005-20260211-001-final.md
```

### Recovery Strategies

| Failure Mode | Recovery Strategy |
|-------------|-------------------|
| Tests fail to write correctly (RED) | Re-invoke ps-tdd-red with specific requirements |
| Implementation doesn't pass tests (GREEN) | Re-invoke ps-tdd-green, debug failing tests |
| Critic agents fail | Re-invoke failed critics only |
| Score < 0.92 after 3 iterations | Escalate to user for decision |
| nse-requirements finds new gaps | Add to EN-005, extend scope |
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
| NO_COLOR conflicts with use_color | Medium | Medium | Define precedence: NO_COLOR > use_color |
| Atomic writes break on read-only fs | Low | Low | Preserve existing graceful degradation |
| Git timeout config not respected | Low | Medium | Add config validation test |
| UNC path edge cases unknown | Medium | Medium | Document known limitations, defer comprehensive testing |
| Critics disagree on docs quality | Low | Medium | Weighted synthesis, majority rules |
| RED phase tests too brittle | Medium | Low | Focus on behavior, not implementation details |

---

## Next Actions

1. Execute Phase 1: nse-requirements + nse-risk (parallel background agents)
2. Execute Phase 1: ps-tdd-red writes failing tests for Batch A (RED)
3. Wait for all Phase 1 agents to complete
4. Execute Barrier 1 cross-pollination
5. Execute Phase 2: ps-tdd-green implements all code/docs (GREEN)
6. Execute Phase 2: ps-tdd-refactor cleans up implementation (REFACTOR)
7. Execute Phase 2: nse-verification creates VCRM
8. Execute Barrier 2 cross-pollination
9. Execute Phase 3: 5 adversarial critics (parallel background agents)
10. Execute Phase 3: nse-verification executes VCRM

---

## Disclaimer

This orchestration plan was generated by the orch-planner agent (v2.1.0) following the proven dual-pipeline cross-pollinated pattern from FEAT-002. Human review recommended before execution.
