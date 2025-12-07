# ClaudePing Setup Guide

Complete step-by-step installation and configuration guide for ClaudePing.

## Prerequisites

Before you begin, ensure you have:
- **Python 3.8 or higher**
- **Git** installed
- **A GitHub account**
- **A phone** with WhatsApp installed
- **macOS, Linux, or Windows with WSL**

## Step 1: Create Twilio Account

Twilio provides the WhatsApp/SMS integration for ClaudePing.

1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free account
3. Verify your email address
4. Verify your phone number

**Cost:** Free trial includes $15 credit. SMS/WhatsApp messages cost $0.0075-$0.0079 per message.

## Step 2: Join WhatsApp Sandbox

Twilio's sandbox lets you test WhatsApp without business verification.

1. Log into [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging → Try it out → Send a WhatsApp message**
3. Note the **sandbox number** (e.g., +1 415-523-8886)
4. Note the **join code** (e.g., "join <word>-<word>")
5. Open **WhatsApp** on your phone
6. Send the join code to the sandbox number
7. Wait for confirmation: "✅ You are all set!"

**Note:** The sandbox is perfect for testing. For production, you'll need to apply for WhatsApp Business approval.

## Step 3: Get Twilio Credentials

1. From the [Twilio Console Dashboard](https://console.twilio.com/)
2. Find your **Account SID** (starts with "AC")
3. Find your **Auth Token** (click "Show" to reveal it)
4. Copy both - you'll need them in Step 8

## Step 4: Get Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Add a payment method (required for API access)
4. Navigate to **Settings → API Keys**
5. Click **Create Key**
6. Copy the key immediately (starts with "sk-ant-")
7. Store it securely - it won't be shown again

**Cost:** Claude API costs vary by model. Sonnet 4 is ~$3-15 per million tokens.

## Step 5: Install Claude Code CLI

### macOS

```bash
# Install via Homebrew
brew install anthropics/tap/claude

# Verify installation
claude --version
```

### Linux

```bash
# Download and install
curl -fsSL https://anthropic.com/claude-code-cli/install.sh | sh

# Verify installation
claude --version
```

### Windows (WSL)

Use the Linux installation instructions above in your WSL terminal.

### Configure Claude CLI

```bash
# Configure with your API key
claude configure

# When prompted, enter your Anthropic API key (sk-ant-...)
```

**Verify it works:**
```bash
claude "echo Hello World"
```

## Step 6: Clone and Setup ClaudePing

```bash
# Clone the repository
git clone https://github.com/Nedak23/claudePing.git
cd claudePing

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt
```

## Step 7: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit the file
nano .env  # or use your preferred editor
```

### Fill in your `.env` file:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # From Step 3
TWILIO_AUTH_TOKEN=your_auth_token_here                 # From Step 3

# WhatsApp - leave blank for sandbox mode
TWILIO_PHONE_NUMBER=

# Your phone number (MUST include country code, no spaces)
WHITELISTED_NUMBERS=+1234567890  # The number you verified in Step 2

# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx  # From Step 4

# GitHub (optional - for automatic PR creation)
GITHUB_TOKEN=

# Server Configuration (defaults work for local development)
SERVER_PORT=8000
SERVER_HOST=0.0.0.0
BASE_URL=http://localhost:8000
```

**Important Notes:**
- `WHITELISTED_NUMBERS` must include country code (e.g., +1 for US)
- This must be the same number you joined the WhatsApp sandbox with
- Multiple numbers: `WHITELISTED_NUMBERS=+1234567890,+0987654321`
- Don't use spaces or quotes around the values

## Step 8: Configure Repositories

ClaudePing requires at least one repository to be registered. You have two options:

### Option A: Use CLI Tool (Recommended)

```bash
# Register your first repository
python repo_admin.py register my-project /absolute/path/to/your/repo \
  --description "My main project" \
  --admin-phone +1234567890

# Verify it was registered
python repo_admin.py list
```

**Auto-discover repositories:**
```bash
# Find all git repos in a directory
python repo_admin.py discover ~/projects --max-depth 3

# Auto-register all found repos
python repo_admin.py discover ~/projects --auto-register --admin-phone +1234567890
```

### Option B: Manual Configuration

```bash
# Copy example configuration
cp config/repositories.json.example config/repositories.json

# Edit the file
nano config/repositories.json
```

**Example `config/repositories.json`:**
```json
{
  "repositories": {
    "my-project": {
      "name": "my-project",
      "path": "/Users/yourname/projects/my-project",
      "remote_url": "https://github.com/yourusername/my-project",
      "description": "My main project",
      "access_control": {
        "+1234567890": ["admin"]
      }
    }
  },
  "default_repository": "my-project"
}
```

**Requirements:**
- Path MUST be absolute (use full path, not ~)
- Path MUST be a valid git repository (contains `.git` directory)
- Your phone number MUST be in `access_control`
- Permissions: `admin` > `write` > `read`

**Validate your configuration:**
```bash
python repo_admin.py validate
```

## Step 9: Install ngrok

ngrok creates a public URL for your local server so Twilio can reach it.

### macOS
```bash
brew install ngrok
```

### Linux
```bash
# Download from https://ngrok.com/download
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

### Windows
Download from https://ngrok.com/download and add to PATH.

### Configure ngrok

1. Sign up at https://ngrok.com/ (free)
2. Get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken
3. Configure ngrok:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

## Step 10: Start the Servers

You need two terminal windows/tabs:

### Terminal 1: Start Flask Server

```bash
cd claudePing
source venv/bin/activate
python app.py
```

You should see:
```
INFO - Multi-repo mode ENABLED
INFO - Loaded 1 repositories
INFO - Starting ClaudePing server on 0.0.0.0:8000
```

### Terminal 2: Start ngrok

```bash
ngrok http 8000
```

You should see output like:
```
Forwarding  https://abcd-1234-5678.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS URL** (the `https://abcd-1234-5678.ngrok-free.app` part).

## Step 11: Configure Twilio Webhook

Tell Twilio where to send incoming messages:

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging → Try it out → Send a WhatsApp message**
3. Scroll down to **Sandbox Configuration**
4. Find "**When a message comes in**"
5. Paste your ngrok URL and add `/sms` at the end:
   ```
   https://your-ngrok-url.ngrok-free.app/sms
   ```
6. Set method to **HTTP POST**
7. Click **Save**

**Important:** The endpoint MUST be `/sms`, not just the base URL!

## Step 12: Test Your Setup

### Send a test message

Open WhatsApp and send this to the sandbox number:
```
STATUS
```

You should receive:
```
Session: <session-id>
Active repo: my-project
Messages: 1
```

### Send a coding request

```
Create a Python function that adds two numbers
```

You should receive a response within 30-60 seconds with:
- Summary of what was done
- Branch name that was created
- Link to full response

**Success!** 🎉 You're now coding via WhatsApp!

## Verification Checklist

- [ ] Twilio account created
- [ ] WhatsApp sandbox joined
- [ ] Anthropic API key obtained
- [ ] Claude Code CLI installed and configured
- [ ] ClaudePing repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] `.env` file configured with all credentials
- [ ] Repository registered and validated
- [ ] ngrok installed and configured
- [ ] Flask server running
- [ ] ngrok tunnel active
- [ ] Twilio webhook configured
- [ ] Test message successful

## Common Setup Issues

### Issue: "Module not found" errors

**Solution:** Make sure virtual environment is activated:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Issue: "Claude command not found"

**Solution:** Reinstall Claude CLI and verify PATH:
```bash
brew reinstall anthropics/tap/claude  # macOS
which claude  # Should show a path
```

### Issue: "Repository configuration not found"

**Solution:** Make sure you registered at least one repository:
```bash
python repo_admin.py validate
python repo_admin.py list
```

### Issue: "Webhook not receiving messages"

**Solution:** Check these items:
1. ngrok is running and tunnel is active
2. Webhook URL ends with `/sms`
3. Webhook is set to HTTP POST
4. Flask server is running without errors
5. Your phone number is in WHITELISTED_NUMBERS

### Issue: "Not authorized" response

**Solution:** Verify your phone number:
1. Check WHITELISTED_NUMBERS in `.env` includes your number
2. Check your number is in repository access_control
3. Include country code (e.g., +1 for US)
4. No spaces in phone number

### Issue: ngrok tunnel expires

**Solution:** Free ngrok tunnels expire after 2 hours:
1. Restart ngrok (get new URL)
2. Update Twilio webhook with new URL
3. Or upgrade to ngrok paid plan for static URLs

## Daily Usage

Every time you want to use ClaudePing:

### Start the system:

**Terminal 1:**
```bash
cd claudePing
source venv/bin/activate
python app.py
```

**Terminal 2:**
```bash
ngrok http 8000
```

If your ngrok URL changed, update the Twilio webhook.

### Stop the system:

1. Press `Ctrl+C` in both terminals
2. Deactivate virtual environment: `deactivate`

## Upgrading to Production

### Use a production WhatsApp number

1. Apply for WhatsApp Business API access in Twilio Console
2. Complete business verification (takes 1-2 weeks)
3. Update `TWILIO_PHONE_NUMBER` in `.env`

### Deploy to a server

Instead of ngrok, deploy to:
- **Heroku** - Easy deployment, free tier available
- **AWS EC2** - Full control, more setup required
- **DigitalOcean** - Simple VPS, $5/month
- **Render** - Modern platform, free tier available

Update `BASE_URL` in `.env` to your production domain.

### Set up static ngrok URL

Upgrade to ngrok paid plan ($8/month) for:
- Static URLs that don't change
- Custom domains
- More tunnels

## Security Best Practices

1. **Never commit `.env` file** - It contains secrets
2. **Rotate API keys periodically** - Every 3-6 months
3. **Use different keys for dev/prod** - Separate environments
4. **Limit phone number whitelist** - Only trusted users
5. **Review repository access** - Check with `repo_admin.py list -v`
6. **Enable 2FA on all accounts** - Twilio, GitHub, Anthropic
7. **Monitor API usage** - Watch for unusual activity

## Next Steps

Now that ClaudePing is set up:

1. Read the [Usage Guide](usage_guide.md) to learn all commands
2. Register additional repositories with `repo_admin.py`
3. Add team members to WHITELISTED_NUMBERS
4. Configure GitHub integration for automatic PRs
5. Customize settings in `.env`

## Getting Help

If you run into issues:

1. Check the [Usage Guide troubleshooting section](usage_guide.md#troubleshooting)
2. Verify setup with: `python repo_admin.py validate`
3. Check logs: `tail -f claudeping.log`
4. Review Flask server output for errors
5. Test Claude CLI directly: `claude "echo test"`

---

**Setup complete!** Start coding via WhatsApp! 🚀
