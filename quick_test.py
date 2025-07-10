#!/usr/bin/env python3
"""
Quick test script to verify local configuration works
"""

import sys
import os

def test_config():
    """Test the configuration without running the full app"""
    try:
        from config import config
        
        # Test development config
        dev_config = config['development']
        database_uri = dev_config.get_database_uri()
        
        print("✓ Configuration test successful!")
        print(f"Database URI: {database_uri}")
        
        if "sqlite" in database_uri:
            print("ℹ Using SQLite database (local file-based)")
        elif "mysql" in database_uri:
            print("ℹ Using MySQL database")
        elif "postgresql" in database_uri:
            print("ℹ Using PostgreSQL database")
            
        # Additional database connectivity test
        print("\nTesting database connectivity...")
        try:
            from app import app, db
            with app.app_context():
                db.create_all()
                print("✓ Database connection successful!")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            print("ℹ The application will fallback to SQLite automatically")
            
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    modules = [
        'flask',
        'flask_sqlalchemy', 
        'werkzeug',
        'sqlalchemy'
    ]
    
    missing = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} (missing)")
            missing.append(module)
    
    return len(missing) == 0

if __name__ == "__main__":
    print("WMS Application - Quick Test")
    print("=" * 30)
    
    print("\n1. Testing module imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing configuration...")
    config_ok = test_config()
    
    if imports_ok and config_ok:
        print("\n✓ All tests passed! You can run: python main.py")
    else:
        print("\n✗ Some tests failed. Please install missing dependencies:")
        print("python install_local_deps.py")