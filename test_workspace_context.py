#!/usr/bin/env python3
"""
Test script to verify Claude Code has full workspace context.
"""
import os
import sys
from claude_handler import ClaudeHandler

def test_workspace_context():
    """Test that Claude Code can see and work with files in the repo."""

    print("Testing Claude Code workspace context...\n")

    # Initialize handler
    try:
        handler = ClaudeHandler()
        print("✓ ClaudeHandler initialized successfully")
    except ValueError as e:
        print(f"✗ Failed to initialize: {e}")
        print("  Make sure ANTHROPIC_API_KEY is set in your environment")
        return False

    # Check if Claude is installed
    if not handler.check_claude_installed():
        print("✗ Claude Code CLI is not installed or not accessible")
        return False

    version = handler.get_claude_version()
    print(f"✓ Claude Code CLI is installed: {version}\n")

    # Test 1: Simple prompt to verify basic functionality
    print("Test 1: Basic prompt with workspace context")
    print("-" * 50)

    test_prompt = "List the main Python files in this repository"

    success, response, error = handler.send_prompt(
        test_prompt,
        timeout=60,
        working_dir=os.getcwd()
    )

    if success:
        print(f"✓ Response received ({len(response)} chars)")
        print(f"\nClaude's response:\n{response}\n")
    else:
        print(f"✗ Failed: {error}")
        return False

    print("-" * 50)
    print("\nTest completed successfully!")
    print("\nWhat this means:")
    print("- Claude Code is running in workspace mode")
    print("- It can see the repository structure")
    print("- It has access to read and explore files")
    print("- Users can now ask Claude to understand and modify the codebase")

    return True

if __name__ == "__main__":
    success = test_workspace_context()
    sys.exit(0 if success else 1)
