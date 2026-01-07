# Agent Guidelines (Linux)

## Environment
* **OS:** Linux (Ubuntu/Debian)
* **Shell:** Bash/Zsh
* **Package Manager:** `uv` (Always use `uv run`, never `pip`)

## Standards
* **Encoding:** UTF-8
* **Paths:** Forward slashes (`/`)
* **No Smart Quotes:** Strictly use straight quotes (`"` or `'`).

## Project Structure
* **Core Logic:** `src/miyori/core/`
* **Interfaces:** `src/miyori/interfaces/`
* **Implementations:** `src/miyori/implementations/`
* **Skills:** See `skills/` for technical manual.
* **Architecture:** Read `ARCHITECTURE.md` for high-level patterns.
