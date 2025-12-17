Redraft ARCHITECTURE.md as a living reference document for continuous feature development with AI agents. The current version is phase-based and marked "COMPLETED" - transform it into ongoing documentation.

## Requirements:

1. **Remove phase/completion language** - this is now a living document
2. **Consolidate into a single comprehensive file** that covers:
   - System overview (what exists and how it fits together)
   - Code conventions (the rules all new code must follow)
   - Key design decisions (why things are the way they are)
   - Extension points (where new features can plug in)
   - Feature planning workflow

3. **Add the transient planning doc convention**:
   - When planning features, a FEATURE_[name].md will be created at root
   - Reference it during implementation
   - It will be delete after the feature is completed

4. **Examine the actual codebase** to document:
   - How interfaces are structured
   - Current implementations and their patterns
   - Config structure and usage
   - The assistant's core loop

## Tone:
Direct, practical, minimal. This is a reference doc, not a tutorial.
**Keep it practical and focused and concise** - this will be in every agent's context

## Structure suggestion (adapt as you see fit):
- System Overview
- Code Conventions
- Extension Points
- Feature Planning Workflow

Preserve any critical details from the current ARCHITECTURE.md that are still relevant.