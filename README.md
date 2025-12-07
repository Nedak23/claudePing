# ClaudePing

**Code via WhatsApp** - Send coding requests via text message and get AI-powered assistance from Claude on the go, with automatic Git branch creation and GitHub integration.

## What is ClaudePing?

ClaudePing lets you interact with Claude Code CLI through WhatsApp or SMS. Just text your coding requests and receive:
- ✅ Automated code changes committed to git branches
- ✅ Support for multiple repositories
- ✅ Natural language commands
- ✅ Full session context across conversations
- ✅ Automatic GitHub integration

## Quick Start

1. **Get the prerequisites**: Twilio account, Claude Code CLI, Python 3.8+
2. **Follow the [Setup Guide](docs/setup.md)** for step-by-step installation
3. **Read the [Usage Guide](docs/usage_guide.md)** to learn commands

## Example Usage

```
You: Create a Python function that calculates fibonacci numbers

ClaudePing: ✓ Done! Modified 1 file. Branch: sms/20241115_143022.
Summary: Created fibonacci function with memoization...
Full: https://your-server.com/response/123456
```

```
You: list repos

ClaudePing: You have 3 repos:
- my-api (active)
- web-frontend
- mobile-app
```

```
You: in web-frontend: add dark mode toggle

ClaudePing: [web-frontend] ✓ Done! Added dark mode toggle...
```

## Key Features

### Multi-Repository Support
- Manage multiple projects from one ClaudePing instance
- Switch between repos with simple commands
- Per-repository access control
- Inline repo targeting: `in my-api: add feature`

### Git Integration
- Automatic branch creation for each request
- Commits with descriptive messages
- Push to GitHub automatically
- Branch naming: `sms/YYYYMMDD_HHMMSS`

### Session Management
- Persistent conversation context
- Start new sessions anytime
- Remembers your active repository
- Full response history

### Access Control
- Whitelist trusted phone numbers
- Per-repository permissions (read/write/admin)
- Multiple users supported
- Secure credential management

## Project Structure

```
claudePing/
├── app.py                      # Main Flask application
├── claude_handler.py           # Claude Code CLI integration
├── git_handler.py              # Git operations
├── repository_manager.py       # Multi-repo support
├── enhanced_session_manager.py # Session & context tracking
├── command_parser.py           # Command interpretation
├── storage.py                  # Response storage
├── repo_admin.py              # Repository admin CLI tool
├── config/
│   └── repositories.json       # Repository configuration
├── docs/
│   ├── setup.md               # Installation guide
│   └── usage_guide.md         # Commands and usage
└── requirements.txt           # Python dependencies
```

## Documentation

- **[Setup Guide](docs/setup.md)** - Complete installation and configuration instructions
- **[Usage Guide](docs/usage_guide.md)** - All commands, examples, and troubleshooting
- **[Multi-Repo Guide](docs/MULTI_REPO_GUIDE.md)** - Detailed multi-repository documentation

## Requirements

- Python 3.8+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/build-with-claude/claude-code)
- [Twilio Account](https://www.twilio.com/try-twilio) (free trial available)
- Git & GitHub account
- ngrok (for local development)

## Quick Example Commands

### Repository Management
```
list repos              # View all repositories
switch to my-api       # Change active repository
info my-api            # Show repository details
repos status           # Check status of all repos
```

### Coding Requests
```
Create a login API endpoint
Add error handling to the payment function
Write unit tests for authentication
Refactor database connection to use pooling
```

### Session Commands
```
STATUS           # Check current session and repo
NEW SESSION      # Start fresh conversation
FULL <id>        # Get complete response
```

## Repository Admin CLI

Manage repositories easily with the `repo_admin.py` tool:

```bash
# Register a repository
python repo_admin.py register my-project /path/to/repo --admin-phone +1234567890

# Auto-discover repos
python repo_admin.py discover ~/projects --auto-register

# List repositories
python repo_admin.py list --verbose

# Grant access to users
python repo_admin.py grant my-project +9876543210 --level write

# Validate configuration
python repo_admin.py validate
```

See `python repo_admin.py --help` for all commands.

## Architecture

ClaudePing consists of several components working together:

1. **Flask Server** - Receives webhooks from Twilio
2. **Claude Handler** - Executes Claude Code CLI commands
3. **Git Handler** - Manages git operations per repository
4. **Repository Manager** - Central registry for multiple repos
5. **Session Manager** - Tracks user context and active repositories
6. **Command Parser** - Interprets user intent and repository targeting
7. **Storage** - Persists responses and session data

## Contributing

This is a personal project built as an MVP. Feedback, suggestions, and contributions are welcome!

### Development Setup

```bash
git clone <your-repo-url>
cd claudePing
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Follow the [Setup Guide](docs/setup.md) for full configuration.

## Troubleshooting

Common issues and solutions are documented in the [Usage Guide](docs/usage_guide.md#troubleshooting).

Quick checks:
```bash
# Verify repositories are configured
python repo_admin.py validate

# Check Claude Code CLI
claude --version

# View application logs
tail -f claudeping.log
```

## License

MIT License - feel free to use and modify for your needs.

## Credits

Built with:
- [Claude Code CLI](https://docs.anthropic.com/en/docs/build-with-claude/claude-code) by Anthropic
- [Twilio API](https://www.twilio.com/) for WhatsApp/SMS
- [Flask](https://flask.palletsprojects.com/) for web server
- [ngrok](https://ngrok.com/) for local development tunneling

---

**Ready to code via text?** Start with the [Setup Guide](docs/setup.md)! 🚀
