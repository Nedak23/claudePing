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

            # Build enhanced prompt with repository context
            enhanced_prompt = self._build_repo_aware_prompt(prompt, repository)

            # Execute Claude Code CLI with full workspace context
            result = subprocess.run(
                ['claude', '-p', enhanced_prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=repository.path,  # Explicitly set working directory
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

    def _build_repo_aware_prompt(self, user_prompt: str, repository: Repository) -> str:
        """
        Build an enhanced prompt with repository-specific context.

        Args:
            user_prompt: The user's original prompt
            repository: Repository object with metadata

        Returns:
            Enhanced prompt with repository context
        """
        context_parts = []

        context_parts.append(f"You are working in the '{repository.name}' repository.")
        context_parts.append(f"Repository path: {repository.path}")

        if repository.description:
            context_parts.append(f"Repository description: {repository.description}")

        context_parts.append("\nYou have full access to:")
        context_parts.append("- Read any file in this codebase using your file reading tools")
        context_parts.append("- Search for code patterns using grep/search tools")
        context_parts.append("- Explore the directory structure")
        context_parts.append("- Edit and create files as needed")
        context_parts.append("\nIMPORTANT: Before making changes, use your tools to explore the codebase and understand the existing structure.")

        context_parts.append("\nUser request:")
        context_parts.append(user_prompt)

        return "\n".join(context_parts)

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
