"""
Repository management for multi-repo support.
"""
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

from git_handler import GitHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Repository:
    """Represents a repository in the system."""

    name: str
    path: str
    remote_url: Optional[str] = None
    description: str = ""
    created_at: str = ""
    last_accessed: str = ""
    access_control: Dict[str, List[str]] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_accessed:
            self.last_accessed = datetime.now().isoformat()
        if self.access_control is None:
            self.access_control = {}

    @property
    def is_valid(self) -> bool:
        """Check if repository path exists and is a valid git repo."""
        if not os.path.exists(self.path):
            return False
        git_dir = os.path.join(self.path, '.git')
        return os.path.isdir(git_dir)

    def has_access(self, phone_number: str, permission: str = 'read') -> bool:
        """
        Check if user has specific permission for this repo.

        Args:
            phone_number: User's phone number
            permission: Permission to check ('read', 'write', 'admin')

        Returns:
            True if user has permission
        """
        user_permissions = self.access_control.get(phone_number, [])
        return permission in user_permissions

    def update_last_accessed(self):
        """Update the last accessed timestamp."""
        self.last_accessed = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert repository to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Repository':
        """Create repository from dictionary."""
        return cls(**data)


class RepositoryManager:
    """Manages multiple repositories and their metadata."""

    def __init__(self, config_path: str = "config/repositories.json"):
        """
        Initialize the repository manager.

        Args:
            config_path: Path to repositories configuration file
        """
        self.config_path = config_path
        self.repositories: Dict[str, Repository] = {}
        self.default_repository: Optional[str] = None

        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        # Load existing configuration
        self._load_config()

    def _load_config(self):
        """Load repositories from configuration file."""
        if not os.path.exists(self.config_path):
            logger.info("No existing repository configuration found")
            return

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            # Load repositories
            for name, repo_data in config.get('repositories', {}).items():
                self.repositories[name] = Repository.from_dict(repo_data)

            # Load default repository
            self.default_repository = config.get('default_repository')

            logger.info(f"Loaded {len(self.repositories)} repositories from config")

        except Exception as e:
            logger.error(f"Error loading repository config: {e}")

    def _save_config(self):
        """Save repositories to configuration file."""
        try:
            config = {
                'repositories': {
                    name: repo.to_dict()
                    for name, repo in self.repositories.items()
                },
                'default_repository': self.default_repository
            }

            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"Saved {len(self.repositories)} repositories to config")

        except Exception as e:
            logger.error(f"Error saving repository config: {e}")
            raise

    def register_repository(self,
                          name: str,
                          path: str,
                          remote_url: Optional[str] = None,
                          description: str = "",
                          access_control: Optional[Dict[str, List[str]]] = None) -> Tuple[bool, str]:
        """
        Register a new repository.

        Args:
            name: User-friendly name for the repository
            path: Absolute path to repository
            remote_url: Git remote URL (optional, will be detected if not provided)
            description: Human-readable description
            access_control: Initial access control mapping

        Returns:
            Tuple of (success, message)
        """
        # Validate name
        if not name or name in self.repositories:
            return False, f"Repository name '{name}' is invalid or already exists"

        # Validate path
        if not os.path.isabs(path):
            return False, "Repository path must be absolute"

        if not os.path.exists(path):
            return False, f"Path does not exist: {path}"

        # Check if it's a git repository
        git_dir = os.path.join(path, '.git')
        if not os.path.isdir(git_dir):
            return False, f"Path is not a git repository: {path}"

        # Auto-detect remote URL if not provided
        if not remote_url:
            try:
                git_handler = GitHandler(path)
                remote_url = git_handler.get_repo_url()
            except Exception as e:
                logger.warning(f"Could not detect remote URL: {e}")

        # Create repository object
        repo = Repository(
            name=name,
            path=path,
            remote_url=remote_url,
            description=description,
            access_control=access_control or {}
        )

        # Add to registry
        self.repositories[name] = repo

        # Set as default if it's the first repository
        if len(self.repositories) == 1:
            self.default_repository = name

        # Save configuration
        self._save_config()

        logger.info(f"Registered repository: {name} at {path}")
        return True, f"Successfully registered repository '{name}'"

    def unregister_repository(self, name: str) -> Tuple[bool, str]:
        """
        Unregister a repository.

        Args:
            name: Repository name

        Returns:
            Tuple of (success, message)
        """
        if name not in self.repositories:
            return False, f"Repository '{name}' not found"

        # Remove from registry
        del self.repositories[name]

        # Update default if needed
        if self.default_repository == name:
            self.default_repository = next(iter(self.repositories.keys())) if self.repositories else None

        # Save configuration
        self._save_config()

        logger.info(f"Unregistered repository: {name}")
        return True, f"Successfully unregistered repository '{name}'"

    def get_repository(self, name: str) -> Optional[Repository]:
        """
        Get a repository by name.

        Args:
            name: Repository name

        Returns:
            Repository object or None if not found
        """
        repo = self.repositories.get(name)
        if repo:
            repo.update_last_accessed()
            self._save_config()
        return repo

    def list_repositories(self, phone_number: Optional[str] = None) -> List[Repository]:
        """
        List all repositories, optionally filtered by user access.

        Args:
            phone_number: Filter by user access (optional)

        Returns:
            List of Repository objects
        """
        repos = list(self.repositories.values())

        if phone_number:
            # Filter by access control
            repos = [
                repo for repo in repos
                if repo.has_access(phone_number, 'read')
            ]

        return repos

    def get_default_repository(self) -> Optional[Repository]:
        """
        Get the default repository.

        Returns:
            Default Repository object or None
        """
        if self.default_repository:
            return self.get_repository(self.default_repository)
        return None

    def set_default_repository(self, name: str) -> Tuple[bool, str]:
        """
        Set the default repository.

        Args:
            name: Repository name

        Returns:
            Tuple of (success, message)
        """
        if name not in self.repositories:
            return False, f"Repository '{name}' not found"

        self.default_repository = name
        self._save_config()

        logger.info(f"Set default repository to: {name}")
        return True, f"Default repository set to '{name}'"

    def discover_repositories(self, search_path: str, max_depth: int = 3) -> List[str]:
        """
        Auto-discover git repositories in directory tree.

        Args:
            search_path: Root path to search
            max_depth: Maximum directory depth to search

        Returns:
            List of discovered repository paths
        """
        discovered = []

        try:
            for root, dirs, files in os.walk(search_path):
                # Check depth
                depth = root[len(search_path):].count(os.sep)
                if depth > max_depth:
                    continue

                # Check if this is a git repo
                if '.git' in dirs:
                    discovered.append(root)
                    # Don't recurse into git repos
                    dirs[:] = []

        except Exception as e:
            logger.error(f"Error discovering repositories: {e}")

        return discovered

    def grant_access(self,
                    repo_name: str,
                    phone_number: str,
                    permissions: List[str]) -> Tuple[bool, str]:
        """
        Grant user access to a repository.

        Args:
            repo_name: Repository name
            phone_number: User's phone number
            permissions: List of permissions to grant ('read', 'write', 'admin')

        Returns:
            Tuple of (success, message)
        """
        repo = self.repositories.get(repo_name)
        if not repo:
            return False, f"Repository '{repo_name}' not found"

        repo.access_control[phone_number] = permissions
        self._save_config()

        logger.info(f"Granted {permissions} access to {phone_number} for {repo_name}")
        return True, f"Access granted successfully"

    def revoke_access(self, repo_name: str, phone_number: str) -> Tuple[bool, str]:
        """
        Revoke user access to a repository.

        Args:
            repo_name: Repository name
            phone_number: User's phone number

        Returns:
            Tuple of (success, message)
        """
        repo = self.repositories.get(repo_name)
        if not repo:
            return False, f"Repository '{repo_name}' not found"

        if phone_number in repo.access_control:
            del repo.access_control[phone_number]
            self._save_config()
            logger.info(f"Revoked access for {phone_number} from {repo_name}")
            return True, "Access revoked successfully"

        return False, "User did not have access to this repository"

    def validate_access(self,
                       phone_number: str,
                       repo_name: str,
                       permission: str = 'read') -> Tuple[bool, str]:
        """
        Validate if user has permission for repository operation.

        Args:
            phone_number: User's phone number
            repo_name: Repository name
            permission: Required permission ('read', 'write', 'admin')

        Returns:
            Tuple of (is_allowed, error_message)
        """
        repo = self.repositories.get(repo_name)
        if not repo:
            return False, f"Repository '{repo_name}' not found"

        if not repo.is_valid:
            return False, f"Repository '{repo_name}' is not valid or accessible"

        if not repo.has_access(phone_number, permission):
            return False, f"No {permission} access to repository '{repo_name}'"

        return True, ""

    def get_repository_stats(self, name: str) -> Optional[Dict]:
        """
        Get statistics about a repository.

        Args:
            name: Repository name

        Returns:
            Dictionary with repository statistics or None
        """
        repo = self.repositories.get(name)
        if not repo:
            return None

        try:
            git_handler = GitHandler(repo.path)

            stats = {
                'name': repo.name,
                'path': repo.path,
                'is_valid': repo.is_valid,
                'current_branch': git_handler.get_current_branch(),
                'has_changes': git_handler.has_uncommitted_changes(),
                'remote_url': repo.remote_url,
                'last_accessed': repo.last_accessed
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting repository stats: {e}")
            return None
