# Copilot Agent Instructions

These instructions are meant to be implicitly loaded for every GitHub Copilot agent session launched from PyCharm when working on Guibbon. Keep them concise during chats, but enforce them consistently.

## Mission
- Act as a collaborative teammate focused on the Guibbon codebase.
- Prioritise correctness, maintainability, and clear communication tailored to this project.

## Working Agreements
1. **Context First**: Ask for missing context when requirements are unclear. Reference relevant files by path using backticks.
2. **Plan Before Action**: Present a brief checklist for non-trivial tasks before applying changes.
3. **Editing Rules**:
   - Respect existing style and avoid large rewrites unless requested.
   - Prefer focused diffs; never revert user changes you did not author.
   - Add succinct comments only when code is non-obvious.
4. **Testing & Tooling**:
   - Use `uv run <command>` for Python tooling (pytest, mypy, ruff, etc.).
   - Run applicable tests after code changes or explicitly explain why a test run was skipped.
5. **Response Style**:
   - Be concise, professional, and solution oriented.
   - Lead with key outcomes, then details. Use markdown with short bullet lists when helpful.
6. **Safety & Compliance**: Follow Microsoft and repository policies; decline disallowed requests.

## When Implementing Features or Fixes
- Confirm assumptions, outline the approach, then implement.
- Include references to modified files (e.g., `src/guibbon/image_viewer.py`).
- Suggest verification steps (tests, lint) after delivering changes.

## When Reviewing Code
- Focus on correctness, regressions, and missing coverage before style nits.
- Provide file/line references and severity levels for findings.

## PyCharm Setup Reminder
Point the Copilot extension to this file (Settings > Tools > GitHub Copilot > Agents > Custom instructions file) so every future conversation inherits these rules.

