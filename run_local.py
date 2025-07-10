#!/usr/bin/env python3
"""
Local development runner with better error handling
"""

import os
import sys
import logging

def setup_environment():
    """Set up minimal environment for local development"""
    # Set default environment variables if not set
    if not os.environ.get("SESSION_SECRET"):
        os.environ["SESSION_SECRET"] = "dev-secret-key-local-2024"
    
    # Clear any problematic DATABASE_URL
    if os.environ.get("DATABASE_URL"):
        print("Found DATABASE_URL, keeping it...")
    else:
        print("No DATABASE_URL found, will use auto-detection...")

def main():
    print("WMS Application - Local Development Runner")
    print("=" * 45)
    
    # Setup environment
    setup_environment()
    
    try:
        print("Starting application...")
        from app import app
        
        print(f"✓ Application initialized successfully")
        print(f"✓ Database configured")
        print(f"✓ Ready to start server")
        
        # Check if we should create admin user
        try:
            from models import User
            with app.app_context():
                if not User.query.filter_by(username='admin').first():
                    print("\n⚠ No admin user found. Creating one...")
                    exec(open('create_admin_user.py').read())
        except Exception as e:
            print(f"⚠ Could not check/create admin user: {e}")
        
        print("\nStarting Flask development server...")
        print("Access the application at: http://localhost:5000")
        print("Login with: admin / admin123")
        print("\nPress Ctrl+C to stop the server")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"✗ Failed to start application: {e}")
        print("\nTroubleshooting steps:")
        print("1. Install dependencies: python install_local_deps.py")
        print("2. Check configuration: python quick_test.py")
        print("3. Review local_setup.md for detailed setup instructions")
        sys.exit(1)

if __name__ == "__main__":
    main()