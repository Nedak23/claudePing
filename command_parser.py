"""
Command parser for detecting repository-related intents.
"""
import re
from dataclasses import dataclass
from typing import Optional, Tuple, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CommandIntent:
    """Represents parsed command intent."""

    type: str  # 'switch_repo', 'inline_repo', 'list_repos', 'repo_info', 'repo_status', 'coding_request'
    repository: Optional[str] = None
    prompt: Optional[str] = None
    parameters: Optional[dict] = None

    def __post_init__(self):
        """Initialize parameters dict if not provided."""
        if self.parameters is None:
            self.parameters = {}


class CommandParser:
    """
    Parses user messages to detect repository-related commands.

    Supports natural language patterns for:
    - Switching repositories
    - Inline repository targeting
    - Repository management commands
    - Regular coding requests
    """

    # Pattern groups for different command types
    SWITCH_PATTERNS = [
        r'^switch to ([a-zA-Z0-9_-]+)$',
        r'^use ([a-zA-Z0-9_-]+)$',
        r'^go to ([a-zA-Z0-9_-]+)$',
        r'^work on ([a-zA-Z0-9_-]+)$',
        r'^change to ([a-zA-Z0-9_-]+)$',
    ]

    INLINE_REPO_PATTERNS = [
        r'^in ([a-zA-Z0-9_-]+):?\s*(.+)$',      # "in project-api: add feature"
        r'^for ([a-zA-Z0-9_-]+):?\s*(.+)$',     # "for web-app: fix bug"
        r'^@([a-zA-Z0-9_-]+):?\s*(.+)$',        # "@api: add endpoint"
        r'^on ([a-zA-Z0-9_-]+):?\s*(.+)$',      # "on frontend: update styles"
    ]

    LIST_REPO_PATTERNS = [
        r'^list repos?$',
        r'^show repos?$',
        r'^list repositories$',
        r'^show repositories$',
        r'^what repos?$',
        r'^my repos?$',
        r'^repos?$',
    ]

    REPO_INFO_PATTERNS = [
        r'^info\s+([a-zA-Z0-9_-]+)$',
        r'^show\s+([a-zA-Z0-9_-]+)$',
        r'^describe\s+([a-zA-Z0-9_-]+)$',
        r'^details?\s+([a-zA-Z0-9_-]+)$',
    ]

    REPO_STATUS_PATTERNS = [
        r'^repos? status$',
        r'^status all$',
        r'^all status$',
    ]

    def __init__(self):
        """Initialize the command parser."""
        # Compile regex patterns for efficiency
        self.switch_regex = [re.compile(p, re.IGNORECASE) for p in self.SWITCH_PATTERNS]
        self.inline_regex = [re.compile(p, re.IGNORECASE) for p in self.INLINE_REPO_PATTERNS]
        self.list_regex = [re.compile(p, re.IGNORECASE) for p in self.LIST_REPO_PATTERNS]
        self.info_regex = [re.compile(p, re.IGNORECASE) for p in self.REPO_INFO_PATTERNS]
        self.status_regex = [re.compile(p, re.IGNORECASE) for p in self.REPO_STATUS_PATTERNS]

    def parse(self, message: str) -> CommandIntent:
        """
        Parse message and return command intent.

        Args:
            message: User's message

        Returns:
            CommandIntent object
        """
        message = message.strip()

        # Try to match switch repository commands
        for pattern in self.switch_regex:
            match = pattern.match(message)
            if match:
                repo_name = match.group(1)
                logger.info(f"Detected switch repo command: {repo_name}")
                return CommandIntent(
                    type='switch_repo',
                    repository=repo_name,
                    prompt=None
                )

        # Try to match inline repository targeting
        for pattern in self.inline_regex:
            match = pattern.match(message)
            if match:
                repo_name = match.group(1)
                prompt = match.group(2).strip()
                logger.info(f"Detected inline repo command: {repo_name} - {prompt[:50]}")
                return CommandIntent(
                    type='inline_repo',
                    repository=repo_name,
                    prompt=prompt
                )

        # Try to match list repos commands
        for pattern in self.list_regex:
            if pattern.match(message):
                logger.info("Detected list repos command")
                return CommandIntent(
                    type='list_repos',
                    repository=None,
                    prompt=None
                )

        # Try to match repo info commands
        for pattern in self.info_regex:
            match = pattern.match(message)
            if match:
                repo_name = match.group(1)
                logger.info(f"Detected repo info command: {repo_name}")
                return CommandIntent(
                    type='repo_info',
                    repository=repo_name,
                    prompt=None
                )

        # Try to match repo status commands
        for pattern in self.status_regex:
            if pattern.match(message):
                logger.info("Detected repo status command")
                return CommandIntent(
                    type='repo_status',
                    repository=None,
                    prompt=None
                )

        # Default: treat as coding request (will use active repository)
        logger.info(f"Detected coding request: {message[:50]}")
        return CommandIntent(
            type='coding_request',
            repository=None,
            prompt=message
        )
