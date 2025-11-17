"""
Repository administration CLI tool.

Provides command-line interface for managing repositories in multi-repo mode.

Usage:
    python repo_admin.py list
    python repo_admin.py register <name> <path> [--description DESC]
    python repo_admin.py unregister <name>
    python repo_admin.py grant <repo> <phone> [--permissions read,write,admin]
    python repo_admin.py revoke <repo> <phone>
    python repo_admin.py info <name>
    python repo_admin.py discover <path> [--auto-register]
"""
import argparse
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from repository_manager import RepositoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_list(repo_manager: RepositoryManager, args):
    """List all repositories."""
    repos = repo_manager.list_repositories()

    if not repos:
        print("No repositories registered.")
        return

    print(f"\nFound {len(repos)} repositories:\n")

    for repo in repos:
        marker = " (default)" if repo.name == repo_manager.default_repository else ""
        status = "✓" if repo.is_valid else "✗"

        print(f"{status} {repo.name}{marker}")
        print(f"  Path: {repo.path}")
        if repo.remote_url:
            print(f"  Remote: {repo.remote_url}")
        if repo.description:
            print(f"  Description: {repo.description}")
        print(f"  Users: {len(repo.access_control)}")
        print()


def cmd_register(repo_manager: RepositoryManager, args):
    """Register a new repository."""
    success, message = repo_manager.register_repository(
        name=args.name,
        path=args.path,
        description=args.description or ""
    )

    if success:
        print(f"✓ {message}")

        # Auto-grant access to admin if specified
        if args.admin_phone:
            repo_manager.grant_access(
                args.name,
                args.admin_phone,
                ['read', 'write', 'admin']
            )
            print(f"✓ Granted admin access to {args.admin_phone}")
    else:
        print(f"✗ {message}")
        sys.exit(1)


def cmd_unregister(repo_manager: RepositoryManager, args):
    """Unregister a repository."""
    # Confirm before removing
    if not args.force:
        response = input(f"Are you sure you want to unregister '{args.name}'? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return

    success, message = repo_manager.unregister_repository(args.name)

    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
        sys.exit(1)


def cmd_grant(repo_manager: RepositoryManager, args):
    """Grant user access to repository."""
    permissions = args.permissions.split(',') if args.permissions else ['read', 'write']

    success, message = repo_manager.grant_access(
        args.repo,
        args.phone,
        permissions
    )

    if success:
        print(f"✓ Granted {', '.join(permissions)} access to {args.phone} for {args.repo}")
    else:
        print(f"✗ {message}")
        sys.exit(1)


def cmd_revoke(repo_manager: RepositoryManager, args):
    """Revoke user access from repository."""
    success, message = repo_manager.revoke_access(args.repo, args.phone)

    if success:
        print(f"✓ Revoked access for {args.phone} from {args.repo}")
    else:
        print(f"✗ {message}")
        sys.exit(1)


def cmd_info(repo_manager: RepositoryManager, args):
    """Show detailed repository information."""
    stats = repo_manager.get_repository_stats(args.name)

    if not stats:
        print(f"✗ Repository '{args.name}' not found")
        sys.exit(1)

    repo = repo_manager.get_repository(args.name)

    print(f"\nRepository: {stats['name']}")
    print(f"Status: {'✓ Valid' if stats['is_valid'] else '✗ Invalid'}")
    print(f"Path: {stats['path']}")
    print(f"Remote: {stats['remote_url'] or 'Not configured'}")
    print(f"Current branch: {stats['current_branch']}")
    print(f"Uncommitted changes: {'Yes' if stats['has_changes'] else 'No'}")
    print(f"Last accessed: {stats['last_accessed']}")

    if repo.description:
        print(f"Description: {repo.description}")

    print(f"\nAccess Control ({len(repo.access_control)} users):")
    for phone, permissions in repo.access_control.items():
        print(f"  {phone}: {', '.join(permissions)}")


def cmd_discover(repo_manager: RepositoryManager, args):
    """Discover git repositories in directory tree."""
    print(f"Scanning {args.path} for git repositories...")

    discovered = repo_manager.discover_repositories(args.path, max_depth=args.depth)

    if not discovered:
        print("No repositories found.")
        return

    print(f"\nFound {len(discovered)} repositories:")

    for i, repo_path in enumerate(discovered, 1):
        print(f"\n{i}. {repo_path}")

        # Check if already registered
        already_registered = any(
            r.path == repo_path
            for r in repo_manager.list_repositories()
        )

        if already_registered:
            print("   (already registered)")
            continue

        if args.auto_register:
            # Auto-register with path-based name
            repo_name = Path(repo_path).name
            success, message = repo_manager.register_repository(
                name=repo_name,
                path=repo_path
            )
            if success:
                print(f"   ✓ Registered as '{repo_name}'")
            else:
                print(f"   ✗ Failed to register: {message}")


def cmd_set_default(repo_manager: RepositoryManager, args):
    """Set default repository."""
    success, message = repo_manager.set_default_repository(args.name)

    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='ClaudePing Repository Administration')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # List command
    parser_list = subparsers.add_parser('list', help='List all repositories')

    # Register command
    parser_register = subparsers.add_parser('register', help='Register a new repository')
    parser_register.add_argument('name', help='Repository name')
    parser_register.add_argument('path', help='Path to repository')
    parser_register.add_argument('--description', help='Repository description')
    parser_register.add_argument('--admin-phone', help='Phone number to grant admin access')

    # Unregister command
    parser_unregister = subparsers.add_parser('unregister', help='Unregister a repository')
    parser_unregister.add_argument('name', help='Repository name')
    parser_unregister.add_argument('--force', action='store_true', help='Skip confirmation')

    # Grant command
    parser_grant = subparsers.add_parser('grant', help='Grant user access to repository')
    parser_grant.add_argument('repo', help='Repository name')
    parser_grant.add_argument('phone', help='Phone number')
    parser_grant.add_argument('--permissions', default='read,write', help='Comma-separated permissions (default: read,write)')

    # Revoke command
    parser_revoke = subparsers.add_parser('revoke', help='Revoke user access from repository')
    parser_revoke.add_argument('repo', help='Repository name')
    parser_revoke.add_argument('phone', help='Phone number')

    # Info command
    parser_info = subparsers.add_parser('info', help='Show repository information')
    parser_info.add_argument('name', help='Repository name')

    # Discover command
    parser_discover = subparsers.add_parser('discover', help='Discover repositories in directory')
    parser_discover.add_argument('path', help='Path to search')
    parser_discover.add_argument('--depth', type=int, default=3, help='Maximum search depth')
    parser_discover.add_argument('--auto-register', action='store_true', help='Automatically register discovered repos')

    # Set default command
    parser_default = subparsers.add_parser('set-default', help='Set default repository')
    parser_default.add_argument('name', help='Repository name')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize repository manager
    try:
        repo_manager = RepositoryManager()
    except Exception as e:
        logger.error(f"Failed to initialize repository manager: {e}")
        sys.exit(1)

    # Execute command
    try:
        if args.command == 'list':
            cmd_list(repo_manager, args)
        elif args.command == 'register':
            cmd_register(repo_manager, args)
        elif args.command == 'unregister':
            cmd_unregister(repo_manager, args)
        elif args.command == 'grant':
            cmd_grant(repo_manager, args)
        elif args.command == 'revoke':
            cmd_revoke(repo_manager, args)
        elif args.command == 'info':
            cmd_info(repo_manager, args)
        elif args.command == 'discover':
            cmd_discover(repo_manager, args)
        elif args.command == 'set-default':
            cmd_set_default(repo_manager, args)
        else:
            logger.error(f"Unknown command: {args.command}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error executing command: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
