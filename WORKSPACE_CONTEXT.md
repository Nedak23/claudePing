# Workspace Context - Full Repository Access

## Overview

Claude Code now has **full workspace context** when processing requests via WhatsApp/SMS. This means Claude can:

- ✅ **Read any file** in the repository
- ✅ **Search for code patterns** using grep/search tools
- ✅ **Explore directory structure** to understand the codebase
- ✅ **Edit and create files** with full context awareness
- ✅ **Understand existing code** before making changes

## What Changed

### Before
```python
# Old behavior: One-off prompt with no context
subprocess.run(['claude', '-p', 'add a function'])
```
Claude received prompts without being aware it was in a codebase.

### After
```python
# New behavior: Workspace-aware prompts
enhanced_prompt = """
You are working in a git repository at: /path/to/repo
You have full access to read, explore, and modify files in this codebase.
Use your file reading and editing tools to understand the code structure before making changes.

User request:
add a function
"""
subprocess.run(['claude', '-p', enhanced_prompt], cwd=repository_path)
```
Claude now knows it's in a codebase and should explore before making changes.

## Implementation Details

### 1. Base ClaudeHandler (`claude_handler.py`)

**New method: `_build_workspace_prompt()`**
- Detects if running in a git repository
- Adds context about available tools and capabilities
- Tells Claude to explore the codebase before making changes

**Updated method: `send_prompt()`**
- Now accepts `working_dir` parameter
- Sets `cwd` when running subprocess
- Enhances all prompts with workspace context

### 2. Repository-Aware Handler (`repo_aware_claude_handler.py`)

**New method: `_build_repo_aware_prompt()`**
- Includes repository name and description
- Explicitly lists available tools (read, search, edit)
- Provides repository-specific context from configuration

**Updated method: `send_prompt_to_repo()`**
- Uses enhanced prompt building
- Explicitly sets `cwd` to repository path
- Maintains full context for multi-repo scenarios

## How It Works

### Single Repository Mode

When a user sends: `"Fix the bug in the authentication module"`

1. **Enhanced prompt created:**
   ```
   You are working in a git repository at: /home/user/claudePing
   You have full access to read, explore, and modify files in this codebase.
   Use your file reading and editing tools to understand the code structure before making changes.

   User request:
   Fix the bug in the authentication module
   ```

2. **Claude Code executes with context:**
   - Runs in the repository directory (`cwd=/home/user/claudePing`)
   - Can use `Read` tool to examine files
   - Can use `Grep` tool to search for patterns
   - Can use `Glob` tool to find files
   - Can use `Edit` tool to modify files

3. **Claude's typical workflow:**
   ```
   1. Search for authentication-related files
   2. Read the authentication module
   3. Identify the bug
   4. Make the fix
   5. Potentially run tests
   ```

### Multi-Repository Mode

When a user sends: `"in project-api: add authentication endpoint"`

1. **Repository-aware prompt created:**
   ```
   You are working in the 'project-api' repository.
   Repository path: /home/user/Projects/api
   Repository description: API microservice

   You have full access to:
   - Read any file in this codebase using your file reading tools
   - Search for code patterns using grep/search tools
   - Explore the directory structure
   - Edit and create files as needed

   IMPORTANT: Before making changes, use your tools to explore the codebase and understand the existing structure.

   User request:
   add authentication endpoint
   ```

2. **Context switching:**
   - Changes to repository directory
   - Runs Claude Code in that context
   - All file operations are relative to that repo
   - Git operations affect only that repository

## Example Interactions

### Example 1: Understanding Code Structure

**User:** "What files handle user authentication?"

**Claude's workflow:**
1. Uses `Grep` to search for "authentication" patterns
2. Uses `Read` to examine relevant files
3. Provides summary of authentication flow
4. Lists specific files and their roles

### Example 2: Making Changes

**User:** "Add input validation to the login endpoint"

**Claude's workflow:**
1. Uses `Grep` to find login endpoint
2. Uses `Read` to understand current implementation
3. Uses `Read` to check if validation utilities exist
4. Uses `Edit` to add validation
5. Commits changes to git branch

### Example 3: Refactoring

**User:** "Refactor the database connection code to use connection pooling"

**Claude's workflow:**
1. Uses `Grep` to find all database connection code
2. Uses `Read` to understand current implementation
3. Uses `Glob` to find related configuration files
4. Uses `Edit` to update connection code
5. Uses `Edit` to update configuration
6. Ensures all references are updated

## Testing

A test script is provided: `test_workspace_context.py`

```bash
# Make sure .env is configured with ANTHROPIC_API_KEY
python3 test_workspace_context.py
```

This will:
1. Initialize ClaudeHandler
2. Send a test prompt asking Claude to list Python files
3. Verify Claude can see and interact with the repository

## Benefits

### For Users
- **Better responses**: Claude understands the full context
- **Safer changes**: Claude explores before modifying
- **Smarter edits**: Changes integrate with existing code patterns
- **More autonomy**: Can handle complex multi-file tasks

### For Developers
- **Less manual context**: Don't need to explain codebase structure
- **Fewer iterations**: Claude gets it right the first time
- **Better code quality**: Changes follow existing patterns
- **Full automation**: Claude can handle entire features end-to-end

## Configuration

No additional configuration needed! The workspace context is automatically enabled for:

- **Single repository mode**: Uses the current working directory
- **Multi-repository mode**: Uses the repository path from `config/repositories.json`

## Limitations

1. **No persistent sessions (yet)**: Each message is independent
   - Future: Add session management to maintain conversation context

2. **Fixed timeout**: 120 seconds per request
   - May need adjustment for very large codebases

3. **No streaming**: Waits for complete response
   - Future: Add streaming support for real-time updates

## Next Steps

Recommended improvements:

1. **Session Management**: Maintain conversation context across messages
   - Store conversation history per user
   - Pass previous messages to Claude
   - Enable "remember what we discussed" functionality

2. **Streaming Responses**: Get real-time updates
   - Show progress as Claude works
   - Better UX for long-running tasks

3. **Tool Usage Logging**: Track what Claude explores
   - Help users understand what Claude examined
   - Provide audit trail for changes

## Migration Notes

**Backwards Compatible**: Existing functionality is preserved.

- All existing SMS commands work the same way
- Multi-repository mode works the same way
- No breaking changes to the API

**What's Different**:
- Prompts are now enhanced with workspace context
- Claude Code sees the full repository
- Better code generation and understanding

## Troubleshooting

### Issue: Claude doesn't seem to use file reading tools

**Solution**: The enhanced prompts explicitly tell Claude to explore. If it's not working:
1. Check that Claude Code CLI is up to date: `claude --version`
2. Verify you're in a git repository: `git status`
3. Check logs for any errors in `claude_handler.py`

### Issue: Changes are made without understanding existing code

**Solution**: This shouldn't happen with workspace context enabled. The prompts specifically instruct Claude to explore first. If it occurs:
1. Verify the enhanced prompt is being used (check logs)
2. Increase timeout if the codebase is very large
3. Make prompts more specific about what to examine

### Issue: Performance is slow

**Solution**: Claude Code needs time to explore large codebases:
1. Consider increasing timeout for complex tasks
2. Be more specific in prompts to narrow the search space
3. Use multi-repository mode to work with smaller, focused repos

## Summary

Claude Code now has **full workspace awareness** and can intelligently explore, understand, and modify your codebase via WhatsApp/SMS. No additional setup required - it just works better!
