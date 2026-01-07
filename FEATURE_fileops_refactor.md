# File Operations Tool Refactor - Implementation Plan

## Objective
Simplify the file operations tool by removing fragile editing modes and establishing a clear, reliable pattern for file modifications: **read → modify → write**.

## Current Problems
- **Fragile line-based edits**: Line numbers shift during multi-step operations
- **Unreliable search/replace**: String matching causes duplication bugs
- **Decision paralysis**: Multiple ways to edit create confusion
- **Token waste**: Fixing failed edits costs more than whole-file rewrites

## Success Criteria
- ✅ Single clear path for file modifications
- ✅ Zero code duplication bugs from editing
- ✅ Simpler tool interface (fewer parameters)
- ✅ Maintains cross-platform compatibility
- ✅ Clear documentation for Miyori's usage patterns

---

## Phase 1: Preparation (Safety First)

### 1.1 Create Feature Branch
```bash
git checkout -b refactor-simplify-fileops
```

### 1.2 Document Current Behavior
- Run existing test suite: `python -m pytest tests/ -v`
- Document any tests that specifically use `edit` operation
- Create backup of current `file_ops.py` in workspace for reference

### 1.3 Update Tests
- Identify tests using `operation="edit"`
- Rewrite them to use read/modify/write pattern
- Add new test: `test_read_modify_write_workflow()`

**Checkpoint**: All tests passing before any code changes

---

## Phase 2: Code Simplification

### 2.1 Remove Edit Functionality
In `src/miyori/implementations/tools/file_ops.py`:

**Remove these functions:**
```python
def _edit_file(path: str, edit_type: str, **kwargs) -> str:
    # DELETE ENTIRE FUNCTION
```

**Remove from main function:**
```python
elif operation == "edit":
    # DELETE THIS ENTIRE BRANCH
```

### 2.2 Remove Edit Parameters
Remove from `file_operations()` signature:
- `edit_type`
- `line_number`
- `action`
- `old_string`
- `new_string`
- `multiline`

Remove corresponding `ToolParameter` definitions from `file_ops_tool`.

### 2.3 Simplify Operation Enum
Update tool definition:
```python
ToolParameter(
    name="operation",
    type="string",
    description="Operation to perform: 'read', 'write', or 'list'",
    required=True,
    enum=["read", "write", "list"]  # Remove "edit"
)
```

### 2.4 Update Tool Description
Replace the entire `description` field with:

```python
description=(
    "Filesystem operations for reading, writing, and navigating files.\n\n"
    "OPERATIONS:\n"
    "• READ: View file contents with pagination (offset/limit)\n"
    "• WRITE: Create or overwrite files (mode: 'overwrite' or 'append')\n"
    "• LIST: Browse directory contents with pagination\n\n"
    "FILE EDITING PATTERN:\n"
    "To modify a file:\n"
    "1. Read the file: operation='read', path='file.py'\n"
    "2. Modify the content in memory\n"
    "3. Write it back: operation='write', path='file.py', content='...'\n\n"
    "This pattern is reliable and prevents issues with stale line numbers "
    "or string matching failures.\n\n"
    "PERMISSIONS:\n"
    "• Read/List: Works anywhere on the filesystem\n"
    "• Write: Restricted to project root directory\n\n"
    "FEATURES:\n"
    "• Paginated reading for large files (use offset/limit)\n"
    "• Binary detection with diagnostic headers\n"
    "• Automatic directory creation for new files\n"
    "• Cross-platform path handling\n"
)
```

---

## Phase 3: Testing & Validation

### 3.1 Unit Tests
Run test suite:
```bash
python -m pytest tests/ -v -k file_op
```

Expected results:
- All read/write/list tests: PASS
- Any edit-based tests: Should be rewritten or removed

### 3.2 Integration Test
Create `tests/test_read_modify_write.py`:
```python
def test_read_modify_write_pattern():
    """Test the recommended file editing workflow."""
    # Write initial file
    # Read it back
    # Modify content
    # Write modified version
    # Verify final state
    pass
```

### 3.3 Manual Testing with Miyori
Test script for Miyori to run:
1. "Read src/miyori/core/miyori.py"
2. "Add a comment to the top of that file"
3. Verify she uses read → write pattern without prompting

---

## Phase 4: Documentation Updates

### 4.1 Update Skills
Create/update `skills/Working_with_Files/SKILL.md`:
```markdown
# Working with Files

## The Pattern
Always use: Read → Modify → Write

## Example
# Read
file_ops(operation='read', path='example.py')

# Modify in memory (just do this in your response)

# Write complete new version
file_ops(operation='write', path='example.py', content='...')

## Why?
- Reliable: No string matching failures
- Verifiable: You see exactly what you're writing
- Simple: One clear path
```

### 4.2 Update agents.md
Add section:
```markdown
## File Editing
Use read-modify-write pattern. The file_operations tool 
does not support line-by-line editing - always rewrite 
the complete file.
```

### 4.3 Update CHANGELOG.md
```markdown
### [Unreleased]
#### Changed
- **file_operations tool**: Removed fragile line-based and 
  search/replace editing. Use read-modify-write pattern for 
  all file modifications.

#### Rationale
Line-based edits caused duplication bugs and stale line 
number issues. Whole-file rewrites are more reliable and 
token-cost is negligible with modern LLMs.
```

---

## Phase 5: Deployment

### 5.1 Code Review Checklist
- [ ] All `edit` operation code removed
- [ ] All edit-related parameters removed
- [ ] Tool description updated
- [ ] Tests passing
- [ ] No cross-platform issues introduced
- [ ] Documentation updated

### 5.2 Merge Strategy
```bash
# Run final test suite
python -m pytest tests/ -v

# Merge to main
git checkout main
git merge refactor-simplify-fileops

# Tag the release
git tag -a v0.2.0 -m "Simplified file operations tool"
```

### 5.3 Rollback Plan
If issues arise:
```bash
git revert HEAD
# Or restore from backup file_ops.py
```

---

## Phase 6: Monitor & Iterate

### 6.1 First Session Test
Watch Miyori's first session with new tool:
- Does she try to use edit operations? (shouldn't exist)
- Does she naturally use read-modify-write?
- Any confusion or friction points?

### 6.2 Metrics to Track
- **File operation success rate**: Should increase
- **Duplicate code bugs**: Should drop to zero
- **Token usage per file edit**: May increase slightly (acceptable)
- **Rate limit hits**: Should decrease (fewer retry loops)

### 6.3 Potential Future Enhancements
Only if needed based on usage patterns:
- [ ] `operation='preview'` - Show diff before writing
- [ ] `verify_checksum` parameter - Prevent accidental overwrites
- [ ] File size warnings before read/write

---

## Appendix: Removed Code Reference

### Functions Being Deleted
- `_edit_file()` - Entire function (~60 lines)

### Parameters Being Removed
- `edit_type` (string, enum)
- `line_number` (integer)
- `action` (string, enum)
- `old_string` (string)
- `new_string` (string)
- `multiline` (boolean)

### Operations Being Removed
- `operation="edit"` with `edit_type="line"`
- `operation="edit"` with `edit_type="search_replace"`

**Lines of Code Reduction**: ~100 lines
**Parameter Count Reduction**: 6 parameters → 0

---

## Timeline Estimate

- **Phase 1 (Prep)**: 15 minutes
- **Phase 2 (Code)**: 30 minutes
- **Phase 3 (Test)**: 20 minutes
- **Phase 4 (Docs)**: 25 minutes
- **Phase 5 (Deploy)**: 10 minutes
- **Phase 6 (Monitor)**: Ongoing

**Total Active Work**: ~2 hours
**Cool-off Period**: 24-48 hours to observe behavior

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Miyori confused by change | Low | Medium | Clear documentation in skills |
| Existing workflows break | Low | High | Test suite + backup branch |
| Token costs increase | Medium | Low | Acceptable tradeoff for reliability |
| Rollback needed | Very Low | Medium | Git revert ready |

---

## Sign-off

- [ ] Implementation plan reviewed
- [ ] Test strategy approved
- [ ] Documentation plan confirmed
- [ ] Rollback procedure understood
- [ ] Ready to begin Phase 1
