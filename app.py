"""
Flask application for Text-Based Coding Companion.
Receives messages via Twilio (WhatsApp or SMS) and interacts with Claude Code CLI.
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

# Multi-repo support imports
from repository_manager import RepositoryManager, Repository
from enhanced_session_manager import EnhancedSessionManager
from repo_aware_claude_handler import RepoAwareClaudeHandler
from git_handler_factory import GitHandlerFactory
from command_parser import CommandParser

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

# Check if multi-repo mode is enabled
def is_multi_repo_enabled() -> bool:
    """Check if multi-repo mode is enabled by presence of config file."""
    return os.path.exists('config/repositories.json')


# Initialize components
try:
    claude_handler = ClaudeHandler()
    response_storage = ResponseStorage()
    session_storage = SessionStorage()
    summary_generator = SummaryGenerator()

    # Multi-repo mode detection
    MULTI_REPO_MODE = is_multi_repo_enabled()

    if MULTI_REPO_MODE:
        logger.info("Multi-repo mode ENABLED")
        # Initialize multi-repo components
        repo_manager = RepositoryManager()
        repo_claude_handler = RepoAwareClaudeHandler()
        session_manager = EnhancedSessionManager(claude_handler, repo_manager, repo_claude_handler)
        git_handler_factory = GitHandlerFactory()
        command_parser = CommandParser()

        # Keep legacy git_handler for backward compatibility
        git_handler = GitHandler()
        logger.info(f"Loaded {len(repo_manager.repositories)} repositories")
    else:
        logger.info("Multi-repo mode DISABLED (using legacy single-repo mode)")
        # Use legacy single-repo components
        session_manager = SessionManager(claude_handler)
        git_handler = GitHandler()
        repo_manager = None
        git_handler_factory = None
        command_parser = None

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
    Handles both SMS format (+1234567890) and WhatsApp format (whatsapp:+1234567890).

    Args:
        phone_number: Phone number to check

    Returns:
        True if whitelisted, False otherwise
    """
    # Remove whatsapp: prefix if present
    clean_number = phone_number.replace('whatsapp:', '').strip()

    whitelist = os.getenv('WHITELISTED_NUMBERS', '').split(',')
    whitelist = [num.strip() for num in whitelist]

    # Check both with and without whatsapp: prefix
    return clean_number in whitelist or phone_number in whitelist


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

        status_msg = summary_generator.generate_status_summary(
            current_branch=current_branch,
            session_active=message_count > 0,
            message_count=message_count
        )

        # Add active repository info if in multi-repo mode
        if MULTI_REPO_MODE:
            active_repo = session_manager.get_active_repository_name(phone_number)
            if active_repo:
                status_msg += f"\nActive repo: {active_repo}"

        return status_msg

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


def process_repo_command(intent, phone_number: str) -> str:
    """
    Process repository management commands (multi-repo mode only).

    Args:
        intent: CommandIntent object
        phone_number: User's phone number

    Returns:
        Response message or None if not a repo command
    """
    if not MULTI_REPO_MODE:
        return None

    if intent.type == 'list_repos':
        repos = session_manager.list_accessible_repositories(phone_number)
        if not repos:
            return "No repositories available. Contact admin to register repositories."

        active_repo = session_manager.get_active_repository_name(phone_number)
        repo_list = []
        for repo in repos:
            marker = " (active)" if repo.name == active_repo else ""
            repo_list.append(f"- {repo.name}{marker}")

        return f"You have {len(repos)} repos:\n" + "\n".join(repo_list)

    elif intent.type == 'switch_repo':
        success, message = session_manager.set_active_repository(phone_number, intent.repository)
        return message

    elif intent.type == 'repo_info':
        stats = repo_manager.get_repository_stats(intent.repository)
        if not stats:
            return f"Repository '{intent.repository}' not found"

        return (
            f"Repo: {stats['name']}\n"
            f"Path: {stats['path']}\n"
            f"Branch: {stats['current_branch']}\n"
            f"Changes: {'Yes' if stats['has_changes'] else 'No'}"
        )

    elif intent.type == 'repo_status':
        repos = session_manager.list_accessible_repositories(phone_number)
        if not repos:
            return "No repositories available"

        status_lines = []
        for repo in repos[:5]:  # Limit to 5 repos for SMS
            git_h = git_handler_factory.get_handler(repo)
            has_changes = git_h.has_uncommitted_changes()
            status = "modified" if has_changes else "clean"
            status_lines.append(f"- {repo.name}: {status}")

        return "Repo status:\n" + "\n".join(status_lines)

    return None


def handle_coding_request(message: str, phone_number: str, repository: Repository = None) -> str:
    """
    Process a coding request through Claude Code.

    Args:
        message: User's message/prompt
        phone_number: User's phone number
        repository: Optional specific repository (for multi-repo mode)

    Returns:
        Response summary to send via SMS
    """
    try:
        # Determine which repository to use
        target_repo = repository
        repo_name = None

        if MULTI_REPO_MODE and not target_repo:
            # Get active repository from session
            target_repo = session_manager.get_active_repository(phone_number)
            if not target_repo:
                return "No active repository. Send 'list repos' to see available repositories or 'switch to <repo>' to select one."

        if target_repo:
            repo_name = target_repo.name
            logger.info(f"Using repository: {repo_name}")

        # Send to Claude Code
        logger.info(f"Sending prompt to Claude: {message[:50]}...")

        if MULTI_REPO_MODE and target_repo:
            # Use repository-aware execution
            success, response, error = session_manager.send_message_to_repo(
                phone_number,
                message,
                target_repo,
                timeout=120
            )
        else:
            # Legacy single-repo mode
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

        # Get appropriate git handler
        if MULTI_REPO_MODE and target_repo:
            git_h = git_handler_factory.get_handler(target_repo)
        else:
            git_h = git_handler

        if git_h.is_git_repo():
            files_changed = git_h.get_changed_files()

            if files_changed:
                # Create a new branch for this task
                success, branch_name, error = git_h.create_branch()

                if success:
                    # Commit the changes
                    commit_msg = f"SMS request: {message[:50]}"
                    git_h.commit_changes(commit_msg)

                    # Push to remote
                    push_success, push_error = git_h.push_branch(branch_name)

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

        # Add repository context if in multi-repo mode
        if MULTI_REPO_MODE and repo_name:
            # Prepend repo name to summary
            summary = f"[{repo_name}] {summary}"

        logger.info(f"Generated summary: {summary}")
        return summary

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return f"Error processing request: {str(e)}"


@app.route('/sms', methods=['POST'])
def sms_webhook():
    """
    Twilio webhook endpoint for incoming messages (SMS or WhatsApp).
    """
    try:
        # Get the incoming message details
        from_number = request.form.get('From')
        message_body = request.form.get('Body', '').strip()

        # Determine message type
        message_type = "WhatsApp" if from_number and from_number.startswith('whatsapp:') else "SMS"
        logger.info(f"Received {message_type} from {from_number}: {message_body[:50]}...")

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

        # Check for special commands (legacy)
        command_response = process_command(message_body, from_number)
        if command_response:
            resp.message(command_response)
            return str(resp)

        # Multi-repo mode: parse command intent
        if MULTI_REPO_MODE:
            intent = command_parser.parse(message_body)
            logger.info(f"Parsed intent: {intent.type}, repo: {intent.repository}")

            # Handle repository management commands
            if intent.type in ['list_repos', 'switch_repo', 'repo_info', 'repo_status']:
                repo_response = process_repo_command(intent, from_number)
                if repo_response:
                    resp.message(repo_response)
                    return str(resp)

            # Handle inline repository targeting
            elif intent.type == 'inline_repo':
                target_repo = repo_manager.get_repository(intent.repository)
                if not target_repo:
                    resp.message(f"Repository '{intent.repository}' not found. Send 'list repos' to see available.")
                    return str(resp)

                # Validate access
                is_allowed, error = repo_manager.validate_access(from_number, intent.repository, 'write')
                if not is_allowed:
                    resp.message(error)
                    return str(resp)

                # Process request in specific repository
                response_message = handle_coding_request(intent.prompt, from_number, target_repo)
                resp.message(response_message)
                return str(resp)

            # Handle regular coding request (uses active repo)
            elif intent.type == 'coding_request':
                response_message = handle_coding_request(intent.prompt, from_number)
                resp.message(response_message)
                return str(resp)

        # Legacy single-repo mode: process as coding request
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
        'messaging': 'WhatsApp and SMS supported',
        'endpoints': {
            'webhook': '/sms (handles both WhatsApp and SMS)',
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
