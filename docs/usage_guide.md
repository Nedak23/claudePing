# ClaudePing Usage Guide

Complete guide to using ClaudePing for coding via WhatsApp/SMS.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [WhatsApp Commands](#whatsapp-commands)
3. [Repository Management](#repository-management)
4. [Repository Admin CLI](#repository-admin-cli)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## Basic Usage

### Sending Coding Requests

Simply send natural language requests via WhatsApp to the Twilio sandbox number:

```
Create a Python function that calculates fibonacci numbers
```

```
Add error handling to the login function
```

```
Write unit tests for the payment module
```

```
Refactor the database connection to use connection pooling
```

ClaudePing will:
1. Create a new git branch
2. Execute your request using Claude
3. Commit changes with descriptive message
4. Push to GitHub
5. Send you a summary response

### Response Format

You'll receive a response like:

```
✓ Done! Modified 2 files. Branch: sms/20241202_143022.

Summary: Created fibonacci function with memoization for optimal performance. Added docstrings and type hints.

Full: https://your-server.com/response/20241202_143022_abc123
```

**Response includes:**
- ✓ Status indicator (success/failure)
- Number of files modified
- Branch name created
- Brief summary of changes
- Link to full detailed response

### Getting Full Responses

To view the complete response:

```
FULL 20241202_143022_abc123
```

This returns the full Claude response with all details.

## WhatsApp Commands

### Session Management

| Command | Description | Example |
|---------|-------------|---------|
| `STATUS` | View current session info | `STATUS` |
| `NEW SESSION` | Start fresh conversation | `NEW SESSION` |
| `FULL <id>` | Get complete response | `FULL 20241202_143022_abc123` |

### Repository Commands

| Command | Description | Example |
|---------|-------------|---------|
| `list repos` | Show all accessible repositories | `list repos` |
| `switch to <repo>` | Change active repository | `switch to my-api` |
| `use <repo>` | Alternative to switch | `use web-frontend` |
| `info <repo>` | Show repository details | `info my-api` |
| `repos status` | Status of all repositories | `repos status` |

### Inline Repository Targeting

Execute a command in a specific repository without switching:

```
in <repo>: <your request>
```

**Examples:**
```
in my-api: add JWT authentication
in web-frontend: add dark mode toggle
in mobile-app: fix navigation bug
```

**Alternative syntaxes:**
```
for my-api: add feature
@my-api: run tests
on my-api: update dependencies
```

## Repository Management

### Understanding Repositories

ClaudePing can manage multiple git repositories simultaneously. Each repository:
- Has its own git history and branches
- Has separate access control
- Maintains independent session context
- Can be targeted inline or set as active

### Viewing Your Repositories

```
list repos
```

Response:
```
You have 3 repos:
- my-api (active)
- web-frontend
- mobile-app
```

### Switching Between Repositories

```
switch to web-frontend
```

Response:
```
✓ Switched to web-frontend
```

Now all commands go to `web-frontend` until you switch again.

### Checking Repository Details

```
info my-api
```

Response:
```
Repository: my-api
Path: /Users/you/projects/api
Remote: https://github.com/you/api
Current branch: main
Status: ✓ Valid
Your access: admin
```

### Active Repository Behavior

When you switch to a repository, it becomes your **active repository**:

```
You: switch to my-api
ClaudePing: ✓ Switched to my-api

You: add login endpoint
ClaudePing: [my-api] ✓ Done! Added /login endpoint...

You: add error handling
ClaudePing: [my-api] ✓ Done! Added error handling...
```

The active repository persists across messages until you switch.

### Using Multiple Repositories

**Scenario: Working on microservices**

```
You: list repos
ClaudePing: You have 4 repos:
- api-gateway
- auth-service (active)
- user-service
- payment-service

You: in user-service: add email verification field
ClaudePing: [user-service] ✓ Done! Added email_verified column...

You: in payment-service: add stripe integration
ClaudePing: [payment-service] ✓ Done! Added Stripe SDK...

You: switch to api-gateway
ClaudePing: ✓ Switched to api-gateway

You: add rate limiting
ClaudePing: [api-gateway] ✓ Done! Added rate limiter middleware...
```

## Repository Admin CLI

The `repo_admin.py` CLI tool manages repositories without manual JSON editing.

### Listing Repositories

```bash
# Basic list
python repo_admin.py list

# Detailed view
python repo_admin.py list --verbose
```

Output:
```
Registered Repositories (3)
===========================

my-api (default)
  Path:   /Users/you/projects/api
  Remote: https://github.com/you/api

web-frontend
  Path:   /Users/you/projects/web
  Remote: https://github.com/you/web

mobile-app
  Path:   /Users/you/projects/mobile
  Remote: https://github.com/you/mobile
```

### Registering a Repository

```bash
python repo_admin.py register <name> <path> [options]
```

**Options:**
- `--remote-url` - Git remote URL (auto-detected if not provided)
- `--description` - Human-readable description
- `--admin-phone` - Phone number to grant admin access
- `--dry-run` - Preview without making changes

**Examples:**

```bash
# Basic registration (auto-detects remote URL)
python repo_admin.py register my-api /Users/you/projects/api \
  --admin-phone +1234567890

# With description
python repo_admin.py register web-app /Users/you/projects/web \
  --description "Main web application" \
  --admin-phone +1234567890

# Preview changes without applying
python repo_admin.py register new-repo /path/to/repo --dry-run
```

### Auto-Discovering Repositories

Find all git repositories in a directory:

```bash
# Scan directory
python repo_admin.py discover ~/projects

# Scan with depth limit
python repo_admin.py discover ~/projects --max-depth 2

# Auto-register all found repos
python repo_admin.py discover ~/projects --auto-register --admin-phone +1234567890
```

Output:
```
Discovering repositories in: /Users/you/projects
Maximum depth: 3

Discovered Repositories (5)
===========================
  api           /Users/you/projects/api
  web           /Users/you/projects/web (already registered)
  mobile        /Users/you/projects/mobile
  admin-panel   /Users/you/projects/admin-panel
  analytics     /Users/you/projects/analytics
```

### Unregistering a Repository

```bash
# With confirmation prompt
python repo_admin.py unregister old-project

# Skip confirmation
python repo_admin.py unregister old-project --force
```

### Granting Access

Give users access to repositories:

```bash
# Grant write access (default)
python repo_admin.py grant my-api +9876543210

# Grant specific level
python repo_admin.py grant my-api +9876543210 --level read
python repo_admin.py grant my-api +9876543210 --level write
python repo_admin.py grant my-api +9876543210 --level admin
```

**Access Levels:**
- `read` - View only, no commits
- `write` - Can commit and push (most common)
- `admin` - Can manage repository and access control

### Revoking Access

```bash
python repo_admin.py revoke my-api +9876543210
```

### Viewing Repository Details

```bash
python repo_admin.py info my-api
```

Output:
```
Repository: my-api
======================
Name:         my-api
Path:         /Users/you/projects/api
Remote URL:   https://github.com/you/api
Description:  API backend service
Default:      Yes
Status:       Valid
Created:      2025-12-01T10:00:00
Last Access:  2025-12-02T14:30:00

Access Control:
  +1234567890          admin
  +9876543210          write
  +5555555555          read

Git Information:
  Current Branch:     main
  Uncommitted Changes: No
```

### Setting Default Repository

```bash
python repo_admin.py set-default my-api
```

The default repository is used when no repository is specified.

### Validating Configuration

Check for issues in your repository configuration:

```bash
python repo_admin.py validate
```

Output:
```
Configuration Validation
========================
✓ Configuration file exists: config/repositories.json
✓ JSON syntax is valid

Validating 3 repositories...
✓ my-api: Valid
✓ web-frontend: Valid
✗ old-project: Invalid
  Path: /Users/you/old-project
  - Path does not exist

✓ Default repository: my-api

✗ Validation failed - see errors above
```

## Advanced Usage

### Multi-Step Workflows

ClaudePing maintains conversation context, so you can build on previous requests:

```
You: Create a REST API endpoint for user login

ClaudePing: ✓ Done! Created /api/login endpoint...

You: Add JWT token generation to it

ClaudePing: ✓ Done! Added JWT token generation...

You: Add rate limiting to prevent brute force

ClaudePing: ✓ Done! Added rate limiter with 5 attempts per minute...

You: Write unit tests for this endpoint

ClaudePing: ✓ Done! Created comprehensive test suite...
```

### Working Across Multiple Repos

```
You: in auth-service: add JWT authentication

ClaudePing: [auth-service] ✓ Done! Added JWT auth...

You: in api-gateway: integrate with auth service

ClaudePing: [api-gateway] ✓ Done! Added auth middleware...

You: in user-service: add protected endpoints

ClaudePing: [user-service] ✓ Done! Added auth decorators...
```

### Session Management

**Check your current session:**
```
STATUS
```

Response:
```
Session: abc123def456
Active repo: my-api
Messages: 15
Started: 2 hours ago
```

**Start fresh when context gets stale:**
```
NEW SESSION
```

Response:
```
✓ New session started
Previous session: abc123def456 (15 messages)
```

### Branch Management

ClaudePing automatically creates branches:
- Format: `sms/YYYYMMDD_HHMMSS`
- Example: `sms/20241202_143022`
- Unique per request
- Automatically pushed to GitHub

You can view and merge branches in GitHub:

```bash
# In your local repository
git fetch origin
git checkout sms/20241202_143022
git log  # Review changes
git merge main
```

## Troubleshooting

### Common Issues

#### Issue: No response from ClaudePing

**Possible causes:**
1. Flask server not running
2. ngrok tunnel expired
3. Twilio webhook not configured
4. Your number not whitelisted

**Solutions:**
```bash
# Check Flask server is running
ps aux | grep "python app.py"

# Check ngrok is running
ps aux | grep ngrok

# Verify your number is whitelisted
grep WHITELISTED_NUMBERS .env

# Check server logs
tail -f claudeping.log
```

#### Issue: "Not authorized" response

**Cause:** Your phone number isn't whitelisted or lacks repo access.

**Solution:**
```bash
# Check whitelist in .env
cat .env | grep WHITELISTED_NUMBERS

# Check repository access
python repo_admin.py info my-api

# Grant access if needed
python repo_admin.py grant my-api +1234567890 --level write
```

#### Issue: "Repository not found"

**Cause:** Repository name doesn't exist or typo.

**Solution:**
```
# List exact repository names
list repos

# Use exact name
switch to my-api
```

#### Issue: "No active repository"

**Cause:** No repository is set as active.

**Solution:**
```
# Switch to a repository
switch to my-api

# Or use inline targeting
in my-api: your request
```

#### Issue: Claude timeout

**Cause:** Request is too complex or Claude is slow.

**Solution:**
- Break request into smaller steps
- Be more specific in your request
- Check Claude API status
- Increase timeout in `claude_handler.py` (default: 120s)

#### Issue: Git push failed

**Possible causes:**
1. No internet connection
2. GitHub authentication failed
3. Repository doesn't have remote
4. Branch protection rules

**Solutions:**
```bash
# Verify remote exists
cd /path/to/repo
git remote -v

# Test GitHub access
git push origin main --dry-run

# Check GitHub token if using HTTPS
cat .env | grep GITHUB_TOKEN

# Try SSH instead of HTTPS
git remote set-url origin git@github.com:user/repo.git
```

#### Issue: Repository validation fails

**Cause:** Path doesn't exist or isn't a git repository.

**Solution:**
```bash
# Validate all repos
python repo_admin.py validate

# Check specific repo
python repo_admin.py info problem-repo

# Fix or remove invalid repo
python repo_admin.py unregister problem-repo

# Register with correct path
python repo_admin.py register problem-repo /correct/path
```

### Debugging Tips

**Check application logs:**
```bash
tail -f claudeping.log
```

**Test Claude CLI directly:**
```bash
claude "echo test"
```

**Verify repository configuration:**
```bash
python repo_admin.py validate
cat config/repositories.json
```

**Test Twilio webhook:**
Send a simple message like "STATUS" and check both:
- Twilio Console logs
- Flask server output
- Application logs

**Check permissions:**
```bash
# List repos with access details
python repo_admin.py list --verbose
```

## Best Practices

### Repository Organization

**Use clear, short names:**
- ✅ `api`, `web`, `mobile`
- ✅ `user-service`, `auth-service`
- ❌ `my_super_long_repository_name_v2`

**Set appropriate access levels:**
- `admin` - Only trusted team leads
- `write` - Most developers
- `read` - Contractors, interns, demos

**Regularly review access:**
```bash
python repo_admin.py list --verbose
```

### Effective Prompting

**Be specific:**
- ✅ "Add JWT authentication to the /login endpoint with 1-hour expiry"
- ❌ "Add auth"

**Break down complex tasks:**
```
1. Create user model with email and password fields
2. Add password hashing with bcrypt
3. Create login endpoint
4. Add JWT token generation
5. Add token validation middleware
```

**Provide context:**
- ✅ "Update the payment function in api/billing.py to use Stripe instead of PayPal"
- ❌ "Update payment"

### Session Management

**Start new sessions when:**
- Switching to completely different task
- Context gets confusing
- Too many messages (>20)
- Starting new feature branch

**Keep sessions focused:**
- One feature per session
- Related changes together
- Clear progression of steps

### Git Workflow

**Review branches before merging:**
```bash
git fetch origin
git checkout sms/20241202_143022
git diff main
git log --oneline
```

**Clean up old branches:**
```bash
# Delete merged branches
git branch -d sms/20241202_143022

# Delete remotely
git push origin --delete sms/20241202_143022
```

**Use GitHub PRs for review:**
1. ClaudePing creates branch
2. Review changes in GitHub
3. Create PR from branch
4. Team reviews and approves
5. Merge to main

### Security Best Practices

**Protect sensitive repositories:**
```bash
# Grant only read access to sensitive repos
python repo_admin.py grant secrets-repo +1234567890 --level read
```

**Regular access audits:**
```bash
# Review who has access
python repo_admin.py list --verbose

# Revoke unnecessary access
python repo_admin.py revoke old-repo +9876543210
```

**Separate dev and production:**
- Use different repositories
- Different access controls
- Different phone number whitelists

**Monitor API usage:**
- Check Anthropic Console for usage
- Watch for unusual patterns
- Set billing alerts

### Performance Tips

**Keep requests focused:**
- Small, specific changes are faster
- Large refactors may timeout
- Break big tasks into steps

**Use inline targeting for quick changes:**
```
in web: fix typo in header
in api: update version number
```

**Switch repos for multi-step work:**
```
switch to web
add dark mode toggle
update theme colors
add theme switcher component
```

## Tips and Tricks

### Quick Status Check

```
STATUS
```

Tells you:
- Current session ID
- Active repository
- Number of messages
- Session duration

### Abbreviations That Work

```
list repos → Shows repositories
switch web → Switches to "web" repository
info api → Shows "api" details
```

### Multi-Repo Workflow Example

**Morning routine:**
```
1. repos status (check what needs attention)
2. switch to priority-repo
3. Make focused changes
4. Verify with STATUS
5. Switch to next repo
```

### Using with GitHub

**Create PRs from ClaudePing branches:**
```bash
# After ClaudePing creates sms/20241202_143022
gh pr create --base main --head sms/20241202_143022 \
  --title "Add JWT authentication" \
  --body "Added by ClaudePing"
```

### Team Collaboration

**Share access to repositories:**
```bash
# Grant access to team members
python repo_admin.py grant my-api +team-member-1 --level write
python repo_admin.py grant my-api +team-member-2 --level write
```

**Set up notifications:**
- GitHub notifications for new branches
- Slack integration for commits
- Email alerts for deployments

## Getting Help

### Resources

- **Setup Guide:** [docs/setup.md](setup.md)
- **README:** [README.md](../README.md)
- **Multi-Repo Guide:** [docs/MULTI_REPO_GUIDE.md](MULTI_REPO_GUIDE.md)

### Support Checklist

Before asking for help, try:

1. ✅ Check troubleshooting section above
2. ✅ Validate configuration: `python repo_admin.py validate`
3. ✅ Check logs: `tail -f claudeping.log`
4. ✅ Test Claude CLI: `claude "echo test"`
5. ✅ Verify webhook: Twilio Console → Logs
6. ✅ Check Flask server is running
7. ✅ Verify ngrok tunnel is active

### Reporting Issues

Include:
- ClaudePing version
- Python version
- Error messages from logs
- Steps to reproduce
- What you expected vs what happened

---

**Happy coding via WhatsApp!** 🚀

For setup instructions, see [Setup Guide](setup.md).
