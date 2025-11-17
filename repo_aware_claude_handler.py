"""
Repository-aware Claude Code CLI handler.
"""
import os
import subprocess
import logging
from typing import Tuple, Optional

from claude_handler import ClaudeHandler
from repository_manager import Repository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RepoAwareClaudeHandler(ClaudeHandler):
    """
    Enhanced ClaudeHandler that can execute in specific repository contexts.

    Extends the base ClaudeHandler to support multi-repository operations
    by changing working directory during execution.
    """

    def send_prompt_to_repo(self,
                           prompt: str,
                           repository: Repository,
                           timeout: int = 120) -> Tuple[bool, str, Optional[str]]:
        """
        Execute Claude Code CLI in a specific repository.

        Args:
            prompt: User's coding request
            repository: Target repository object
            timeout: Execution timeout in seconds

        Returns:
            Tuple of (success, response, error)
        """
        if not repository.is_valid:
            error_msg = f"Repository '{repository.name}' is not valid or not accessible"
            logger.error(error_msg)
            return False, "", error_msg

        original_cwd = os.getcwd()

        try:
            # Change to repository directory
            os.chdir(repository.path)
            logger.info(f"Executing Claude in repository: {repository.name} at {repository.path}")

            # Execute Claude Code CLI
            result = subprocess.run(
                ['claude', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self._prepare_env()
            )

            if result.returncode == 0:
                response = result.stdout.strip()
                logger.info(f"Claude response received for {repository.name} ({len(response)} chars)")
                return True, response, None
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"Claude command failed in {repository.name}: {error_msg}")
                return False, "", error_msg

        except subprocess.TimeoutExpired:
            error_msg = f"Request timed out after {timeout} seconds"
            logger.error(f"Claude command timed out in {repository.name}")
            return False, "", error_msg

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error running Claude in {repository.name}: {error_msg}")
            return False, "", error_msg

        finally:
            # Always restore original directory
            os.chdir(original_cwd)
            logger.debug(f"Restored working directory to {original_cwd}")

    def send_prompt_to_repo_path(self,
                                 prompt: str,
                                 repo_path: str,
                                 repo_name: str = None,
                                 timeout: int = 120) -> Tuple[bool, str, Optional[str]]:
        """
        Execute Claude Code CLI in a specific repository path.

        Convenience method for when you have a path but not a Repository object.

        Args:
            prompt: User's coding request
            repo_path: Path to repository
            repo_name: Optional repository name for logging
            timeout: Execution timeout in seconds

        Returns:
            Tuple of (success, response, error)
        """
        # Validate path
        if not os.path.exists(repo_path):
            return False, "", f"Repository path does not exist: {repo_path}"

        git_dir = os.path.join(repo_path, '.git')
        if not os.path.isdir(git_dir):
            return False, "", f"Path is not a git repository: {repo_path}"

        original_cwd = os.getcwd()
        display_name = repo_name or repo_path

        try:
            # Change to repository directory
            os.chdir(repo_path)
            logger.info(f"Executing Claude in repository: {display_name}")

            # Execute Claude Code CLI
            result = subprocess.run(
                ['claude', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self._prepare_env()
            )

            if result.returncode == 0:
                response = result.stdout.strip()
                logger.info(f"Claude response received for {display_name} ({len(response)} chars)")
                return True, response, None
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"Claude command failed in {display_name}: {error_msg}")
                return False, "", error_msg

        except subprocess.TimeoutExpired:
            error_msg = f"Request timed out after {timeout} seconds"
            logger.error(f"Claude command timed out in {display_name}")
            return False, "", error_msg

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error running Claude in {display_name}: {error_msg}")
            return False, "", error_msg

        finally:
            # Always restore original directory
            os.chdir(original_cwd)

    def _prepare_env(self) -> dict:
        """
        Prepare environment variables for Claude execution.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # Ensure API key is set
        if self.api_key:
            env['ANTHROPIC_API_KEY'] = self.api_key

        return env

    def get_execution_context(self, repository: Repository) -> dict:
        """
        Get execution context information for a repository.

        Args:
            repository: Repository object

        Returns:
            Dictionary with execution context
        """
        return {
            'repository_name': repository.name,
            'repository_path': repository.path,
            'repository_url': repository.remote_url,
            'working_directory': repository.path,
            'is_valid': repository.is_valid
        }
