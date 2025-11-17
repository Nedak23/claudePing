# Multi-Repository Support - User Guide

**Version:** 1.0
**Status:** Implemented (Phases 1-4)

---

## Overview

ClaudePing now supports working with **multiple repositories** simultaneously! You can switch between projects, target specific repos with commands, and manage your entire development portfolio via SMS/WhatsApp.

### Key Features

- ✅ Work with multiple repositories from a single ClaudePing instance
- ✅ Switch between repositories with natural language commands
- ✅ Target specific repos inline: `"in project-api: add login"`
- ✅ Per-repository access control
- ✅ Backward compatible with single-repo mode
- ✅ Automatic branch management per repository
- ✅ Repository discovery and auto-registration

---

## Quick Start

### 1. Enable Multi-Repo Mode

Run the migration script to enable multi-repo support:

```bash
# Dry run first to see what will happen
python migrate_to_multirepo.py --dry-run

# Run the actual migration
python migrate_to_multirepo.py

# Restart ClaudePing
python app.py
```

### 2. Register Additional Repositories

```bash
# Register a repository
python repo_admin.py register project-api /path/to/api --admin-phone +1234567890

# List all repositories
python repo_admin.py list

# Auto-discover and register repos
python repo_admin.py discover /home/user/projects --auto-register
```

### 3. Start Using Multi-Repo Commands

Send messages via WhatsApp/SMS:

```
list repos                          → See all your repositories
switch to project-api               → Change active repository
in project-api: add login endpoint  → Run command in specific repo
repos status                        → Check status of all repos
```

---

## User Commands

### Repository Management

| Command | Description | Example |
|---------|-------------|---------|
| `list repos` | Show all accessible repositories | `list repos` |
| `switch to <repo>` | Change active repository | `switch to project-api` |
| `info <repo>` | Show repository details | `info web-app` |
| `repos status` | Status of all repositories | `repos status` |

### Inline Repository Targeting

Execute commands in a specific repository without switching:

```
in <repo>: <command>        → in project-api: add feature X
for <repo>: <command>       → for web-app: fix navbar bug
@<repo>: <command>          → @api: run tests
on <repo>: <command>        → on frontend: update styles
```

**Example:**

```
User: in project-api: add JWT authentication to login endpoint

Response: [project-api] ✓ Done! Added JWT auth to /login.
Branch: sms/20251115_143000. Files: api/auth.py, api/models.py
```

### Active Repository Mode

When you switch to a repository, all subsequent commands use that repo until you switch again:

```
User: switch to web-app
Response: ✓ Switched to web-app

User: add dark mode toggle
Response: [web-app] ✓ Done! Added dark mode...
          [continues to use web-app]

User: switch to api
Response: ✓ Switched to api (was: web-app)
```

---

## Admin Guide

### Repository Administration

Use the `repo_admin.py` CLI tool to manage repositories:

#### List Repositories

```bash
python repo_admin.py list
```

Output:
```
Found 3 repositories:

✓ claudeping (default)
  Path: /home/user/claudePing
  Remote: https://github.com/user/claudePing
  Users: 2

✓ project-api
  Path: /home/user/projects/api
  Remote: https://github.com/user/api
  Users: 1
```

#### Register a Repository

```bash
python repo_admin.py register my-project /path/to/project \
  --description "My awesome project" \
  --admin-phone +1234567890
```

#### Unregister a Repository

```bash
python repo_admin.py unregister old-project --force
```

#### Grant User Access

```bash
# Grant read/write access
python repo_admin.py grant project-api +1234567890

# Grant specific permissions
python repo_admin.py grant web-app +0987654321 --permissions read

# Grant admin access
python repo_admin.py grant sensitive-repo +1111111111 --permissions read,write,admin
```

#### Revoke User Access

```bash
python repo_admin.py revoke project-api +1234567890
```

#### View Repository Details

```bash
python repo_admin.py info project-api
```

Output:
```
Repository: project-api
Status: ✓ Valid
Path: /home/user/projects/api
Remote: https://github.com/user/api
Current branch: main
Uncommitted changes: No
Last accessed: 2025-11-15T14:30:00

Access Control (2 users):
  +1234567890: read, write, admin
  +0987654321: read, write
```

#### Discover Repositories

```bash
# Scan directory for git repos
python repo_admin.py discover /home/user/projects --depth 3

# Auto-register discovered repos
python repo_admin.py discover /home/user/projects --auto-register
```

#### Set Default Repository

```bash
python repo_admin.py set-default project-api
```

---

## Configuration

### Repository Configuration File

Multi-repo mode uses `config/repositories.json`:

```json
{
  "repositories": {
    "claudeping": {
      "name": "claudeping",
      "path": "/home/user/claudePing",
      "remote_url": "https://github.com/user/claudePing",
      "description": "Main ClaudePing project",
      "created_at": "2025-11-15T10:00:00Z",
      "last_accessed": "2025-11-15T14:30:00Z",
      "access_control": {
        "+1234567890": ["read", "write", "admin"]
      }
    },
    "project-api": {
      "name": "project-api",
      "path": "/home/user/projects/api",
      "remote_url": "https://github.com/user/api",
      "description": "API backend",
      "created_at": "2025-11-15T11:00:00Z",
      "last_accessed": "2025-11-15T15:00:00Z",
      "access_control": {
        "+1234567890": ["read", "write"],
        "+0987654321": ["read"]
      }
    }
  },
  "default_repository": "claudeping"
}
```

### Access Control Permissions

| Permission | Capabilities |
|------------|-------------|
| `read` | View repo status, list files, read code (no commits) |
| `write` | Create branches, commit changes, push to remote |
| `admin` | Register/unregister repos, manage user access |

### Environment Variables

No new environment variables required! Multi-repo works with existing configuration.

---

## Migration Guide

### Migrating from Single-Repo Mode

The migration is **backward compatible** and **non-destructive**.

#### Step 1: Backup

```bash
python migrate_to_multirepo.py --dry-run
```

Review the output to see what changes will be made.

#### Step 2: Run Migration

```bash
python migrate_to_multirepo.py
```

This will:
1. Create backup in `backups/backup_YYYYMMDD_HHMMSS/`
2. Generate `config/repositories.json`
3. Add repository metadata to existing responses
4. Update session files with repository context
5. Verify migration success

#### Step 3: Restart ClaudePing

```bash
python app.py
```

You should see:
```
INFO - Multi-repo mode ENABLED
INFO - Loaded 1 repositories
```

#### Step 4: Test

Send a WhatsApp message:
```
list repos
```

Expected response:
```
You have 1 repos:
- claudeping (active)
```

### Rollback

If you need to rollback:

```bash
# Stop ClaudePing
pkill -f app.py

# Remove multi-repo config
rm config/repositories.json

# Restore from backup
cp -r backups/backup_YYYYMMDD_HHMMSS/* .

# Restart ClaudePing (will run in single-repo mode)
python app.py
```

---

## Architecture

### Components

1. **RepositoryManager** - Central registry for repositories
2. **Repository** - Data model with access control
3. **EnhancedSessionManager** - Tracks active repo per user
4. **CommandParser** - Detects repo commands and intent
5. **RepoAwareClaudeHandler** - Executes Claude in repo context
6. **GitHandlerFactory** - Creates repo-specific git handlers

### Mode Detection

ClaudePing automatically detects which mode to run in:

- **Multi-repo mode:** `config/repositories.json` exists
- **Single-repo mode:** No config file (legacy behavior)

### Data Flow

```
User Message → Command Parser → Intent Recognition
    ↓
Repository Resolution (if needed)
    ↓
Access Control Validation
    ↓
Claude Execution (in repo context)
    ↓
Git Operations (branch, commit, push)
    ↓
Response with Repo Context
```

---

## Troubleshooting

### Issue: "No active repository"

**Solution:** Switch to a repository first:
```
switch to project-name
```

Or use inline targeting:
```
in project-name: your command
```

### Issue: "Repository not found"

**Cause:** Repository name doesn't match registered name.

**Solution:** List repositories to see exact names:
```
list repos
```

Then use the exact name:
```
switch to exact-repo-name
```

### Issue: "No write access"

**Cause:** User doesn't have write permissions for repository.

**Solution:** Admin must grant access:
```bash
python repo_admin.py grant repo-name +1234567890 --permissions read,write
```

### Issue: Multi-repo mode not enabled

**Symptom:** Commands like `list repos` don't work.

**Solution:** Run migration:
```bash
python migrate_to_multirepo.py
```

### Issue: Repository path invalid

**Cause:** Repository moved or deleted.

**Solution:** Update path or unregister:
```bash
python repo_admin.py unregister old-repo
python repo_admin.py register new-repo /new/path
```

---

## Best Practices

### Naming Repositories

- Use short, memorable names: `api`, `web`, `mobile`
- Use hyphens for multi-word names: `user-service`, `admin-panel`
- Avoid spaces and special characters
- Keep names under 20 characters for SMS readability

### Access Control

- Grant `admin` only to trusted users
- Use `read` for view-only access (safe for demos)
- Default to `read,write` for regular developers
- Regularly audit access with `repo_admin.py info <repo>`

### Repository Organization

- Keep related projects grouped by path
- Use descriptive descriptions for each repo
- Set appropriate default repository
- Regularly check `repos status` to see what needs attention

### SMS Best Practices

- Use inline targeting for one-off commands
- Switch repos for multiple commands in same project
- Check active repo with `STATUS` command
- Use abbreviations: `list repos` instead of `list repositories`

---

## Examples

### Scenario 1: Working on Multiple Microservices

```
User: list repos
Response: You have 4 repos:
- api-gateway (active)
- user-service
- auth-service
- payment-service

User: in auth-service: add rate limiting to /login endpoint
Response: [auth-service] ✓ Done! Added rate limiting...

User: in user-service: add email verification field
Response: [user-service] ✓ Done! Added email_verified field...

User: repos status
Response: Repo status:
- api-gateway: clean
- user-service: modified
- auth-service: modified
- payment-service: clean
```

### Scenario 2: Switching Context

```
User: switch to frontend
Response: ✓ Switched to frontend

User: add loading spinner to dashboard
Response: [frontend] ✓ Done! Added spinner component...

User: fix navbar alignment on mobile
Response: [frontend] ✓ Done! Fixed navbar CSS...

User: switch to backend
Response: ✓ Switched to backend (was: frontend)

User: optimize database queries
Response: [backend] ✓ Done! Added indexes...
```

### Scenario 3: Admin Managing Repositories

```bash
# Discover new projects
$ python repo_admin.py discover /home/user/projects

Found 5 repositories:
1. /home/user/projects/web-app
2. /home/user/projects/mobile-app
3. /home/user/projects/api
4. /home/user/projects/analytics
5. /home/user/projects/admin-panel

# Register the important ones
$ python repo_admin.py register web-app /home/user/projects/web-app --admin-phone +1234567890
$ python repo_admin.py register api /home/user/projects/api --admin-phone +1234567890

# Grant access to team member
$ python repo_admin.py grant web-app +0987654321 --permissions read,write
$ python repo_admin.py grant api +0987654321 --permissions read

# Check configuration
$ python repo_admin.py list

Found 3 repositories:
✓ claudeping (default)
✓ web-app
✓ api
```

---

## FAQ

**Q: Does multi-repo mode affect existing functionality?**
A: No! It's fully backward compatible. Single-repo deployments continue working.

**Q: Can I disable multi-repo mode?**
A: Yes, just delete `config/repositories.json` and restart. ClaudePing will run in single-repo mode.

**Q: How many repositories can I have?**
A: Recommended: 5-50 repos per installation. Performance tested up to 100 repos.

**Q: Do I need separate Twilio numbers for each repo?**
A: No! One Twilio number works for all repositories.

**Q: Can multiple users share the same repository?**
A: Yes! Use `repo_admin.py grant` to give multiple users access.

**Q: What happens if I typo a repository name?**
A: ClaudePing will suggest available repositories: "Repository 'wep-app' not found. Available: web-app, mobile-app, api"

**Q: Can I use multi-repo with WhatsApp?**
A: Yes! All commands work identically over WhatsApp and SMS.

**Q: Are there extra costs for multi-repo mode?**
A: No! Same Twilio costs, no additional infrastructure needed.

---

## Roadmap

### Phase 5-8 (Upcoming)

- [ ] Enhanced UX with repo shortcuts
- [ ] Cross-repo operations (status all, search all)
- [ ] Repository templates
- [ ] Advanced security audit logging
- [ ] Comprehensive test suite
- [ ] Performance monitoring dashboards
- [ ] Auto-backup and disaster recovery

### Future Enhancements

- Repository groups/categories
- Multi-user collaboration features
- Repository analytics and insights
- Voice command support
- Integration with GitHub API for PR creation

---

## Support

For issues or questions:

1. Check this guide and troubleshooting section
2. Review logs: Check `claudeping.log` for errors
3. Test with `python repo_admin.py list` to verify configuration
4. Create an issue on GitHub: [github.com/Nedak23/claudePing/issues]

---

## Credits

Multi-repository support implemented as part of the CTO Strategic Plan.
See `docs/CTO_MULTI_REPO_PLAN.md` for full architectural details.

---

**Happy multi-repo coding!** 🚀
