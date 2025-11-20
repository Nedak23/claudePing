"""
Response storage module for saving and retrieving Claude Code responses.
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any


class ResponseStorage:
    """Handles storage and retrieval of Claude Code responses."""

    def __init__(self, storage_dir: str = "responses"):
        """
        Initialize the response storage.

        Args:
            storage_dir: Directory to store response files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def generate_id(self) -> str:
        """Generate a unique ID for a response based on timestamp."""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    def save_response(self,
                     response_text: str,
                     phone_number: str,
                     prompt: str,
                     branch_name: Optional[str] = None,
                     files_changed: Optional[list] = None) -> str:
        """
        Save a Claude Code response to storage.

        Args:
            response_text: The full response from Claude Code
            phone_number: The user's phone number
            prompt: The original prompt sent by user
            branch_name: Git branch name if applicable
            files_changed: List of files modified

        Returns:
            Unique ID for the saved response
        """
        response_id = self.generate_id()

        data = {
            "id": response_id,
            "timestamp": datetime.now().isoformat(),
            "phone_number": phone_number,
            "prompt": prompt,
            "response": response_text,
            "branch_name": branch_name,
            "files_changed": files_changed or []
        }

        file_path = os.path.join(self.storage_dir, f"{response_id}.json")

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        return response_id

    def get_response(self, response_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a response by ID.

        Args:
            response_id: The unique response ID

        Returns:
            Response data dictionary or None if not found
        """
        file_path = os.path.join(self.storage_dir, f"{response_id}.json")

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            return json.load(f)

    def list_responses(self, phone_number: Optional[str] = None, limit: int = 10) -> list:
        """
        List recent responses, optionally filtered by phone number.

        Args:
            phone_number: Filter by phone number (optional)
            limit: Maximum number of responses to return

        Returns:
            List of response summaries
        """
        responses = []

        # Get all response files
        files = sorted(
            [f for f in os.listdir(self.storage_dir) if f.endswith('.json')],
            reverse=True
        )

        for filename in files[:limit * 2]:  # Read more to filter
            file_path = os.path.join(self.storage_dir, filename)

            with open(file_path, 'r') as f:
                data = json.load(f)

            # Filter by phone number if specified
            if phone_number and data.get('phone_number') != phone_number:
                continue

            responses.append({
                'id': data['id'],
                'timestamp': data['timestamp'],
                'prompt': data['prompt'][:50] + '...' if len(data['prompt']) > 50 else data['prompt'],
                'branch_name': data.get('branch_name')
            })

            if len(responses) >= limit:
                break

        return responses


class SessionStorage:
    """Handles storage of conversation sessions."""

    def __init__(self, storage_dir: str = "sessions"):
        """
        Initialize the session storage.

        Args:
            storage_dir: Directory to store session files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def get_session_file(self, phone_number: str) -> str:
        """Get the session file path for a phone number."""
        # Sanitize phone number for filename (handle WhatsApp format)
        safe_number = phone_number.replace('whatsapp:', '').replace('+', '').replace('-', '').replace(':', '')
        return os.path.join(self.storage_dir, f"{safe_number}.json")

    def get_session(self, phone_number: str) -> Dict[str, Any]:
        """
        Get the current session for a phone number.

        Args:
            phone_number: The user's phone number

        Returns:
            Session data dictionary
        """
        session_file = self.get_session_file(phone_number)

        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                return json.load(f)

        # Create new session
        return {
            "phone_number": phone_number,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "conversation_history": [],
            "current_branch": None,
            "active_repository": None
        }

    def update_session(self,
                      phone_number: str,
                      prompt: str,
                      response: str,
                      branch_name: Optional[str] = None):
        """
        Update session with new conversation entry.

        Args:
            phone_number: The user's phone number
            prompt: User's prompt
            response: Claude's response
            branch_name: Current branch name if applicable
        """
        session = self.get_session(phone_number)

        session["last_activity"] = datetime.now().isoformat()
        session["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response[:200]  # Store truncated for session tracking
        })

        if branch_name:
            session["current_branch"] = branch_name

        # Keep only last 20 messages
        session["conversation_history"] = session["conversation_history"][-20:]

        session_file = self.get_session_file(phone_number)
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)

    def clear_session(self, phone_number: str):
        """
        Clear/reset a user's session.

        Args:
            phone_number: The user's phone number
        """
        session_file = self.get_session_file(phone_number)
        if os.path.exists(session_file):
            os.remove(session_file)
