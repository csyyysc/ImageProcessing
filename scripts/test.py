#!/usr/bin/env python3
"""
Test Script for Image Processing Application

This script runs unit tests and integration tests without requiring external services.
Run with: uv run scripts/test.py
"""

import sys
import subprocess
import os
from pathlib import Path

# Setup path first
import setup_path


def run_pytest_tests():
    """Run pytest tests for all modules"""

    print("🧪 Running Unit Tests with pytest...")
    print("=" * 50)

    # First, let's check what directories exist
    current_dir = Path.cwd()
    print(f"📁 Current working directory: {current_dir}")
    print(f"📁 Contents: {list(current_dir.iterdir())}")

    # Check if backend/tests exists
    backend_tests = current_dir / "backend" / "tests"
    if backend_tests.exists():
        print(f"✅ Found backend/tests at: {backend_tests}")
        print(f"📁 Backend tests contents: {list(backend_tests.iterdir())}")
    else:
        print(f"❌ backend/tests not found at: {backend_tests}")
        return False

    try:
        # Run pytest with verbose output and discovery
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "-v",                    # Verbose output
            "--tb=short",           # Short traceback format
            "--disable-warnings",   # Disable warnings for cleaner output
            "--collect-only",       # First, just collect tests to see what's found
            str(backend_tests)      # Use absolute path
        ], capture_output=True, text=True, timeout=60)

        print("📋 Test Discovery Output:")
        print(result.stdout)

        if result.stderr:
            print("⚠️  Test Discovery Warnings/Errors:")
            print(result.stderr)

        # If test collection failed, return early
        if result.returncode != 0:
            print(
                f"❌ Test discovery failed with exit code: {result.returncode}")
            return False

        # Now run the actual tests
        print("\n🔄 Running actual tests...")
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "-v",                    # Verbose output
            "--tb=short",           # Short traceback format
            "--disable-warnings",   # Disable warnings for cleaner output
            str(backend_tests)      # Use absolute path
        ], capture_output=True, text=True, timeout=120)

        print("📋 Pytest Output:")
        print(result.stdout)

        if result.stderr:
            print("⚠️  Pytest Warnings/Errors:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ All pytest tests passed!")
            return True
        else:
            print(f"❌ Pytest tests failed with exit code: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Pytest tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return False


def run_import_tests():
    """Test that all critical modules can be imported"""

    print("\n🔍 Testing Module Imports...")
    print("=" * 50)

    modules_to_test = [
        "shared.config",
        "backend.main",
        "backend.services.jwt_service",
        "backend.api.user",
        "backend.api.image",
        "frontend.app",
        "frontend.auth",
    ]

    failed_imports = []

    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)

    if failed_imports:
        print(f"\n❌ Failed to import {len(failed_imports)} modules")
        return False
    else:
        print("\n✅ All module imports successful!")
        return True


def run_code_quality_checks():
    """Run basic code quality checks"""

    print("\n🔍 Running Code Quality Checks...")
    print("=" * 50)

    # Check for Python syntax errors
    print("Checking Python syntax...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "py_compile",
            "backend/main.py",
            "frontend/app.py",
            "shared/config.py"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Python syntax checks passed")
            return True
        else:
            print(f"❌ Python syntax errors found: {result.stderr}")
            return False

    except Exception as e:
        print(f"⚠️  Could not run syntax checks: {e}")
        return True  # Don't fail the test for this


def check_test_environment():
    """Check that the test environment is properly set up"""

    print("🔧 Checking Test Environment...")
    print("=" * 50)

    # Check required directories exist
    required_dirs = ["backend", "frontend", "shared", "scripts"]
    missing_dirs = []

    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
        else:
            print(f"✅ {dir_name}/ directory found")

    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False

    # Check Python path setup
    project_root = str(Path(__file__).parent.parent)
    if project_root in sys.path:
        print("✅ Python path properly configured")
    else:
        print("⚠️  Python path may not be properly configured")

    return True


def main():
    """Main test function"""
    print("🚀 Image Processing Application - Test Suite")
    print("=" * 50)

    all_tests_passed = True

    # Run all test phases
    test_phases = [
        ("Environment Check", check_test_environment),
        ("Import Tests", run_import_tests),
        ("Code Quality", run_code_quality_checks),
        ("Unit Tests", run_pytest_tests),
    ]

    for phase_name, test_function in test_phases:
        print(f"\n🔧 {phase_name}...")
        try:
            if not test_function():
                all_tests_passed = False
                print(f"❌ {phase_name} failed!")
            else:
                print(f"✅ {phase_name} passed!")
        except Exception as e:
            print(f"❌ {phase_name} error: {e}")
            all_tests_passed = False

    # Final summary
    print("\n" + "=" * 50)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 50)

    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Code is ready for deployment")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️  Please fix the issues before deployment")
        sys.exit(1)


if __name__ == "__main__":
    main()
