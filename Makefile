.PHONY: help install test test-cov lint lint-fix deps-check deps-update deps-security clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install project dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run all linting checks (before commit)"
	@echo "  lint-fix     - Run linting and auto-fix what can be fixed"
	@echo "  deps-check   - Check for outdated packages and conflicts"
	@echo "  deps-update  - Update dependencies safely"
	@echo "  deps-security- Check for security vulnerabilities"
	@echo "  deps-full    - Full dependency health check"
	@echo "  clean        - Clean up temporary files"

# Install dependencies
install:
	pip install -e ".[dev]"

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=src/training_readiness --cov-report=html

# Run all linting checks (use before commit)
lint:
	@echo "🔍 Running linting checks..."
	@pre-commit run --all-files

# Run linting and auto-fix what can be fixed
lint-fix:
	@echo "🔧 Running linting with auto-fixes..."
	@pre-commit run --all-files --hook-stage manual

# Check dependencies
deps-check:
	@echo "🔍 Checking for outdated packages..."
	@pip list --outdated || echo "✅ All packages up to date"
	@echo ""
	@echo "🔍 Checking for dependency conflicts..."
	@pip check || echo "❌ Conflicts found"
	@echo ""
	@echo "📋 Checking pyproject.toml sync..."
	@python scripts/manage_deps.py sync

# Check which packages can be upgraded
deps-upgradeable:
	@python scripts/manage_deps.py upgradeable

# Update dependencies
deps-update:
	@echo "🔄 Updating dependencies..."
	@python scripts/manage_deps.py update

# Security check
deps-security:
	@echo "🔒 Checking for security vulnerabilities..."
	@pip install safety 2>/dev/null || true
	@safety check || echo "⚠️  Security issues found"

# Full dependency health check
deps-full: deps-check deps-security
	@echo "🏥 Full dependency health check complete!"

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
