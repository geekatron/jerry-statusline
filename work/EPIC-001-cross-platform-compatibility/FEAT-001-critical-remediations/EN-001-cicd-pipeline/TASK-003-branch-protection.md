# TASK-003: Enable Branch Protection Rules

> **Type:** task
> **Status:** pending
> **Priority:** high
> **Created:** 2026-02-03T00:00:00Z
> **Parent:** EN-001
> **Owner:** -
> **Effort:** 0.5h

---

## Description

Configure GitHub branch protection rules to require CI/CD pass before merging to main.

---

## Acceptance Criteria

- [ ] Branch protection enabled on `main` branch
- [ ] "Require status checks to pass before merging" enabled
- [ ] "Tests" workflow required as status check
- [ ] Direct pushes to main blocked (require PR)

---

## Implementation Notes

1. Go to Repository Settings > Branches
2. Add branch protection rule for `main`
3. Enable:
   - Require a pull request before merging
   - Require status checks to pass before merging
   - Select "Tests" as required status check

---

## Related Items

- Parent: [EN-001: CI/CD Pipeline Implementation](../EN-001-cicd-pipeline.md)
- Depends on: TASK-001 (workflow must exist first)

---

## Evidence

### Verification

- [ ] Screenshot of branch protection settings
- [ ] Attempt direct push to main fails
- [ ] PR requires CI pass to merge

---

## History

| Date | Status | Notes |
|------|--------|-------|
| 2026-02-03 | pending | Task created |

---
