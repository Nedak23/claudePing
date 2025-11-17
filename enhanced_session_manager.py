"""
Enhanced session manager with multi-repository support.
"""
import logging
from typing import Tuple, Optional, List, Dict
from datetime import datetime

from claude_handler import SessionManager, ClaudeHandler
from repository_manager import RepositoryManager, Repository
from repo_aware_claude_handler import RepoAwareClaudeHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedSessionManager(SessionManager):
    """
    Extends SessionManager with multi-repository capabilities.

    Tracks user's active repository and repository history in addition
    to regular session management.
    """

    def __init__(self,
                 claude_handler: ClaudeHandler,
                 repo_manager: RepositoryManager,
                 repo_claude_handler: Optional[RepoAwareClaudeHandler] = None):
        """
        Initialize the enhanced session manager.

        Args:
            claude_handler: ClaudeHandler instance for base functionality
            repo_manager: RepositoryManager instance
            repo_claude_handler: Optional RepoAwareClaudeHandler (will create if not provided)
        """
        super().__init__(claude_handler)
        self.repo_manager = repo_manager

        # Create RepoAwareClaudeHandler if not provided
        if repo_claude_handler is None:
            api_key = getattr(claude_handler, 'api_key', None)
            self.repo_claude_handler = RepoAwareClaudeHandler(api_key=api_key)
        else:
            self.repo_claude_handler = repo_claude_handler

        # Track active repository per user (in-memory)
        # This is in addition to persistent storage
        self._active_repos: Dict[str, str] = {}

    def set_active_repository(self,
                             phone_number: str,
                             repo_name: str) -> Tuple[bool, str]:
        """
        Switch user's active repository.

        Args:
            phone_number: User's phone number
            repo_name: Repository name to switch to

        Returns:
            Tuple of (success, message)
        """
        # Check if repository exists
        repo = self.repo_manager.get_repository(repo_name)
        if not repo:
            available = [r.name for r in self.repo_manager.list_repositories(phone_number)]
            if available:
                return False, f"Repository '{repo_name}' not found. Available: {', '.join(available)}"
            else:
                return False, f"Repository '{repo_name}' not found"

        # Validate access
        is_allowed, error = self.repo_manager.validate_access(phone_number, repo_name, 'read')
        if not is_allowed:
            return False, error

        # Get previous active repo for message
        old_repo = self._active_repos.get(phone_number)

        # Update active repository
        self._active_repos[phone_number] = repo_name

        logger.info(f"User {phone_number} switched to repository: {repo_name}")

        # Build response message
        if old_repo and old_repo != repo_name:
            message = f"Switched to {repo_name} (was: {old_repo})"
        else:
            message = f"Switched to {repo_name}"

        return True, message

    def get_active_repository(self, phone_number: str) -> Optional[Repository]:
        """
        Get user's current active repository.

        Args:
            phone_number: User's phone number

        Returns:
            Repository object or None
        """
        # Check in-memory cache first
        repo_name = self._active_repos.get(phone_number)

        if repo_name:
            return self.repo_manager.get_repository(repo_name)

        # Fall back to default repository
        default_repo = self.repo_manager.get_default_repository()
        if default_repo:
            # Check access
            is_allowed, _ = self.repo_manager.validate_access(phone_number, default_repo.name, 'read')
            if is_allowed:
                # Set as active for this user
                self._active_repos[phone_number] = default_repo.name
                return default_repo

        return None

    def get_active_repository_name(self, phone_number: str) -> Optional[str]:
        """
        Get user's active repository name.

        Args:
            phone_number: User's phone number

        Returns:
            Repository name or None
        """
        repo = self.get_active_repository(phone_number)
        return repo.name if repo else None

    def send_message_to_repo(self,
                            phone_number: str,
                            message: str,
                            repository: Repository,
                            timeout: int = 120) -> Tuple[bool, str, Optional[str]]:
        """
        Send a message to Claude in the context of a specific repository.

        Args:
            phone_number: User's phone number
            message: Message to send
            repository: Target repository
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, response, error)
        """
        # Validate access
        is_allowed, error = self.repo_manager.validate_access(phone_number, repository.name, 'read')
        if not is_allowed:
            return False, "", error

        # Execute in repository context
        success, response, error = self.repo_claude_handler.send_prompt_to_repo(
            message,
            repository,
            timeout
        )

        # Update active repository if successful
        if success:
            self._active_repos[phone_number] = repository.name

        return success, response, error

    def send_message(self,
                    phone_number: str,
                    message: str,
                    repository_name: Optional[str] = None,
                    timeout: int = 120) -> Tuple[bool, str, Optional[str]]:
        """
        Send a message in the context of a user's session.

        This is an override of the base SessionManager.send_message that adds
        repository awareness.

        Args:
            phone_number: User's phone number
            message: Message to send
            repository_name: Optional specific repository (uses active if not provided)
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, response, error)
        """
        # Determine target repository
        if repository_name:
            repo = self.repo_manager.get_repository(repository_name)
            if not repo:
                return False, "", f"Repository '{repository_name}' not found"
        else:
            repo = self.get_active_repository(phone_number)
            if not repo:
                # Fall back to base implementation if no repos configured
                return super().send_message(phone_number, message, timeout)

        # Send message to specific repository
        return self.send_message_to_repo(phone_number, message, repo, timeout)

    def get_repository_history(self, phone_number: str, limit: int = 5) -> List[str]:
        """
        Get user's recently used repositories.

        Args:
            phone_number: User's phone number
            limit: Maximum number of repos to return

        Returns:
            List of repository names
        """
        # For now, return accessible repositories sorted by last accessed
        repos = self.repo_manager.list_repositories(phone_number)
        repos.sort(key=lambda r: r.last_accessed, reverse=True)

        return [r.name for r in repos[:limit]]

    def validate_repo_access(self, phone_number: str, repo_name: str) -> bool:
        """
        Check if user has access to a repository.

        Args:
            phone_number: User's phone number
            repo_name: Repository name

        Returns:
            True if user has access
        """
        is_allowed, _ = self.repo_manager.validate_access(phone_number, repo_name, 'read')
        return is_allowed

    def list_accessible_repositories(self, phone_number: str) -> List[Repository]:
        """
        List all repositories accessible to user.

        Args:
            phone_number: User's phone number

        Returns:
            List of Repository objects
        """
        return self.repo_manager.list_repositories(phone_number)

    def clear_session(self, phone_number: str):
        """
        Clear a user's session including repository context.

        Args:
            phone_number: User's phone number
        """
        # Clear active repository
        if phone_number in self._active_repos:
            del self._active_repos[phone_number]

        # Call parent clear_session
        super().clear_session(phone_number)

        logger.info(f"Cleared session and repository context for {phone_number}")
