# Text-Based Coding Companion

A tool that lets you interact with Claude Code via text messages. Send coding requests via SMS and get AI-powered coding assistance on the go, with automatic branch creation and GitHub integration.

## Features

- 📱 **SMS Interface**: Send coding requests via text message
- 🤖 **Claude Code Integration**: Leverages Claude Code CLI for intelligent coding assistance
- 🌿 **Auto Branch Creation**: Automatically creates Git branches for code changes
- 💾 **Response Storage**: Full responses stored and accessible via web link
- 📊 **Session Management**: Maintains conversation context across messages
- 🔒 **Phone Whitelist**: Security through phone number authorization

## Architecture

```
[Your Phone]
    ↓ SMS
[Twilio]
    ↓ Webhook
[Flask Server]
    ↓
[Claude Code CLI] → [Git/GitHub]
    ↓
[Summary via SMS]
```

## Prerequisites

1. **Python 3.8+**
2. **Claude Code CLI** - Install from [Anthropic](https://docs.anthropic.com)
3. **Twilio Account** - For SMS functionality
4. **Git Repository** - For code change management
5. **ngrok** (for local development) - To expose local server to Twilio

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd claudePing
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Claude Code CLI

Follow the official installation instructions at [Anthropic Claude Code](https://docs.anthropic.com).

Verify installation:
```bash
claude --version
```

### 5. Set Up Twilio

1. **Create a Twilio Account**: Go to [twilio.com](https://www.twilio.com/try-twilio)
2. **Get a Phone Number**:
   - Navigate to Phone Numbers → Buy a Number
   - Choose a number with SMS capabilities
3. **Get Your Credentials**:
   - Account SID: Found on your Twilio Console Dashboard
   - Auth Token: Found on your Twilio Console Dashboard

### 6. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Whitelisted phone numbers (comma-separated)
WHITELISTED_NUMBERS=+1234567890,+0987654321

# Claude API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# GitHub Token (optional, for private repos)
GITHUB_TOKEN=your_github_token_here

# Server Configuration
SERVER_PORT=5000
SERVER_HOST=0.0.0.0
BASE_URL=http://localhost:5000
```

**Important**:
- Replace `your_account_sid_here` and `your_auth_token_here` with your actual Twilio credentials
- Add your phone number to `WHITELISTED_NUMBERS`
- Get your Anthropic API key from [Anthropic Console](https://console.anthropic.com/)

### 7. Set Up ngrok (for Local Development)

1. **Install ngrok**: Download from [ngrok.com](https://ngrok.com/download)

2. **Start ngrok**:
   ```bash
   ngrok http 5000
   ```

3. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

4. **Update `.env`**:
   ```env
   BASE_URL=https://abc123.ngrok.io
   ```

5. **Configure Twilio Webhook**:
   - Go to Twilio Console → Phone Numbers → Your Number
   - Under "Messaging", set "A MESSAGE COMES IN" to:
     ```
     https://abc123.ngrok.io/sms
     ```
   - Set method to `HTTP POST`
   - Save

## Usage

### Starting the Server

```bash
python app.py
```

You should see:
```
Starting server on 0.0.0.0:5000
Press Ctrl+C to stop
```

### Sending SMS Commands

Once the server is running and Twilio is configured, you can text your Twilio number:

#### Regular Coding Request
```
Create a Python function to calculate fibonacci numbers
```

Response:
```
✓ Done! Modified 1 file. Branch: sms/20231115_143022.
Summary: Created fibonacci function with memoization...
Full: https://abc123.ngrok.io/response/20231115_143022_123456
```

#### Special Commands

**Start New Session**:
```
NEW SESSION
```

**Check Status**:
```
STATUS
```

**Get Full Response** (if summary was truncated):
```
FULL 20231115_143022_123456
```

## Project Structure

```
claudePing/
├── app.py                  # Main Flask application
├── claude_handler.py       # Claude Code CLI integration
├── git_handler.py          # Git operations (branch, commit, push)
├── storage.py              # Response and session storage
├── summary_generator.py    # SMS summary generation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── responses/             # Stored full responses (JSON)
├── sessions/              # User session data
└── tests/
    └── test_local.py      # Local testing utilities
```

## How It Works

1. **Receive SMS**: Twilio forwards incoming SMS to `/sms` webhook
2. **Validate**: Check if phone number is whitelisted
3. **Process Command**: Check for special commands (NEW SESSION, STATUS, etc.)
4. **Send to Claude**: Forward request to Claude Code CLI
5. **Git Operations**:
   - Detect file changes
   - Create new branch (`sms/timestamp`)
   - Commit changes
   - Push to GitHub
6. **Store Response**: Save full response with metadata
7. **Generate Summary**: Create concise SMS-friendly summary
8. **Send SMS**: Reply with summary and link to full response

## Configuration

### Whitelist Management

Add phone numbers to `.env`:
```env
WHITELISTED_NUMBERS=+12345678901,+10987654321,+15555555555
```

### Timeout Settings

Adjust Claude Code timeout in `claude_handler.py`:
```python
def send_prompt(self, prompt: str, timeout: int = 120):
```

### Summary Length

Adjust summary length in `summary_generator.py`:
```python
def __init__(self, max_length: int = 150):
```

## Testing

### Local Testing Without SMS

Use the test utility:

```bash
python tests/test_local.py
```

This allows you to:
- Test Claude Code integration
- Test Git operations
- Test response generation
- All without needing SMS/Twilio

### Health Check

Visit `http://localhost:5000/health` to verify:
- Server is running
- Claude Code is installed
- Git repository is detected

## Troubleshooting

### Claude Code Not Found
```
Error: Claude Code CLI not detected
```

**Solution**: Install Claude Code CLI and ensure it's in your PATH

### Twilio Webhook Not Receiving Messages
1. Check ngrok is running
2. Verify webhook URL in Twilio console matches ngrok URL
3. Check Twilio phone number is SMS-enabled

### Phone Number Not Whitelisted
```
Sorry, your number is not authorized to use this service.
```

**Solution**: Add your phone number to `WHITELISTED_NUMBERS` in `.env`

### Git Push Failed (403 Error)
```
Authentication failed
```

**Solution**:
1. Set `GITHUB_TOKEN` in `.env`
2. Ensure token has repo write permissions
3. Verify branch name starts with `claude/` and ends with session ID

### Response Timeout
```
Request timed out after 120 seconds
```

**Solution**: Increase timeout in `claude_handler.py` for complex requests

## API Endpoints

### `POST /sms`
Twilio webhook endpoint for incoming SMS

### `GET /response/<id>`
Retrieve full response by ID

**Response**:
```json
{
  "id": "20231115_143022_123456",
  "timestamp": "2023-11-15T14:30:22",
  "prompt": "Create a Python function...",
  "response": "Here's the function...",
  "branch_name": "sms/20231115_143022",
  "files_changed": ["fibonacci.py"]
}
```

### `GET /health`
Health check endpoint

### `GET /`
Service info and available endpoints

## Security Considerations

1. **Whitelist Only**: Only authorized phone numbers can use the service
2. **API Key Protection**: Store API keys in `.env`, never commit to Git
3. **HTTPS Only**: Use HTTPS for production (ngrok provides this)
4. **Rate Limiting**: Consider adding rate limiting for production use
5. **Input Validation**: All inputs are validated before processing

## Limitations (MVP)

- Single user (personal use)
- Local deployment only
- No advanced session management
- Basic error handling
- SMS character limits (summaries truncated)

## Future Enhancements

- Multi-user support with user authentication
- Web dashboard for managing sessions
- Advanced conversation history
- Support for multiple repositories
- Integration with other messaging platforms (Slack, Discord)
- Cloud deployment (AWS Lambda, Heroku)
- Enhanced error recovery
- Analytics and usage tracking

## Contributing

This is a personal MVP project. Feedback and suggestions welcome!

## License

MIT License - feel free to use and modify for your needs.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs in the console
3. Test with `test_local.py`
4. Check Twilio webhook logs in Twilio Console

## Acknowledgments

- Built with [Claude Code](https://www.anthropic.com) by Anthropic
- SMS powered by [Twilio](https://www.twilio.com)
- Uses [Flask](https://flask.palletsprojects.com/) for web framework