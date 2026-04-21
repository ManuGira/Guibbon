# PR Review Skill

## Purpose

Conduct structured, multi-step PR reviews for Guibbon Phase 1 modules. Use when you need:
- Detailed findings with root cause analysis
- Systematic checklist-driven review
- Historical tracking of review rounds
- Feedback that can be delegated to the PR Reviewer Agent

**Lightweight quick check?** Use **[PR Reviewer Agent](../../agents/pr-reviewer.agent.md)** instead — runs after CI passes and gives approval/rejection recommendation.

## Workflow

This skill walks through a three-phase review:

### Phase 1: Pre-Review Setup
- [ ] Confirm CI passed (all gates green)
- [ ] Note module being reviewed (1=params, 2=descriptor, 3=buildable, 4=app)
- [ ] Identify locked design decisions that apply (see project-knowledge.md)
- [ ] Review ARCHITECTURE.md section for this module

### Phase 2: Systematic Review (per checklist below)
- [ ] Architecture alignment
- [ ] Code quality
- [ ] Test coverage
- [ ] Type safety
- [ ] Documentation

**For each finding**: Record category, severity (must-fix/nice-to-have), explanation, suggested fix

### Phase 3: Recommendation
- [ ] Approve (all must-fix items resolved)
- [ ] Request Changes (list blockers)
- [ ] Request Conditional (approve if minor revisions)

---

## Review Checklists

### ✅ Architecture Alignment

**For Module 1 (params.py):**
- [ ] `_make_tracked_type()` creates subclasses inheriting from base types
- [ ] `_wrap_value()` attaches `_parent` and `_field_name` to tracked instances
- [ ] `GetPath()` reconstructs dotted paths by walking parent chain
- [ ] `@_params_decorator` extracts descriptors, applies `@dataclass`, wraps `__init__`
- [ ] Tracked values pass `isinstance()` checks (e.g., `isinstance(params.size, int)` → True)
- [ ] Descriptor metadata stored on CLASS via `__guibbon_descriptors__`

**For Module 2 (descriptor.py):**
- [ ] `_BaseDescriptor` has `triggered_callbacks` list attribute
- [ ] Descriptors support `.on_widget_change(new_value)` method
- [ ] `.get_triggered_descriptors()` returns list of `"field.callback_type"` strings
- [ ] `BuildableDescriptor` protocol defines `widget_class` attribute
- [ ] No tight coupling to Tkinter (pluggable for PySide6 later)

**For Module 3 (buildable.py):**
- [ ] `BuildableWidget` protocol defines zero-framework interface
- [ ] Protocol methods: `build(parent, descriptor)`, `get_value()`, `set_value(val)`
- [ ] No tkinter imports in protocol definition

**For Module 4 (app.py):**
- [ ] `need_update` cascades from children to parent (aggregates flags)
- [ ] `modified_descriptors` collected per cycle and broadcast to callbacks
- [ ] Event loop: collect triggers → build descriptor list → call user callbacks → clear
- [ ] Orchestrator decoupled from ImageViewer and Controller

### 🎯 Code Quality

- [ ] Private functions prefixed with `_`
- [ ] No circular imports between modules
- [ ] Magic numbers replaced with named constants
- [ ] Docstrings on public functions/classes (include examples for API entry points)
- [ ] Comments explain "why", not "what"
- [ ] No commented-out code or debug print statements
- [ ] Follows naming conventions in `params.py` reference

### 🧪 Test Coverage

**Coverage gates:**
- [ ] ≥ 80% coverage for non-GUI code
- [ ] New functions have corresponding tests
- [ ] Edge cases: empty values, None, boundary conditions, invalid inputs
- [ ] Test names describe what they verify (e.g., `test_slider_fires_on_drag_callback`)
- [ ] Happy path AND error path covered

**Test structure:**
- [ ] Setup/teardown properly isolates tests
- [ ] Tkinter singleton managed (shared `_tk_root` if needed)
- [ ] Fixtures used for repeated setup
- [ ] No hardcoded paths (use `pathlib` for cross-platform)

### 🔒 Type Safety

- [ ] All function parameters annotated
- [ ] All return types specified
- [ ] No `Any` without comment explaining why
- [ ] `dict[str, T]` instead of bare `dict`
- [ ] `list[T]` instead of bare `list`
- [ ] `Optional[T]` for nullable fields
- [ ] Dataclass fields with type hints
- [ ] Generic types correctly parameterized

### 📚 Documentation

- [ ] Module docstring explains purpose and usage
- [ ] Public functions have docstrings with parameters, returns, examples
- [ ] Complex algorithms have inline comments
- [ ] ARCHITECTURE.md updated if design changes
- [ ] Backward compatibility noted if applicable

---

## Common Review Findings

### 🔴 Must Fix

**Architecture**:
- Tracked value wrapping inconsistent (some fields wrapped, others not)
- Descriptor metadata on instance instead of class
- Callback list using non-standard string format (should be `"field.callback_type"`)

**Code Quality**:
- Circular imports detected
- Public API functions without docstrings

**Tests**:
- No tests for new functions
- Empty test file or placeholder tests

**Type Safety**:
- Untyped function (all params/returns missing annotations)
- Bare `dict`/`list` instead of parameterized types

### 🟡 Nice to Have

- Docstring examples could be more detailed
- Consider adding `__repr__` for debugging
- Test names could be more specific
- Comment explaining non-obvious logic

---

## Decision Matrix

| CI | Coverage | Architecture | Type Safety | Approval |
|----|----------|--------------|-------------|----------|
| ✅ | ✅ | ✅ | ✅ | **Approve** |
| ✅ | ✅ | ✅ | ⚠️ | **Request Changes** |
| ✅ | ⚠️ | ✅ | ✅ | **Request Changes** |
| ✅ | ✅ | ⚠️ | ✅ | **Request Changes** |
| ❌ | — | — | — | **Reject** (fix CI first) |

---

## Recording Findings

When you find an issue, document it like this:

```
**[Category]** Finding title
- Severity: must-fix | nice-to-have  
- Location: file.py#L42
- Description: What the issue is
- Suggested fix: How to resolve it
```

**Example**:
```
**[Type Safety]** Untyped callback parameter
- Severity: must-fix
- Location: descriptor.py#L18 in `on_widget_change()` 
- Description: Parameter `value` lacks type annotation
- Suggested fix: Change `def on_widget_change(self, value):` 
  to `def on_widget_change(self, value: int | str | float | bool):`
```

---

## Next Steps

1. ✅ Use this checklist for systematic review
2. 📋 Document findings in the review comment
3. 🚀 Invoke **PR Reviewer Agent** for quick approval/rejection recommendation
4. 📊 Track review rounds (if changes requested, re-review until approval)

