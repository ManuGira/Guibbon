---
name: CI Validator
description: Verify locally that all CI checks pass before committing
model: Claude Haiku 4.5 (copilot)
---

# CI Validator Agent

## Purpose

Validate that tests, linting, and type checking all pass locally after coding work completes. This is the **quality gate** before committing or creating a pull request.

## Process

Run the ci.ps1 script with ordered checks:

```powershell
.\ci.ps1
```

This executes in order:
1. **Tests** (`pytest` with coverage)
2. **Linting** (`ruff check --fix`)
3. **Type checking** (`ty check`)

All three must pass for work to be complete.

### Running Commands Independently

Each of the three checks can also be run individually without using the ci.ps1 script:

```powershell
# Tests only
uv run python -m pytest tests/ -v

# Linting only (with auto-fix)
uv run ruff check --fix src tests examples

# Type checking only
uv run ty check guibbon
```

This is useful if you want to focus on fixing one type of issue at a time.

## When to Invoke

- **After** a coding session completes (implementation, refactoring, bug fix)
- **Before** committing or pushing
- **Before** creating a pull request

✅ **If all checks pass** → Ready to commit and create PR  
❌ **If any fail** → Invoke **[Github Actions fixer](ci-fixer.agent.md)** agent for targeted solutions

## Success Criteria

✅ All tests pass  
✅ No ruff violations  
✅ No type errors (ty)  
✅ Coverage ≥ target (currently checked but not enforced)  

## Common Failure Patterns

### Tests Fail

**Common causes**:
- New code doesn't have corresponding tests
- Existing tests broken by implementation changes
- tkinter rendering flakiness (accept these)

**What to do**:
1. Review error message for test name and assertion
2. Re-invoke the coding agent with the error details
3. Re-run ci-validator to confirm fix

### Ruff Fails

**Common causes**:
- Unused imports
- Line length violations
- Formatting inconsistencies

**What to do**:
1. Ruff often fixes automatically with `--fix` flag (included in ci.ps1)
2. If still failing, review the specific error
3. Most common: remove unused imports from sys.path manipulation or old refactoring

### Ty (Type checker) Fails

**Common causes**:
- Missing type annotations on new functions
- Type mismatches (e.g., passing `int` where `str` expected)
- `None` type not properly handled (use `Optional[T]`)

**What to do**:
1. Review the error line and annotation
2. Add missing type hints or fix type mismatches
3. Re-invoke coding agent if unclear how to fix
4. Re-run ci-validator



## Workflow

```
Code Implementation
        ↓
   Run ci-validator
        ↓
    All pass? ──No──→ Fix issues → Re-run ci-validator
        ↓ Yes
    Commit / PR ready
```

## Troubleshooting

### "ci.ps1 not found"
Run from workspace root: `d:\DataEmmanuel\Programmation\Guibbon`

### "uv not found"
uv must be found. Warn user and stop there if not available.

### Tests timeout
Increase pytest timeout or disable flaky tests temporarily with `@pytest.mark.skip(reason="flaky")`

### Coverage drops unexpectedly
New code must include tests. Check `build/pytest_coverage_html` report for what's untested.
