"""
Claude Code CLI integration handler.
"""
import subprocess
import os
import logging
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeHandler:
    """Handles interaction with Claude Code CLI."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude handler.

        Args:
            api_key: Anthropic API key (will use env var if not provided)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")

        # Set the API key in environment
        os.environ['ANTHROPIC_API_KEY'] = self.api_key

    def send_prompt(self, prompt: str, timeout: int = 120, working_dir: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Send a prompt to Claude Code CLI and get the response.

        Args:
            prompt: The prompt to send to Claude
            timeout: Maximum time to wait for response (seconds)
            working_dir: Directory to run Claude in (defaults to current directory)

        Returns:
            Tuple of (success, response_text, error_message)
        """
        try:
            # Prepare environment with workspace context
            env = os.environ.copy()

            # Enhance prompt with workspace context
            enhanced_prompt = self._build_workspace_prompt(prompt, working_dir or os.getcwd())

            # Run Claude Code with the prompt
            # Using -p flag to pass prompt directly
            result = subprocess.run(
                ['claude', '-p', enhanced_prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir,  # Run in the specified directory
                env=env
            )

            if result.returncode == 0:
                response = result.stdout.strip()
                logger.info(f"Claude response received ({len(response)} chars)")
                return True, response, None
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"Claude command failed: {error_msg}")
                return False, "", error_msg

        except subprocess.TimeoutExpired:
            logger.error(f"Claude command timed out after {timeout}s")
            return False, "", f"Request timed out after {timeout} seconds"

        except Exception as e:
            logger.error(f"Error running Claude: {str(e)}")
            return False, "", str(e)

    def send_interactive_prompt(self, prompt: str, session_id: str, timeout: int = 120) -> Tuple[bool, str, Optional[str]]:
        """
        Send a prompt to Claude Code in interactive mode with session persistence.

        This allows maintaining conversation context across multiple prompts.

        Args:
            prompt: The prompt to send to Claude
            session_id: Unique identifier for the conversation session
            timeout: Maximum time to wait for response (seconds)

        Returns:
            Tuple of (success, response_text, error_message)
        """
        # For MVP, we'll use a simpler approach with direct prompting
        # In a production version, we could maintain a persistent Claude process
        # For now, we include session context in the prompt

        return self.send_prompt(prompt, timeout)

    def _build_workspace_prompt(self, user_prompt: str, working_dir: str) -> str:
        """
        Build an enhanced prompt with workspace context.

        Args:
            user_prompt: The user's original prompt
            working_dir: Current working directory (repository path)

        Returns:
            Enhanced prompt with workspace context
        """
        # Check if we're in a git repository
        is_git_repo = os.path.isdir(os.path.join(working_dir, '.git'))

        context_parts = []

        if is_git_repo:
            context_parts.append(f"You are working in a git repository at: {working_dir}")
            context_parts.append("You have full access to read, explore, and modify files in this codebase.")
            context_parts.append("Use your file reading and editing tools to understand the code structure before making changes.")
        else:
            context_parts.append(f"You are working in directory: {working_dir}")
            context_parts.append("You have access to read and modify files in this directory.")

        context_parts.append("\nUser request:")
        context_parts.append(user_prompt)

        return "\n".join(context_parts)

    def check_claude_installed(self) -> bool:
        """
        Check if Claude Code CLI is installed and accessible.

        Returns:
            True if Claude is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def get_claude_version(self) -> Optional[str]:
        """
        Get the installed Claude Code version.

        Returns:
            Version string or None if not installed
        """
        try:
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return None


class SessionManager:
    """Manages Claude conversation sessions for different users."""

    def __init__(self, claude_handler: ClaudeHandler):
        """
        Initialize the session manager.

        Args:
            claude_handler: ClaudeHandler instance to use
        """
        self.claude = claude_handler
        self.sessions = {}  # phone_number -> session data

    def send_message(self, phone_number: str, message: str, timeout: int = 120) -> Tuple[bool, str, Optional[str]]:
        """
        Send a message in the context of a user's session.

        Args:
            phone_number: User's phone number (session ID)
            message: Message to send
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, response, error)
        """
        session_id = phone_number.replace('+', '').replace('-', '')

        # For MVP, we're not maintaining persistent state
        # Each message is independent
        # In future versions, we could enhance this with conversation history

        success, response, error = self.claude.send_interactive_prompt(
            message,
            session_id,
            timeout
        )

        return success, response, error

    def clear_session(self, phone_number: str):
        """
        Clear a user's session.

        Args:
            phone_number: User's phone number
        """
        session_id = phone_number.replace('+', '').replace('-', '')
        if session_id in self.sessions:
            del self.sessions[session_id]
        logger.info(f"Cleared session for {phone_number}")

    def get_session_info(self, phone_number: str) -> dict:
        """
        Get information about a user's session.

        Args:
            phone_number: User's phone number

        Returns:
            Session information dictionary
        """
        session_id = phone_number.replace('+', '').replace('-', '')

        if session_id in self.sessions:
            return self.sessions[session_id]

        return {
            'session_id': session_id,
            'active': False,
            'message_count': 0
        }
