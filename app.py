"""
Flask application for Text-Based Coding Companion.
Receives SMS via Twilio webhook and interacts with Claude Code CLI.
"""
import os
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
import logging

from claude_handler import ClaudeHandler, SessionManager
from git_handler import GitHandler
from storage import ResponseStorage, SessionStorage
from summary_generator import SummaryGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize components
try:
    claude_handler = ClaudeHandler()
    session_manager = SessionManager(claude_handler)
    git_handler = GitHandler()
    response_storage = ResponseStorage()
    session_storage = SessionStorage()
    summary_generator = SummaryGenerator()

    # Initialize Twilio client
    twilio_client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )

    logger.info("All components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {str(e)}")
    raise


def is_whitelisted(phone_number: str) -> bool:
    """
    Check if a phone number is whitelisted.

    Args:
        phone_number: Phone number to check

    Returns:
        True if whitelisted, False otherwise
    """
    whitelist = os.getenv('WHITELISTED_NUMBERS', '').split(',')
    whitelist = [num.strip() for num in whitelist]
    return phone_number in whitelist


def process_command(command: str, phone_number: str) -> str:
    """
    Process special commands (NEW SESSION, STATUS, etc.).

    Args:
        command: The command string
        phone_number: User's phone number

    Returns:
        Response message
    """
    command_upper = command.strip().upper()

    if command_upper == 'NEW SESSION':
        session_storage.clear_session(phone_number)
        session_manager.clear_session(phone_number)
        return "New session started! Previous conversation cleared."

    elif command_upper == 'STATUS':
        session = session_storage.get_session(phone_number)
        current_branch = session.get('current_branch')
        message_count = len(session.get('conversation_history', []))

        return summary_generator.generate_status_summary(
            current_branch=current_branch,
            session_active=message_count > 0,
            message_count=message_count
        )

    elif command_upper.startswith('FULL '):
        # Get full response by ID
        response_id = command[5:].strip()
        response_data = response_storage.get_response(response_id)

        if response_data:
            # Split into multiple messages if needed
            full_response = response_data['response']
            chunks = summary_generator.split_long_message(full_response, max_length=1500)
            return chunks[0] if chunks else "Response not found"
        else:
            return f"Response {response_id} not found"

    return None


def handle_coding_request(message: str, phone_number: str) -> str:
    """
    Process a coding request through Claude Code.

    Args:
        message: User's message/prompt
        phone_number: User's phone number

    Returns:
        Response summary to send via SMS
    """
    try:
        # Send to Claude Code
        logger.info(f"Sending prompt to Claude: {message[:50]}...")
        success, response, error = session_manager.send_message(
            phone_number,
            message,
            timeout=120
        )

        if not success:
            logger.error(f"Claude request failed: {error}")
            return f"Error: {error or 'Failed to get response from Claude'}"

        logger.info(f"Received Claude response ({len(response)} chars)")

        # Check for file changes and create branch if needed
        branch_name = None
        files_changed = []

        if git_handler.is_git_repo():
            files_changed = git_handler.get_changed_files()

            if files_changed:
                # Create a new branch for this task
                success, branch_name, error = git_handler.create_branch()

                if success:
                    # Commit the changes
                    commit_msg = f"SMS request: {message[:50]}"
                    git_handler.commit_changes(commit_msg)

                    # Push to remote
                    push_success, push_error = git_handler.push_branch(branch_name)

                    if not push_success:
                        logger.warning(f"Failed to push branch: {push_error}")
                        branch_name = f"{branch_name} (push failed)"
                else:
                    logger.warning(f"Failed to create branch: {error}")

        # Store full response
        response_id = response_storage.save_response(
            response_text=response,
            phone_number=phone_number,
            prompt=message,
            branch_name=branch_name,
            files_changed=files_changed
        )

        # Update session
        session_storage.update_session(
            phone_number=phone_number,
            prompt=message,
            response=response,
            branch_name=branch_name
        )

        # Generate summary for SMS
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        summary = summary_generator.generate_summary(
            response=response,
            branch_name=branch_name,
            files_changed=files_changed,
            response_id=response_id,
            base_url=base_url
        )

        logger.info(f"Generated summary: {summary}")
        return summary

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return f"Error processing request: {str(e)}"


@app.route('/sms', methods=['POST'])
def sms_webhook():
    """
    Twilio webhook endpoint for incoming SMS messages.
    """
    try:
        # Get the incoming message details
        from_number = request.form.get('From')
        message_body = request.form.get('Body', '').strip()

        logger.info(f"Received SMS from {from_number}: {message_body[:50]}...")

        # Create Twilio response
        resp = MessagingResponse()

        # Check whitelist
        if not is_whitelisted(from_number):
            logger.warning(f"Rejected message from non-whitelisted number: {from_number}")
            resp.message("Sorry, your number is not authorized to use this service.")
            return str(resp)

        if not message_body:
            resp.message("Please send a message with your coding request.")
            return str(resp)

        # Check for special commands
        command_response = process_command(message_body, from_number)
        if command_response:
            resp.message(command_response)
            return str(resp)

        # Process coding request
        response_message = handle_coding_request(message_body, from_number)
        resp.message(response_message)

        return str(resp)

    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}", exc_info=True)
        resp = MessagingResponse()
        resp.message("An error occurred processing your request. Please try again.")
        return str(resp)


@app.route('/response/<response_id>', methods=['GET'])
def get_response(response_id):
    """
    Web endpoint to retrieve full response by ID.

    Args:
        response_id: The response ID
    """
    response_data = response_storage.get_response(response_id)

    if not response_data:
        return jsonify({'error': 'Response not found'}), 404

    return jsonify({
        'id': response_data['id'],
        'timestamp': response_data['timestamp'],
        'prompt': response_data['prompt'],
        'response': response_data['response'],
        'branch_name': response_data.get('branch_name'),
        'files_changed': response_data.get('files_changed', [])
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    status = {
        'status': 'healthy',
        'claude_installed': claude_handler.check_claude_installed(),
        'git_repo': git_handler.is_git_repo()
    }

    return jsonify(status)


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with service info."""
    return jsonify({
        'service': 'Text-Based Coding Companion',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'sms_webhook': '/sms',
            'get_response': '/response/<id>',
            'health': '/health'
        }
    })


if __name__ == '__main__':
    # Verify Claude Code is installed
    if not claude_handler.check_claude_installed():
        logger.warning("Claude Code CLI not detected. Please ensure it's installed.")

    # Get configuration
    host = os.getenv('SERVER_HOST', '0.0.0.0')
    port = int(os.getenv('SERVER_PORT', 5000))

    logger.info(f"Starting server on {host}:{port}")
    logger.info("Press Ctrl+C to stop")

    # Run Flask app
    app.run(host=host, port=port, debug=True)
