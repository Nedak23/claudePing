# ClaudePing Commands Reference

## Special Commands

### NEW SESSION

**Purpose:** Start a fresh conversation, clearing all previous context.

**Usage:**
```
NEW SESSION
```

**When to use:**
- Starting a completely different project
- Switching to an unrelated task
- Claude seems confused from previous context
- You want to clear conversation history

**Response:**
```
New session started! Previous conversation cleared.
```

### STATUS

**Purpose:** Check current session information and active branch.

**Usage:**
```
STATUS
```

**Response:**
```
Session active (5 msgs). Branch: sms/20241115_143022
Last activity: 2024-11-15 14:35:22
Files modified: 3
```

**What you get:**
- Number of messages in current session
- Current git branch name
- Timestamp of last activity
- Number of files modified in this session

**When to use:**
- Check which branch you're currently on
- See how many messages in current conversation
- Verify session is still active
- Check last activity time

### FULL

**Purpose:** Retrieve the complete response for a previous request.

**Usage:**
```
FULL 20241115_143022_123456
```

Replace the ID with the one from your previous summary response.

**When to use:**
- Summary was too short and you need details
- You want to see the complete code Claude wrote
- You need to review the full explanation
- You want to copy/paste the full response

**Response:**
The complete, untruncated response from Claude, including:
- Full code blocks
- Complete explanations
- All details that were truncated in summary

**How to get the ID:**
Every response includes a link like:
```
Full: https://your-server.com/response/20241115_143022_123456
                                        ^^^^^^^^^^^^^^^^^^^^^^
                                        This is the ID
```