#!/usr/bin/env python3
"""
Dependency Management Script for Training Readiness Project

This script automates common dependency management tasks:
- Check for outdated packages
- Update dependencies safely
- Verify dependency conflicts
- Generate requirements files
"""

import subprocess
import sys
import argparse
from pathlib import Path
import re


def run_command(cmd, check=True, timeout=30):
    """Run a command and return the result with timeout"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        print(f"  ⏰ Command timed out after {timeout} seconds: {cmd}")
        return "", "Command timed out", 1
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode


def check_outdated():
    """Check for outdated packages"""
    print("🔍 Checking for outdated packages...")
    stdout, stderr, code = run_command("pip list --outdated", check=False)

    if code == 0 and stdout.strip():
        print("📦 Outdated packages found:")
        print(stdout)
        return True
    else:
        print("✅ All packages are up to date!")
        return False


def check_conflicts():
    """Check for dependency conflicts"""
    print("🔍 Checking for dependency conflicts...")
    stdout, stderr, code = run_command("pip check", check=False)

    if code == 0:
        print("✅ No dependency conflicts found!")
        return True
    else:
        print("❌ Dependency conflicts found:")
        print(stderr)
        return False


def check_pyproject_sync():
    """Check if pyproject.toml is in sync with installed packages"""
    print("📋 Checking pyproject.toml sync...")

    # Use pip's built-in tools to check if we can install from pyproject.toml
    stdout, stderr, code = run_command("pip install --dry-run -e .", check=False)
    if code == 0:
        print("  ✅ pyproject.toml can be installed successfully")
        return True
    else:
        print("  ❌ Issues with pyproject.toml installation:")
        print(stderr)
        return False


def check_pyproject_health():
    """Check if pyproject.toml is properly configured"""
    print("📋 Checking pyproject.toml health...")

    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)

    project = config.get("project", {})
    issues_found = False

    # Check required fields
    required_fields = ["name", "version", "dependencies"]
    for field in required_fields:
        if field not in project:
            print(f"  ❌ Missing required field: {field}")
            issues_found = True

    # Check dependencies format
    dependencies = project.get("dependencies", [])
    for dep in dependencies:
        if not (">=" in dep or "==" in dep or "~=" in dep):
            print(f"  ⚠️  Dependency without version constraint: {dep}")

    if not issues_found:
        print("  ✅ pyproject.toml is properly configured")

    return not issues_found


def show_dependency_info():
    """Show dependency information using pip's built-in tools"""
    print("🔍 Analyzing dependencies...")

    # Use pip's built-in conflict checker
    stdout, stderr, code = run_command("pip check", check=False)
    if code == 0:
        print("  ✅ No dependency conflicts found")
    else:
        print("  ❌ Dependency conflicts found:")
        print(stdout)

    # Show what packages are installed
    print("\n📦 Installed packages:")
    stdout, stderr, code = run_command("pip list", check=False)
    if code == 0:
        print(stdout)


def check_upgradeable():
    """Check which packages can actually be upgraded"""
    print("🔍 Checking which packages can be upgraded...")

    # First get the list of outdated packages
    stdout, stderr, code = run_command("pip list --outdated", check=False)
    if code != 0 or not stdout.strip():
        print("✅ No outdated packages found!")
        return

    outdated_packages = []
    for line in stdout.strip().split("\n")[2:]:  # Skip header lines
        if line.strip():
            parts = line.split()
            if len(parts) >= 3:
                package_name = parts[0]
                outdated_packages.append(package_name)

    if not outdated_packages:
        print("✅ No outdated packages found!")
        return

    print(f"📦 Found {len(outdated_packages)} outdated packages")

    # Test upgrading the entire project to see what actually gets upgraded
    print("\n🔍 Testing full project upgrade...")
    stdout, stderr, code = run_command(
        "pip install --upgrade --dry-run -e '.[dev]'", check=False
    )

    if code == 0:
        # Parse the output to see what would be upgraded
        upgradeable = []
        constrained = []

        # Look for packages that would actually be upgraded
        for line in stdout.split("\n"):
            if "Would install" in line:
                # Extract package name from "Would install package-name-version"
                parts = line.split()
                if len(parts) >= 3 and parts[0] == "Would" and parts[1] == "install":
                    package_with_version = parts[2]
                    # Extract package name (remove version suffix)
                    if "-" in package_with_version:
                        package_name = package_with_version.rsplit("-", 1)[0]
                        if package_name in outdated_packages:
                            upgradeable.append(package_name)

        # Any outdated packages not in upgradeable are constrained
        constrained = [pkg for pkg in outdated_packages if pkg not in upgradeable]

        print("\n📊 Summary:")
        print(f"  ✅ Upgradeable: {len(upgradeable)} packages")
        print(f"  ⚠️  Constrained: {len(constrained)} packages")

        if upgradeable:
            print(f"\n📦 Upgradeable packages: {', '.join(upgradeable)}")

        if constrained:
            print(f"\n⚠️  Constrained packages: {', '.join(constrained)}")
            print("💡 These packages are pinned by dependency constraints")
            print("💡 They cannot be upgraded without breaking other dependencies")

            # Show what's constraining them
            print("\n🔍 Checking constraints...")
            for package in constrained:
                print(f"  📋 {package}:")
                # Check what packages require this package
                stdout, stderr, code = run_command(f"pip show {package}", check=False)
                if code == 0:
                    for line in stdout.split("\n"):
                        if line.startswith("Required-by:"):
                            required_by = line.split(":", 1)[1].strip()
                            if required_by and required_by != "None":
                                print(f"    Required by: {required_by}")
                                # Check if the requiring package has version constraints
                                for req_pkg in required_by.split(","):
                                    req_pkg = req_pkg.strip()
                                    # Use pkg_resources to get detailed requirements
                                    stdout2, stderr2, code2 = run_command(
                                        f"python -c \"import pkg_resources; reqs = pkg_resources.get_distribution('{req_pkg}').requires(); print('\\n'.join([str(r) for r in reqs if '{package}' in str(r)]))\"",
                                        check=False,
                                    )
                                    if code2 == 0 and stdout2.strip():
                                        print(
                                            f"      {req_pkg} requires: {stdout2.strip()}"
                                        )
                                    else:
                                        # Fallback to pip show
                                        stdout3, stderr3, code3 = run_command(
                                            f"pip show {req_pkg}", check=False
                                        )
                                        if code3 == 0:
                                            for line3 in stdout3.split("\n"):
                                                if line3.startswith("Requires:"):
                                                    requires = line3.split(":", 1)[
                                                        1
                                                    ].strip()
                                                    if (
                                                        requires
                                                        and requires != "None"
                                                        and package in requires
                                                    ):
                                                        print(
                                                            f"      {req_pkg} requires: {requires}"
                                                        )
    else:
        print("❌ Cannot determine upgradeable packages due to dependency conflicts")
        print("💡 Try 'python scripts/manage_deps.py update' to attempt resolution")


def update_dependencies(force=False):
    """Update dependencies safely"""
    print("🔄 Updating dependencies...")

    # Update pip first
    print("📦 Updating pip...")
    run_command("pip install --upgrade pip")

    # Let pip's dependency resolver handle everything
    print("📦 Updating all packages from pyproject.toml...")
    stdout, stderr, code = run_command("pip install --upgrade -e '.[dev]'", check=False)

    if code != 0:
        print("❌ Update failed. This might be due to dependency conflicts.")
        print(
            "💡 Try running 'pip install --upgrade --force-reinstall -e .[dev]' to force resolution"
        )
        print("💡 Or check for conflicts with 'python scripts/manage_deps.py check'")
        return False

    print("✅ Dependencies updated successfully!")
    return True


def validate_environment():
    """Validate that the environment matches pyproject.toml"""
    print("🔍 Validating environment...")

    # Check if we can install from pyproject.toml
    stdout, stderr, code = run_command("pip install --dry-run -e .", check=False)
    if code == 0:
        print("  ✅ Environment can be installed from pyproject.toml")
        return True
    else:
        print("  ❌ Environment installation issues:")
        print(stderr)
        return False


def security_check():
    """Check for security vulnerabilities"""
    print("🔒 Checking for security vulnerabilities...")

    # Install pip-audit if not present
    stdout, stderr, code = run_command("pip show pip-audit", check=False)
    if code != 0:
        print("📦 Installing pip-audit...")
        run_command("pip install pip-audit")

    # Run security audit
    stdout, stderr, code = run_command("pip-audit", check=False)

    if code == 0:
        print("✅ No security vulnerabilities found!")
    else:
        print("⚠️  Security vulnerabilities found:")
        print(stdout)


def full_check():
    """Run a full dependency health check"""
    print("🏥 Running full dependency health check...\n")

    # Check for outdated packages
    has_outdated = check_outdated()
    print()

    # Check which packages are upgradeable/constrained
    check_upgradeable()
    print()

    # Check for conflicts
    has_conflicts = not check_conflicts()
    print()

    # Check pyproject.toml sync
    has_sync_issues = not check_pyproject_sync()
    print()

    # Check pyproject.toml health
    has_health_issues = not check_pyproject_health()
    print()

    # Validate environment
    has_env_issues = not validate_environment()
    print()

    # Security check
    security_check()
    print()

    # Summary - only count actual issues, not constrained packages
    actual_issues = sum(
        [has_conflicts, has_sync_issues, has_health_issues, has_env_issues]
    )
    if actual_issues > 0:
        print(f"⚠️  {actual_issues} issue(s) found that need attention.")
        if has_conflicts:
            print("💡 Run 'python scripts/manage_deps.py check' to see conflicts")
        if has_sync_issues or has_health_issues:
            print("💡 Check your pyproject.toml configuration")
        if has_env_issues:
            print(
                "💡 Run 'python scripts/manage_deps.py update' to fix environment issues"
            )
    elif has_outdated:
        print(
            "ℹ️  Some packages are outdated but constrained by dependencies (this is normal)"
        )
        print("💡 Run 'python scripts/manage_deps.py upgradeable' for details")
    else:
        print("✅ All dependency checks passed!")


def add_dependency(package_name, version_spec=None, dev=False):
    """Add a new dependency to pyproject.toml and install it"""
    print(f"📦 Adding {package_name} to dependencies...")

    # First, try to install the package to get its version
    install_cmd = f"pip install {package_name}"
    if version_spec:
        install_cmd += f"{version_spec}"

    print(f"🔧 Installing {package_name}...")
    stdout, stderr, code = run_command(install_cmd, check=False)

    if code != 0:
        print(f"❌ Failed to install {package_name}:")
        print(stderr)
        return False

    # Get the installed version
    stdout, stderr, code = run_command(f"pip show {package_name}", check=False)
    if code != 0:
        print(f"❌ Could not get version info for {package_name}")
        return False

    installed_version = None
    for line in stdout.split("\n"):
        if line.startswith("Version:"):
            installed_version = line.split(":", 1)[1].strip()
            break

    if not installed_version:
        print(f"❌ Could not determine version for {package_name}")
        return False

    print(f"📋 Found version: {installed_version}")
    # Read current pyproject.toml
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ pyproject.toml not found")
        return False

    # Parse the TOML content to find dependencies section
    if dev:
        section_pattern = r"\[project\.optional-dependencies\]\s*\n(.*?)(?=\n\[|\Z)"
        section_name = "dev"
    else:
        section_pattern = r"\[project\]\s*\n(.*?)(?=\n\[|\Z)"
        section_name = "dependencies"
    section_match = re.search(section_pattern, content, re.DOTALL)
    if not section_match:
        print(f"❌ Could not find [project.{section_name}] section in pyproject.toml")
        return False

    section_content = section_match.group(1)

    # Check if package is already in dependencies
    if f"{package_name}>=" in section_content or f"{package_name}==" in section_content:
        print(f"⚠️  {package_name} is already in {section_name}")
        return True

    # Add the new dependency
    dependency_line = f"    {package_name}>={installed_version},\n"

    # Find the dependencies list
    if dev:
        deps_pattern = r"(dev\s*=\s*\[)(.*?)(\])"
    else:
        deps_pattern = r"(dependencies\s*=\s*\[)(.*?)(\])"

    deps_match = re.search(deps_pattern, section_content, re.DOTALL)
    if not deps_match:
        print(f"❌ Could not find {section_name} list in pyproject.toml")
        return False

    deps_start = deps_match.group(1)
    deps_content = deps_match.group(2)
    deps_end = deps_match.group(3)

    # Add the new dependency to the list
    new_deps_content = deps_content.rstrip() + "\n" + dependency_line

    # Replace the dependencies section
    new_section_content = section_content.replace(
        deps_start + deps_content + deps_end, deps_start + new_deps_content + deps_end
    )

    # Replace the section in the full content
    new_content = content.replace(section_content, new_section_content)

    # Write back to pyproject.toml
    try:
        with open("pyproject.toml", "w") as f:
            f.write(new_content)
        print(f"✅ Added {package_name}>=[{installed_version}] to {section_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to write pyproject.toml: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Manage project dependencies")
    parser.add_argument(
        "action",
        choices=[
            "check",
            "update",
            "validate",
            "security",
            "sync",
            "constraints",
            "upgradeable",
            "full",
            "add",
        ],
        help="Action to perform",
    )
    parser.add_argument(
        "--force", action="store_true", help="Force updates even if conflicts exist"
    )
    parser.add_argument(
        "--dev", action="store_true", help="Add to dev dependencies (for add' action)"
    )
    parser.add_argument(
        "package", nargs="?", help="Package name to add (for add action)"
    )

    args = parser.parse_args()

    # Ensure we're in the project root
    if not Path("pyproject.toml").exists():
        print(
            "❌ Error: pyproject.toml not found. Run this script from the project root."
        )
        sys.exit(1)

    if args.action == "add":
        if not args.package:
            print("❌ Error: Package name required for 'add' action")
            print("Usage: python scripts/manage_deps.py add <package_name> [--dev]")
            sys.exit(1)

        success = add_dependency(args.package, dev=args.dev)
        if success:
            print(f"✅ Successfully added {args.package} to pyproject.toml")
            print(
                "💡 Run 'python scripts/manage_deps.py update' to ensure everything is in sync"
            )
        else:
            print(f"❌ Failed to add {args.package}")
            sys.exit(1)

    elif args.action == "check":
        check_outdated()
        print()
        check_conflicts()

    elif args.action == "update":
        update_dependencies(force=args.force)

    elif args.action == "validate":
        validate_environment()

    elif args.action == "security":
        security_check()

    elif args.action == "sync":
        check_pyproject_sync()
        print()
        check_pyproject_health()

    elif args.action == "constraints":
        show_dependency_info()

    elif args.action == "upgradeable":
        check_upgradeable()

    elif args.action == "full":
        full_check()


if __name__ == "__main__":
    main()
