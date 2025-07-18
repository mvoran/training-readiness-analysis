# Dependency Management

This project includes automated tools for dependency management that help you maintain a healthy, secure, and up-to-date environment.

## Quick Start

**When you add a new dependency:**
```bash
# 1. Add your dependency to pyproject.toml (see details below)
# 2. Install it
pip install -e .

# 3. Verify everything works
make deps-validate

# 4. Check for any security issues
make deps-security
```

**Before committing code:**
```bash
# 1. Run linting checks (catches formatting issues)
make lint

# 2. If linting fails, auto-fix what can be fixed
make lint-fix

# 3. Quick dependency health check
make deps-check

# 4. If you've been working for a while, run a full check
make deps-full
```

## How to Add Dependencies

The project includes an automated tool to add dependencies. When you add an import like `import requests` to your code, use the automated dependency manager:

```bash
# Add a main dependency
python scripts/manage_deps.py add requests

# Add a development dependency (testing, linting, etc.)
python scripts/manage_deps.py add pytest --dev
```

**What the tool does:**
1. **Installs the package** to get the latest version
2. **Determines the version** automatically
3. **Adds it to pyproject.toml** with proper `>=` version constraint
4. **Checks for duplicates** to avoid conflicts
5. **Maintains formatting** of the TOML file

### Manual Method (if needed)

If you need to add dependencies manually, add them to the appropriate section in `pyproject.toml`:

```toml
dependencies = [
    "pandas>=2.0.0",
    "duckdb>=1.3.0",
    # ... existing dependencies ...
    "requests>=2.31.0",  # Add your new dependency here
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    # ... existing dev dependencies ...
    "your-dev-package>=1.0.0",  # Add here
]
```

**Version constraint patterns:**
- `"requests>=2.31.0"` - At least version 2.31.0 (recommended)
- `"requests==2.31.0"` - Exactly version 2.31.0 (avoid unless necessary)
- `"requests~=2.31.0"` - At least 2.31.0 but less than 2.32.0 (pinned minor)
- `"requests"` - Any version (not recommended for production)

### Quick Workflow
```bash
# 1. Add import to your .py file
# 2. Use automated tool to add dependency
python scripts/manage_deps.py add your-package

# 3. Verify everything works
make deps-validate

# 4. If it works, you're done!
```

## When to Use Each Command

**`make deps-check`** - Your go-to command for:
- Before commits
- After pulling changes
- When something feels "off" with your environment
- Quick validation that dependencies are properly installed

**`make deps-upgradeable`** - Use when:
- You want to see what packages can be updated
- You're curious about dependency constraints
- Planning maintenance work

**`make deps-update`** - Use when:
- You want to update all possible dependencies
- After running `deps-upgradeable` shows available updates
- During scheduled maintenance

**`make deps-security`** - Use when:
- After adding new dependencies
- Before deploying to production
- During security audits

**`make deps-full`** - Use when:
- Setting up a new environment
- Troubleshooting dependency issues
- Comprehensive health check (takes longer)

## Common Scenarios

**Scenario 1: You just added a new package**
```bash
# 1. Use automated tool to add dependency
python scripts/manage_deps.py add your-package

# 2. Verify it works
make deps-validate

# 3. Check for security issues
make deps-security
```

**Scenario 2: You're about to commit**
```bash
# 1. Run linting checks first
make lint

# 2. If linting fails, auto-fix and re-check
make lint-fix
make lint

# 3. Quick dependency check
make deps-check

# 4. If it fails, run full check to understand the issue
make deps-full
```

**Scenario 3: You pulled changes and something broke**
```bash
# 1. Check if dependencies are the issue
make deps-check

# 2. If that doesn't help, run full validation
make deps-full

# 3. Reinstall if needed
pip install -e .
```

**Scenario 4: Monthly maintenance**
```bash
# 1. See what can be updated
make deps-upgradeable

# 2. Update if there are safe updates
make deps-update

# 3. Verify everything still works
make deps-full
```

## What Each Command Does

- **`deps-check`**: Quick validation that all dependencies are properly installed and compatible
- **`deps-upgradeable`**: Shows which packages can be updated vs. which are constrained by other dependencies
- **`deps-update`**: Safely updates all packages that can be upgraded without breaking dependencies
- **`deps-security`**: Checks for known security vulnerabilities in your dependencies
- **`deps-full`**: Comprehensive health check including validation, security, and constraint analysis
- **`deps-validate`**: Verifies your environment is properly set up

## Example Output

When you run `make deps-upgradeable`, you'll see something like:
```bash
🔍 Checking which packages can be upgraded...
📦 Found 5 outdated packages

📊 Summary:
  ✅ Upgradeable: 2 packages (requests, pytest)
  ⚠️  Constrained: 3 packages (duckdb, pydantic, pydantic_core)

💡 Constrained packages cannot be upgraded without breaking other dependencies
💡 Upgradeable packages can be safely updated with: make deps-update
```

## Available Commands

### Using Make Commands
```bash
# Check dependencies
make deps-check

# Check which packages are upgradeable
make deps-upgradeable

# Update dependencies
make deps-update

# Security check
make deps-security

# Full health check
make deps-full

# See all available commands
make help
```

### Using the Python Script Directly
```bash
# Check for outdated packages and conflicts
python scripts/manage_deps.py check

# Check which packages can actually be upgraded vs. constrained
python scripts/manage_deps.py upgradeable

# Update dependencies safely (uses pip's resolver)
python scripts/manage_deps.py update

# Full dependency health check
python scripts/manage_deps.py full

# Validate environment setup
python scripts/manage_deps.py validate

# Security vulnerability check
python scripts/manage_deps.py security

# Show dependency information and constraints
python scripts/manage_deps.py constraints
```
