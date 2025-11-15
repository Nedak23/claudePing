# ClaudePing

Send coding requests via **WhatsApp** and get AI-powered assistance from Claude on the go, with automatic Git branch creation and GitHub integration.

## Setup

### Prerequisites

- **Python 3.8+**
- **Claude Code CLI** - [Install guide](https://docs.anthropic.com)
- **Twilio Account** - For WhatsApp (free trial)
- **Git & GitHub** - For code management
- **ngrok** - For local development

### Step-by-Step Setup

#### 1. Create Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Sign up and verify your phone number

#### 2. Join WhatsApp Sandbox

1. In Twilio Console: **Messaging → Try it out → Send a WhatsApp message**
2. Note the sandbox number (e.g., +1 415-523-8886)
3. Open WhatsApp on your phone
4. Send the join code to the sandbox number (displayed on page)
5. Wait for confirmation: "✅ You are all set!"

#### 3. Get Twilio Credentials

From Twilio Console dashboard, copy:
- **Account SID** (starts with "AC")
- **Auth Token** (click "Show" to reveal)

#### 4. Get Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up/login and add payment method
3. **Settings → API Keys → Create Key**
4. Copy the key immediately (starts with "sk-ant-")

#### 5. Install Claude Code CLI
**Install**
```bash
brew install anthropics/tap/claude
```

**Configure:**
```bash
claude configure
# Enter your Anthropic API key when prompted
```

**Verify:**
```bash
claude --version
```

#### 6. Setup Project

```bash
# Clone repository
git clone <your-repo-url>
cd claudePing

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

#### 7. Configure `.env`

Edit `.env` with your credentials:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here

# WhatsApp - leave blank for sandbox
TWILIO_PHONE_NUMBER=

# Your phone number (include country code, no spaces)
WHITELISTED_NUMBERS=+1234567890

# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx

# GitHub (optional)
GITHUB_TOKEN=

# Server Config (defaults are fine)
SERVER_PORT=8000
SERVER_HOST=0.0.0.0
BASE_URL=http://localhost:8000
```

**Important:**
- Use YOUR phone number for `WHITELISTED_NUMBERS` (the one you verified)
- Include country code (e.g., +1 for US)

#### 8. Install & Configure ngrok

**Mac:**
```bash
brew install ngrok
```

**Setup ngrok account:**
1. Go to https://ngrok.com/ and sign up (free)
2. Copy your auth token from https://dashboard.ngrok.com/get-started/your-authtoken
3. Configure: `ngrok config add-authtoken YOUR_TOKEN_HERE`

#### 9. Start Servers

**Terminal 1 - Flask Server:**
```bash
cd claudePing
source venv/bin/activate
python app.py
```

**Terminal 2 - ngrok:**
```bash
ngrok http 5000
```

Copy the **HTTPS forwarding URL** from ngrok (e.g., `https://abcd-1234.ngrok-free.app`)

#### 10. Configure Webhook

1. Edit `.env` and update `BASE_URL` with your ngrok URL
2. Go to Twilio Console: **Messaging → Try it out → Send a WhatsApp message**
3. Scroll to "Sandbox Configuration"
4. In "When a message comes in": Enter `https://your-ngrok-url.ngrok-free.app/sms`
5. Method: **HTTP POST**
6. Click **Save**

**Note:** The endpoint is `/sms`

#### 11. Test It! 🎉

Send a WhatsApp message to the sandbox number:
```
Create a Python function that adds two numbers
```

You should receive a response within 30-60 seconds with:
- A summary of what was done
- Branch name created
- Link to full response

**Success!** You're now coding via WhatsApp! 🚀

---

## Usage

### Send Coding Requests

Just message naturally in WhatsApp:

```
Create a Python function to calculate fibonacci numbers
```

```
Add error handling to the add_numbers function
```

```
Write unit tests for my authentication module
```

```
Refactor the database connection to use connection pooling
```

### Response Format

You'll receive:
```
✓ Done! Modified 1 file. Branch: sms/20241115_143022.
Summary: Created fibonacci function with memoization...
Full: https://your-server.com/response/20241115_143022_123456
```

### Special Commands

ClaudePing supports special commands for session management:

- `NEW SESSION` - Start fresh conversation
- `STATUS` - Check current session info
- `FULL <id>` - Get complete response

**[View Complete Commands Guide →](COMMANDS.md)**

## Project Structure

```
claudePing/
├── app.py                  # Main Flask application
├── claude_handler.py       # Claude Code CLI integration
├── git_handler.py          # Git operations (branch, commit, push)
├── storage.py              # Response and session storage
├── summary_generator.py    # Message summary generation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── README.md               # This file
├── COMMANDS.md             # Complete commands reference
├── responses/              # Stored full responses (JSON)
├── sessions/               # User session data
└── tests/
    └── test_local.py       # Local testing utilities
```

### Adding Multiple Users

Add multiple phone numbers to `.env`:
```env
WHITELISTED_NUMBERS=+12345678901,+10987654321,+15555555555
```

Each person must:
1. Join the Twilio WhatsApp sandbox (send join code)
2. Have their number added to the whitelist

### Timeout Settings

Adjust Claude timeout in `claude_handler.py`:
```python
def send_prompt(self, prompt: str, timeout: int = 120):
```

### Summary Length

Adjust in `summary_generator.py`:
```python
def __init__(self, max_length: int = 150):
```

---

## Daily Usage

### Starting Your Session

Every time you want to use the system:

**Terminal 1:**
```bash
cd ~/Projects/claudePing
source venv/bin/activate
python app.py
```

**Terminal 2:**
```bash
ngrok http 8000
```

### Stopping the System

1. Press `Ctrl+C` in both terminals
2. Deactivate venv: `deactivate`

## Contributing

This is a personal MVP project. Feedback and suggestions welcome!

---

## License

MIT License - feel free to use and modify for your needs.

---