"""
Response summary generator for SMS messages.
"""
import re
from typing import List, Optional


class SummaryGenerator:
    """Generates concise summaries of Claude Code responses for SMS."""

    def __init__(self, max_length: int = 150):
        """
        Initialize the summary generator.

        Args:
            max_length: Maximum length of summary (default 150 for SMS with some buffer)
        """
        self.max_length = max_length

    def generate_summary(self,
                        response: str,
                        branch_name: Optional[str] = None,
                        files_changed: Optional[List[str]] = None,
                        response_id: Optional[str] = None,
                        base_url: Optional[str] = None) -> str:
        """
        Generate a concise summary of a Claude response for SMS.

        Args:
            response: Full Claude response text
            branch_name: Git branch name if applicable
            files_changed: List of files that were modified
            response_id: ID for retrieving full response
            base_url: Base URL for full response link

        Returns:
            Concise summary string suitable for SMS
        """
        # Extract key information
        summary_parts = []

        # Add completion indicator
        if self._response_indicates_completion(response):
            summary_parts.append("✓ Done!")
        else:
            summary_parts.append("Response:")

        # Add file change info
        if files_changed and len(files_changed) > 0:
            file_count = len(files_changed)
            summary_parts.append(f"Modified {file_count} file{'s' if file_count != 1 else ''}")

        # Add branch info
        if branch_name:
            # Shorten branch name if needed
            short_branch = self._shorten_branch_name(branch_name)
            summary_parts.append(f"Branch: {short_branch}")

        # Create base summary
        base_summary = ". ".join(summary_parts) + "."

        # Extract key content from response
        content_summary = self._extract_key_content(response)

        # Combine
        full_summary = f"{base_summary} {content_summary}"

        # Add link to full response if available
        if response_id and base_url:
            link = f"{base_url}/response/{response_id}"
            full_summary += f" Full: {link}"

        # Truncate if needed
        if len(full_summary) > self.max_length:
            truncate_at = self.max_length - 3
            full_summary = full_summary[:truncate_at] + "..."

        return full_summary

    def _response_indicates_completion(self, response: str) -> bool:
        """
        Check if response indicates task completion.

        Args:
            response: Claude response text

        Returns:
            True if response indicates completion
        """
        completion_indicators = [
            r'\bdone\b',
            r'\bcompleted\b',
            r'\bfinished\b',
            r'\bsuccess',
            r'\bcreated\b',
            r'\badded\b',
            r'\bupdated\b',
            r'\bfixed\b',
        ]

        response_lower = response.lower()
        for pattern in completion_indicators:
            if re.search(pattern, response_lower):
                return True

        return False

    def _extract_key_content(self, response: str, max_words: int = 15) -> str:
        """
        Extract key content from response.

        Args:
            response: Full response text
            max_words: Maximum number of words to include

        Returns:
            Extracted summary
        """
        # Remove code blocks
        response = re.sub(r'```[\s\S]*?```', '[code]', response)

        # Remove excessive whitespace
        response = re.sub(r'\s+', ' ', response)

        # Try to find the first meaningful sentence
        sentences = re.split(r'[.!?]+', response)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Meaningful sentence
                words = sentence.split()[:max_words]
                summary = ' '.join(words)
                if len(words) >= max_words:
                    summary += "..."
                return summary

        # Fallback: just take first N words
        words = response.split()[:max_words]
        summary = ' '.join(words)
        if len(response.split()) > max_words:
            summary += "..."

        return summary

    def _shorten_branch_name(self, branch_name: str, max_length: int = 20) -> str:
        """
        Shorten branch name for display.

        Args:
            branch_name: Full branch name
            max_length: Maximum length

        Returns:
            Shortened branch name
        """
        if len(branch_name) <= max_length:
            return branch_name

        # Try to keep the meaningful part
        # For format like "sms/20231115_123456"
        parts = branch_name.split('/')
        if len(parts) > 1:
            # Keep prefix and shorten timestamp
            prefix = parts[0]
            suffix = parts[-1]
            if len(suffix) > 10:
                suffix = suffix[-8:]  # Last 8 chars of timestamp
            return f"{prefix}/{suffix}"

        # Fallback: just truncate
        return branch_name[:max_length-3] + "..."

    def generate_status_summary(self,
                               current_branch: Optional[str] = None,
                               session_active: bool = False,
                               message_count: int = 0) -> str:
        """
        Generate a status summary for the STATUS command.

        Args:
            current_branch: Current Git branch
            session_active: Whether session is active
            message_count: Number of messages in session

        Returns:
            Status summary string
        """
        parts = []

        if session_active:
            parts.append(f"Session active ({message_count} msgs)")
        else:
            parts.append("No active session")

        if current_branch:
            short_branch = self._shorten_branch_name(current_branch)
            parts.append(f"Branch: {short_branch}")

        return ". ".join(parts) + "."

    def split_long_message(self, message: str, max_length: int = 160) -> List[str]:
        """
        Split a long message into multiple SMS-sized chunks.

        Args:
            message: Message to split
            max_length: Maximum length per chunk

        Returns:
            List of message chunks
        """
        if len(message) <= max_length:
            return [message]

        chunks = []
        words = message.split()
        current_chunk = ""

        for word in words:
            if len(current_chunk) + len(word) + 1 <= max_length:
                if current_chunk:
                    current_chunk += " "
                current_chunk += word
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = word

        if current_chunk:
            chunks.append(current_chunk)

        # Add part indicators if multiple chunks
        if len(chunks) > 1:
            chunks = [f"({i+1}/{len(chunks)}) {chunk}" for i, chunk in enumerate(chunks)]

        return chunks
