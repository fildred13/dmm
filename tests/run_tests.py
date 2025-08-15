#!/usr/bin/env python3
"""
Test runner script for the Media Management Tool
"""

import sys
import subprocess
import os


def run_tests():
    """Run the test suite"""
    print("🧪 Running Media Management Tool Test Suite")
    print("=" * 50)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest is not installed. Please install it with:")
        print("   pip install pytest pytest-cov pytest-mock")
        return 1
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=media_processor",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode


def run_specific_tests(test_path=None):
    """Run specific tests"""
    if test_path is None:
        return run_tests()
    
    cmd = [sys.executable, "-m", "pytest", test_path, "-v"]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Tests in {test_path} passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests in {test_path} failed with exit code {e.returncode}")
        return e.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_path = sys.argv[1]
        exit_code = run_specific_tests(test_path)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code)
