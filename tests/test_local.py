"""
Local testing utility for Text-Based Coding Companion.
Test functionality without needing SMS/Twilio.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from claude_handler import ClaudeHandler, SessionManager
from git_handler import GitHandler
from storage import ResponseStorage, SessionStorage
from summary_generator import SummaryGenerator

# Load environment variables
load_dotenv()


def test_storage():
    """Test response and session storage."""
    print("\n=== Testing Storage ===")

    # Test response storage
    response_storage = ResponseStorage()

    response_id = response_storage.save_response(
        response_text="This is a test response from Claude Code.",
        phone_number="+1234567890",
        prompt="Create a test function",
        branch_name="sms/test_20231115",
        files_changed=["test.py"]
    )

    print(f"✓ Saved response with ID: {response_id}")

    # Retrieve response
    retrieved = response_storage.get_response(response_id)
    print(f"✓ Retrieved response: {retrieved['prompt'][:30]}...")

    # Test session storage
    session_storage = SessionStorage()

    session_storage.update_session(
        phone_number="+1234567890",
        prompt="Test prompt",
        response="Test response",
        branch_name="sms/test_branch"
    )

    session = session_storage.get_session("+1234567890")
    print(f"✓ Session created with {len(session['conversation_history'])} messages")

    print("✓ Storage tests passed!\n")


def test_git():
    """Test Git operations."""
    print("\n=== Testing Git Operations ===")

    git_handler = GitHandler()

    # Check if git repo
    is_repo = git_handler.is_git_repo()
    print(f"Git repository detected: {is_repo}")

    if is_repo:
        current_branch = git_handler.get_current_branch()
        print(f"✓ Current branch: {current_branch}")

        # Get changed files (if any)
        changed_files = git_handler.get_changed_files()
        print(f"✓ Changed files: {len(changed_files)} file(s)")

        # Get repo URL
        repo_url = git_handler.get_repo_url()
        print(f"✓ Repository URL: {repo_url}")
    else:
        print("⚠ Not a git repository - some tests skipped")

    print("✓ Git tests passed!\n")


def test_summary_generator():
    """Test summary generation."""
    print("\n=== Testing Summary Generator ===")

    summary_gen = SummaryGenerator()

    # Test summary generation
    response = """
    I've created a Python function to calculate Fibonacci numbers using memoization.
    This approach is efficient for computing Fibonacci sequences. Here's the implementation:

    def fibonacci(n, memo={}):
        if n in memo:
            return memo[n]
        if n <= 1:
            return n
        memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
        return memo[n]
    """

    summary = summary_gen.generate_summary(
        response=response,
        branch_name="sms/20231115_143022",
        files_changed=["fibonacci.py"],
        response_id="test123",
        base_url="http://localhost:5000"
    )

    print(f"Summary: {summary}")
    print(f"✓ Summary length: {len(summary)} characters")

    # Test status summary
    status = summary_gen.generate_status_summary(
        current_branch="sms/20231115_143022",
        session_active=True,
        message_count=5
    )

    print(f"Status: {status}")

    # Test message splitting
    long_message = "This is a very long message. " * 20
    chunks = summary_gen.split_long_message(long_message, max_length=160)
    print(f"✓ Split long message into {len(chunks)} chunks")

    print("✓ Summary generator tests passed!\n")


def test_claude_installed():
    """Test if Claude Code CLI is installed."""
    print("\n=== Testing Claude Code CLI ===")

    try:
        claude_handler = ClaudeHandler()
        is_installed = claude_handler.check_claude_installed()

        if is_installed:
            version = claude_handler.get_claude_version()
            print(f"✓ Claude Code CLI is installed: {version}")
        else:
            print("⚠ Claude Code CLI not detected")
            print("  Install from: https://docs.anthropic.com")

    except ValueError as e:
        print(f"⚠ {str(e)}")
        print("  Please set ANTHROPIC_API_KEY in .env file")

    print()


def interactive_test():
    """Interactive test mode - send actual prompts to Claude."""
    print("\n=== Interactive Test Mode ===")
    print("This will send actual requests to Claude Code CLI")
    print("Make sure you have set up your .env file with ANTHROPIC_API_KEY")
    print()

    try:
        # Initialize components
        claude_handler = ClaudeHandler()
        session_manager = SessionManager(claude_handler)
        git_handler = GitHandler()
        response_storage = ResponseStorage()
        session_storage = SessionStorage()
        summary_gen = SummaryGenerator()

        test_phone = "+1234567890"

        while True:
            prompt = input("\nEnter prompt (or 'quit' to exit): ").strip()

            if prompt.lower() in ['quit', 'exit', 'q']:
                print("Exiting interactive mode")
                break

            if not prompt:
                continue

            print("\nSending to Claude Code...")

            # Send to Claude
            success, response, error = session_manager.send_message(
                test_phone,
                prompt,
                timeout=120
            )

            if not success:
                print(f"Error: {error}")
                continue

            print(f"\nFull Response:\n{response}\n")

            # Check for file changes
            files_changed = []
            branch_name = None

            if git_handler.is_git_repo():
                files_changed = git_handler.get_changed_files()
                print(f"Files changed: {len(files_changed)}")

            # Generate summary
            response_id = response_storage.save_response(
                response_text=response,
                phone_number=test_phone,
                prompt=prompt,
                branch_name=branch_name,
                files_changed=files_changed
            )

            summary = summary_gen.generate_summary(
                response=response,
                branch_name=branch_name,
                files_changed=files_changed,
                response_id=response_id,
                base_url="http://localhost:5000"
            )

            print(f"\nSMS Summary:\n{summary}\n")
            print(f"Response saved with ID: {response_id}")

    except Exception as e:
        print(f"Error in interactive mode: {str(e)}")


def main():
    """Main test runner."""
    print("=" * 60)
    print("Text-Based Coding Companion - Local Test Suite")
    print("=" * 60)

    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n⚠ Warning: .env file not found")
        print("  Copy .env.example to .env and configure your settings")
        print()

    # Run tests
    try:
        test_storage()
        test_git()
        test_summary_generator()
        test_claude_installed()

        print("\n" + "=" * 60)
        print("All basic tests completed!")
        print("=" * 60)

        # Ask if user wants interactive mode
        response = input("\nRun interactive test mode? (y/n): ").strip().lower()
        if response == 'y':
            interactive_test()

    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
