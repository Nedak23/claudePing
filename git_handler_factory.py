"""
Factory for creating and caching GitHandler instances.
"""
from typing import Dict
import logging

from git_handler import GitHandler
from repository_manager import Repository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHandlerFactory:
    """
    Creates and caches GitHandler instances per repository.

    Implements singleton pattern per repository to avoid creating
    multiple handlers for the same repository.
    """

    def __init__(self):
        """Initialize the factory."""
        self._handlers: Dict[str, GitHandler] = {}

    def get_handler(self, repository: Repository) -> GitHandler:
        """
        Get or create GitHandler for a repository.

        Args:
            repository: Repository object

        Returns:
            GitHandler instance for the repository
        """
        # Use repository name as cache key
        cache_key = repository.name

        # Return cached handler if exists
        if cache_key in self._handlers:
            logger.debug(f"Using cached GitHandler for {repository.name}")
            return self._handlers[cache_key]

        # Create new handler
        handler = GitHandler(repo_path=repository.path)
        self._handlers[cache_key] = handler

        logger.info(f"Created new GitHandler for {repository.name} at {repository.path}")
        return handler

    def get_handler_by_path(self, repo_path: str, cache_key: str = None) -> GitHandler:
        """
        Get or create GitHandler for a repository path.

        Args:
            repo_path: Path to repository
            cache_key: Optional cache key (defaults to repo_path)

        Returns:
            GitHandler instance
        """
        if cache_key is None:
            cache_key = repo_path

        # Return cached handler if exists
        if cache_key in self._handlers:
            logger.debug(f"Using cached GitHandler for {cache_key}")
            return self._handlers[cache_key]

        # Create new handler
        handler = GitHandler(repo_path=repo_path)
        self._handlers[cache_key] = handler

        logger.info(f"Created new GitHandler for path {repo_path}")
        return handler

    def invalidate(self, repo_name: str):
        """
        Remove cached handler for a repository.

        Useful when repository configuration changes or needs to be reloaded.

        Args:
            repo_name: Repository name to invalidate
        """
        if repo_name in self._handlers:
            del self._handlers[repo_name]
            logger.info(f"Invalidated GitHandler cache for {repo_name}")

    def invalidate_all(self):
        """Clear all cached handlers."""
        count = len(self._handlers)
        self._handlers.clear()
        logger.info(f"Invalidated all {count} cached GitHandlers")

    def get_cached_count(self) -> int:
        """
        Get number of cached handlers.

        Returns:
            Number of cached GitHandler instances
        """
        return len(self._handlers)
