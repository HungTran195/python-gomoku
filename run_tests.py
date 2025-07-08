#!/usr/bin/env python3
"""
Test runner for the Gomoku game project
"""

import sys
import os
import subprocess
from pathlib import Path

def run_unittest_tests():
    """Run unittest-based tests"""
    print("Running unittest tests...")
    print("=" * 50)
    
    # Run the unit tests
    test_file = Path(__file__).parent / "tests" / "unit" / "test_game.py"
    
    if test_file.exists():
        result = subprocess.run([
            sys.executable, "-m", "unittest", str(test_file), "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    else:
        print(f"Test file not found: {test_file}")
        return False

def run_pytest_tests():
    """Run pytest-based tests"""
    print("\nRunning pytest tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except FileNotFoundError:
        print("pytest not found. Install it with: pip install pytest")
        return False

def run_specific_test(test_name):
    """Run a specific test"""
    print(f"Running specific test: {test_name}")
    print("=" * 50)
    
    test_file = Path(__file__).parent / "tests" / "unit" / "test_game.py"
    
    if test_file.exists():
        result = subprocess.run([
            sys.executable, "-m", "unittest", f"test_game.{test_name}", "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    else:
        print(f"Test file not found: {test_file}")
        return False

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "unittest":
            success = run_unittest_tests()
        elif command == "pytest":
            success = run_pytest_tests()
        elif command == "all":
            success1 = run_unittest_tests()
            success2 = run_pytest_tests()
            success = success1 and success2
        elif command == "specific" and len(sys.argv) > 2:
            success = run_specific_test(sys.argv[2])
        else:
            print("Usage:")
            print("  python run_tests.py unittest    - Run unittest tests")
            print("  python run_tests.py pytest      - Run pytest tests")
            print("  python run_tests.py all         - Run all tests")
            print("  python run_tests.py specific <test_name> - Run specific test")
            return 1
    else:
        # Default: run unittest tests
        success = run_unittest_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 