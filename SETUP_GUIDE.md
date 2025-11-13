# Complete Setup Guide - Text-Based Coding Companion

**Time Required:** 30-45 minutes
**Difficulty:** Intermediate
**Prerequisites:** Basic command line knowledge

This guide will walk you through every step needed to get your Text-Based Coding Companion up and running.

---

## Table of Contents

1. [Before You Begin](#before-you-begin)
2. [Step 1: Install System Prerequisites](#step-1-install-system-prerequisites)
3. [Step 2: Set Up Twilio Account](#step-2-set-up-twilio-account)
4. [Step 3: Get Anthropic API Key](#step-3-get-anthropic-api-key)
5. [Step 4: Install Claude Code CLI](#step-4-install-claude-code-cli)
6. [Step 5: Clone and Configure Project](#step-5-clone-and-configure-project)
7. [Step 6: Set Up ngrok](#step-6-set-up-ngrok)
8. [Step 7: Configure Twilio Webhook](#step-7-configure-twilio-webhook)
9. [Step 8: Start the Server](#step-8-start-the-server)
10. [Step 9: Send Your First SMS](#step-9-send-your-first-sms)
11. [Step 10: Verify Git Integration](#step-10-verify-git-integration)
12. [Troubleshooting](#troubleshooting)

---

## Before You Begin

### What You'll Need

- [ ] A computer (Mac, Linux, or Windows with WSL)
- [ ] Internet connection
- [ ] A phone capable of sending SMS
- [ ] Credit card for Twilio (they offer free trial credits)
- [ ] Credit card for Anthropic API (pay-as-you-go pricing)
- [ ] A GitHub account
- [ ] Git installed on your computer
- [ ] Python 3.8 or higher

### Expected Costs

- **Twilio:** $1/month for phone number + $0.0075 per SMS (Free trial: $15 credit)
- **Anthropic API:** ~$0.003 per request (varies by model usage)
- **Total Monthly (estimated):** $2-5 for personal use

### Time Breakdown

- Twilio setup: 10 minutes
- API keys: 5 minutes
- Claude Code install: 5 minutes
- Project setup: 10 minutes
- Testing: 10 minutes

---

## Step 1: Install System Prerequisites

### Check Python Version

Open your terminal and run:

```bash
python3 --version
```

**Expected Output:**
```
Python 3.8.10
```

or any version 3.8+. If you see this, you're good! If not:

**Mac:**
```bash
brew install python3
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Windows (WSL):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Verify Git Installation

```bash
git --version
```

**Expected Output:**
```
git version 2.x.x
```

If not installed:

**Mac:**
```bash
brew install git
```

**Ubuntu/Debian:**
```bash
sudo apt install git
```

### Check Your GitHub Account

Make sure you're logged into GitHub:

```bash
git config --global user.name
git config --global user.email
```

If these are empty, set them:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Step 2: Set Up Twilio Account

### 2.1 Create Twilio Account

1. **Go to Twilio's website:** https://www.twilio.com/try-twilio

2. **Click "Sign up for free"**

3. **Fill out the registration form:**
   - First name
   - Last name
   - Email address
   - Password

4. **Verify your email** - Check your inbox and click the verification link

5. **Verify your phone number:**
   - Enter your personal phone number
   - Enter the verification code you receive via SMS
   - ⚠️ **IMPORTANT:** This is the number you'll use to text the bot!

### 2.2 Get a Twilio Phone Number

1. **After verification, you'll see the Twilio Console**

2. **Click "Get a Trial Number"** (big blue button)

3. **Twilio will suggest a number** - Click "Choose this Number"
   - This will be your bot's phone number
   - Save this number somewhere - you'll need it!

4. **Write down your number:**
   ```
   My Twilio Number: +1 (___) ___-____
   ```

### 2.3 Get Your Twilio Credentials

1. **Look at your Twilio Console Dashboard**

2. **Find the "Account Info" section** (should be visible on main page)

3. **Copy these three values:**

   **Account SID:** (starts with "AC")
   ```
   Example: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   **Auth Token:** (click "Show" to reveal)
   ```
   Example: your_auth_token_here
   ```

4. **Save these somewhere safe** - you'll need them in Step 5

   ```
   TWILIO_ACCOUNT_SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN: your_auth_token_here
   TWILIO_PHONE_NUMBER: +1__________
   ```

### 2.4 Add Your Phone to Verified Numbers

1. **In Twilio Console, go to:** Phone Numbers → Manage → Verified Caller IDs

2. **Click the red "+" button**

3. **Enter your personal phone number** (the one you want to text from)

4. **Verify it** via SMS code

✅ **Checkpoint:** You should have:
- A Twilio account
- A Twilio phone number
- Account SID and Auth Token saved
- Your personal phone verified

---

## Step 3: Get Anthropic API Key

### 3.1 Create Anthropic Account

1. **Go to:** https://console.anthropic.com/

2. **Click "Sign Up"** or "Login with Google/GitHub"

3. **Complete registration**

4. **Add payment method:**
   - Go to Settings → Billing
   - Add credit card
   - Set up billing (pay-as-you-go)

### 3.2 Generate API Key

1. **In Anthropic Console, go to:** Settings → API Keys

2. **Click "Create Key"**

3. **Name your key:** "claudePing" or "SMS Bot"

4. **Copy the API key immediately** - you can't see it again!
   ```
   Example: sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

5. **Save it:**
   ```
   ANTHROPIC_API_KEY: sk-ant-api03-_________________________________
   ```

⚠️ **IMPORTANT:** This key is like a password. Never share it or commit it to GitHub!

✅ **Checkpoint:** You have your Anthropic API key saved

---

## Step 4: Install Claude Code CLI

### 4.1 Install Claude Code

**Mac:**
```bash
brew install anthropics/tap/claude
```

**Linux:**
```bash
# Download the latest release
curl -fsSL https://claude.ai/download/cli/linux | sh
```

**Windows (WSL):**
```bash
# Same as Linux
curl -fsSL https://claude.ai/download/cli/linux | sh
```

### 4.2 Verify Installation

```bash
claude --version
```

**Expected Output:**
```
claude version x.x.x
```

### 4.3 Configure Claude Code

```bash
claude configure
```

When prompted:
1. **Enter your API key:** Paste your Anthropic API key from Step 3
2. **Choose model:** Select the default (usually claude-3-sonnet)

### 4.4 Test Claude Code

```bash
claude -p "Say hello!"
```

**Expected Output:**
```
Hello! How can I help you today?
```

✅ **Checkpoint:** Claude Code CLI is working

---

## Step 5: Clone and Configure Project

### 5.1 Clone the Repository

```bash
# Navigate to where you want the project
cd ~/Projects  # or wherever you keep code

# Clone the repo
git clone https://github.com/YOUR_USERNAME/claudePing.git

# Enter the directory
cd claudePing
```

### 5.2 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# Mac/Linux:
source venv/bin/activate

# Windows (WSL):
source venv/bin/activate
```

**Expected Output:**
```
(venv) user@computer:~/Projects/claudePing$
```

Notice the `(venv)` prefix - this means it's activated!

### 5.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed flask-3.0.0 twilio-8.11.0 python-dotenv-1.0.0
```

### 5.4 Create Environment File

```bash
# Copy the example file
cp .env.example .env

# Open it in your editor
nano .env
# or
vim .env
# or
code .env  # if you use VS Code
```

### 5.5 Fill In Your Environment Variables

Edit the `.env` file with your actual values:

```env
# Twilio Configuration (from Step 2)
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+12345678901

# Your personal phone number (the one you verified in Twilio)
WHITELISTED_NUMBERS=+12345678901

# Claude API Key (from Step 3)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# GitHub Token (optional for now - leave blank)
GITHUB_TOKEN=

# Server Configuration (keep these defaults)
SERVER_PORT=5000
SERVER_HOST=0.0.0.0
BASE_URL=http://localhost:5000
```

**Important:**
- Replace ALL placeholder values with your real credentials
- Phone numbers must include country code (e.g., +1 for US)
- No spaces around the `=` sign
- Don't add quotes around values

### 5.6 Save and Verify

```bash
# If using nano, press: Ctrl+X, then Y, then Enter
# If using vim, press: Esc, then type :wq, then Enter

# Verify the file exists
ls -la .env
```

✅ **Checkpoint:** You have:
- Repository cloned
- Virtual environment activated
- Dependencies installed
- `.env` file configured with your credentials

---

## Step 6: Set Up ngrok

ngrok creates a secure tunnel from the internet to your local machine, allowing Twilio to send webhooks to your local server.

### 6.1 Install ngrok

**Mac:**
```bash
brew install ngrok
```

**Linux:**
```bash
# Download
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok
```

**Windows (WSL):**
```bash
# Same as Linux above
```

### 6.2 Create ngrok Account (Free)

1. **Go to:** https://ngrok.com/
2. **Click "Sign up"** - use Google/GitHub for quick signup
3. **After login, go to:** https://dashboard.ngrok.com/get-started/your-authtoken
4. **Copy your authtoken**

### 6.3 Configure ngrok

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with the token from the dashboard.

### 6.4 Test ngrok

⚠️ **DON'T START IT YET** - we'll do this in Step 8. Just verify it's installed:

```bash
ngrok version
```

**Expected Output:**
```
ngrok version x.x.x
```

✅ **Checkpoint:** ngrok is installed and configured

---

## Step 7: Configure Twilio Webhook

We'll do this after starting the server, but let's prepare.

### What is a Webhook?

A webhook is a URL that Twilio will call when someone sends an SMS to your Twilio number. Our Flask server will listen at this URL.

### The Webhook URL Format

```
https://[NGROK-ID].ngrok-free.app/sms
```

We'll get the `[NGROK-ID]` part when we start ngrok in Step 8.

✅ **Checkpoint:** You understand what a webhook is

---

## Step 8: Start the Server

Now we'll start everything up!

### 8.1 Open Two Terminal Windows

You'll need **two terminal windows/tabs**:
- **Terminal 1:** For the Flask server
- **Terminal 2:** For ngrok

### 8.2 Terminal 1 - Start Flask Server

```bash
# Make sure you're in the project directory
cd ~/Projects/claudePing

# Activate virtual environment
source venv/bin/activate

# Start the server
python app.py
```

**Expected Output:**
```
2024-11-15 14:30:22 - __main__ - INFO - All components initialized successfully
2024-11-15 14:30:22 - __main__ - INFO - Starting server on 0.0.0.0:5000
2024-11-15 14:30:22 - __main__ - INFO - Press Ctrl+C to stop
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.x:5000
Press CTRL+C to quit
```

✅ If you see this, your server is running!

⚠️ If you see errors:
- "ANTHROPIC_API_KEY must be set" → Check your .env file
- "Address already in use" → Something else is using port 5000, change SERVER_PORT in .env
- Module import errors → Reinstall dependencies: `pip install -r requirements.txt`

**Leave this terminal running!**

### 8.3 Terminal 2 - Start ngrok

Open a **new terminal window/tab**:

```bash
ngrok http 5000
```

**Expected Output:**
```
ngrok

Session Status                online
Account                       your@email.com (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abcd-1234-5678-9abc.ngrok-free.app -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

### 8.4 Copy Your ngrok URL

Look for the **Forwarding** line:
```
Forwarding    https://abcd-1234-5678-9abc.ngrok-free.app -> http://localhost:5000
```

**Copy the HTTPS URL:** `https://abcd-1234-5678-9abc.ngrok-free.app`

⚠️ **IMPORTANT:**
- Use the HTTPS version (not HTTP)
- Your URL will be different each time you restart ngrok
- Free plan URLs change every session (upgrade for static URLs)

### 8.5 Update Your .env File

In a **third terminal** or text editor:

```bash
# Edit .env
nano .env
```

Update the `BASE_URL` line:
```env
BASE_URL=https://abcd-1234-5678-9abc.ngrok-free.app
```

Save and exit.

**You don't need to restart the Flask server** - it will pick up the change.

### 8.6 Test Your Server

In a **web browser**, go to:
```
https://YOUR-NGROK-URL.ngrok-free.app/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "claude_installed": true,
  "git_repo": true
}
```

✅ If you see this, your server is accessible from the internet!

**Leave both terminals running!**

✅ **Checkpoint:**
- Flask server running in Terminal 1
- ngrok running in Terminal 2
- Server accessible via ngrok URL
- /health endpoint returns healthy status

---

## Step 9: Configure Twilio Webhook (For Real This Time)

### 9.1 Go to Twilio Console

1. **Log into Twilio:** https://console.twilio.com/
2. **Navigate to:** Phone Numbers → Manage → Active Numbers
3. **Click on your Twilio phone number**

### 9.2 Configure Messaging

Scroll down to the **Messaging** section.

**Under "A MESSAGE COMES IN":**
1. **Select:** Webhook
2. **Method:** HTTP POST
3. **URL:** Enter your ngrok URL + `/sms`
   ```
   https://abcd-1234-5678-9abc.ngrok-free.app/sms
   ```

   ⚠️ **Don't forget the `/sms` at the end!**

**Example:**
```
Webhook: https://1234-abcd.ngrok-free.app/sms
HTTP POST
```

### 9.3 Save Configuration

1. **Click "Save" at the bottom** (red button)
2. **Wait for "Saved"** confirmation

✅ **Checkpoint:** Twilio webhook is configured

---

## Step 10: Send Your First SMS!

🎉 **Everything is ready! Let's test it!**

### 10.1 Send a Test Message

From your phone, send an SMS to your **Twilio phone number**:

```
Create a Python function that adds two numbers
```

### 10.2 Watch Your Terminal

**In Terminal 1 (Flask server), you should see:**

```
2024-11-15 14:35:10 - __main__ - INFO - Received SMS from +12345678901: Create a Python function that adds two numbers
2024-11-15 14:35:10 - __main__ - INFO - Sending prompt to Claude: Create a Python function that adds two numbers...
2024-11-15 14:35:15 - claude_handler - INFO - Claude response received (234 chars)
2024-11-15 14:35:16 - __main__ - INFO - Generated summary: ✓ Done! Modified 1 file. Branch: sms/20241115_143516...
```

### 10.3 Check Your Phone

Within 30-60 seconds, you should receive an SMS response like:

```
✓ Done! Modified 1 file. Branch: sms/20241115_143516.
Summary: Created add_numbers function that takes two parameters...
Full: https://1234-abcd.ngrok-free.app/response/20241115_143516_123456
```

🎉 **IT WORKS!**

### 10.4 Verify the Response Link

Click the link in the SMS (or copy it to a browser) to see the full response.

**Expected:** JSON with the complete Claude response.

✅ **Checkpoint:** You've successfully sent your first SMS and received a response!

---

## Step 11: Verify Git Integration

### 11.1 Check Git Status

In a **new terminal** (or Terminal 3):

```bash
cd ~/Projects/claudePing
git status
```

**Expected Output:**
```
On branch sms/20241115_143516
Your branch is up to date with 'origin/sms/20241115_143516'.

nothing to commit, working tree clean
```

You should see you're on a new branch!

### 11.2 Check Git Log

```bash
git log -1
```

**Expected Output:**
```
commit abc123def456...
Author: Your Name <your@email.com>
Date:   Fri Nov 15 14:35:16 2024

    SMS request: Create a Python function that adds two numbers
```

### 11.3 View the Created File

```bash
ls -la *.py
```

You should see a new Python file created by Claude!

### 11.4 View on GitHub

1. **Go to your GitHub repository**
2. **Click "Branches"**
3. **Find your new branch:** `sms/20241115_143516`
4. **Click it to view the code**

🎉 **The file is on GitHub!**

✅ **Checkpoint:** Git integration is working - branches created and pushed automatically

---

## Advanced Testing

### Test Special Commands

#### NEW SESSION
```
Send SMS: NEW SESSION
```

**Expected Response:**
```
New session started! Previous conversation cleared.
```

#### STATUS
```
Send SMS: STATUS
```

**Expected Response:**
```
Session active (1 msgs). Branch: sms/20241115...
```

#### FULL Response
```
Send SMS: FULL 20241115_143516_123456
```

Replace the ID with one from a previous response.

**Expected Response:**
Full Claude response split into SMS chunks.

---

## Daily Usage

### Starting Your Work Session

Every time you want to use the system:

**Terminal 1 - Flask Server:**
```bash
cd ~/Projects/claudePing
source venv/bin/activate
python app.py
```

**Terminal 2 - ngrok:**
```bash
ngrok http 5000
```

**Terminal 3 - Get ngrok URL:**
```bash
# Copy the HTTPS forwarding URL from Terminal 2

# Update .env
nano .env
# Update BASE_URL with new ngrok URL
```

**Update Twilio Webhook:**
1. Go to Twilio Console
2. Update webhook URL with new ngrok URL
3. Save

**Now you can text!**

### Stopping the System

1. **Terminal 1:** Press `Ctrl+C` to stop Flask
2. **Terminal 2:** Press `Ctrl+C` to stop ngrok
3. **Deactivate venv:** `deactivate`

---

## Troubleshooting

### Problem: "Phone number not authorized"

**Solution:**
1. Open `.env` file
2. Check `WHITELISTED_NUMBERS` has YOUR phone number
3. Include country code: `+12345678901`
4. Restart Flask server

### Problem: No SMS response received

**Check:**
1. Is Flask server running? (Check Terminal 1)
2. Is ngrok running? (Check Terminal 2)
3. Did you update Twilio webhook with current ngrok URL?
4. Check Flask logs for errors
5. Check Twilio Console → Monitor → Logs → Errors

### Problem: "Claude Code CLI not detected"

**Solution:**
```bash
# Verify installation
claude --version

# If not found, reinstall
brew install anthropics/tap/claude  # Mac
# or
curl -fsSL https://claude.ai/download/cli/linux | sh  # Linux

# Reconfigure
claude configure
# Enter your API key
```

### Problem: "Git push failed"

**Possible causes:**
1. **Not authenticated to GitHub**
   ```bash
   # Set up GitHub authentication
   gh auth login
   # or
   git config --global credential.helper store
   git push  # Enter credentials
   ```

2. **No internet connection**
   - Check your connection
   - Git push will retry automatically (4 times)

3. **Branch name issue**
   - Make sure you're not on `main` branch
   - System should create `sms/` branches automatically

### Problem: ngrok URL keeps changing

**Symptom:** Have to update Twilio webhook every time you restart.

**Solutions:**
1. **Upgrade to ngrok paid plan** ($8/month) for static URLs
2. **Use Twilio Functions** instead of local server (advanced)
3. **Deploy to cloud** (Heroku, Railway, etc.) for permanent URL

### Problem: "Address already in use" (Port 5000)

**Solution:**
```bash
# Find what's using port 5000
lsof -ti:5000

# Kill it
kill -9 $(lsof -ti:5000)

# Or use a different port
# Edit .env:
SERVER_PORT=5001

# Then use ngrok with new port:
ngrok http 5001
```

### Problem: Very slow responses

**Possible causes:**
1. **Complex request** - Claude needs time to think
2. **Large codebase** - More files to analyze
3. **Network latency** - Check internet connection

**Solutions:**
- Increase timeout in `claude_handler.py` (line 33)
- Be more specific in your requests
- Break large tasks into smaller requests

### Problem: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# If still failing, try:
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Problem: Can't see full response on phone

**Solution:**
The SMS contains a link to the full response. Options:
1. Click the link in the SMS
2. Send: `FULL [response_id]` (get ID from summary)
3. Visit: `http://localhost:5000/response/[id]` in browser

### Problem: Webhook returns 500 error

**Check Flask logs:**
Look at Terminal 1 for Python errors.

**Common causes:**
1. `.env` file misconfigured
2. Missing API keys
3. Code syntax errors (shouldn't happen with provided code)

**Debug:**
```bash
# Test the health endpoint
curl http://localhost:5000/health

# Check logs
# All errors will appear in Terminal 1
```

---

## Getting Help

### View Logs

**Flask Server Logs:** Terminal 1
**ngrok Logs:** Terminal 2 or http://127.0.0.1:4040 (ngrok web interface)
**Twilio Logs:** Twilio Console → Monitor → Logs

### Test Locally Without SMS

```bash
cd ~/Projects/claudePing
python tests/test_local.py
```

This tests all components without needing SMS/Twilio.

### Check System Health

```bash
# Visit in browser
http://localhost:5000/health

# Or use curl
curl http://localhost:5000/health
```

### Community Support

- **GitHub Issues:** Report bugs in the repo
- **Twilio Support:** https://support.twilio.com/
- **Anthropic Docs:** https://docs.anthropic.com/

---

## Next Steps

### Now That It's Working

1. **Try different prompts:**
   - "Add error handling to add_numbers.py"
   - "Write unit tests for the add function"
   - "Refactor this code to be more efficient"

2. **Check your branches on GitHub:**
   - Each SMS creates a new branch
   - Review the code changes
   - Merge good ones to main

3. **Set up keyboard shortcuts** for starting/stopping the system

4. **Bookmark your ngrok web interface:** http://127.0.0.1:4040

### Production Deployment (Future)

When you're ready to deploy permanently:
1. Deploy to cloud (Heroku, Railway, AWS)
2. Get a permanent URL (no more ngrok)
3. Set up monitoring and alerts
4. Add rate limiting
5. Support multiple users

See `MVP_STATUS.md` for the full roadmap.

---

## Quick Reference Card

### Start System
```bash
# Terminal 1
cd ~/Projects/claudePing && source venv/bin/activate && python app.py

# Terminal 2
ngrok http 5000

# Terminal 3
# Copy ngrok URL, update .env BASE_URL
# Update Twilio webhook if URL changed
```

### Stop System
```bash
# Both terminals: Ctrl+C
```

### SMS Commands
- **Regular prompt:** Just type your coding request
- **NEW SESSION:** Start fresh conversation
- **STATUS:** Check current session info
- **FULL [id]:** Get full response

### Important URLs
- **Health Check:** http://localhost:5000/health
- **ngrok Dashboard:** http://127.0.0.1:4040
- **Twilio Console:** https://console.twilio.com/
- **Anthropic Console:** https://console.anthropic.com/

### Important Files
- **`.env`** - Your credentials (NEVER commit!)
- **`app.py`** - Main server
- **`responses/`** - Saved responses
- **`sessions/`** - Session data

---

## Congratulations! 🎉

You've successfully set up your Text-Based Coding Companion!

You can now code from anywhere just by sending a text message. Pretty cool, right?

**Happy coding on the go! 📱💻**

---

**Last Updated:** November 2025
**Guide Version:** 1.0
**For:** Text-Based Coding Companion MVP v1.0.0
