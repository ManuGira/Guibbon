---
description: "Use when implementing or testing Phase 1 core modules (params.py, descriptor.py, buildable.py, app.py). Covers architecture spec, coding patterns, and quality gates."
applyTo: "src/guibbon/core/**/*.py"
---

# Phase 1 Core Implementation Context

## Spec References

- Full design spec: `ARCHITECTURE.md` — read before coding any module
- Reference implementation: `src/guibbon/core/params.py` — follow its patterns
- Project decisions (locked): `project-knowledge.md`

## Module Responsibilities (Phase 1)

| Module | Responsibility |
|--------|---------------|
| `params.py` ✅ | `@guibbon.params` decorator, tracked types, `GetPath` |
| `descriptor.py` | `Descriptor` base, `BuildableDescriptor`, `SliderDescriptor`, `RadioDescriptor` |
| `buildable.py` | `BuildableWidget` protocol (no framework imports) |
| `app.py` | App orchestrator, `need_update` cascading, `modified_descriptors` collection |

## Locked Design Rules

- **Tracked values ARE their base types**: `TrackedInt` inherits from `int`; `isinstance(params.size, int)` → True
- **Descriptor metadata on CLASS**: store in `__guibbon_descriptors__`, not on instances
- **Modified descriptors**: list of `"field.callback_type"` strings (e.g. `"size.on_drag"`)
- **No Tkinter imports in `core/`**: protocols/base classes only; keep pluggable for PySide6
- **`triggered_callbacks`**: appended per event, cleared after each app cycle

## Coding Patterns from params.py

```python
# Private helpers: prefix with _
def _make_tracked_type(base: type) -> type: ...

# Descriptor metadata on class attribute
cls.__guibbon_descriptors__ = {...}

# Wrap field values with parent tracking
self.size = _wrap_value(default, parent=self, field_name="size")
```

## Tests

- Mirror source structure: `tests/test_<module>.py`
- 100% coverage for all non-GUI code
- Test names describe behavior: `test_slider_fires_on_drag_callback`
- Edge cases: None defaults, empty options, nested params

## Quality Gate

After implementing a module:
```powershell
.\ci.ps1  # Must pass: pytest + ruff + ty
```
Then invoke the **PR Reviewer** agent before merging.
