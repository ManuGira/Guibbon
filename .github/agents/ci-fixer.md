---
name: Github Actions fixer
description: Fix CI errors
---

# CI-Fixer Agent

## Purpose
Fix code issues that cause GitHub Actions CI failures, ensuring that tests, formatting, and type checks pass both locally and in CI environments.

## Local CI Verification Commands

Before pushing, verify all CI checks pass locally:

### 1. Run Tests
```bash
uv run pytest
```
- Runs all unit tests
- Checks code coverage
- Expected: All tests passing, coverage ≥ 80%

### 2. Format Check
```bash
uv run ruff check
```
- Checks code formatting and linting rules
- Expected: No errors or warnings

### 3. Type Check
```bash
uv run mypy .
```
- Verifies type annotations and type safety
- Expected: Success with no type errors

## Common CI Failure Patterns and Solutions

### Test Failures

**Problem**: Tests pass locally but fail in CI
- **Causes**:
  - Platform-specific issues (Windows vs Linux)
  - Missing dependencies in CI environment
  - Race conditions or timing issues
  - File path differences (separators, case sensitivity)
  - Intermittent tkinter errors on shared resources

- **Solutions**:
  1. Check if tests create/destroy tkinter instances properly
     - Use shared `_tk_root` with `setUpModule()`/`tearDownModule()`
     - Add `assert _tk_root is not None` before using it
  2. Ensure proper cleanup in `tearDown()` methods
  3. Use `try-except` blocks for tkinter operations
  4. Make file paths platform-independent with `pathlib` or `os.path`
  5. Check for hardcoded absolute paths

### Type Check Failures (mypy)

**Problem**: mypy errors in CI but not locally
- **Causes**:
  - Different mypy version
  - Missing type stubs
  - Optional/None type issues
  - Type narrowing not recognized

- **Solutions**:
  1. Add explicit type assertions: `assert variable is not None`
  2. Use proper type annotations for all function parameters and returns
  3. Fix union types: `Optional[X]` or `X | None`
  4. Ensure Mock objects are properly typed in tests
  5. Check dataclass field types match usage

### Format Check Failures (ruff)

**Problem**: ruff errors in CI but not locally
- **Causes**:
  - Different ruff version
  - IDE auto-formatting overriding ruff rules
  - Unused imports or variables
  - Line length violations

- **Solutions**:
  1. Run `uv run ruff check --fix` to auto-fix issues
  2. Remove unused imports and variables
  3. Break long lines properly
  4. Follow consistent naming conventions

## Step-by-Step Troubleshooting Process

### 1. Identify the Failing Check
- Read the GitHub Actions log carefully
- Note which check failed: pytest, ruff, or mypy
- Copy the exact error messages

### 2. Reproduce Locally
```bash
# Clean environment
rm -rf .pytest_cache __pycache__ build/

# Run the specific failing check
uv run pytest -v  # for test failures
uv run mypy .     # for type errors
uv run ruff check # for format errors
```

### 3. Fix the Issues
- Address errors from most specific to most general
- Fix one error at a time
- Re-run the check after each fix
- Verify all three checks pass before pushing

### 4. Verify the Fix
```bash
# Run all checks together
uv run pytest && uv run mypy . && uv run ruff check
```

## Best Practices for CI Stability

### Test Writing
- Always use shared tkinter root in test modules
- Add proper type hints to test functions
- Use Mock objects correctly (not for type-checked callbacks)
- Clean up resources in tearDown()
- Make tests deterministic (no random data, timing dependencies)

### Type Safety
- Add type hints to all new functions
- Use `assert` statements to narrow Optional types
- Declare dataclass fields with proper types
- Import types from correct modules

### Code Quality
- Keep functions under 50 lines when possible
- Use meaningful variable names
- Add docstrings to public functions
- Follow project conventions

## Quick Reference

| Issue | Command | Fix |
|-------|---------|-----|
| Test fails | `uv run pytest -v` | Check test isolation, cleanup |
| Type error | `uv run mypy .` | Add assertions, fix annotations |
| Format error | `uv run ruff check` | Run with `--fix` flag |
| Import error | Check logs | Add missing dependency |
| Coverage low | `uv run pytest --cov` | Add more tests |

## Emergency Checklist

When CI fails unexpectedly:
- [ ] Pull latest changes from main branch
- [ ] Clean build artifacts: `rm -rf build/ .pytest_cache/`
- [ ] Update dependencies: `uv sync`
- [ ] Run all three checks locally
- [ ] Check GitHub Actions logs for platform-specific issues
- [ ] Verify Python version matches CI (check `.github/workflows/`)
- [ ] Look for intermittent tkinter errors (may need shared root pattern)

## Notes
- These commands run the same checks as GitHub Actions
- Always verify locally before pushing
- CI uses Ubuntu Linux - consider platform differences
- Intermittent failures often indicate resource management issues