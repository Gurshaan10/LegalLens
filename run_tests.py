#!/usr/bin/env python3
"""
Test runner script for Legal Lens
Runs all tests with coverage and generates reports
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    parser = argparse.ArgumentParser(description='Run Legal Lens tests')
    parser.add_argument('--backend', action='store_true', help='Run only backend tests')
    parser.add_argument('--frontend', action='store_true', help='Run only frontend tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent
    backend_dir = project_root / 'backend'
    frontend_dir = project_root / 'frontend'
    
    print("🧪 Legal Lens Test Runner")
    print("=" * 50)
    
    success = True
    
    # Backend tests
    if not args.frontend:
        print("\n🔧 Running Backend Tests...")
        backend_success = run_backend_tests(backend_dir, args)
        success = success and backend_success
    
    # Frontend tests
    if not args.backend:
        print("\n⚛️  Running Frontend Tests...")
        frontend_success = run_frontend_tests(frontend_dir, args)
        success = success and frontend_success
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

def run_backend_tests(backend_dir, args):
    """Run backend tests"""
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Install test dependencies if needed
    print("📦 Installing test dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    # Run tests
    test_command = "pytest"
    if args.verbose:
        test_command += " -v"
    if args.coverage:
        test_command += " --cov=. --cov-report=term-missing"
    if args.html:
        test_command += " --cov-report=html"
    
    print(f"🔍 Running: {test_command}")
    success, stdout, stderr = run_command(test_command)
    
    if success:
        print("✅ Backend tests passed!")
        if stdout:
            print(stdout)
    else:
        print("❌ Backend tests failed!")
        if stderr:
            print(stderr)
    
    return success

def run_frontend_tests(frontend_dir, args):
    """Run frontend tests"""
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if package.json exists
    package_json = frontend_dir / 'package.json'
    if not package_json.exists():
        print("❌ Frontend package.json not found")
        return False
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Install dependencies
    print("📦 Installing frontend dependencies...")
    success, stdout, stderr = run_command("npm install")
    if not success:
        print(f"❌ Failed to install frontend dependencies: {stderr}")
        return False
    
    # Run tests
    test_command = "npm test"
    if args.verbose:
        test_command += " -- --verbose"
    if args.coverage:
        test_command += " -- --coverage"
    
    print(f"🔍 Running: {test_command}")
    success, stdout, stderr = run_command(test_command)
    
    if success:
        print("✅ Frontend tests passed!")
        if stdout:
            print(stdout)
    else:
        print("❌ Frontend tests failed!")
        if stderr:
            print(stderr)
    
    return success

if __name__ == "__main__":
    sys.exit(main()) 