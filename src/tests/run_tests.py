# run_tests.py
import pytest
import sys

def main():
    """Run all tests"""
    args = [
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "tests/"
    ]
    
    # Run tests
    result = pytest.main(args)
    
    # Exit with test result
    sys.exit(result)

if __name__ == "__main__":
    main()