# Red Team Review -- EN-005

**Reviewer:** critic-red-team (adversarial)
**Workflow:** en005-20260211-001
**Date:** 2026-02-12
**Files Reviewed:** statusline.py, test_statusline.py, GETTING_STARTED.md
**Methodology:** Code inspection + automated adversarial test execution

---

## Scores

| Dimension | Weight | Score | Findings |
|-----------|--------|-------|----------|
| Correctness | 0.25 | 0.93 | Core logic correct. NO_COLOR="" (empty string) handled properly. String-for-number config crashes script (minor). ANSI injection via config fields passes through unsanitized. |
| Completeness | 0.20 | 0.88 | All 15 requirements addressed in code. However: test VT-EN005-003 (empty string NO_COLOR) is specified in VCRM but NOT actually implemented in test suite. Documentation has stale references to old "cache" segment naming. |
| Robustness | 0.25 | 0.91 | Excellent graceful degradation on read-only FS, missing HOME, corrupt state. Atomic write works correctly. Concurrent invocations produce valid state files. Minor: string-for-number in JSON payload produces "ECW: Error - TypeError" instead of safe fallback. |
| Maintainability | 0.15 | 0.95 | Clean DRY pattern with `_colors_enabled()`. Consistent config threading. Good type hints. Ruff-clean. |
| Documentation | 0.15 | 0.82 | SSH/tmux instructions are correct. However: verification section shows obsolete output format (cache % instead of fresh/cached tokens). Quick Reference "Color Meanings" table references Cache/Session color thresholds that do not exist in code. Example 4 uses `"cache": false` but correct key is `"tokens"`. |
| **Weighted Average** | | **0.905** | Below 0.92 target. Documentation inaccuracies and missing test are primary deductors. |

---

## Critical Findings (must fix)

### C-1: Documentation shows wrong segment format in Verification section

**Location:** GETTING_STARTED.md lines 451-462
**Severity:** Critical (user-facing confusion)

The "What you should see" section shows:
```
... | ⚡ 0% | ⏱️ 0m [░░░░░░░░░░] 0% | ...
```

But the actual script output (verified by running tests) produces:
```
... | ⚡ 0→ 0↺ | ⏱️ 0m 0tok | ...
```

The tokens segment shows fresh/cached token counts with arrow indicators, NOT a percentage. The session segment shows duration + total tokens, NOT a progress bar. This discrepancy will confuse new users who follow the Getting Started guide and see different output than documented.

The segment breakdown table at line 462 describes the segment as "Cache efficiency | Shows % of tokens served from cache" which is completely wrong -- it actually shows absolute fresh/cached token counts.

### C-2: Quick Reference Color Meanings table references non-existent thresholds

**Location:** GETTING_STARTED.md lines 1160-1164

The "Color Meanings" table includes columns for "Cache" and "Session" with green/yellow/red threshold ranges:
```
| Cache | Session |
| >60% | <50% |
| 30-60% | 50-80% |
| <30% | >80% |
```

The Cache segment (now called Tokens) does NOT use percentage-based color thresholds. It uses `tokens_fresh` (orange, color 214) and `tokens_cached` (cyan, color 81) as fixed colors. There are no green/yellow/red thresholds for cache ratio. The Session segment also uses a fixed cyan color (color 87) with no threshold logic.

These documented thresholds are fabricated and do not correspond to any code logic.

---

## Major Findings (should fix)

### M-1: VCRM test VT-EN005-003 (NO_COLOR empty string) not implemented

**Location:** test_statusline.py, VCRM test plan
**Impact:** Verification gap

The VCRM specifies:
> VT-EN005-003 | REQ-003 | `run_color_matrix_test()` + empty string | Presence check, not truthiness

However, `run_color_matrix_test()` only tests 4 scenarios with `NO_COLOR="1"` or unset. It never tests `NO_COLOR=""` (empty string). While my adversarial testing confirmed the code correctly handles this case (using `os.environ.get("NO_COLOR") is not None` at line 334), the test suite does not verify this critical edge case.

The VCRM claimed this test existed. It does not. This is a verification gap.

### M-2: ANSI escape injection via config string fields

**Location:** statusline.py, all config-sourced strings used in output
**Impact:** Low-severity security (requires config file write access)

Config fields like `cost.currency_symbol` and `display.separator` are embedded directly into terminal output without sanitization. An attacker with write access to the config file can inject arbitrary ANSI escape sequences:

```json
{"cost": {"currency_symbol": "\u001b[31mINJECTED\u001b[0m "}}
```

Verified: the injected `\x1b[31m` sequence passes through to stdout verbatim. While this requires local file access (limiting real-world risk), it contrasts with the git branch sanitization at line 688 which correctly strips ANSI codes via `_ANSI_ESCAPE_RE`. The inconsistency suggests the sanitization policy was not applied uniformly.

Note: `_ANSI_ESCAPE_RE` already exists and is used for git output. It should also be applied to config string fields that appear in terminal output.

### M-3: Documentation uses obsolete "cache" segment key name

**Location:** GETTING_STARTED.md line 635
**Impact:** User confusion, non-functional config

Example 4 ("Only show model, context, and cost") uses:
```json
{
  "segments": {
    "cache": false,
    ...
  }
}
```

But the actual config key was renamed from `"cache"` to `"tokens"` (see statusline.py line 82 comment and DEFAULT_CONFIG at line 82). The code at line 1010 uses `segments_config.get("tokens", True)`, so setting `"cache": false` would have NO EFFECT -- the tokens segment would still appear.

### M-4: String values in numeric JSON fields crash the script

**Location:** statusline.py, multiple extract functions
**Impact:** Low (requires malformed input from Claude Code)

When JSON payload contains string values where numbers are expected (e.g., `"total_cost_usd": "not_a_number"`), the script outputs:
```
ECW: Error - TypeError
```

While the top-level exception handler prevents a traceback, the entire status line is lost. A more robust approach would be to use `safe_get` with type validation or try/except around arithmetic operations, allowing partial rendering of unaffected segments.

---

## Minor Findings (nice to fix)

### m-1: Temp file leak on non-OSError exception in json.dump

**Location:** statusline.py lines 307-317

The inner `try/except` in `save_state()` only catches `OSError`. If `json.dump` were to raise a different exception (e.g., `TypeError`, `ValueError` for non-serializable state), the temp file would not be closed or cleaned up. In practice, the state dict only contains simple int/str values, so this cannot currently happen. However, using a `finally` block or broader exception handling would be more defensive.

### m-2: Non-dict JSON input silently produces default output

**Location:** statusline.py `main()` + `safe_get()`

When the input is valid JSON but not a dict (e.g., `[1,2,3]` or `"hello"`), the script does not error but produces default output as if all fields were missing. This is arguably correct behavior (graceful degradation) but could mask integration issues if Claude Code changes its output format.

### m-3: `safe_get` treats None values as missing

**Location:** statusline.py line 387

```python
return current if current is not None else default
```

If a JSON field has an explicit `None` (null) value, `safe_get` replaces it with the default. This is correct for most cases but could theoretically mask intentional null values from Claude Code's API.

### m-4: auto_compact_width=0 disables auto-compact but is not documented

**Location:** statusline.py line 993

Setting `auto_compact_width` to 0 (`if display_config["auto_compact_width"] > 0`) causes the condition to short-circuit, effectively disabling auto-compact mode. This behavior is intentional but not documented anywhere.

### m-5: Compaction detection persists stale data across sessions

**Location:** statusline.py `extract_compaction_info()`

The state file persists `last_compaction_from` and `last_compaction_to` indefinitely. If a compaction was detected in a previous session, the compaction indicator continues to appear in new sessions until token counts exceed the previous values. There is no session-based reset mechanism.

### m-6: tmux configuration recommendation is incomplete

**Location:** GETTING_STARTED.md line 916

The recommended `set -g default-terminal "screen-256color"` is correct for basic 256-color support, but modern tmux (3.2+) users should prefer `tmux-256color` which provides better compatibility. Additionally, the docs do not mention `set -ga terminal-overrides ",*256col*:Tc"` which is needed for true-color (24-bit) support. This is a minor accuracy point since the script only uses 256-color ANSI codes.

---

## Recommendations

### To reach 0.92 target:

1. **Fix GETTING_STARTED.md verification output** (C-1): Update the "What you should see" example and segment breakdown table to match actual v2.1.0 output format (`⚡ 0→ 0↺` not `⚡ 0%`, `⏱️ 0m 0tok` not `⏱️ 0m [bar] 0%`).

2. **Fix Color Meanings table** (C-2): Remove or correct the Cache and Session columns that reference non-existent threshold logic. Replace with accurate descriptions of the fixed-color scheme used.

3. **Add NO_COLOR="" empty string test** (M-1): Add a 5th scenario to `run_color_matrix_test()` with `env["NO_COLOR"] = ""` to match VCRM specification VT-EN005-003.

4. **Fix "cache" to "tokens" in Example 4** (M-3): Change `"cache": false` to `"tokens": false` in GETTING_STARTED.md line 635.

### Lower priority:

5. **Sanitize config strings** (M-2): Apply `_ANSI_ESCAPE_RE.sub("", value)` to `currency_symbol` and `separator` before output.

6. **Defensive numeric handling** (M-4): Wrap arithmetic in segment builders with try/except to allow partial rendering on malformed input.

---

## Evidence Summary

| Test ID | Input | Expected | Actual | Result |
|---------|-------|----------|--------|--------|
| RT-01 | NO_COLOR="" | 0 ANSI codes | 0 ANSI codes | PASS |
| RT-02 | use_color="yes" | Colors enabled (truthy) | Colors enabled | PASS (but type-unsafe) |
| RT-03 | use_color=0 | 0 ANSI codes | 0 ANSI codes | PASS |
| RT-04 | NO_COLOR=1MB string | No crash | No crash | PASS |
| RT-05 | NO_COLOR=unicode | 0 ANSI codes | 0 ANSI codes | PASS |
| RT-06 | ANSI in currency_symbol | Sanitized | Passes through | FAIL |
| RT-07 | ANSI in separator | Sanitized | Passes through | FAIL |
| RT-08 | context_window_size=0 | No div-by-zero | No crash | PASS |
| RT-09 | Negative token counts | No crash | No crash | PASS |
| RT-10 | All None values | Graceful | Graceful | PASS |
| RT-11 | Empty JSON {} | Graceful | Graceful | PASS |
| RT-12 | Non-dict JSON | Graceful | Graceful | PASS |
| RT-13 | String-for-number | Graceful | "ECW: Error - TypeError" | PARTIAL |
| RT-14 | 5 concurrent instances | No state corruption | Valid JSON state file | PASS |
| RT-15 | cost=infinity | No crash | No crash | PASS |
| RT-16 | Path traversal state_file | N/A | Creates file at traversed path | NOTED |
| RT-17 | VCRM VT-EN005-003 coverage | Test exists | Test missing | FAIL |
| RT-18 | Doc accuracy vs code | Match | Mismatch in 4 places | FAIL |

**21/21 automated tests pass.**
**18 red team adversarial probes: 14 PASS, 2 FAIL (ANSI injection), 1 PARTIAL (type error), 1 NOTED (path traversal)**
