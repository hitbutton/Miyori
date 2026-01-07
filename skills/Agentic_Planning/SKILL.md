# Skill: Agentic Planning & Reasoning

This skill defines the protocol for Miyori's multi-step autonomous tasks, using external files as a "working memory" to maintain transparency and prevent context bloat.

## 1. The Planning Protocol (Manus-Lite)
For any task requiring 3 or more steps, Miyori must externalize her state into the `workspace/` directory.

### Mandatory: `task_plan.md`
Created at the start of every complex loop. It must contain:
- **Goal**: A clear definition of the finished state.
- **Phases**: Checkboxes for high-level progress.
- **Errors & Decisions**: A log of technical pivots and failed attempts to prevent looping.
- **Status**: A one-line description of the current action.

### Optional: `notes.md`
Used for research-heavy tasks. Store technical documentation, code snippets, or long tool outputs here instead of keeping them in the chat history. "Store, don't stuff."

## 2. Iteration Workflow
1. **Initialize**: Create `task_plan.md` before taking any other action.
2. **Read Before Act**: At the start of a turn, read the plan to refresh goals and avoid "attention drift."
3. **Act & Update**: After a significant action or error, update the plan.
4. **Finalize**: Summarize the result and delete or archive the plan as appropriate.

## 3. Best Practices
- **Verbal Leaness**: Keep conversational responses brief. Point the user to the plan file for detailed progress.
- **Error Logging**: Every failed command or rejected edit must be logged in the plan with a "Resolution" attempt.
- **Context Management**: If a file read returns massive data, summarize it in the chat and save the full version to `notes.md`.
