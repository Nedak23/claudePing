# WhatsApp Setup Guide - Text-Based Coding Companion

**Time Required:** 20-30 minutes
**Difficulty:** Beginner
**Cost:** FREE (using Twilio WhatsApp Sandbox)

This guide shows you how to set up the Text-Based Coding Companion using **WhatsApp** instead of SMS.

---

## Why WhatsApp Instead of SMS?

### ✅ Advantages of WhatsApp

1. **No A2P 10DLC Compliance** - Skip the business registration!
2. **Free Sandbox** - Test for free, no phone number costs
3. **No SMS Costs** - WhatsApp messages are free
4. **Better Features** - Rich formatting, media support
5. **Works Worldwide** - No international SMS costs
6. **Instant Setup** - 5 minutes vs hours for SMS

### ❌ SMS Disadvantages (Why We're NOT Using It)

1. **A2P 10DLC Required** - Needs business registration
2. **Costs Money** - $1/month number + $0.0075/message
3. **Complex Setup** - Takes days for approval
4. **US-Only Issue** - A2P compliance for US numbers

### WhatsApp Sandbox vs Production

**Sandbox (Free - For Personal Use):**
- ✅ Free forever
- ✅ Perfect for personal use
- ✅ Works immediately
- ⚠️ Must "join" sandbox (one-time setup)
- ⚠️ Shows "sandbox" in sender name

**Production WhatsApp ($$$):**
- Requires approved WhatsApp Business account
- Facebook/Meta approval process
- Costs apply
- Custom sender name
- **Not needed for personal use!**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Create Twilio Account](#step-1-create-twilio-account)
3. [Step 2: Access WhatsApp Sandbox](#step-2-access-whatsapp-sandbox)
4. [Step 3: Join the Sandbox](#step-3-join-the-sandbox)
5. [Step 4: Get Your Twilio Credentials](#step-4-get-your-twilio-credentials)
6. [Step 5: Clone and Configure Project](#step-5-clone-and-configure-project)
7. [Step 6: Set Up ngrok](#step-6-set-up-ngrok)
8. [Step 7: Configure WhatsApp Webhook](#step-7-configure-whatsapp-webhook)
9. [Step 8: Start the Server](#step-8-start-the-server)
10. [Step 9: Send Your First Message](#step-9-send-your-first-message)
11. [Step 10: Verify Git Integration](#step-10-verify-git-integration)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You'll Need

- [ ] A computer (Mac, Linux, or Windows with WSL)
- [ ] Internet connection
- [ ] WhatsApp installed on your phone
- [ ] A GitHub account
- [ ] Git installed
- [ ] Python 3.8 or higher
- [ ] Claude Code CLI installed
- [ ] Anthropic API key

**Cost: $0 for WhatsApp sandbox** (only Claude API usage ~$2-5/month)

---

## Step 1: Create Twilio Account

### 1.1 Sign Up for Twilio

1. **Go to:** https://www.twilio.com/try-twilio
2. **Click "Sign up for free"**
3. **Fill out the form:**
   - First name
   - Last name
   - Email
   - Password

4. **Verify your email** - Click the link in your inbox

5. **Verify your phone number:**
   - Enter your mobile number
   - Enter the SMS verification code
   - ✅ This is the number you'll use for WhatsApp!

### 1.2 Complete Twilio Setup

1. **Answer the welcome questions:**
   - Which product? → "Messaging"
   - What are you building? → "Alerts & Notifications"
   - How do you want to build? → "With code"
   - What is your preferred language? → "Python"

2. **Skip phone number purchase** - We don't need it for WhatsApp!

✅ **Checkpoint:** You have a Twilio account with verified phone number

---

## Step 2: Access WhatsApp Sandbox

### 2.1 Navigate to WhatsApp Sandbox

1. **Log into Twilio Console:** https://console.twilio.com/

2. **In the left sidebar, go to:**
   ```
   Messaging → Try it out → Send a WhatsApp message
   ```

   Or directly: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn

3. **You'll see the WhatsApp Sandbox page**

### 2.2 What You'll See

The page shows:
- **Sandbox Phone Number** (e.g., +1 415-523-8886)
- **Join Code** (e.g., "join <random-words>")
- Instructions for joining

✅ **Checkpoint:** You're on the WhatsApp Sandbox page

---

## Step 3: Join the Sandbox

This is a one-time setup to connect your WhatsApp to Twilio's sandbox.

### 3.1 Open WhatsApp on Your Phone

1. **Open WhatsApp** on your mobile device

2. **Start a new chat** with the sandbox number shown on the Twilio page
   - Example: +1 415-523-8886 (your number will be different)

### 3.2 Send the Join Code

1. **Type the join code exactly as shown** on the Twilio page
   - Example: `join orange-tiger`
   - **Note:** Your code will be different - use the one on YOUR Twilio page!

2. **Send the message**

### 3.3 Confirm Connection

**You'll receive an automatic reply from Twilio:**

```
Twilio Sandbox: ✅ You are all set!

Reply to this message to test your integration.
Text STOP to quit.
```

✅ **Checkpoint:** You've successfully joined the WhatsApp sandbox!

**⚠️ Important:**
- This connection is permanent (no need to rejoin)
- If you send "STOP", you'll need to rejoin with the code again
- Each person who wants to use the bot must join the sandbox

---

## Step 4: Get Your Twilio Credentials

### 4.1 Find Your Credentials

1. **Go to Twilio Console:** https://console.twilio.com/

2. **On the main dashboard, find "Account Info"**

3. **Copy these values:**

   **Account SID:** (starts with "AC")
   ```
   Example: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   **Auth Token:** (click "Show" to reveal)
   ```
   Example: your_auth_token_here
   ```

### 4.2 Save Your Credentials

Write these down - you'll need them soon:

```
TWILIO_ACCOUNT_SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN: your_auth_token_here
```

✅ **Checkpoint:** You have your Twilio credentials saved

---

## Step 5: Clone and Configure Project

### 5.1 Clone the Repository

```bash
# Navigate to your projects folder
cd ~/Projects

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

# You should see (venv) prefix in your terminal
```

### 5.3 Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed flask-3.0.0 twilio-8.11.0 python-dotenv-1.0.0
```

### 5.4 Create Environment File

```bash
# Copy the example
cp .env.example .env

# Edit it
nano .env
# or
code .env  # if using VS Code
```

### 5.5 Configure Your .env File

**Fill in your actual values:**

```env
# Twilio Configuration (from Step 4)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here

# WhatsApp Configuration
# Leave blank for sandbox (Twilio provides the number)
TWILIO_PHONE_NUMBER=

# Your phone number (the one you verified and joined sandbox with)
# Format: +1234567890 (include country code, no spaces)
WHITELISTED_NUMBERS=+1234567890

# Claude API Key (from Anthropic Console)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# GitHub Token (optional - can leave blank)
GITHUB_TOKEN=

# Server Configuration (keep defaults)
SERVER_PORT=5000
SERVER_HOST=0.0.0.0
BASE_URL=http://localhost:5000
```

**Important:**
- Use YOUR phone number for `WHITELISTED_NUMBERS`
- Include country code (e.g., +1 for US)
- Don't put "whatsapp:" prefix - the code handles it automatically
- Leave `TWILIO_PHONE_NUMBER` blank for sandbox

### 5.6 Save and Verify

```bash
# Save (Ctrl+X, then Y, then Enter in nano)

# Verify file exists
ls -la .env
```

✅ **Checkpoint:** Project configured with your credentials

---

## Step 6: Set Up ngrok

ngrok creates a tunnel so Twilio can reach your local server.

### 6.1 Install ngrok

**Mac:**
```bash
brew install ngrok
```

**Linux:**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok
```

### 6.2 Create ngrok Account

1. **Go to:** https://ngrok.com/
2. **Sign up** (use Google/GitHub for quick signup)
3. **After login, go to:** https://dashboard.ngrok.com/get-started/your-authtoken
4. **Copy your auth token**

### 6.3 Configure ngrok

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with your actual token.

✅ **Checkpoint:** ngrok is installed and configured

---

## Step 7: Configure WhatsApp Webhook

We'll do this after starting the server in Step 8, but let's understand it first.

### What is a Webhook?

A webhook is a URL that Twilio calls when someone sends you a WhatsApp message. Our Flask server will listen at this URL and respond.

### The Webhook URL Format

```
https://[YOUR-NGROK-ID].ngrok-free.app/sms
```

We'll get the `[YOUR-NGROK-ID]` when we start ngrok in Step 8.

✅ **Checkpoint:** You understand webhooks

---

## Step 8: Start the Server

### 8.1 Open Two Terminal Windows

You need **two terminals**:
- **Terminal 1:** Flask server
- **Terminal 2:** ngrok

### 8.2 Terminal 1 - Start Flask

```bash
# Make sure you're in the project directory
cd ~/Projects/claudePing

# Activate virtual environment
source venv/bin/activate

# Start server
python app.py
```

**Expected output:**
```
2024-11-15 14:30:22 - __main__ - INFO - All components initialized successfully
2024-11-15 14:30:22 - __main__ - INFO - Starting server on 0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

✅ **Leave this running!**

### 8.3 Terminal 2 - Start ngrok

```bash
ngrok http 5000
```

**Expected output:**
```
ngrok

Session Status                online
Forwarding                    https://abcd-1234.ngrok-free.app -> http://localhost:5000
```

### 8.4 Copy Your ngrok URL

Look for the **Forwarding** line with HTTPS:
```
https://abcd-1234.ngrok-free.app
```

**Copy this URL** - you'll need it next!

### 8.5 Update .env with ngrok URL

In a **third terminal** or text editor:

```bash
nano .env
```

Update the `BASE_URL`:
```env
BASE_URL=https://abcd-1234.ngrok-free.app
```

Save and exit. **No need to restart Flask.**

### 8.6 Test Your Server

In a browser, visit:
```
https://your-ngrok-url.ngrok-free.app/health
```

**Expected:**
```json
{
  "status": "healthy",
  "claude_installed": true,
  "git_repo": true
}
```

✅ **Checkpoint:** Both servers running, accessible via ngrok

---

## Step 9: Configure WhatsApp Webhook (For Real)

### 9.1 Go to Twilio WhatsApp Sandbox Settings

1. **Twilio Console:** https://console.twilio.com/
2. **Navigate to:** Messaging → Try it out → Send a WhatsApp message
3. **Or directly:** https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn

### 9.2 Scroll Down to "Sandbox Configuration"

You'll see a section labeled **"When a message comes in"**

### 9.3 Configure the Webhook

**In the "When a message comes in" field:**

1. **Enter your ngrok URL + `/sms`:**
   ```
   https://abcd-1234.ngrok-free.app/sms
   ```

   ⚠️ **Don't forget `/sms` at the end!**

2. **Method:** HTTP POST (should be selected by default)

3. **Click "Save"** (red button at bottom)

**Example:**
```
Webhook URL: https://1234-abcd.ngrok-free.app/sms
Method: HTTP POST
```

✅ **Checkpoint:** Webhook configured!

---

## Step 10: Send Your First Message!

🎉 **Everything is ready!**

### 10.1 Send a Test Message

**On your phone, in WhatsApp:**

1. **Open the chat with the Twilio Sandbox number**
2. **Type and send:**
   ```
   Create a Python function that adds two numbers
   ```

### 10.2 Watch Your Terminal

**In Terminal 1 (Flask server):**

```
2024-11-15 14:35:10 - INFO - Received WhatsApp from whatsapp:+1234567890: Create a Python function that adds two numbers
2024-11-15 14:35:10 - INFO - Sending prompt to Claude: Create a Python function...
2024-11-15 14:35:15 - INFO - Claude response received (234 chars)
2024-11-15 14:35:16 - INFO - Generated summary: ✓ Done! Modified 1 file...
```

### 10.3 Check WhatsApp

Within 30-60 seconds, you'll receive a WhatsApp message:

```
✓ Done! Modified 1 file. Branch: sms/20241115_143516.
Summary: Created add_numbers function that takes two parameters...
Full: https://1234-abcd.ngrok-free.app/response/20241115_143516_123456
```

🎉 **IT WORKS!**

### 10.4 Click the Link

Tap the link in WhatsApp to see the full Claude response in your browser.

✅ **Checkpoint:** Successfully sent and received your first message!

---

## Step 11: Verify Git Integration

### 11.1 Check Git Status

In a new terminal:

```bash
cd ~/Projects/claudePing
git status
```

**Expected:**
```
On branch sms/20241115_143516
```

You're on a new branch created automatically!

### 11.2 Check Git Log

```bash
git log -1
```

**Expected:**
```
commit abc123...
Author: Your Name <your@email.com>
Date:   Fri Nov 15 14:35:16 2024

    SMS request: Create a Python function that adds two numbers
```

### 11.3 View Created Files

```bash
ls -la *.py
```

You should see new Python files created by Claude!

### 11.4 View on GitHub

1. Go to your GitHub repository
2. Click "Branches"
3. Find your new branch
4. View the code changes

🎉 **Git integration working!**

✅ **Checkpoint:** Auto-branch creation and push working

---

## Using WhatsApp Commands

### Regular Coding Requests

Just type normally:
```
Create a login function with JWT authentication
```

```
Add error handling to the add_numbers function
```

### Special Commands

#### NEW SESSION
```
NEW SESSION
```
**Response:**
```
New session started! Previous conversation cleared.
```

#### STATUS
```
STATUS
```
**Response:**
```
Session active (3 msgs). Branch: sms/20241115...
```

#### FULL Response
```
FULL 20241115_143516_123456
```
**Response:** Full Claude response (if too long for one message)

---

## Daily Usage

### Starting Your Session

**Every time you want to use the system:**

**Terminal 1:**
```bash
cd ~/Projects/claudePing
source venv/bin/activate
python app.py
```

**Terminal 2:**
```bash
ngrok http 5000
```

**Then:**
1. Copy new ngrok URL from Terminal 2
2. Update `.env` BASE_URL
3. Update Twilio webhook with new ngrok URL
4. Start messaging on WhatsApp!

### Stopping the System

1. **Terminal 1:** Ctrl+C (stop Flask)
2. **Terminal 2:** Ctrl+C (stop ngrok)
3. **Deactivate venv:** `deactivate`

---

## WhatsApp vs SMS Differences

### What's Different?

| Feature | SMS Version | WhatsApp Version |
|---------|-------------|------------------|
| Setup | Complex (A2P) | Simple (Sandbox) |
| Cost | $1-3/month | FREE |
| Approval Time | Days | Instant |
| Phone Number | Need to buy | Twilio provides |
| Message Prefix | None (paid) | "Sent via Twilio Sandbox" |
| Rich Media | No | Yes (future feature) |
| International | Extra cost | Free |

### What's the Same?

- ✅ Same code commands (NEW SESSION, STATUS, etc.)
- ✅ Same Claude integration
- ✅ Same Git automation
- ✅ Same response storage
- ✅ Same web endpoints

---

## WhatsApp Sandbox Limitations

### Sandbox Restrictions

1. **Join Code Required**
   - Each user must send "join xxx-xxx" first
   - One-time setup per user
   - If someone sends "STOP", they need to rejoin

2. **Sender Name**
   - Shows "Twilio Sandbox for WhatsApp"
   - Not customizable in sandbox
   - Production allows custom name

3. **Persistent Connection**
   - Connection lasts 24 hours of inactivity
   - After 24h silence, may need to send join code again
   - Just send any message to keep active

4. **Multiple Users**
   - Each person needs to join sandbox separately
   - Add their numbers to WHITELISTED_NUMBERS in .env

### Not a Problem for Personal Use!

For a personal coding assistant, these limitations are **perfectly fine**:
- ✅ You only join once
- ✅ You'll use it frequently (< 24h gaps)
- ✅ "Sandbox" label is fine for personal use
- ✅ FREE forever!

---

## Going to Production (Optional)

If you want to remove "Sandbox" branding:

### Requirements

1. **WhatsApp Business Account**
   - Apply through Facebook Business Manager
   - Approval process (1-2 weeks)
   - Business verification required

2. **Twilio WhatsApp-Enabled Number**
   - Register your business
   - Get number approved for WhatsApp
   - Additional costs apply

3. **Message Templates**
   - Pre-approve message formats
   - Compliance requirements

**Cost:** $5-20/month

### For Personal Use: **Not Worth It**

Sandbox is perfect for personal coding assistant use!

---

## Troubleshooting

### Problem: Didn't receive join confirmation

**Solutions:**
1. Check you messaged the correct sandbox number (from YOUR Twilio console)
2. Make sure you sent the exact join code (case-sensitive)
3. Verify WhatsApp is connected to internet
4. Try sending the join code again

### Problem: Bot doesn't respond to messages

**Check:**
1. ✅ Flask server running? (Terminal 1)
2. ✅ ngrok running? (Terminal 2)
3. ✅ Webhook configured with current ngrok URL?
4. ✅ Your number in WHITELISTED_NUMBERS?
5. ✅ Joined the sandbox?

**Debug:**
- Check Flask logs in Terminal 1
- Visit: http://127.0.0.1:4040 (ngrok web interface) to see requests
- Check Twilio Console → Monitor → Logs

### Problem: "Your number is not authorized"

**Solution:**
```bash
# Edit .env
nano .env

# Check WHITELISTED_NUMBERS has YOUR number
WHITELISTED_NUMBERS=+1234567890

# Include country code, no spaces
# Don't add "whatsapp:" prefix
```

Restart Flask server after changing .env.

### Problem: "Claude Code CLI not detected"

**Solution:**
```bash
# Verify installation
claude --version

# If not found
brew install anthropics/tap/claude  # Mac
# or
curl -fsSL https://claude.ai/download/cli/linux | sh  # Linux

# Configure
claude configure
# Enter API key
```

### Problem: ngrok URL keeps changing

**Symptom:** Must update webhook every restart

**Solutions:**
1. **Paid ngrok** ($8/month) - static URLs
2. **Deploy to cloud** - permanent URL (Heroku, Railway, etc.)
3. **Accept it** - Free tier = changing URLs

### Problem: Connection expired after 24h

**Symptom:** Bot stops responding after a day

**Solution:**
Just send any message to reconnect! The system handles it automatically.

If that doesn't work, resend the join code.

### Problem: Multiple people want to use it

**Solution:**

1. **Each person must:**
   - Join the Twilio sandbox (send join code)
   - Tell you their phone number

2. **You add their numbers to .env:**
   ```env
   WHITELISTED_NUMBERS=+1234567890,+1987654321,+1555555555
   ```

3. **Restart Flask server**

---

## Costs Summary

### WhatsApp Version (This Setup)

**Twilio:**
- ✅ Account: FREE
- ✅ Sandbox: FREE
- ✅ Messages: FREE
- **Total: $0/month**

**Claude API:**
- Pay-per-use: ~$0.003-$0.01 per request
- Estimated: $2-5/month for personal use

**ngrok:**
- ✅ Free tier: OK for personal use
- ⚠️ URLs change each restart
- Paid ($8/month): Static URLs

**Grand Total: ~$2-5/month**

(Just Claude API costs!)

---

## Quick Reference

### Important URLs

- **Twilio Console:** https://console.twilio.com/
- **WhatsApp Sandbox:** https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
- **ngrok Dashboard:** http://127.0.0.1:4040
- **Health Check:** http://localhost:5000/health

### WhatsApp Commands

- **Coding request:** Just type it normally
- **NEW SESSION:** Clear conversation
- **STATUS:** Check session info
- **FULL [id]:** Get complete response

### Start System

```bash
# Terminal 1
cd ~/Projects/claudePing && source venv/bin/activate && python app.py

# Terminal 2
ngrok http 5000

# Then update webhook with new ngrok URL
```

---

## Congratulations! 🎉

You've successfully set up your WhatsApp coding companion!

**Benefits you're getting:**
- ✅ Code from anywhere via WhatsApp
- ✅ No SMS/phone number costs
- ✅ No A2P compliance hassles
- ✅ Free Twilio sandbox
- ✅ Automatic Git integration
- ✅ Only pay for Claude API (~$5/month)

**Now you can code on the go just by sending a WhatsApp message!**

Happy coding! 💻📱

---

**Last Updated:** November 2025
**Guide Version:** 1.0
**For:** Text-Based Coding Companion - WhatsApp Edition
