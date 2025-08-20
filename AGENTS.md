# AGENTS.md

## Build, Run, and Test Commands
- **Run main app:** `uv run vibrance.py` or `python vibrance.py`
- **Install dependencies:** `pip install -r requirements.txt`
- **No explicit test or lint commands found.** If tests are added, use standard Python (`pytest`, `unittest`) conventions.

## Code Style Guidelines
- **Python Version:** 3.11+
- **Imports:** Use absolute imports. Group: standard library, third-party, local modules.
- **Formatting:** Follow PEP8. Use 4 spaces for indentation. Keep lines ≤ 88 chars.
- **Types:** Use type hints for function signatures and variables where possible.
- **Naming:**
  - Variables/functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`
- **Error Handling:** Use try/except for external calls (I/O, API, LLM). Log errors with context.
- **Macros:** Add to `MACROS` dict in `app/macros.py`.
- **LLM/Code Modes:** See `app/mode/llm.py` and `app/mode/code.py` for customization.
- **Comments:** Use docstrings for modules, classes, and functions. Inline comments for complex logic.
- **Contributions:** Forks only; no PRs accepted.

*No Cursor or Copilot rules detected. Update this file if such rules are added.*
