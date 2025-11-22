#!/usr/bin/env python3
"""
Domain Finder - Environment Validation Script
Validates that all dependencies and configuration are correct.

Version: 1.0
Date: 2025-11-15
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.NC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.NC}")

def check_python_version():
    """Check Python version is 3.8+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.8+ required (found: {version.major}.{version.minor}.{version.micro})")
        return False

def check_dependencies():
    """Check required packages are installed"""
    required_packages = [
        'requests',
        'pandas',
        'dotenv',
        'yaml'
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            elif package == 'yaml':
                __import__('yaml')
            else:
                __import__(package)
            print_success(f"Package '{package}' installed")
        except ImportError:
            print_error(f"Package '{package}' NOT installed")
            all_installed = False
    
    return all_installed

def check_env_file():
    """Check .env file exists and has required variables"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print_error(".env file NOT found")
        print_info("Run: cp .env.example .env")
        return False
    
    print_success(".env file exists")
    
    # Check for required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['GOOGLE_API_KEY', 'GOOGLE_CSE_ID']
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f'your_{var.lower()}_here':
            # Mask the actual value for security
            if 'KEY' in var:
                masked = value[:10] + '...' if len(value) > 10 else value
            else:
                masked = value[:8] + '...' if len(value) > 8 else value
            print_success(f"{var} = {masked}")
        elif value == f'your_{var.lower()}_here':
            print_warning(f"{var} still has placeholder value")
            print_info(f"Edit .env and add your actual {var}")
            all_present = False
        else:
            print_error(f"{var} NOT found in .env")
            all_present = False
    
    return all_present

def check_directory_structure():
    """Check required directories exist"""
    required_dirs = [
        'data/input',
        'data/output',
        'logs',
        'src',
        'scripts',
        'docs'
    ]
    
    all_exist = True
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"Directory '{dir_path}' exists")
        else:
            print_error(f"Directory '{dir_path}' NOT found")
            all_exist = False
    
    return all_exist

def check_input_file():
    """Check input CSV file exists"""
    input_file = Path('data/input/schools_womens_volleyball_all_divisions.csv')
    
    if input_file.exists():
        size = input_file.stat().st_size / 1024  # KB
        print_success(f"Input file exists ({size:.1f} KB)")
        return True
    else:
        print_error("Input CSV file NOT found")
        return False

def check_config_file():
    """Check config.yaml file exists"""
    config_file = Path('config.yaml')
    
    if config_file.exists():
        print_success("config.yaml exists")
        
        # Try to parse it
        try:
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            print_success("config.yaml is valid YAML")
            return True
        except Exception as e:
            print_error(f"config.yaml has syntax errors: {e}")
            return False
    else:
        print_warning("config.yaml NOT found (will use defaults)")
        return True  # Not critical

def main():
    """Main validation function"""
    print("\n" + "="*70)
    print("🔍 DOMAIN FINDER - ENVIRONMENT VALIDATION")
    print("="*70 + "\n")
    
    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Environment Variables": check_env_file(),
        "Directory Structure": check_directory_structure(),
        "Input File": check_input_file(),
        "Configuration": check_config_file()
    }
    
    print("\n" + "="*70)
    print("📊 VALIDATION SUMMARY")
    print("="*70 + "\n")
    
    all_passed = True
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:.<30} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*70)
    
    if all_passed:
        print_success("🎉 ALL CHECKS PASSED!")
        print("\nYou're ready to run:")
        print_info("   python src/domain_finder.py")
    else:
        print_error("❌ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running.")
        print_info("See USAGE_GUIDE.md for detailed instructions")
        sys.exit(1)
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()