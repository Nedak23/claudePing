"""
Migration script to convert single-repo setup to multi-repo structure.

This script:
1. Creates initial repository configuration
2. Migrates existing responses (backward compatible)
3. Migrates session data with repository context
4. Creates backups before migration

Usage:
    python migrate_to_multirepo.py [--dry-run] [--backup-dir BACKUP_DIR]
"""
import os
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_current_git_remote() -> str:
    """Get the remote URL of the current repository."""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            check=True
        )
        url = result.stdout.strip()

        # Convert SSH to HTTPS
        if url.startswith('git@github.com:'):
            url = url.replace('git@github.com:', 'https://github.com/')

        # Remove .git suffix
        if url.endswith('.git'):
            url = url[:-4]

        return url
    except:
        return None


def get_whitelisted_numbers() -> list:
    """Get whitelisted numbers from environment."""
    from dotenv import load_dotenv
    load_dotenv()

    whitelist = os.getenv('WHITELISTED_NUMBERS', '').split(',')
    return [num.strip() for num in whitelist if num.strip()]


def create_backup(backup_dir: str) -> bool:
    """
    Create backup of current data.

    Args:
        backup_dir: Directory to store backup

    Returns:
        True if successful
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")

        logger.info(f"Creating backup at {backup_path}")

        # Backup responses
        if os.path.exists('responses'):
            shutil.copytree('responses', os.path.join(backup_path, 'responses'))
            logger.info("Backed up responses/")

        # Backup sessions
        if os.path.exists('sessions'):
            shutil.copytree('sessions', os.path.join(backup_path, 'sessions'))
            logger.info("Backed up sessions/")

        # Backup config if exists
        if os.path.exists('config'):
            shutil.copytree('config', os.path.join(backup_path, 'config'))
            logger.info("Backed up config/")

        logger.info(f"Backup completed at {backup_path}")
        return True

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False


def create_initial_repo_config(repo_name: str = "claudeping",
                               repo_path: str = ".",
                               dry_run: bool = False) -> dict:
    """
    Create initial repositories.json configuration.

    Args:
        repo_name: Name for the default repository
        repo_path: Path to the repository
        dry_run: If True, don't write files

    Returns:
        Configuration dictionary
    """
    logger.info("Creating initial repository configuration")

    # Get repository details
    abs_path = os.path.abspath(repo_path)
    remote_url = get_current_git_remote()
    whitelisted = get_whitelisted_numbers()

    config = {
        'repositories': {
            repo_name: {
                'name': repo_name,
                'path': abs_path,
                'remote_url': remote_url,
                'description': 'Main ClaudePing project (migrated from single-repo)',
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_control': {
                    num: ['read', 'write', 'admin']
                    for num in whitelisted
                }
            }
        },
        'default_repository': repo_name
    }

    logger.info(f"Repository configuration created: {repo_name}")
    logger.info(f"  Path: {abs_path}")
    logger.info(f"  Remote: {remote_url}")
    logger.info(f"  Users with access: {len(whitelisted)}")

    if not dry_run:
        # Create config directory
        os.makedirs('config', exist_ok=True)

        # Write configuration
        config_path = 'config/repositories.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"Configuration written to {config_path}")

    return config


def migrate_responses(default_repo: str = "claudeping",
                     dry_run: bool = False) -> int:
    """
    Migrate existing responses to new structure.

    Old: responses/{id}.json
    New: responses/{id}.json (with added repository fields)

    Args:
        default_repo: Default repository name
        dry_run: If True, don't modify files

    Returns:
        Number of responses migrated
    """
    logger.info("Migrating response files")

    if not os.path.exists('responses'):
        logger.info("No responses directory found, skipping")
        return 0

    migrated = 0
    response_files = [f for f in os.listdir('responses') if f.endswith('.json')]

    abs_path = os.path.abspath('.')
    remote_url = get_current_git_remote()

    for filename in response_files:
        filepath = os.path.join('responses', filename)

        try:
            # Read existing response
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Check if already migrated
            if 'repository_name' in data:
                logger.debug(f"Skipping {filename} (already migrated)")
                continue

            # Add repository metadata
            data['repository_name'] = default_repo
            data['repository_path'] = abs_path
            data['repository_url'] = remote_url

            if not dry_run:
                # Write updated response
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)

            migrated += 1
            logger.debug(f"Migrated {filename}")

        except Exception as e:
            logger.error(f"Error migrating {filename}: {e}")

    logger.info(f"Migrated {migrated} response files")
    return migrated


def migrate_sessions(default_repo: str = "claudeping",
                    dry_run: bool = False) -> int:
    """
    Migrate existing session files to new structure.

    Adds:
    - active_repository field
    - repository_history
    - current_branch as dict instead of string

    Args:
        default_repo: Default repository name
        dry_run: If True, don't modify files

    Returns:
        Number of sessions migrated
    """
    logger.info("Migrating session files")

    if not os.path.exists('sessions'):
        logger.info("No sessions directory found, skipping")
        return 0

    migrated = 0
    session_files = [f for f in os.listdir('sessions') if f.endswith('.json')]

    for filename in session_files:
        filepath = os.path.join('sessions', filename)

        try:
            # Read existing session
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Check if already migrated
            if 'active_repository' in data:
                logger.debug(f"Skipping {filename} (already migrated)")
                continue

            # Add repository context
            data['active_repository'] = default_repo

            # Add repository history
            data['repository_history'] = [
                {
                    'repository': default_repo,
                    'switched_at': data.get('created_at', datetime.now().isoformat())
                }
            ]

            # Convert current_branch to dict
            old_branch = data.get('current_branch')
            if old_branch and isinstance(old_branch, str):
                data['current_branch'] = {
                    default_repo: old_branch
                }
            elif not old_branch:
                data['current_branch'] = {}

            if not dry_run:
                # Write updated session
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)

            migrated += 1
            logger.debug(f"Migrated {filename}")

        except Exception as e:
            logger.error(f"Error migrating {filename}: {e}")

    logger.info(f"Migrated {migrated} session files")
    return migrated


def verify_migration() -> bool:
    """
    Verify that migration was successful.

    Returns:
        True if migration appears successful
    """
    logger.info("Verifying migration")

    issues = []

    # Check config exists
    if not os.path.exists('config/repositories.json'):
        issues.append("Configuration file not found")
    else:
        try:
            with open('config/repositories.json') as f:
                config = json.load(f)

            if 'repositories' not in config:
                issues.append("repositories field missing from config")

            if 'default_repository' not in config:
                issues.append("default_repository field missing from config")

        except Exception as e:
            issues.append(f"Error reading config: {e}")

    # Check responses
    if os.path.exists('responses'):
        response_files = [f for f in os.listdir('responses') if f.endswith('.json')]
        migrated_count = 0

        for filename in response_files[:10]:  # Sample first 10
            filepath = os.path.join('responses', filename)
            try:
                with open(filepath) as f:
                    data = json.load(f)
                if 'repository_name' in data:
                    migrated_count += 1
            except:
                pass

        if migrated_count == 0 and len(response_files) > 0:
            issues.append("No responses appear to be migrated")

    # Check sessions
    if os.path.exists('sessions'):
        session_files = [f for f in os.listdir('sessions') if f.endswith('.json')]
        migrated_count = 0

        for filename in session_files[:10]:  # Sample first 10
            filepath = os.path.join('sessions', filename)
            try:
                with open(filepath) as f:
                    data = json.load(f)
                if 'active_repository' in data:
                    migrated_count += 1
            except:
                pass

        if migrated_count == 0 and len(session_files) > 0:
            issues.append("No sessions appear to be migrated")

    if issues:
        logger.warning("Verification found issues:")
        for issue in issues:
            logger.warning(f"  - {issue}")
        return False
    else:
        logger.info("Verification passed!")
        return True


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description='Migrate ClaudePing to multi-repo mode')
    parser.add_argument('--dry-run', action='store_true', help='Perform dry run without making changes')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('--repo-name', default='claudeping', help='Name for default repository')
    parser.add_argument('--repo-path', default='.', help='Path to repository')
    parser.add_argument('--skip-backup', action='store_true', help='Skip backup creation')

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("ClaudePing Multi-Repo Migration")
    logger.info("=" * 60)

    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")

    # Step 1: Create backup
    if not args.skip_backup and not args.dry_run:
        logger.info("\nStep 1: Creating backup")
        os.makedirs(args.backup_dir, exist_ok=True)
        if not create_backup(args.backup_dir):
            logger.error("Backup failed! Aborting migration.")
            return 1
    else:
        logger.info("\nStep 1: Skipping backup (dry-run or --skip-backup)")

    # Step 2: Create repository configuration
    logger.info("\nStep 2: Creating repository configuration")
    config = create_initial_repo_config(
        repo_name=args.repo_name,
        repo_path=args.repo_path,
        dry_run=args.dry_run
    )

    # Step 3: Migrate responses
    logger.info("\nStep 3: Migrating responses")
    response_count = migrate_responses(
        default_repo=args.repo_name,
        dry_run=args.dry_run
    )

    # Step 4: Migrate sessions
    logger.info("\nStep 4: Migrating sessions")
    session_count = migrate_sessions(
        default_repo=args.repo_name,
        dry_run=args.dry_run
    )

    # Step 5: Verify migration
    if not args.dry_run:
        logger.info("\nStep 5: Verifying migration")
        if not verify_migration():
            logger.warning("Verification found issues. Please review.")
            return 1

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Migration Summary")
    logger.info("=" * 60)
    logger.info(f"Repository name: {args.repo_name}")
    logger.info(f"Repository path: {os.path.abspath(args.repo_path)}")
    logger.info(f"Responses migrated: {response_count}")
    logger.info(f"Sessions migrated: {session_count}")

    if args.dry_run:
        logger.info("\nDRY RUN completed. Re-run without --dry-run to apply changes.")
    else:
        logger.info("\nMigration completed successfully!")
        logger.info("Multi-repo mode is now ENABLED.")
        logger.info("\nNext steps:")
        logger.info("1. Restart the ClaudePing server")
        logger.info("2. Test with: 'list repos' command")
        logger.info("3. Register additional repositories if needed")

    return 0


if __name__ == '__main__':
    exit(main())
