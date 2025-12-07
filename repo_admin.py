#!/usr/bin/env python3
"""
Repository Administration CLI Tool

Command-line interface for managing ClaudePing repositories.
Provides easy commands for registering, listing, and managing repositories
without manual JSON editing.
"""
import argparse
import os
import sys
import json
from typing import List, Optional

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # Define dummy color constants if colorama not available
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = ""
    class Style:
        BRIGHT = RESET_ALL = ""

from repository_manager import RepositoryManager, Repository


def print_success(message: str):
    """Print success message in green."""
    if HAS_COLOR:
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    else:
        print(f"✓ {message}")


def print_error(message: str):
    """Print error message in red."""
    if HAS_COLOR:
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", file=sys.stderr)
    else:
        print(f"✗ {message}", file=sys.stderr)


def print_warning(message: str):
    """Print warning message in yellow."""
    if HAS_COLOR:
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    else:
        print(f"⚠ {message}")


def print_info(message: str):
    """Print info message in blue."""
    if HAS_COLOR:
        print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")
    else:
        print(message)


def print_header(text: str):
    """Print a header."""
    if HAS_COLOR:
        print(f"\n{Style.BRIGHT}{Fore.WHITE}{text}{Style.RESET_ALL}")
    else:
        print(f"\n{text}")
    print("=" * len(text))


def confirm(prompt: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.

    Args:
        prompt: Confirmation prompt
        default: Default answer if user presses enter

    Returns:
        True if user confirms, False otherwise
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()

    if not response:
        return default

    return response in ['y', 'yes']


def get_git_remote_url(repo_path: str) -> Optional[str]:
    """
    Extract remote URL from git config.

    Args:
        repo_path: Path to repository

    Returns:
        Remote URL or None
    """
    git_config = os.path.join(repo_path, '.git', 'config')

    if not os.path.exists(git_config):
        return None

    try:
        with open(git_config, 'r') as f:
            lines = f.readlines()

        # Look for [remote "origin"] section
        in_origin = False
        for line in lines:
            line = line.strip()
            if line == '[remote "origin"]':
                in_origin = True
            elif in_origin and line.startswith('url ='):
                return line.split('=', 1)[1].strip()
            elif in_origin and line.startswith('['):
                # New section, origin didn't have URL
                break

    except Exception:
        pass

    return None


class RegisterCommand:
    """Handle repository registration."""

    @staticmethod
    def add_parser(subparsers):
        """Add register command parser."""
        parser = subparsers.add_parser(
            'register',
            help='Register a new repository',
            description='Register a new repository with ClaudePing'
        )
        parser.add_argument('name', help='Repository name (unique identifier)')
        parser.add_argument('path', help='Absolute path to repository')
        parser.add_argument('--remote-url', help='Git remote URL (auto-detected if not provided)')
        parser.add_argument('--description', default='', help='Repository description')
        parser.add_argument('--admin-phone', help='Admin phone number (e.g., +1234567890)')
        parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
        parser.set_defaults(func=RegisterCommand.execute)

    @staticmethod
    def execute(args, manager: RepositoryManager):
        """Execute register command."""
        # Convert to absolute path
        path = os.path.abspath(os.path.expanduser(args.path))

        # Validate path exists
        if not os.path.exists(path):
            print_error(f"Path does not exist: {path}")
            return 1

        # Check if it's a git repository
        git_dir = os.path.join(path, '.git')
        if not os.path.isdir(git_dir):
            print_error(f"Not a git repository: {path}")
            print_info("Hint: Initialize with 'git init' first")
            return 1

        # Auto-detect remote URL if not provided
        remote_url = args.remote_url
        if not remote_url:
            remote_url = get_git_remote_url(path)
            if remote_url:
                print_info(f"Auto-detected remote URL: {remote_url}")

        # Build access control
        access_control = {}
        if args.admin_phone:
            access_control[args.admin_phone] = ['admin']

        # Show preview
        print_header("Repository Registration")
        print(f"Name:        {args.name}")
        print(f"Path:        {path}")
        print(f"Remote URL:  {remote_url or '(none)'}")
        print(f"Description: {args.description or '(none)'}")
        if access_control:
            print(f"Admin:       {args.admin_phone}")

        if args.dry_run:
            print_warning("\nDry run - no changes made")
            return 0

        # Confirm
        if not confirm("\nProceed with registration?", default=True):
            print_info("Cancelled")
            return 0

        # Register repository
        success, message = manager.register_repository(
            name=args.name,
            path=path,
            remote_url=remote_url,
            description=args.description,
            access_control=access_control
        )

        if success:
            print_success(message)
            if len(manager.repositories) == 1:
                print_info(f"Set as default repository")
            return 0
        else:
            print_error(message)
            return 1


class ListCommand:
    """Handle repository listing."""

    @staticmethod
    def add_parser(subparsers):
        """Add list command parser."""
        parser = subparsers.add_parser(
            'list',
            help='List all registered repositories',
            description='Display all registered repositories'
        )
        parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
        parser.set_defaults(func=ListCommand.execute)

    @staticmethod
    def execute(args, manager: RepositoryManager):
        """Execute list command."""
        repos = manager.list_repositories()

        if not repos:
            print_warning("No repositories registered")
            print_info("Use 'repo_admin.py register' to add a repository")
            return 0

        print_header(f"Registered Repositories ({len(repos)})")

        for repo in repos:
            is_default = repo.name == manager.default_repository

            # Repository name with default marker
            name_display = f"{repo.name}"
            if is_default:
                if HAS_COLOR:
                    name_display = f"{Style.BRIGHT}{Fore.GREEN}{repo.name} (default){Style.RESET_ALL}"
                else:
                    name_display = f"{repo.name} (default)"
            else:
                if HAS_COLOR:
                    name_display = f"{Style.BRIGHT}{repo.name}{Style.RESET_ALL}"

            print(f"\n{name_display}")
            print(f"  Path:   {repo.path}")

            if repo.remote_url:
                print(f"  Remote: {repo.remote_url}")

            if args.verbose:
                if repo.description:
                    print(f"  Description: {repo.description}")

                # Show access control
                if repo.access_control:
                    print(f"  Access Control:")
                    for phone, perms in repo.access_control.items():
                        perms_str = ', '.join(perms)
                        print(f"    {phone}: {perms_str}")

                # Show validity
                valid_str = "✓ valid" if repo.is_valid else "✗ invalid"
                if HAS_COLOR:
                    color = Fore.GREEN if repo.is_valid else Fore.RED
                    print(f"  Status: {color}{valid_str}{Style.RESET_ALL}")
                else:
                    print(f"  Status: {valid_str}")

        print()  # Empty line at end
        return 0


class UnregisterCommand:
    """Handle repository unregistration."""

    @staticmethod
    def add_parser(subparsers):
        """Add unregister command parser."""
        parser = subparsers.add_parser(
            'unregister',
            help='Unregister a repository',
            description='Remove a repository from ClaudePing'
        )
        parser.add_argument('name', help='Repository name to unregister')
        parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation')
        parser.set_defaults(func=UnregisterCommand.execute)

    @staticmethod
    def execute(args, manager: RepositoryManager):
        """Execute unregister command."""
        # Check if repository exists
        if args.name not in manager.repositories:
            print_error(f"Repository '{args.name}' not found")
            return 1

        repo = manager.repositories[args.name]

        # Show what will be removed
        print_header("Unregister Repository")
        print(f"Name: {args.name}")
        print(f"Path: {repo.path}")

        if args.name == manager.default_repository:
            print_warning("This is the default repository!")
            if len(manager.repositories) > 1:
                print_info("Another repository will become the default")

        # Confirm unless --force
        if not args.force:
            if not confirm("\nAre you sure you want to unregister this repository?", default=False):
                print_info("Cancelled")
                return 0

        # Unregister
        success, message = manager.unregister_repository(args.name)

        if success:
            print_success(message)
            return 0
        else:
            print_error(message)
            return 1


class DiscoverCommand:
    """Handle repository discovery."""

    @staticmethod
    def add_parser(subparsers):
        """Add discover command parser."""
        parser = subparsers.add_parser(
            'discover',
            help='Auto-discover git repositories',
            description='Recursively search for git repositories in a directory'
        )
        parser.add_argument('path', help='Directory to search')
        parser.add_argument('--max-depth', type=int, default=3, help='Maximum search depth (default: 3)')
        parser.add_argument('--auto-register', action='store_true', help='Automatically register found repos')
        parser.add_argument('--admin-phone', help='Admin phone for auto-registered repos')
        parser.set_defaults(func=DiscoverCommand.execute)

    @staticmethod
    def execute(args, manager: RepositoryManager):
        """Execute discover command."""
        search_path = os.path.abspath(os.path.expanduser(args.path))

        if not os.path.exists(search_path):
            print_error(f"Path does not exist: {search_path}")
            return 1

        if not os.path.isdir(search_path):
            print_error(f"Not a directory: {search_path}")
            return 1

        print_info(f"Discovering repositories in: {search_path}")
        print_info(f"Maximum depth: {args.max_depth}")

        # Discover repositories
        discovered = manager.discover_repositories(search_path, args.max_depth)

        if not discovered:
            print_warning("No git repositories found")
            return 0

        print_header(f"Discovered Repositories ({len(discovered)})")

        # Show discovered repos
        for path in discovered:
            # Generate a name from the directory
            name = os.path.basename(path)

            # Check if already registered
            already_registered = any(
                repo.path == path for repo in manager.repositories.values()
            )

            status = "(already registered)" if already_registered else ""
            print(f"  {name:30} {path} {status}")

        # Auto-register if requested
        if args.auto_register:
            print()
            registered = 0
            skipped = 0

            for path in discovered:
                name = os.path.basename(path)

                # Skip if already registered
                if any(repo.path == path for repo in manager.repositories.values()):
                    skipped += 1
                    continue

                # Build access control
                access_control = {}
                if args.admin_phone:
                    access_control[args.admin_phone] = ['admin']

                # Register
                remote_url = get_git_remote_url(path)
                success, message = manager.register_repository(
                    name=name,
                    path=path,
                    remote_url=remote_url,
                    access_control=access_control
                )

                if success:
                    print_success(f"Registered: {name}")
                    registered += 1
                else:
                    print_error(f"Failed to register {name}: {message}")

            print()
            print_info(f"Registered: {registered}, Skipped: {skipped}")

        return 0


class GrantCommand:
    """Handle access granting."""

    @staticmethod
    def add_parser(subparsers):
        """Add grant command parser."""
        parser = subparsers.add_parser(
            'grant',
            help='Grant user access to repository',
            description='Grant a user access to a repository'
        )
        parser.add_argument('repo', help='Repository name')
        parser.add_argument('phone', help='Phone number (e.g., +1234567890)')
        parser.add_argument('--level', choices=['read', 'write', 'admin'], default='write',
                          help='Access level (default: write)')
        parser.set_defaults(func=GrantCommand.execute)

    @staticmethod
    def execute(args, manager: RepositoryManager):
        """Execute grant command."""
        # Check if repository exists
        if args.repo not in manager.repositories:
            print_error(f"Repository '{args.repo}' not found")
            return 1

        # Grant access
        success, message = manager.grant_access(
            args.repo,
            args.phone,
            [args.level]
        )

        if success:
            print_success(f"Granted {args.level} access to {args.phone} for '{args.repo}'")
            return 0
        else:
            print_error(message)
            return 1


class RevokeCommand:
    """Handle access revocation."""

    @staticmethod
    def add_parser(subparsers):
        """Add revoke command parser."""
        parser = subparsers.add_parser(
            'revoke',
            help='Revoke user access from repository',
            description='Revoke a user\'s access to a repository'
        )
        parser.add_argument('repo', help='Repository name')
        parser.add_argument('phone', help='Phone number')
        parser.set_defaults(func=RevokeCommand.execute)

    @staticmethod
    def execute(args, manager: RepositoryManager):
        """Execute revoke command."""
        # Check if repository exists
        if args.repo not in manager.repositories:
            print_error(f"Repository '{args.repo}' not found")
            return 1

        # Revoke access
        success, message = manager.revoke_access(args.repo, args.phone)

        if success:
            print_success(f"Revoked access for {args.phone} from '{args.repo}'")
            return 0
        else:
            print_error(message)
            return 1


class InfoCommand:
    """Handle repository info display."""

    @staticmethod
    def add_parser(subparsers):
        """Add info command parser."""
        parser = subparsers.add_parser(
            'info',
            help='Show detailed repository information',
            description='Display detailed information about a repository'
        )
        parser.add_argument('repo', help='Repository name')
        parser.set_defaults(func=InfoCommand.execute)

    @staticmethod
    def execute(args, manager: RepositoryManager):
        """Execute info command."""
        # Check if repository exists
        if args.repo not in manager.repositories:
            print_error(f"Repository '{args.repo}' not found")
            return 1

        repo = manager.repositories[args.repo]
        is_default = repo.name == manager.default_repository

        print_header(f"Repository: {args.repo}")

        print(f"Name:         {repo.name}")
        print(f"Path:         {repo.path}")
        print(f"Remote URL:   {repo.remote_url or '(none)'}")
        print(f"Description:  {repo.description or '(none)'}")
        print(f"Default:      {'Yes' if is_default else 'No'}")

        # Validity check
        valid_str = "Valid" if repo.is_valid else "Invalid"
        if HAS_COLOR:
            color = Fore.GREEN if repo.is_valid else Fore.RED
            print(f"Status:       {color}{valid_str}{Style.RESET_ALL}")
        else:
            print(f"Status:       {valid_str}")

        print(f"Created:      {repo.created_at}")
        print(f"Last Access:  {repo.last_accessed}")

        # Access control
        if repo.access_control:
            print(f"\nAccess Control:")
            for phone, perms in sorted(repo.access_control.items()):
                perms_str = ', '.join(perms)
                print(f"  {phone:20} {perms_str}")
        else:
            print(f"\nAccess Control: (none)")

        # Get repository stats if possible
        stats = manager.get_repository_stats(args.repo)
        if stats and 'current_branch' in stats:
            print(f"\nGit Information:")
            print(f"  Current Branch:     {stats.get('current_branch', 'unknown')}")
            print(f"  Uncommitted Changes: {'Yes' if stats.get('has_changes') else 'No'}")

        return 0


class SetDefaultCommand:
    """Handle setting default repository."""

    @staticmethod
    def add_parser(subparsers):
        """Add set-default command parser."""
        parser = subparsers.add_parser(
            'set-default',
            help='Set default repository',
            description='Set which repository is used by default'
        )
        parser.add_argument('repo', help='Repository name')
        parser.set_defaults(func=SetDefaultCommand.execute)

    @staticmethod
    def execute(args, manager: RepositoryManager):
        """Execute set-default command."""
        success, message = manager.set_default_repository(args.repo)

        if success:
            print_success(message)
            return 0
        else:
            print_error(message)
            return 1


class ValidateCommand:
    """Handle configuration validation."""

    @staticmethod
    def add_parser(subparsers):
        """Add validate command parser."""
        parser = subparsers.add_parser(
            'validate',
            help='Validate repository configuration',
            description='Check repositories.json for issues'
        )
        parser.set_defaults(func=ValidateCommand.execute)

    @staticmethod
    def execute(args, manager: RepositoryManager):
        """Execute validate command."""
        print_header("Configuration Validation")

        # Check if config file exists
        if not os.path.exists(manager.config_path):
            print_error(f"Configuration file not found: {manager.config_path}")
            return 1

        print_success(f"Configuration file exists: {manager.config_path}")

        # Validate JSON syntax
        try:
            with open(manager.config_path, 'r') as f:
                json.load(f)
            print_success("JSON syntax is valid")
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON: {e}")
            return 1

        # Check repositories
        repos = manager.list_repositories()
        if not repos:
            print_warning("No repositories registered")
            return 0

        print_info(f"\nValidating {len(repos)} repositories...")

        all_valid = True
        for repo in repos:
            if repo.is_valid:
                print_success(f"{repo.name}: Valid")
            else:
                print_error(f"{repo.name}: Invalid")
                print_info(f"  Path: {repo.path}")

                if not os.path.exists(repo.path):
                    print_error(f"  - Path does not exist")
                elif not os.path.isabs(repo.path):
                    print_error(f"  - Path is not absolute")
                elif not os.path.isdir(os.path.join(repo.path, '.git')):
                    print_error(f"  - Not a git repository (no .git directory)")

                all_valid = False

        # Check default repository
        if manager.default_repository:
            if manager.default_repository in manager.repositories:
                print_success(f"\nDefault repository: {manager.default_repository}")
            else:
                print_error(f"\nDefault repository '{manager.default_repository}' does not exist!")
                all_valid = False
        else:
            print_warning("\nNo default repository set")

        # Summary
        print()
        if all_valid:
            print_success("All validations passed")
            return 0
        else:
            print_error("Validation failed - see errors above")
            return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='ClaudePing Repository Administration Tool',
        epilog='For more information, see docs/MULTI_REPO_GUIDE.md'
    )

    parser.add_argument(
        '--config',
        default='config/repositories.json',
        help='Path to repositories.json (default: config/repositories.json)'
    )

    subparsers = parser.add_subparsers(
        title='commands',
        description='Available commands',
        dest='command',
        required=True
    )

    # Add command parsers
    RegisterCommand.add_parser(subparsers)
    ListCommand.add_parser(subparsers)
    UnregisterCommand.add_parser(subparsers)
    DiscoverCommand.add_parser(subparsers)
    GrantCommand.add_parser(subparsers)
    RevokeCommand.add_parser(subparsers)
    InfoCommand.add_parser(subparsers)
    SetDefaultCommand.add_parser(subparsers)
    ValidateCommand.add_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # Initialize repository manager
    try:
        manager = RepositoryManager(config_path=args.config)
    except Exception as e:
        print_error(f"Failed to initialize repository manager: {e}")
        return 1

    # Execute command
    try:
        return args.func(args, manager)
    except KeyboardInterrupt:
        print_warning("\nCancelled by user")
        return 130
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if '--verbose' in sys.argv or '-v' in sys.argv:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
