#!/usr/bin/env python3
"""
Setup and Run Script for Insurance Document Q&A System
Checks dependencies, sets up environment, and runs tests
"""

import os
import sys
import subprocess
from pathlib import Path
from loguru import logger

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    logger.info("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def check_environment():
    """Check environment setup"""
    logger.info("Checking environment...")
    
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        logger.warning("OPENROUTER_API_KEY not set. You'll need to set this before running tests.")
        print("\nTo set your API key:")
        print("export OPENROUTER_API_KEY='your_api_key_here'")
        return False
    
    # Check dataset directory
    dataset_path = Path("./dataset")
    if not dataset_path.exists():
        logger.error("Dataset directory not found")
        return False
    
    pdf_files = list(dataset_path.glob("*.pdf"))
    if not pdf_files:
        logger.error("No PDF files found in dataset directory")
        return False
    
    logger.info(f"Found {len(pdf_files)} PDF files in dataset")
    return True

def run_tests():
    """Run the test suite"""
    logger.info("Starting test suite...")
    try:
        subprocess.check_call([sys.executable, "test_runner.py"])
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Test suite failed: {e}")
        return False

def main():
    """Main setup and run function"""
    print("Insurance Document Q&A System - Setup and Run")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Check environment
    if not check_environment():
        print("\nEnvironment check failed. Please fix the issues above and try again.")
        return 1
    
    # Run tests
    print("\nStarting test execution...")
    if run_tests():
        print("\n✅ All tests completed successfully!")
        return 0
    else:
        print("\n❌ Tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)