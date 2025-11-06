"""
Git operations handler for managing branches and commits.
"""
import os
from datetime import datetime
from typing import Optional, Tuple, List
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHandler:
    """Handles Git operations like branch creation, commits, and pushes."""

    def __init__(self, repo_path: str = "."):
        """
        Initialize the Git handler.

        Args:
            repo_path: Path to the Git repository (defaults to current directory)
        """
        self.repo_path = repo_path

    def is_git_repo(self) -> bool:
        """Check if the current directory is a Git repository."""
        git_dir = os.path.join(self.repo_path, '.git')
        return os.path.isdir(git_dir)

    def get_current_branch(self) -> Optional[str]:
        """Get the name of the current Git branch."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def create_branch(self, prefix: str = "sms") -> Tuple[bool, str, Optional[str]]:
        """
        Create a new branch with timestamp.

        Args:
            prefix: Prefix for the branch name

        Returns:
            Tuple of (success, branch_name, error_message)
        """
        if not self.is_git_repo():
            return False, "", "Not a git repository"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name = f"{prefix}/{timestamp}"

        try:
            # Create and checkout new branch
            subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Created and checked out branch: {branch_name}")
            return True, branch_name, None

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f"Failed to create branch: {error_msg}")
            return False, "", error_msg

    def get_changed_files(self) -> List[str]:
        """
        Get list of files that have been modified or are untracked.

        Returns:
            List of changed file paths
        """
        try:
            # Get modified files
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            changed_files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    # Format is "XY filename", we want the filename
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        changed_files.append(parts[1])

            return changed_files

        except subprocess.CalledProcessError:
            return []

    def commit_changes(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Stage and commit all changes.

        Args:
            message: Commit message

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Stage all changes
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            # Commit
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"Committed changes: {message}")
            return True, None

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f"Failed to commit: {error_msg}")
            return False, error_msg

    def push_branch(self, branch_name: str, max_retries: int = 4) -> Tuple[bool, Optional[str]]:
        """
        Push branch to remote with retry logic.

        Args:
            branch_name: Name of the branch to push
            max_retries: Maximum number of retry attempts

        Returns:
            Tuple of (success, error_message)
        """
        import time

        retry_delays = [2, 4, 8, 16]  # Exponential backoff

        for attempt in range(max_retries):
            try:
                subprocess.run(
                    ['git', 'push', '-u', 'origin', branch_name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30
                )

                logger.info(f"Successfully pushed branch: {branch_name}")
                return True, None

            except subprocess.TimeoutExpired:
                error_msg = "Push timed out"
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(f"Push attempt {attempt + 1} failed, retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"Push failed after {max_retries} attempts")
                    return False, error_msg

            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else str(e)

                # Check if it's a network error (retry) or auth error (don't retry)
                if "403" in error_msg or "authentication" in error_msg.lower():
                    logger.error(f"Authentication failed: {error_msg}")
                    return False, error_msg

                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(f"Push attempt {attempt + 1} failed, retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"Push failed after {max_retries} attempts: {error_msg}")
                    return False, error_msg

        return False, "Max retries exceeded"

    def get_repo_url(self) -> Optional[str]:
        """
        Get the remote repository URL.

        Returns:
            GitHub repository URL or None
        """
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            url = result.stdout.strip()

            # Convert SSH URL to HTTPS
            if url.startswith('git@github.com:'):
                url = url.replace('git@github.com:', 'https://github.com/')

            # Remove .git suffix
            if url.endswith('.git'):
                url = url[:-4]

            return url

        except subprocess.CalledProcessError:
            return None

    def get_branch_url(self, branch_name: str) -> Optional[str]:
        """
        Get the GitHub URL for a specific branch.

        Args:
            branch_name: Name of the branch

        Returns:
            Full GitHub URL to the branch or None
        """
        repo_url = self.get_repo_url()
        if repo_url:
            return f"{repo_url}/tree/{branch_name}"
        return None

    def has_uncommitted_changes(self) -> bool:
        """Check if there are any uncommitted changes."""
        changed_files = self.get_changed_files()
        return len(changed_files) > 0
