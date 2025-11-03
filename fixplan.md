# Windows CI Failure Analysis and Fix Plan

## Problem Summary

GitHub Actions CI tests are failing on Windows with Tcl/Tk initialization errors. The tests run successfully on Ubuntu but fail on Windows across all Python versions (3.10, 3.11, 3.12, 3.13).

## Error Analysis

### Main Error
```
_tkinter.TclError: Can't find a usable init.tcl in the following directories: 
    {C:\hostedtoolcache\windows\Python\3.13.9\x64\tcl\tcl8.6}

C:/hostedtoolcache/windows/Python/3.13.9/x64/tcl/tcl8.6/init.tcl: couldn't read file "C:/hostedtoolcache/windows/Python/3.13.9/x64/tcl/tcl8.6/init.tcl": No error
```

### Root Cause
The Windows Python installation from `actions/setup-python` does not include Tcl/Tk files in the expected location. When `tk.Tk()` is called in the test module setup (`setUpModule()` in `tests/interactive_overlays/test_multi_slider.py`), Python's tkinter cannot find the required Tcl/Tk initialization files.

### Affected Tests
- `tests/interactive_overlays/test_multi_slider.py::TestMultiSliderOverlay::test_canvas_to_slider_conversion`
- `tests/interactive_overlays/test_multi_slider.py::TestMultiSliderOverlay::test_create_overlay`
- `tests/interactive_overlays/test_multi_slider.py::TestMultiSliderOverlay::test_slider_to_canvas_conversion`

All 3 tests fail at the `setUpModule()` stage when attempting to create a Tk root window.

### Test Results
- **Passed**: 175/178 tests (98.3%)
- **Failed**: 3/178 tests (1.7%)
- **Coverage**: 86% (remains good despite failures)

## Current CI Configuration Analysis

From `.github/workflows/tests.yml`:

### Ubuntu Handling (Working)
```yaml
- name: Install tkinter (Ubuntu only)
  if: ${{ matrix.os == 'ubuntu-latest' }}
  run: |
    # Disable ESM repositories to avoid firewall issues
    sudo sed -i 's/^deb.*esm.ubuntu.com/#&/' /etc/apt/sources.list.d/*.list 2>/dev/null || true
    sudo apt-get update -o Acquire::Retries=3 -o Acquire::http::Timeout=10 && sudo apt-get install -y python3-tk

- name: Run tests (Ubuntu)
  if: matrix.os == 'ubuntu-latest'
  run: |
    export DISPLAY=:99 
    Xvfb :99 &  
    uv run pytest
```
✅ Ubuntu explicitly installs `python3-tk` and uses a virtual display (Xvfb)

### Windows Handling (Broken)
```yaml
- name: Run tests (Windows)
  if: matrix.os == 'windows-latest'
  run: |
    echo "Running tests"
    uv run pytest
```
❌ Windows has no special setup for Tcl/Tk

## Solution Options

### Option 1: Install Tcl/Tk on Windows (Preferred)
**Approach**: Add a Windows-specific setup step to ensure Tcl/Tk is available

**Pros**:
- Tests will run on Windows, maintaining cross-platform coverage
- Catches Windows-specific bugs
- Aligns with current Ubuntu approach

**Cons**:
- Requires additional CI setup time
- May be unstable if Tcl/Tk installation changes

### Option 2: Skip Tkinter Tests on Windows
**Approach**: Mark tkinter tests to skip on Windows platform

**Pros**:
- Simple implementation
- No CI dependency management needed

**Cons**:
- Reduces test coverage on Windows
- May miss Windows-specific issues
- Not ideal for a GUI library

### Option 3: Use Headless Testing Mode
**Approach**: Mock or skip Tk root creation when running in headless environments

**Pros**:
- Works across all platforms
- Faster tests

**Cons**:
- Doesn't test real tkinter behavior
- Complex refactoring of tests

## Recommended Fix Plan

**Choose Option 1**: Properly install Tcl/Tk on Windows runners

### Implementation Steps

1. **Add Windows Tcl/Tk Installation Step**
   - Add a conditional step before "Run tests (Windows)" in `.github/workflows/tests.yml`
   - Use `choco` (Chocolatey) or download Tcl/Tk directly
   - Set `TCL_LIBRARY` and `TK_LIBRARY` environment variables

2. **Verify Installation**
   - Test that tkinter can import successfully
   - Print diagnostic information for debugging

3. **Set Environment Variables**
   - Ensure Python can find Tcl/Tk libraries by setting proper paths

### Proposed Code Changes

#### `.github/workflows/tests.yml` modifications:

```yaml
- name: Install tkinter dependencies (Windows only)
  if: ${{ matrix.os == 'windows-latest' }}
  run: |
    echo "Setting up Tcl/Tk for Python on Windows"
    # Python on Windows from setup-python should include tkinter
    # Verify it's available
    python -c "import tkinter; print('tkinter available'); import sys; print(f'Python: {sys.executable}')"

- name: Run tests (Windows)
  if: matrix.os == 'windows-latest'
  run: |
    echo "Running tests on Windows"
    uv run pytest
```

If verification fails, may need to install Tcl/Tk explicitly:

```yaml
- name: Install Tcl/Tk (Windows only)
  if: ${{ matrix.os == 'windows-latest' }}
  run: |
    # Install Tcl/Tk via Chocolatey
    choco install tcl --version=8.6.13 -y
    # Set environment variables for Python to find Tcl/Tk
    echo "TCL_LIBRARY=C:\Tcl\lib\tcl8.6" >> $GITHUB_ENV
    echo "TK_LIBRARY=C:\Tcl\lib\tk8.6" >> $GITHUB_ENV
```

### Alternative: Use actions/setup-python with Explicit Tcl/Tk

The Python installations from the `actions/setup-python` action should include Tcl/Tk. The issue might be that we're using `uv` to manage Python versions, which might not include Tcl/Tk.

**Better solution**: Ensure we're using the system Python that includes Tcl/Tk, or verify the Python from `uv` includes it.

## Testing Strategy

1. **Local Testing**: Cannot fully replicate Windows environment locally (Linux/Mac dev machines)
2. **CI Testing**: 
   - Make changes to workflow
   - Push to a test branch
   - Monitor CI runs on Windows
3. **Verification**:
   - All 178 tests should pass on Windows
   - Test execution time should remain reasonable
   - Coverage should maintain ≥86%

## Risk Assessment

**Low Risk**: 
- Changes are confined to CI configuration
- No production code changes
- Easy to revert if issues arise

## Success Criteria

- ✅ All 178 tests pass on Windows (currently 175/178)
- ✅ Tests pass on all Python versions (3.10, 3.11, 3.12, 3.13)
- ✅ Tests pass on both Windows and Ubuntu
- ✅ Code coverage remains ≥86%
- ✅ CI execution time remains under 5 minutes per job

## Notes

The issue is specifically with Python 3.13.9 in the logs, but likely affects all versions. The `uv` tool is being used to manage Python versions and dependencies, which might be installing Python without the full Tcl/Tk support that typically comes with standard Python Windows installers.

## Investigation Needed

Before implementing, we should verify:
1. Does `uv python install` include Tcl/Tk on Windows?
2. Can we use a different Python installation method?
3. Should we switch from `uv python pin` to `actions/setup-python`?
