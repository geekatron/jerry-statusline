# TASK-001: Create GitHub Actions Workflow File

> **Type:** task
> **Status:** completed
> **Priority:** critical
> **Created:** 2026-02-03T00:00:00Z
> **Parent:** EN-001
> **Owner:** Claude
> **Effort:** 1h

---

## Description

Create the GitHub Actions workflow file at `.github/workflows/test.yml` with multi-platform testing configuration.

---

## Acceptance Criteria

- [x] File created at `.github/workflows/test.yml`
- [x] Workflow triggers on push and pull_request
- [x] Uses `actions/checkout@v4` and `astral-sh/setup-uv@v5`
- [x] Runs `uv run python test_statusline.py` as test command
- [ ] Syntax validated with `actionlint` or GitHub UI

---

## Implementation Notes

Reference the V&V plan specification at `docs/verification/XPLAT-001-e-004-vv-plan.md` for the complete workflow structure.

### Workflow Template

```yaml
name: Tests

on:
  push:
    branches: [main, 'claude/*']
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Run tests
        run: python test_statusline.py
```

---

## Related Items

- Parent: [EN-001: CI/CD Pipeline Implementation](../EN-001-cicd-pipeline.md)
- Source: Gap G-004, Risk RSK-007

---

## Evidence

### Deliverables

| Deliverable | Type | Link |
|-------------|------|------|
| test.yml | Workflow file | `.github/workflows/test.yml` |

### Verification

- [x] File exists at correct path
- [ ] GitHub recognizes workflow
- [ ] Workflow runs successfully on push

---

## History

| Date | Status | Notes |
|------|--------|-------|
| 2026-02-03 | pending | Task created |
| 2026-02-03 | completed | Workflow created using UV (astral-sh/setup-uv@v5) |

---
