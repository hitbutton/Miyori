# Agent Guidelines

## Environment
* **OS:** Windows 11 (Windows Terminal)
* **Shell:** PowerShell 7 (Core)
* **Python:** Project `.venv` only
* **Package Manager:** `uv` (Never use `pip`)

## Terminal & Encoding Standards
* **Encoding:** UTF-8 (No BOM) for all files and strings.
* **Command Syntax:** Use standard ASCII for PowerShell flags and logic.
* **No Smart Quotes:** Strictly use straight quotes (`"` or `'`). Never use `“`, `”`, `‘`, or `’`.
* **Paths:** Use Windows-style backslashes (`\`) for terminal commands.

## Execution Rules
* Always prefix Python execution with `uv run`.
* Use `uv add <package>` for new dependencies.
* Refer to `config.json` at the root for environment-specific variables.

## Project Structure
* **Contracts:** `src/interfaces/`
* **Implementations:** `src/implementations/`
* **Documentation:** Read `ARCHITECTURE.md` before implementation to ensure pattern compliance.