# TASK-003: Enable Branch Protection Rules

> **Type:** task
> **Status:** completed
> **Priority:** high
> **Created:** 2026-02-03T00:00:00Z
> **Parent:** EN-001
> **Owner:** Claude
> **Effort:** 0.5h

---

## Description

Configure GitHub branch protection rules to match jerry-core repository configuration. This includes creating a ruleset that prevents direct pushes to main and requires PR reviews.

---

## Reference Configuration (jerry-core)

The jerry-core repository has the following ruleset that should be replicated:

### Ruleset: "Don't fuck with main"

| Setting | Value |
|---------|-------|
| Target | Branch (default branch) |
| Enforcement | Active |

### Rules Configured

| Rule | Description |
|------|-------------|
| `deletion` | Prevent deletion of the main branch |
| `non_fast_forward` | Prevent force pushes to main |
| `pull_request` | Require pull requests before merging |

### Pull Request Requirements

| Setting | Value |
|---------|-------|
| Required approving reviews | 1 |
| Dismiss stale reviews on push | No |
| Require code owner review | No |
| Require last push approval | No |
| Required review thread resolution | No |
| Allowed merge methods | merge, squash, rebase |

### Repository Settings to Match

| Setting | jerry-core | jerry-statusline | Action |
|---------|------------|------------------|--------|
| Wiki Enabled | ✅ Yes | ❌ No | Enable |
| Delete Branch on Merge | ❌ No | ❌ No | ✅ OK |
| Squash Merge | ✅ Yes | ✅ Yes | ✅ OK |
| Merge Commit | ✅ Yes | ✅ Yes | ✅ OK |
| Rebase Merge | ✅ Yes | ✅ Yes | ✅ OK |

---

## Acceptance Criteria

- [x] Branch protection ruleset created matching jerry-core
- [x] Ruleset named "Don't fuck with main" (or similar)
- [x] Deletion protection enabled
- [x] Force push protection enabled
- [x] PR required with 1 approving review
- [x] Wiki enabled on repository
- [x] Direct pushes to main blocked

---

## Implementation Steps

### Option 1: GitHub UI

1. Go to Repository Settings → Rules → Rulesets
2. Click "New ruleset" → "New branch ruleset"
3. Configure:
   - **Name:** `Don't fuck with main`
   - **Enforcement status:** Active
   - **Target branches:** Add target → Include default branch
   - **Rules:**
     - ✅ Restrict deletions
     - ✅ Block force pushes
     - ✅ Require a pull request before merging
       - Required approvals: 1
4. Save ruleset
5. Go to Settings → General → Features → Enable Wikis

### Option 2: GitHub CLI (requires admin PAT)

```bash
# Create ruleset
gh api repos/geekatron/jerry-statusline/rulesets --method POST --input - <<'EOF'
{
  "name": "Don't fuck with main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["merge", "squash", "rebase"]
      }
    }
  ]
}
EOF

# Enable wiki
gh repo edit geekatron/jerry-statusline --enable-wiki
```

---

## Prerequisites

- Repository admin access required
- GitHub PAT with `repo` and `admin:repo` scopes for CLI method

---

## Related Items

- Parent: [EN-001: CI/CD Pipeline Implementation](../EN-001-cicd-pipeline.md)
- Reference: geekatron/jerry-core ruleset ID 11752960
- Depends on: TASK-001 (workflow must exist first)

---

## Evidence

### Verification

- [x] Ruleset visible in Settings → Rules → Rulesets
- [x] Direct push to main fails with protection error
- [x] PR requires 1 approval before merge
- [x] Wiki tab visible on repository

### Completed Configuration

| Item | Value |
|------|-------|
| Ruleset ID | 12426458 |
| Ruleset URL | https://github.com/geekatron/jerry-statusline/rules/12426458 |
| Wiki | Enabled |

### API Verification Command

```bash
# Verify ruleset exists
gh api repos/geekatron/jerry-statusline/rulesets

# Verify wiki enabled
gh repo view geekatron/jerry-statusline --json hasWikiEnabled
```

---

## History

| Date | Status | Notes |
|------|--------|-------|
| 2026-02-03 | pending | Task created |
| 2026-02-03 | in_progress | Documented jerry-core configuration to match |
| 2026-02-03 | completed | Ruleset created via API, wiki enabled |

---
