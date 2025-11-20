"""
Session manager with multi-repository support.
"""
import logging
import json
import os
from typing import Tuple, Optional, List, Dict
from datetime import datetime

from repository_manager import RepositoryManager, Repository
from repo_aware_claude_handler import RepoAwareClaudeHandler
from storage import SessionStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages Claude conversation sessions with multi-repository support.

    Tracks user's active repository with both in-memory cache and
    persistent storage for session continuity.
    """

    def __init__(self,
                 repo_manager: RepositoryManager,
                 repo_claude_handler: RepoAwareClaudeHandler,
                 session_storage: SessionStorage):
        """
        Initialize the session manager.

        Args:
            repo_manager: RepositoryManager instance
            repo_claude_handler: RepoAwareClaudeHandler instance
            session_storage: SessionStorage instance for persistence
        """
        self.repo_manager = repo_manager
        self.repo_claude_handler = repo_claude_handler
        self.session_storage = session_storage

        # Track active repository per user (in-memory cache)
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

        # Update active repository in memory
        self._active_repos[phone_number] = repo_name

        # Persist to session storage
        self._persist_active_repo(phone_number, repo_name)

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

        Checks in-memory cache first, then session storage, then falls back
        to default repository.

        Args:
            phone_number: User's phone number

        Returns:
            Repository object or None
        """
        # Check in-memory cache first
        repo_name = self._active_repos.get(phone_number)

        # If not in memory, check session storage
        if not repo_name:
            session = self.session_storage.get_session(phone_number)
            repo_name = session.get('active_repository')

        if repo_name:
            repo = self.repo_manager.get_repository(repo_name)
            if repo:
                # Cache it in memory for next time
                self._active_repos[phone_number] = repo_name
                return repo
            else:
                # Cached repo no longer exists, clear it
                logger.warning(f"Cached repository '{repo_name}' no longer exists for {phone_number}")
                if phone_number in self._active_repos:
                    del self._active_repos[phone_number]

        # Fall back to default repository
        default_repo = self.repo_manager.get_default_repository()
        if default_repo:
            # Check access
            is_allowed, error_msg = self.repo_manager.validate_access(phone_number, default_repo.name, 'read')
            if is_allowed:
                # Set as active for this user
                self._active_repos[phone_number] = default_repo.name
                self._persist_active_repo(phone_number, default_repo.name)
                logger.info(f"Set default repository '{default_repo.name}' as active for {phone_number}")
                return default_repo
            else:
                # User doesn't have access to default repo
                logger.warning(f"User {phone_number} doesn't have access to default repository: {error_msg}")

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
            self._persist_active_repo(phone_number, repository.name)

        return success, response, error

    def send_message(self,
                    phone_number: str,
                    message: str,
                    repository_name: Optional[str] = None,
                    timeout: int = 120) -> Tuple[bool, str, Optional[str]]:
        """
        Send a message in the context of a user's session.

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
                return False, "", "No repository selected. Send 'list repos' to see available repositories or 'switch to <repo>' to select one."

        # Send message to specific repository
        return self.send_message_to_repo(phone_number, message, repo, timeout)

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
        # Clear active repository from memory
        if phone_number in self._active_repos:
            del self._active_repos[phone_number]

        # Clear from persistent storage
        self.session_storage.clear_session(phone_number)

        logger.info(f"Cleared session and repository context for {phone_number}")

    def _persist_active_repo(self, phone_number: str, repo_name: str):
        """
        Persist active repository to session storage.

        Args:
            phone_number: User's phone number
            repo_name: Repository name to persist
        """
        session = self.session_storage.get_session(phone_number)
        session['active_repository'] = repo_name

        # Update session file directly
        session_file = self.session_storage.get_session_file(phone_number)
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)

        logger.debug(f"Persisted active repository '{repo_name}' for {phone_number}")
