# Multi-Repository Support - CTO Strategic Plan

**Author:** CTO Planning Session
**Date:** 2025-11-15
**Status:** DRAFT - Architectural Planning
**Project:** ClaudePing Multi-Repo Enhancement

---

## Executive Summary

### Current State
ClaudePing is a WhatsApp/SMS-based AI coding assistant that enables users to send coding requests and receive AI-powered assistance from Claude Code CLI. The system currently operates on a **single repository only** (hardcoded to the current working directory).

### Proposed Enhancement
Enable users to work with **multiple repositories** and **switch between them dynamically** via messaging commands, while maintaining security, session context, and user experience quality.

### Strategic Impact
- **User Value:** 10x increase in utility - users can manage entire project portfolios
- **Market Differentiation:** First SMS-based multi-repo coding assistant
- **Technical Debt:** Requires significant architectural refactoring
- **Timeline:** 6-8 weeks for full implementation (phased approach)
- **Risk Level:** Medium (backward compatibility and data migration concerns)

---

## 1. Problem Statement

### Current Limitations

1. **Single Repository Lock-in**
   - System operates only on `/home/user/claudePing` directory
   - Users cannot access other projects
   - GitHandler hardcoded to `repo_path = "."`

2. **No Context Switching**
   - Each user locked to one repo per deployment
   - No way to specify target repository in commands
   - Session state doesn't track repository context

3. **Scalability Ceiling**
   - Can't serve users with multiple projects
   - Requires separate deployments for each repo
   - No repo discovery or management

### User Pain Points

**Scenario:** Developer managing 3 projects
- **Current:** Must run 3 separate ClaudePing instances
- **Desired:** Single instance, switch repos via commands like:
  - `"switch to project-api"`
  - `"in project-web: add login page"`
  - `"list my repos"`

---

## 2. Strategic Objectives

### Primary Goals

1. **Multi-Repo Management**
   - Support 5-50 repositories per installation
   - Enable repository registration and discovery
   - Maintain isolation between repositories

2. **Seamless Repo Switching**
   - Natural language commands for switching
   - Context preservation during switches
   - Clear confirmation of active repository

3. **Backward Compatibility**
   - Existing single-repo deployments continue working
   - Graceful migration path for current users
   - No breaking changes to core functionality

4. **Security & Authorization**
   - Per-user, per-repo access control
   - Prevent unauthorized repository access
   - Audit trail for multi-repo operations

### Success Metrics

- **Adoption:** 80% of users register 2+ repositories within 30 days
- **Performance:** Repo switching completes in <2 seconds
- **Reliability:** 99.9% success rate for cross-repo operations
- **Security:** Zero unauthorized repo access incidents

---

## 3. Technical Architecture

### 3.1 Core Components (New)

#### A. Repository Registry

**Purpose:** Central registry for all available repositories

```python
class RepositoryManager:
    """
    Manages multiple repositories and their metadata
    """
    def __init__(self, config_path: str = "config/repositories.json"):
        self.repositories: Dict[str, Repository] = {}
        self.config_path = config_path

    def register_repository(self, name: str, path: str,
                           remote_url: str = None) -> Repository:
        """Register a new repository"""

    def get_repository(self, name: str) -> Repository:
        """Retrieve repository by name"""

    def list_repositories(self, user: str = None) -> List[Repository]:
        """List all repositories (optionally filtered by user access)"""

    def discover_repositories(self, search_path: str) -> List[str]:
        """Auto-discover git repositories in directory tree"""

    def remove_repository(self, name: str) -> bool:
        """Unregister a repository"""
```

**Data Model:**
```python
@dataclass
class Repository:
    name: str              # User-friendly name (e.g., "project-api")
    path: str              # Absolute filesystem path
    remote_url: str        # Git remote URL
    description: str       # Optional description
    created_at: datetime
    last_accessed: datetime
    access_control: Dict[str, List[str]]  # {phone_number: [permissions]}

    # Computed properties
    @property
    def git_handler(self) -> GitHandler:
        """Get GitHandler instance for this repo"""

    @property
    def is_valid(self) -> bool:
        """Check if repo still exists and is valid git repo"""
```

**Storage:** `config/repositories.json`
```json
{
  "repositories": {
    "claudeping": {
      "name": "claudeping",
      "path": "/home/user/claudePing",
      "remote_url": "https://github.com/Nedak23/claudePing.git",
      "description": "Main ClaudePing project",
      "created_at": "2025-11-15T10:00:00Z",
      "last_accessed": "2025-11-15T14:30:00Z",
      "access_control": {
        "+1234567890": ["read", "write", "admin"]
      }
    },
    "project-api": {
      "name": "project-api",
      "path": "/home/user/projects/api",
      "remote_url": "https://github.com/user/api.git",
      "access_control": {
        "+1234567890": ["read", "write"]
      }
    }
  },
  "default_repository": "claudeping"
}
```

---

#### B. Enhanced Session Manager

**Purpose:** Track user's active repository and repo history

```python
class EnhancedSessionManager(SessionManager):
    """
    Extends SessionManager with multi-repo capabilities
    """
    def __init__(self, claude_handler: ClaudeHandler,
                 repo_manager: RepositoryManager):
        super().__init__(claude_handler)
        self.repo_manager = repo_manager

    def set_active_repository(self, phone_number: str,
                              repo_name: str) -> Tuple[bool, str]:
        """Switch user's active repository"""

    def get_active_repository(self, phone_number: str) -> Repository:
        """Get user's current active repository"""

    def get_repository_history(self, phone_number: str) -> List[str]:
        """Get user's recently used repositories"""

    def validate_repo_access(self, phone_number: str,
                            repo_name: str) -> bool:
        """Check if user has access to repository"""
```

**Enhanced Session Model:**
```json
{
  "phone_number": "+1234567890",
  "created_at": "2025-11-15T10:00:00Z",
  "last_activity": "2025-11-15T14:30:00Z",

  "active_repository": "project-api",
  "repository_history": [
    {
      "repository": "project-api",
      "switched_at": "2025-11-15T14:30:00Z"
    },
    {
      "repository": "claudeping",
      "switched_at": "2025-11-15T14:00:00Z"
    }
  ],

  "conversation_history": [
    {
      "timestamp": "2025-11-15T14:30:00Z",
      "repository": "project-api",
      "prompt": "add login endpoint",
      "response": "Created POST /login endpoint..."
    }
  ],

  "current_branch": {
    "claudeping": "sms/20251115_140000",
    "project-api": "sms/20251115_143000"
  }
}
```

---

#### C. Command Parser & Intent Recognition

**Purpose:** Parse user messages to extract repo context and commands

```python
class CommandParser:
    """
    Parses user messages to detect repo-related commands
    """

    # Command patterns
    SWITCH_PATTERNS = [
        r"switch to (\w+)",
        r"use (\w+)",
        r"go to (\w+)",
        r"work on (\w+)"
    ]

    INLINE_REPO_PATTERNS = [
        r"in (\w+):?\s*(.+)",      # "in project-api: add feature"
        r"for (\w+):?\s*(.+)",     # "for web-app: fix bug"
        r"@(\w+):?\s*(.+)"         # "@api: add endpoint"
    ]

    REPO_COMMANDS = [
        "list repos",
        "list repositories",
        "show repos",
        "what repos",
        "my repos"
    ]

    def parse(self, message: str) -> CommandIntent:
        """Parse message and return intent"""

    def extract_repo_context(self, message: str) -> Tuple[str, str]:
        """
        Extract repository and actual prompt
        Returns: (repo_name or None, cleaned_prompt)
        """

    def is_repo_command(self, message: str) -> bool:
        """Check if message is a repo management command"""

@dataclass
class CommandIntent:
    type: str  # 'switch_repo', 'inline_repo', 'list_repos', 'coding_request'
    repository: str = None
    prompt: str = None
    parameters: Dict = None
```

**Example Parsing:**
```python
# Input: "switch to project-api"
CommandIntent(
    type='switch_repo',
    repository='project-api',
    prompt=None
)

# Input: "in web-app: add dark mode toggle"
CommandIntent(
    type='inline_repo',
    repository='web-app',
    prompt='add dark mode toggle'
)

# Input: "list my repos"
CommandIntent(
    type='list_repos',
    repository=None,
    prompt=None
)

# Input: "fix the login bug" (uses active repo)
CommandIntent(
    type='coding_request',
    repository=None,  # Will use session's active_repository
    prompt='fix the login bug'
)
```

---

#### D. Repo-Aware Git Handler Factory

**Purpose:** Create GitHandler instances for specific repositories

```python
class GitHandlerFactory:
    """
    Creates and caches GitHandler instances per repository
    """
    def __init__(self):
        self._handlers: Dict[str, GitHandler] = {}

    def get_handler(self, repository: Repository) -> GitHandler:
        """
        Get or create GitHandler for repository
        Implements singleton pattern per repo
        """
        if repository.name not in self._handlers:
            self._handlers[repository.name] = GitHandler(
                repo_path=repository.path
            )
        return self._handlers[repository.name]

    def invalidate(self, repo_name: str):
        """Remove cached handler (useful for repo updates)"""
        self._handlers.pop(repo_name, None)
```

---

#### E. Repo-Aware Claude Handler

**Purpose:** Execute Claude Code CLI in specific repository contexts

```python
class RepoAwareClaudeHandler(ClaudeHandler):
    """
    Enhanced ClaudeHandler that can work with multiple repositories
    """

    def send_prompt_to_repo(self, prompt: str,
                           repository: Repository,
                           timeout: int = 300) -> Tuple[bool, str, str]:
        """
        Execute Claude Code CLI in specific repository

        Args:
            prompt: User's coding request
            repository: Target repository object
            timeout: Execution timeout in seconds

        Returns:
            (success, response, error)
        """
        try:
            # Change to repository directory for execution
            original_cwd = os.getcwd()
            os.chdir(repository.path)

            result = subprocess.run(
                ['claude', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self._prepare_env()
            )

            success = result.returncode == 0
            response = result.stdout
            error = result.stderr if not success else None

            return success, response, error

        finally:
            # Always restore original directory
            os.chdir(original_cwd)
```

---

### 3.2 Enhanced Data Models

#### Response Model (Enhanced)
```json
{
  "id": "20251115_143022_123456",
  "timestamp": "2025-11-15T14:30:22.123456",
  "phone_number": "+1234567890",

  "repository_name": "project-api",
  "repository_path": "/home/user/projects/api",
  "repository_url": "https://github.com/user/api.git",

  "prompt": "add login endpoint",
  "response": "Created POST /login endpoint with JWT auth...",

  "branch_name": "sms/20251115_143022",
  "files_changed": ["api/routes/auth.py", "api/models/user.py"],

  "execution_context": {
    "working_directory": "/home/user/projects/api",
    "claude_version": "1.2.3",
    "execution_time_ms": 4523
  }
}
```

#### Storage Structure (Enhanced)
```
/home/user/claudePing/
├── config/
│   └── repositories.json          # NEW: Repo registry
├── responses/
│   ├── claudeping/                # NEW: Per-repo responses
│   │   └── 20251115_140000.json
│   └── project-api/               # NEW: Per-repo responses
│       └── 20251115_143000.json
├── sessions/
│   └── {phone_number}.json        # Enhanced with repo context
└── logs/
    └── repo_operations.log        # NEW: Audit trail
```

---

### 3.3 Updated Application Flow

```
User sends: "in project-api: add login endpoint"
    ↓
Twilio Webhook → Flask App (/sms)
    ↓
┌─────────────────────────────────────────┐
│ 1. Authentication                       │
│    - is_whitelisted(phone_number)       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 2. Command Parsing (NEW)                │
│    - CommandParser.parse()              │
│    - Extract: repo="project-api"        │
│              prompt="add login..."      │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 3. Repository Resolution (NEW)          │
│    - RepositoryManager.get_repository() │
│    - Validate user access               │
│    - Get Repository object              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 4. Session Management (ENHANCED)        │
│    - Get/create session                 │
│    - Update active_repository           │
│    - Track repo history                 │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 5. Claude Execution (ENHANCED)          │
│    - RepoAwareClaudeHandler             │
│    - Execute in repo.path directory     │
│    - Capture output                     │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 6. Git Operations (ENHANCED)            │
│    - GitHandlerFactory.get_handler()    │
│    - Create branch in specific repo     │
│    - Commit with repo context           │
│    - Push to correct remote             │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 7. Response Storage (ENHANCED)          │
│    - Save with repository metadata      │
│    - Store in repo-specific directory   │
│    - Update session with repo context   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 8. Summary Generation (ENHANCED)        │
│    - Include repository name            │
│    - "✓ Done in project-api! ..."       │
└─────────────────────────────────────────┘
    ↓
Send SMS/WhatsApp response
```

---

## 4. User Experience Design

### 4.1 Command Interface

#### Repository Management Commands

| Command | Action | Example Response |
|---------|--------|------------------|
| `list repos` | Show all accessible repos | `You have 3 repos: claudeping (active), project-api, web-app` |
| `switch to [repo]` | Change active repo | `✓ Switched to project-api` |
| `info [repo]` | Show repo details | `project-api: /home/user/projects/api, Branch: main, 15 files changed` |
| `repos status` | Status of all repos | `claudeping: clean, project-api: 3 files changed, web-app: clean` |

#### Inline Repository Targeting

```
User: "in project-api: add login endpoint"
Response: "✓ Done in project-api! Added POST /login endpoint.
          Branch: sms/20251115_143000. Files: api/routes/auth.py +45 lines"

User: "for web-app: fix navbar css"
Response: "✓ Done in web-app! Fixed navbar alignment.
          Branch: sms/20251115_144500. Files: styles/navbar.css"

User: "@api: run tests"
Response: "✓ Tests passed in project-api! 24 tests, all green. No changes made."
```

#### Active Repository Usage

```
User: "switch to web-app"
Response: "✓ Switched to web-app (was: claudeping)"

User: "add dark mode"
Response: "✓ Done! Added dark mode toggle in Settings.
          [uses web-app because it's active]
          Branch: sms/20251115_145000"
```

### 4.2 Error Handling & Feedback

#### Repository Not Found
```
User: "switch to unknown-repo"
Response: "❌ Repository 'unknown-repo' not found.
          Available: claudeping, project-api, web-app.
          Send 'list repos' to see all."
```

#### Access Denied
```
User: "in private-repo: make changes"
Response: "❌ Access denied to 'private-repo'.
          Contact admin to request access."
```

#### Repository Issues
```
User: "in project-api: add feature"
Response: "⚠️ Warning: project-api has uncommitted changes in main branch.
          Created branch anyway: sms/20251115_150000
          [response continues...]"
```

### 4.3 Context Awareness

**Summary Format (Enhanced):**
```
✓ Done in [repo-name]! [summary]
Branch: [branch]. Files: [count]. Full: [url]

Active repo: [current-repo]
```

**Example:**
```
✓ Done in project-api! Added JWT authentication to /login endpoint.
Branch: sms/20251115_143000. Files: 3 modified, 2 created.
Full: http://example.com/response/20251115_143000

Active repo: project-api
```

---

## 5. Security & Authorization

### 5.1 Access Control Model

#### Three-Tier Permission System

1. **Repository-Level Access**
   ```python
   Repository.access_control = {
       "+1234567890": ["read", "write", "admin"],
       "+0987654321": ["read"]  # Read-only access
   }
   ```

2. **User-Level Whitelist**
   - Existing `WHITELISTED_NUMBERS` remains (system access)
   - New `REPO_ACCESS_CONTROL` for granular permissions

3. **Default Repository**
   - Users without explicit repo selection use default
   - Backward compatible with single-repo setup

#### Permission Levels

| Level | Capabilities |
|-------|-------------|
| **read** | View repo status, list files, read code (no commits) |
| **write** | Create branches, commit, push (standard user) |
| **admin** | Register/remove repos, manage access, configure settings |

### 5.2 Access Validation Flow

```python
def validate_repo_operation(phone_number: str,
                           repo_name: str,
                           operation: str) -> Tuple[bool, str]:
    """
    Validate if user can perform operation on repository

    Args:
        phone_number: User identifier
        repo_name: Target repository
        operation: 'read', 'write', or 'admin'

    Returns:
        (is_allowed, error_message)
    """
    # 1. Check system whitelist
    if not is_whitelisted(phone_number):
        return False, "Not authorized for ClaudePing"

    # 2. Get repository
    repo = repo_manager.get_repository(repo_name)
    if not repo:
        return False, f"Repository '{repo_name}' not found"

    # 3. Check repo-level permissions
    user_permissions = repo.access_control.get(phone_number, [])

    # 4. Validate operation
    if operation == 'read' and 'read' not in user_permissions:
        return False, "No read access to this repository"

    if operation == 'write' and 'write' not in user_permissions:
        return False, "No write access to this repository"

    if operation == 'admin' and 'admin' not in user_permissions:
        return False, "No admin access to this repository"

    return True, None
```

### 5.3 Audit Trail

**Log All Repository Operations:**
```python
# logs/repo_operations.log
{
  "timestamp": "2025-11-15T14:30:22Z",
  "phone_number": "+1234567890",
  "operation": "switch_repository",
  "from_repo": "claudeping",
  "to_repo": "project-api",
  "success": true
}

{
  "timestamp": "2025-11-15T14:31:15Z",
  "phone_number": "+1234567890",
  "operation": "execute_command",
  "repository": "project-api",
  "prompt": "add login endpoint",
  "branch_created": "sms/20251115_143000",
  "files_changed": 3,
  "success": true
}

{
  "timestamp": "2025-11-15T14:32:00Z",
  "phone_number": "+0987654321",
  "operation": "access_denied",
  "repository": "private-repo",
  "reason": "insufficient_permissions",
  "success": false
}
```

---

## 6. Migration Strategy

### 6.1 Backward Compatibility Approach

**Phase 1: Additive Changes Only**
- Add new components without removing old ones
- Single-repo functionality continues working
- New multi-repo features opt-in

**Detection Logic:**
```python
def is_multi_repo_enabled() -> bool:
    """Check if multi-repo mode is enabled"""
    return os.path.exists('config/repositories.json')

# In app.py
if is_multi_repo_enabled():
    # Use new RepositoryManager, EnhancedSessionManager
    repo_manager = RepositoryManager()
    session_manager = EnhancedSessionManager(claude_handler, repo_manager)
else:
    # Use legacy single-repo mode
    session_manager = SessionManager(claude_handler)
```

### 6.2 Data Migration

#### Step 1: Migrate Existing Responses
```python
def migrate_responses():
    """
    Migrate existing responses to new structure
    """
    # Old: responses/{id}.json
    # New: responses/claudeping/{id}.json

    old_responses = Path('responses').glob('*.json')
    default_repo = 'claudeping'

    for response_file in old_responses:
        # Load existing response
        with open(response_file) as f:
            data = json.load(f)

        # Add repository metadata
        data['repository_name'] = default_repo
        data['repository_path'] = '/home/user/claudePing'
        data['repository_url'] = get_current_git_remote()

        # Move to new location
        new_path = f'responses/{default_repo}/{response_file.name}'
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        with open(new_path, 'w') as f:
            json.dump(data, f, indent=2)
```

#### Step 2: Migrate Session Data
```python
def migrate_sessions():
    """
    Enhance existing sessions with repository context
    """
    for session_file in Path('sessions').glob('*.json'):
        with open(session_file) as f:
            data = json.load(f)

        # Add new fields with defaults
        data['active_repository'] = 'claudeping'
        data['repository_history'] = [
            {
                'repository': 'claudeping',
                'switched_at': data.get('created_at')
            }
        ]
        data['current_branch'] = {
            'claudeping': data.get('current_branch')
        }

        # Save updated session
        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)
```

#### Step 3: Create Initial Repository Config
```python
def create_initial_repo_config():
    """
    Create repositories.json from current setup
    """
    config = {
        'repositories': {
            'claudeping': {
                'name': 'claudeping',
                'path': '/home/user/claudePing',
                'remote_url': get_current_git_remote(),
                'description': 'Main ClaudePing project',
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_control': {
                    # Give all whitelisted numbers admin access
                    num: ['read', 'write', 'admin']
                    for num in get_whitelisted_numbers()
                }
            }
        },
        'default_repository': 'claudeping'
    }

    os.makedirs('config', exist_ok=True)
    with open('config/repositories.json', 'w') as f:
        json.dump(config, f, indent=2)
```

### 6.3 Migration Execution Plan

**Pre-Migration Checklist:**
- [ ] Backup all data (`responses/`, `sessions/`)
- [ ] Test migration scripts on copy
- [ ] Verify git remotes are accessible
- [ ] Check disk space for duplicated data

**Migration Steps:**
1. **Backup** - Create timestamped backup of entire data directory
2. **Migrate Responses** - Run `migrate_responses()`
3. **Migrate Sessions** - Run `migrate_sessions()`
4. **Create Config** - Run `create_initial_repo_config()`
5. **Deploy New Code** - Update application with multi-repo support
6. **Verify** - Test with existing users, check all data accessible
7. **Monitor** - Watch logs for 48 hours, verify no errors
8. **Cleanup** - After 2 weeks, archive old response files

**Rollback Plan:**
- Keep old data directory for 30 days
- If issues detected, restore from backup
- Revert code to previous version
- Single-repo mode continues working

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Build core multi-repo infrastructure

**Deliverables:**
- [ ] `RepositoryManager` class with JSON storage
- [ ] `Repository` data model
- [ ] `GitHandlerFactory` for repo-specific handlers
- [ ] `RepoAwareClaudeHandler` with directory switching
- [ ] Unit tests for all new components (80% coverage)

**Success Criteria:**
- Can register/list/get repositories programmatically
- Can create GitHandler for specific repo paths
- Can execute Claude CLI in different directories

**Risk:** Directory switching may cause race conditions
**Mitigation:** Implement per-request context isolation

---

### Phase 2: Session & Command Parsing (Week 2-3)
**Goal:** Enable repository context in user sessions

**Deliverables:**
- [ ] `EnhancedSessionManager` with active repo tracking
- [ ] `CommandParser` for intent recognition
- [ ] Enhanced session data model with repo history
- [ ] Session storage updates (backward compatible)
- [ ] Integration tests for session management

**Success Criteria:**
- Sessions track active repository
- Parse "switch to X" and "in X: Y" commands
- Session persists repo context across restarts

**Risk:** Command parsing accuracy <80%
**Mitigation:** Use regex patterns + fuzzy matching for repo names

---

### Phase 3: Request Flow Integration (Week 3-4)
**Goal:** Wire multi-repo support into main request handler

**Deliverables:**
- [ ] Update `handle_coding_request()` with repo resolution
- [ ] Implement access control validation
- [ ] Enhanced response storage with repo metadata
- [ ] Update summary generator with repo context
- [ ] End-to-end testing with multiple repos

**Success Criteria:**
- Can process requests with inline repo targeting
- Correct repo used for Claude execution and git ops
- Responses include accurate repo metadata

**Risk:** Breaking existing single-repo functionality
**Mitigation:** Feature flag + parallel code paths

---

### Phase 4: Data Migration (Week 4-5)
**Goal:** Migrate existing data to new structure

**Deliverables:**
- [ ] Migration scripts (responses, sessions, config)
- [ ] Data validation tools
- [ ] Backup and rollback procedures
- [ ] Migration documentation
- [ ] Dry-run testing on production data copy

**Success Criteria:**
- All existing responses accessible in new structure
- All sessions retain conversation history
- Zero data loss during migration
- Rollback tested and verified

**Risk:** Data corruption during migration
**Mitigation:** Atomic operations, backups, dry-run validation

---

### Phase 5: User Experience & Commands (Week 5-6)
**Goal:** Polish user-facing features

**Deliverables:**
- [ ] Repository discovery feature
- [ ] "list repos" command with status
- [ ] "switch to" command with confirmation
- [ ] Enhanced error messages for repo issues
- [ ] SMS-optimized responses with repo context
- [ ] User acceptance testing

**Success Criteria:**
- Users can discover and register new repos
- Clear feedback for all repo operations
- Error messages guide users to resolution
- 90% user satisfaction in testing

**Risk:** SMS character limits make responses unclear
**Mitigation:** Progressive disclosure, use abbreviations

---

### Phase 6: Security & Access Control (Week 6-7)
**Goal:** Implement robust authorization

**Deliverables:**
- [ ] Per-repo access control system
- [ ] Permission validation in all operations
- [ ] Audit logging for repo operations
- [ ] Admin commands for access management
- [ ] Security testing and penetration testing

**Success Criteria:**
- Users can't access unauthorized repos
- All operations logged with user attribution
- Admin can grant/revoke access via commands
- Zero security vulnerabilities in testing

**Risk:** Privilege escalation bugs
**Mitigation:** Security review, principle of least privilege

---

### Phase 7: Testing & Documentation (Week 7-8)
**Goal:** Ensure production readiness

**Deliverables:**
- [ ] Comprehensive test suite (unit, integration, E2E)
- [ ] Performance testing (response times, concurrency)
- [ ] User documentation (commands, setup guide)
- [ ] Admin documentation (deployment, config)
- [ ] API documentation for developers
- [ ] Monitoring and alerting setup

**Success Criteria:**
- 90% code coverage
- <2s average repo switching time
- <5s average request processing time
- Documentation complete and accurate

**Risk:** Performance degradation with many repos
**Mitigation:** Caching, lazy loading, profiling

---

### Phase 8: Deployment & Monitoring (Week 8)
**Goal:** Launch to production

**Deliverables:**
- [ ] Staged rollout plan (10% → 50% → 100% users)
- [ ] Monitoring dashboards (repo ops, errors, latency)
- [ ] Alerting rules for failures
- [ ] Rollback procedures tested
- [ ] On-call runbook

**Success Criteria:**
- Zero critical bugs in production
- 99.9% uptime during rollout
- <1% error rate
- Positive user feedback

**Risk:** Unexpected production issues
**Mitigation:** Gradual rollout, feature flags, quick rollback

---

## 8. Resource Requirements

### 8.1 Engineering Team

| Role | Allocation | Duration | Responsibilities |
|------|------------|----------|------------------|
| **Senior Backend Engineer** | 100% | 8 weeks | Core architecture, RepositoryManager, integration |
| **Backend Engineer** | 100% | 6 weeks | Command parsing, session management, testing |
| **QA Engineer** | 50% | 3 weeks | Test planning, automation, UAT |
| **DevOps Engineer** | 25% | 2 weeks | Migration scripts, monitoring, deployment |
| **Engineering Manager** | 25% | 8 weeks | Coordination, risk management, decisions |

**Total:** ~3 FTE-months

### 8.2 Infrastructure

**Development:**
- Test repositories (5-10 sample repos)
- Staging environment with multi-repo setup
- CI/CD pipeline updates

**Production:**
- No significant infrastructure changes
- Disk space: +20% for repo metadata and separated responses
- Monitoring: New dashboards for repo operations

### 8.3 External Dependencies

- **Twilio:** No changes required
- **Claude Code CLI:** Verify supports directory switching (likely yes)
- **Git:** Standard operations, no special requirements
- **GitHub:** May need additional API rate limits for multiple repos

---

## 9. Risks & Mitigation

### 9.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Directory switching race conditions** | Medium | High | Implement per-request isolation, use subprocess cwd parameter |
| **Git conflicts across repos** | Low | Medium | Each repo has independent branches, minimal conflict risk |
| **Performance degradation** | Medium | Medium | Implement caching, lazy loading, profile and optimize |
| **Data migration failures** | Low | Critical | Extensive testing, atomic operations, rollback plan |
| **Claude CLI doesn't support cwd change** | Low | Critical | Test early in Phase 1, have subprocess wrapper fallback |

### 9.2 User Experience Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Confusing command syntax** | Medium | Medium | User testing, clear error messages, examples in docs |
| **Users forget active repo** | High | Low | Include repo name in every response, visual indicators |
| **SMS character limits** | High | Medium | Aggressive summarization, progressive disclosure |
| **Accidental wrong repo operations** | Medium | High | Confirmation for destructive ops, clear repo context |

### 9.3 Security Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Unauthorized repo access** | Low | Critical | Strict access control validation, audit logging |
| **Path traversal attacks** | Low | High | Whitelist allowed repo paths, validate all inputs |
| **Secrets exposure across repos** | Medium | High | Per-repo .env files, document security best practices |
| **Social engineering** | Low | Medium | Rate limiting, user education, audit trail |

### 9.4 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Low adoption (users don't need multi-repo)** | Medium | Medium | User research before committing, phased rollout |
| **Support burden increases** | High | Medium | Comprehensive docs, clear error messages, automation |
| **Breaking existing workflows** | Low | High | Backward compatibility, migration support, rollback plan |
| **Timeline slippage** | Medium | Medium | Buffer time built in, MVP scope defined, bi-weekly checkpoints |

---

## 10. Success Criteria & Metrics

### 10.1 Launch Criteria

Must achieve ALL before production launch:

- [ ] **Functionality:** All 8 implementation phases complete
- [ ] **Testing:** 90% code coverage, all E2E tests passing
- [ ] **Performance:** <2s repo switching, <5s request processing
- [ ] **Security:** Security review passed, no critical vulnerabilities
- [ ] **Reliability:** 99.9% uptime in staging for 1 week
- [ ] **Documentation:** User and admin docs complete and reviewed
- [ ] **Migration:** Successfully migrated staging data with zero loss
- [ ] **Rollback:** Rollback tested and verified in staging

### 10.2 Post-Launch Metrics (30 days)

**Adoption Metrics:**
- ✅ Target: 50% of active users register 2+ repositories
- ✅ Target: 100+ repo switches per day
- ✅ Target: 30% of requests use inline repo targeting

**Performance Metrics:**
- ✅ Target: P95 repo switch time <3s
- ✅ Target: P95 request processing time <7s
- ✅ Target: 99.9% uptime

**Quality Metrics:**
- ✅ Target: <1% error rate
- ✅ Target: <5 critical bugs per week
- ✅ Target: Zero security incidents

**User Satisfaction:**
- ✅ Target: 80% users rate experience 4/5 or higher
- ✅ Target: <10% feature revert requests
- ✅ Target: Positive feedback on repo switching UX

---

## 11. Alternative Approaches Considered

### Alternative 1: Separate ClaudePing Instance Per Repo
**Approach:** Deploy one ClaudePing instance for each repository

**Pros:**
- Simplest implementation
- Perfect isolation
- No code changes needed

**Cons:**
- High operational overhead (manage N instances)
- No unified user experience
- Resource intensive
- Can't easily switch between repos

**Decision:** ❌ Rejected - Poor scalability and UX

---

### Alternative 2: Claude Code Workspace Files
**Approach:** Use Claude Code's workspace switching instead of directory switching

**Pros:**
- Leverages Claude's built-in features
- May preserve more context

**Cons:**
- Requires deep Claude Code CLI integration
- May not support programmatic workspace switching
- Less control over behavior

**Decision:** ❌ Rejected - Uncertain CLI support, less flexible

---

### Alternative 3: Git Worktrees
**Approach:** Use git worktrees to have multiple checkouts of same repo

**Pros:**
- Native git feature
- Shares .git directory (space efficient)

**Cons:**
- Only works for single repo with multiple branches
- Doesn't solve multi-repo problem
- Added complexity

**Decision:** ❌ Rejected - Doesn't address core requirement

---

### Alternative 4: Containerized Execution
**Approach:** Run each Claude request in isolated container with mounted repo

**Pros:**
- Perfect isolation
- Security benefits
- Reproducible environments

**Cons:**
- Significant infrastructure changes
- Performance overhead (container startup)
- Complexity in Docker setup

**Decision:** ⚠️ Future consideration - Good for Phase 2 (multi-tenancy)

---

### Alternative 5: Repository Proxy Pattern (SELECTED)
**Approach:** Central RepositoryManager proxies to repo-specific handlers

**Pros:**
- Clean architecture
- Easy to extend
- Minimal performance overhead
- Backward compatible

**Cons:**
- More code changes than status quo
- Requires migration

**Decision:** ✅ SELECTED - Best balance of features, performance, and maintainability

---

## 12. Future Enhancements (Post-MVP)

### 12.1 Short-term (3-6 months)

**Repository Discovery & Auto-Registration**
- Auto-scan directories for git repos
- Suggest repos based on recent git activity
- One-command registration: "register /path/to/repo as my-project"

**Enhanced Repository Management**
- Rename repositories
- Archive/unarchive repos
- Repository groups/categories
- Favorite/pinned repos

**Cross-Repository Operations**
- "status all repos" - unified status view
- Bulk operations across repos
- Dependency tracking between repos

### 12.2 Long-term (6-12 months)

**Multi-User Collaboration**
- Shared repositories between users
- Team access control
- Activity feed per repository

**Advanced Git Operations**
- Branch management across repos
- PR creation from SMS
- Merge conflict resolution assistance

**Repository Templates**
- Pre-configured repo setups
- Quick project scaffolding
- Best practices enforcement

**Analytics & Insights**
- Most active repositories
- User productivity metrics
- Code quality trends per repo

### 12.3 Research Items

**Voice Interface**
- WhatsApp voice messages for commands
- Speech-to-text for coding requests

**Repository Clustering**
- Automatically group related repos
- Monorepo support
- Microservices architecture awareness

**AI-Powered Repository Recommendations**
- Suggest which repo for ambiguous requests
- Learn user patterns over time
- Context-aware repo selection

---

## 13. Open Questions & Decisions Needed

### Critical Decisions (Block Phase 1)

1. **Repository Naming Convention**
   - ❓ Allow spaces in repo names? (`my-project` vs `My Project`)
   - ❓ Enforce unique names globally or per-user?
   - ❓ Allow repo aliases/nicknames?

2. **Default Repository Behavior**
   - ❓ Should users explicitly set default repo, or use last active?
   - ❓ What happens if default repo is deleted?
   - ❓ Warn users when no explicit repo specified?

3. **Access Control Granularity**
   - ❓ Need branch-level permissions? (e.g., protect main)
   - ❓ Support repo groups for easier permission management?
   - ❓ Audit log retention policy?

### Important Decisions (Block Phase 3)

4. **Error Recovery**
   - ❓ Auto-retry failed git operations across repos?
   - ❓ Queue requests if repo is locked/busy?
   - ❓ Fallback behavior if repo unavailable?

5. **Performance Optimization**
   - ❓ Cache GitHandler instances? For how long?
   - ❓ Lazy load repo metadata or eager load?
   - ❓ Max number of repos per user?

6. **Migration Timing**
   - ❓ Migrate during maintenance window or live?
   - ❓ Force all users at once or gradual opt-in?
   - ❓ Support both old and new format indefinitely?

### Nice-to-Have Decisions (Post-MVP)

7. **Repository Metadata**
   - ❓ Track repo size, file count, languages?
   - ❓ Store repo health metrics?
   - ❓ Integration with GitHub API for stars, issues?

8. **User Preferences**
   - ❓ Per-user settings for repo behavior?
   - ❓ Notification preferences per repo?
   - ❓ Custom summary formats per repo?

---

## 14. Recommendations & Next Steps

### Immediate Actions (This Week)

1. **Validate Assumptions**
   - [ ] Test Claude Code CLI with different working directories
   - [ ] Verify git operations work with `cwd` parameter
   - [ ] Confirm Twilio SMS character limits with repo names

2. **Stakeholder Alignment**
   - [ ] Review this plan with engineering team
   - [ ] Get user feedback on proposed command syntax
   - [ ] Confirm timeline and resource allocation

3. **Prototype**
   - [ ] Build minimal RepositoryManager (no persistence)
   - [ ] Test directory switching with Claude CLI
   - [ ] Validate command parsing regex patterns

### Week 1 Kickoff

1. **Team Formation**
   - Assign engineers to roles
   - Set up communication channels
   - Schedule daily standups

2. **Environment Setup**
   - Create test repositories (5 sample projects)
   - Set up staging environment
   - Configure CI/CD for new structure

3. **Begin Phase 1**
   - Start `RepositoryManager` implementation
   - Write unit tests in parallel
   - Document decisions in ADR (Architecture Decision Records)

### Success Milestones

- **Week 2:** ✅ Core components implemented, unit tests passing
- **Week 4:** ✅ End-to-end flow working with 2 repos in dev
- **Week 6:** ✅ Data migration completed in staging
- **Week 8:** ✅ Production deployment, 10% user rollout
- **Week 10:** ✅ 100% rollout, monitoring stable

---

## 15. Conclusion

### Strategic Value

Multi-repository support transforms ClaudePing from a **single-project tool** into a **portfolio management platform**. This enhancement:

- **10x User Value:** Manage entire project ecosystem from SMS
- **Market Differentiation:** First multi-repo SMS coding assistant
- **Scalability Foundation:** Architecture supports future multi-tenant features
- **Backward Compatible:** Existing users unaffected during migration

### Investment Summary

- **Timeline:** 8 weeks (2 months)
- **Team Size:** 3 FTEs
- **Risk Level:** Medium (manageable with mitigation strategies)
- **Complexity:** Moderate refactoring, no infrastructure overhaul

### Recommendation

**✅ PROCEED** with phased implementation approach:

1. Build multi-repo foundation (Phases 1-3)
2. Validate with beta users before migration
3. Execute careful data migration (Phase 4)
4. Polish UX and security (Phases 5-6)
5. Launch with gradual rollout (Phase 8)

This plan provides a **robust, secure, and user-friendly** path to multi-repository support while maintaining the simplicity and reliability that makes ClaudePing valuable.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-15
**Status:** DRAFT - Awaiting Approval
**Next Review:** After prototype validation (Week 1)

---

## Appendix A: Command Reference

```
# Repository Management
list repos              → Show all accessible repositories
switch to <repo>        → Change active repository
info <repo>            → Show repository details
repos status           → Status of all repositories

# Inline Repository Targeting
in <repo>: <prompt>    → Execute in specific repo
for <repo>: <prompt>   → Execute in specific repo
@<repo>: <prompt>      → Execute in specific repo

# Admin Commands (future)
register <path> as <name>  → Register new repository
remove repo <name>         → Unregister repository
grant <user> <repo>        → Grant access to user
```

## Appendix B: Data Model Schemas

See sections 3.1 and 3.2 for complete schemas.

## Appendix C: Migration Scripts

See section 6.2 for implementation details.

---

*End of CTO Strategic Plan - Multi-Repository Support*
