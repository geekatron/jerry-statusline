# Security Code Review Report

**PS ID:** SEC-001
**Entry ID:** e-003
**Topic:** Code Security Review
**Repository:** jerry-statusline
**Version Reviewed:** 2.1.0
**Review Date:** 2026-02-03
**Reviewer:** ps-reviewer agent (v2.0.0)

---

## Executive Summary

This security review analyzed the jerry-statusline repository, a Claude Code status line display tool. The codebase is a Python-based utility that processes JSON input from stdin, displays contextual information, and integrates with git. Overall, the codebase demonstrates **good security practices** with some areas for improvement.

**Risk Assessment:** LOW to MEDIUM

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 1 |
| Medium | 3 |
| Low | 4 |
| Info | 3 |

---

## Files Reviewed

| File | Lines | Purpose |
|------|-------|---------|
| statusline.py | 962 | Main status line script |
| test_statusline.py | 626 | Test suite |
| .github/workflows/test.yml | 105 | CI/CD pipeline |
| .claude/settings.local.json | 30 | Local permissions (out of scope but notable) |

---

## Findings

### SEC-001-001: Exposed GitHub PAT in Local Settings

**Severity:** HIGH
**Category:** Secrets Management / OWASP A01:2021 - Broken Access Control

**Location:** `.claude/settings.local.json:20-23`

**Description:**
A GitHub Personal Access Token (PAT) is exposed in plaintext within the local settings file. While this file is likely in `.gitignore`, it was found in the repository context.

**Evidence:**
```json
"Bash(TOKEN=\"github_pat_11AAFL73Y01MWFgWsGTg2V_...\")"
```

**Impact:**
- Unauthorized access to GitHub repositories
- Potential for malicious commits or repository manipulation
- Token scope may allow broader access than intended

**Recommendation:**
1. Immediately rotate the exposed GitHub PAT
2. Use environment variables or a secure secrets manager
3. Add `.claude/settings.local.json` to `.gitignore` if not already
4. Consider using GitHub's fine-grained PATs with minimal permissions

---

### SEC-001-002: Subprocess Execution Without Shell Escaping

**Severity:** MEDIUM
**Category:** Command Injection / OWASP A03:2021 - Injection

**Location:** `statusline.py:570-593`

**Description:**
The `get_git_info` function executes git commands using user-controlled `cwd` parameter. While `subprocess.run` is used without `shell=True` (good practice), the `cwd` parameter comes from JSON input.

**Evidence:**
```python
def get_git_info(data: Dict, config: Dict) -> Optional[Tuple[str, bool, int]]:
    # ...
    cwd = safe_get(data, "workspace", "current_dir") or safe_get(data, "cwd")
    if not cwd:
        return None

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,  # User-controlled from JSON input
            capture_output=True,
            text=True,
            timeout=timeout,
        )
```

**Impact:**
- Path traversal to unintended directories
- Information disclosure from arbitrary git repositories
- Denial of service via slow/large repositories

**Mitigating Factors:**
- Uses array form (not shell string) - prevents command injection
- Timeout is implemented (2 seconds default)
- Read-only git operations only

**Recommendation:**
1. Validate that `cwd` is an existing directory
2. Consider restricting to known project directories
3. Sanitize path to prevent traversal (e.g., resolve symlinks, check against allowlist)

---

### SEC-001-003: Unvalidated File Path in Transcript Parsing

**Severity:** MEDIUM
**Category:** Path Traversal / OWASP A01:2021 - Broken Access Control

**Location:** `statusline.py:306-348`

**Description:**
The `parse_transcript_for_tools` function accepts a file path from JSON input and reads it without validation.

**Evidence:**
```python
def parse_transcript_for_tools(transcript_path: str, config: Dict) -> Dict[str, int]:
    # ...
    if not transcript_path or not Path(transcript_path).exists():
        debug_log(f"Transcript not found: {transcript_path}")
        return {}
    # ...
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
```

**Impact:**
- Arbitrary file read on the system
- Information disclosure of sensitive files
- Potential denial of service with large files

**Mitigating Factors:**
- Tools feature is disabled by default (`"enabled": False`)
- Only parses JSONL format (non-JSONL lines are skipped)
- Reads line-by-line (memory efficient)

**Recommendation:**
1. Validate that `transcript_path` is within expected directories (e.g., `/tmp`, `~/.claude`)
2. Use `os.path.realpath()` to resolve symlinks before validation
3. Add file size limit check before processing

---

### SEC-001-004: State File Written to User-Controlled Path

**Severity:** MEDIUM
**Category:** Arbitrary File Write / OWASP A01:2021 - Broken Access Control

**Location:** `statusline.py:248-257`

**Description:**
The `save_state` function writes JSON data to a path specified in configuration, which can be overridden by user config files.

**Evidence:**
```python
def save_state(config: Dict, state: Dict[str, Any]) -> None:
    state_file = Path(os.path.expanduser(config["compaction"]["state_file"]))
    # ...
    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f)
```

**Impact:**
- Directory creation at arbitrary locations
- File overwrite at arbitrary locations (limited to JSON content)

**Mitigating Factors:**
- Written content is controlled (JSON structure with token counts)
- Requires user to create malicious config file first
- Default path is safe (`~/.claude/ecw-statusline-state.json`)

**Recommendation:**
1. Validate state file path is within expected directories
2. Use a fixed directory with only filename being configurable
3. Validate path does not contain `..` sequences

---

### SEC-001-005: JSON Parsing Without Size Limits

**Severity:** LOW
**Category:** Denial of Service / OWASP A05:2021 - Security Misconfiguration

**Location:** `statusline.py:939-951`

**Description:**
The main entry point reads all stdin input without size limits and parses it as JSON.

**Evidence:**
```python
def main() -> None:
    # ...
    input_data = sys.stdin.read().strip()

    if not input_data:
        debug_log("No input received")
        print("ECW: No data")
        return

    try:
        data = json.loads(input_data)
```

**Impact:**
- Memory exhaustion with extremely large input
- CPU exhaustion with deeply nested JSON

**Mitigating Factors:**
- Script is invoked by Claude Code, which controls input
- Short-lived process (status line display)
- Python's json module has some built-in limits

**Recommendation:**
1. Add a maximum input size check (e.g., 1MB)
2. Consider using `json.load()` with a limited reader
3. Add recursion depth limit if processing untrusted input

---

### SEC-001-006: Debug Output May Leak Information

**Severity:** LOW
**Category:** Information Disclosure / OWASP A09:2021 - Security Logging and Monitoring Failures

**Location:** `statusline.py:207-210`

**Description:**
Debug mode controlled by environment variable outputs file paths, token counts, and error details to stderr.

**Evidence:**
```python
def debug_log(message: str) -> None:
    if os.environ.get("ECW_DEBUG") == "1":
        print(f"[ECW-DEBUG] {message}", file=sys.stderr)
```

Used in various places:
- Line 179: `debug_log(f"Loaded config from {config_path}")`
- Line 182: `debug_log(f"Config load error from {config_path}: {e}")`
- Line 503: `debug_log(f"Compaction detected: {from_tokens} -> {to_tokens}")`

**Impact:**
- Leakage of file paths and system structure
- Exposure of error details that could aid attackers

**Mitigating Factors:**
- Disabled by default (requires `ECW_DEBUG=1`)
- Output goes to stderr, not stdout
- No secrets or credentials in debug output

**Recommendation:**
1. Ensure debug mode is never enabled in production
2. Sanitize paths before logging (remove home directory)
3. Add warning about not enabling in shared environments

---

### SEC-001-007: Test Suite Creates Temporary Files Without Secure Permissions

**Severity:** LOW
**Category:** Insecure Temporary Files / OWASP A05:2021 - Security Misconfiguration

**Location:** `test_statusline.py:251-261, 303-308, 504-511`

**Description:**
Test suite creates temporary files with default permissions, which may be world-readable.

**Evidence:**
```python
# Line 253
config_file = tempfile.NamedTemporaryFile(
    mode="w", suffix=".json", delete=False
)

# Line 303
with tempfile.NamedTemporaryFile(
    mode="w", suffix=".jsonl", delete=False
) as tf:
```

**Impact:**
- Test data potentially readable by other users on shared systems
- Config files with paths could be modified by attackers

**Mitigating Factors:**
- Test suite only, not production code
- Files are cleaned up after tests
- No sensitive data in test payloads

**Recommendation:**
1. Use `os.chmod()` to set restrictive permissions (0o600)
2. Consider using `tempfile.mkstemp()` which allows mode specification
3. Ensure cleanup occurs in `finally` blocks (already done)

---

### SEC-001-008: Error Messages May Reveal Internal Structure

**Severity:** LOW
**Category:** Information Disclosure / OWASP A09:2021 - Security Logging and Monitoring Failures

**Location:** `statusline.py:956-958`

**Description:**
Exception handling reveals exception type names to stdout.

**Evidence:**
```python
except Exception as e:
    debug_log(f"Unexpected error: {e}")
    print(f"ECW: Error - {type(e).__name__}")
```

**Impact:**
- Reveals Python exception types (e.g., `FileNotFoundError`, `PermissionError`)
- Could help attackers understand system behavior

**Mitigating Factors:**
- Only exception type name, not full traceback
- Generic error handling is already in place

**Recommendation:**
1. Use generic error message without exception type in production
2. Log detailed errors only in debug mode

---

### SEC-001-009: CI/CD Pipeline Uses Pinned Action Versions (Good Practice)

**Severity:** INFO (Positive Finding)
**Category:** Supply Chain Security

**Location:** `.github/workflows/test.yml`

**Description:**
The CI/CD pipeline uses versioned actions (`actions/checkout@v4`, `astral-sh/setup-uv@v5`).

**Evidence:**
```yaml
- name: Checkout repository
  uses: actions/checkout@v4

- name: Install uv
  uses: astral-sh/setup-uv@v5
```

**Impact:**
Positive - Reduces risk of supply chain attacks through action hijacking.

**Recommendation:**
1. Consider using SHA pinning for even stronger supply chain security
2. Example: `uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11`

---

### SEC-001-010: Security Scanning in CI/CD (Good Practice)

**Severity:** INFO (Positive Finding)
**Category:** DevSecOps

**Location:** `.github/workflows/test.yml:69-104`

**Description:**
The pipeline includes multiple security scanning tools.

**Evidence:**
```yaml
- name: Gitleaks - Secret Scanning
  run: gitleaks detect --source . --verbose --exit-code 1

- name: Bandit - Python Security Linter
  run: uv run --with bandit bandit -r statusline.py -f json -o bandit-report.json || true

- name: Trivy - Vulnerability Scanner
  uses: aquasecurity/trivy-action@master
```

**Impact:**
Positive - Provides defense-in-depth security testing.

**Recommendation:**
1. Consider failing the build on Bandit findings (currently uses `|| true`)
2. Add SARIF upload for GitHub Security tab integration
3. Pin Trivy action version (currently using `@master`)

---

### SEC-001-011: No Shell Injection via subprocess (Good Practice)

**Severity:** INFO (Positive Finding)
**Category:** Command Injection Prevention

**Location:** `statusline.py:570-593`, `test_statusline.py:264-273`

**Description:**
All subprocess calls use array form without `shell=True`.

**Evidence:**
```python
result = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],  # Array form
    cwd=cwd,
    capture_output=True,
    text=True,
    timeout=timeout,
)
```

**Impact:**
Positive - Prevents shell injection attacks.

**Recommendation:**
Continue this practice. Document as security requirement.

---

## OWASP Top 10 Analysis

| OWASP Category | Relevance | Findings |
|----------------|-----------|----------|
| A01:2021 Broken Access Control | Medium | SEC-001-002, SEC-001-003, SEC-001-004 |
| A02:2021 Cryptographic Failures | N/A | No cryptographic operations |
| A03:2021 Injection | Low | SEC-001-002 (mitigated) |
| A04:2021 Insecure Design | Low | Generally good design |
| A05:2021 Security Misconfiguration | Low | SEC-001-005, SEC-001-007 |
| A06:2021 Vulnerable Components | Low | Uses stdlib only |
| A07:2021 Auth Failures | N/A | No authentication |
| A08:2021 Data Integrity Failures | Low | JSON from trusted source |
| A09:2021 Security Logging Failures | Low | SEC-001-006, SEC-001-008 |
| A10:2021 SSRF | N/A | No outbound requests |

---

## Risk Summary

### Attack Vectors Considered

1. **Malicious JSON Input** - LOW RISK
   - Input comes from Claude Code (trusted source)
   - JSON parsing is standard library
   - No direct code execution from input

2. **File System Attacks** - MEDIUM RISK
   - Path traversal partially mitigated
   - State file write is configurable
   - Transcript read is disabled by default

3. **Subprocess Attacks** - LOW RISK
   - Array form subprocess (no shell injection)
   - Timeouts implemented
   - Read-only git operations

4. **Denial of Service** - LOW RISK
   - No input size limits
   - Short-lived process
   - Git timeout prevents hangs

5. **Information Disclosure** - LOW RISK
   - Debug mode disabled by default
   - Error messages are generic
   - No secrets in output

---

## Recommendations Summary

### High Priority
1. **Rotate the exposed GitHub PAT immediately** (SEC-001-001)
2. **Validate file paths** before reading transcripts or writing state (SEC-001-003, SEC-001-004)

### Medium Priority
3. **Add input size limits** for JSON parsing (SEC-001-005)
4. **Validate cwd path** before git operations (SEC-001-002)
5. **Pin CI/CD action versions** to SHA hashes (SEC-001-009)

### Low Priority
6. **Sanitize debug output** to remove sensitive paths (SEC-001-006)
7. **Use generic error messages** in production (SEC-001-008)
8. **Set secure permissions** on temporary files in tests (SEC-001-007)

---

## Compliance Notes

- **Zero external dependencies** - Reduces supply chain risk
- **Python stdlib only** - Well-audited security
- **CI/CD security scanning** - Gitleaks, Bandit, Trivy
- **Timeout handling** - Prevents resource exhaustion

---

## Conclusion

The jerry-statusline codebase demonstrates **good security awareness** with proper subprocess handling, timeout implementation, and CI/CD security scanning. The primary concerns are:

1. An exposed GitHub PAT in local settings (HIGH severity)
2. Unvalidated file paths from JSON input (MEDIUM severity)

With the recommended fixes applied, this codebase would meet a **low security risk** profile appropriate for a developer tooling utility.

---

**Review Completed:** 2026-02-03
**Next Review Recommended:** After implementing HIGH/MEDIUM fixes
