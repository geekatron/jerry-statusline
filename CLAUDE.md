# CLAUDE.md - ECW Status Line

> Project-specific instructions for Claude Code

## Project Overview

ECW (Evolved Claude Workflow) Status Line is a single-file, self-contained Python script providing real-time visibility into Claude Code session state.

- **Language:** Python 3.9+ (stdlib only, zero dependencies)
- **Architecture:** Single-file deployment (`statusline.py`)
- **Tests:** `test_statusline.py`

---

## Python Environment Rules

### UV is Required (HARD RULE)

**ALWAYS use `uv` for Python operations.** Never use `pip`, `python3`, or `python` directly.

| Operation | Correct | Incorrect |
|-----------|---------|-----------|
| Run script | `uv run python script.py` | `python3 script.py` |
| Run tests | `uv run python test_statusline.py` | `python test_statusline.py` |
| Install package | `uv pip install package` | `pip install package` |
| Run with deps | `uv run --with package script.py` | N/A |

### Why UV?

1. **Cross-platform consistency** - Same commands work on macOS, Linux, Windows
2. **Fast** - 10-100x faster than pip
3. **Python version management** - Handles Python installation automatically
4. **No virtual env activation needed** - `uv run` handles it

### UV Command Patterns

```bash
# Run a Python script (no project dependencies)
uv run python script.py

# Run with specific Python version
uv run --python 3.11 python script.py

# Run with additional dependencies (ad-hoc)
uv run --with requests python script.py

# Install a tool globally
uv tool install ruff

# Run a tool
uv run ruff check .
```

### GitHub Actions with UV

Always use `astral-sh/setup-uv` action:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v5
  with:
    python-version: ${{ matrix.python-version }}
    enable-cache: true

- name: Run tests
  run: uv run python test_statusline.py
```

---

## Testing Rules

### Running Tests

```bash
# Run all tests
uv run python test_statusline.py

# Run with debug output
ECW_DEBUG=1 uv run python test_statusline.py
```

### Test Structure

- Tests are in `test_statusline.py`
- Uses subprocess to invoke `statusline.py` with mock JSON payloads
- 12 functional tests covering normal, warning, critical, and edge cases

---

## Code Style Rules

### Linting

```bash
# Check code style
uv run ruff check statusline.py test_statusline.py

# Auto-fix issues
uv run ruff check --fix statusline.py test_statusline.py

# Format code
uv run ruff format statusline.py test_statusline.py
```

### Python Style

- Type hints required for all functions
- Docstrings for public functions
- Max line length: 100 characters
- Use `pathlib.Path` for cross-platform paths
- Use `subprocess.run()` with list arguments (no `shell=True`)

---

## Git Rules

### Branch Naming

- Feature branches: `claude/*` (triggers CI)
- Main branch: `main`

### Commit Messages

Follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Test changes

---

## File Locations

| File | Purpose |
|------|---------|
| `statusline.py` | Main script (single-file deployment) |
| `test_statusline.py` | Test suite |
| `WORKTRACKER.md` | Work item tracking manifest |
| `work/` | Work breakdown structure |
| `docs/` | Analysis and research documents |
| `.github/workflows/test.yml` | CI/CD pipeline |

---

## Cross-Platform Considerations

- All paths use `pathlib.Path` for cross-platform compatibility
- No shell-specific syntax in subprocess calls
- ANSI colors supported on modern terminals (Windows Terminal, iTerm2, etc.)
- Emoji can be disabled via `use_emoji: false` in config
