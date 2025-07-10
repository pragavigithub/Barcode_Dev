#!/usr/bin/env python3
"""
Local development dependency installer for WMS Application
Run this script to install all required dependencies for local development
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}: {e}")
        return False

def check_package(package):
    """Check if a package is already installed"""
    try:
        __import__(package)
        print(f"✓ {package} is already installed")
        return True
    except ImportError:
        print(f"✗ {package} is not installed")
        return False

def main():
    print("WMS Application - Local Development Setup")
    print("=" * 50)
    
    # Required packages for local development
    packages = {
        'flask': 'flask',
        'flask_sqlalchemy': 'flask-sqlalchemy',
        'pymysql': 'pymysql',
        'werkzeug': 'werkzeug',
        'sqlalchemy': 'sqlalchemy',
        'pillow': 'pillow',
        'qrcode': 'qrcode[pil]',
        'requests': 'requests',
        'gunicorn': 'gunicorn',
        'email_validator': 'email-validator',
        'pyjwt': 'pyjwt'
    }
    
    print("\nChecking installed packages...")
    missing_packages = []
    
    for import_name, pip_name in packages.items():
        if not check_package(import_name):
            missing_packages.append(pip_name)
    
    if not missing_packages:
        print("\n✓ All required packages are installed!")
        print("\nYou can now run the application with:")
        print("python main.py")
        return
    
    print(f"\nFound {len(missing_packages)} missing packages:")
    for package in missing_packages:
        print(f"  - {package}")
    
    # Ask user for confirmation
    response = input("\nDo you want to install missing packages? (y/n): ")
    if response.lower() not in ['y', 'yes']:
        print("Installation cancelled. Please install packages manually:")
        print(f"pip install {' '.join(missing_packages)}")
        return
    
    print("\nInstalling missing packages...")
    failed_packages = []
    
    for package in missing_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Failed to install {len(failed_packages)} packages:")
        for package in failed_packages:
            print(f"  - {package}")
        print("\nPlease install them manually:")
        print(f"pip install {' '.join(failed_packages)}")
    else:
        print("\n✓ All packages installed successfully!")
    
    print("\nNext steps:")
    print("1. Set up your MySQL database (see local_setup.md)")
    print("2. Configure environment variables")
    print("3. Run: python main.py")

if __name__ == "__main__":
    main()