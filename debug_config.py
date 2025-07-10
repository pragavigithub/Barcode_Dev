#!/usr/bin/env python3
"""
Debug configuration and environment variables
"""

import os

def debug_environment():
    """Debug environment variables and configuration"""
    print("Environment Variables Debug")
    print("=" * 40)
    
    # Check all MySQL related environment variables
    mysql_vars = [
        'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_HOST', 
        'MYSQL_PORT', 'MYSQL_DATABASE', 'DATABASE_URL'
    ]
    
    print("\nMySQL Environment Variables:")
    for var in mysql_vars:
        value = os.environ.get(var)
        if value:
            # Hide password for security
            if 'PASSWORD' in var:
                print(f"  {var}: {'*' * len(value)}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: NOT SET")
    
    # Test configuration
    print("\nTesting Configuration:")
    try:
        from config import config
        dev_config = config['development']
        database_uri = dev_config.get_database_uri()
        
        print(f"Database URI: {database_uri}")
        
        if "sqlite" in database_uri:
            print("Status: Using SQLite (fallback)")
        elif "mysql" in database_uri:
            print("Status: Using MySQL configuration")
        elif "postgresql" in database_uri:
            print("Status: Using PostgreSQL")
            
    except Exception as e:
        print(f"Configuration Error: {e}")
    
    # Test database connection
    print("\nTesting Database Connection:")
    try:
        from app import app, db
        with app.app_context():
            # Try to connect to database
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("This is expected if MySQL isn't running or configured")

if __name__ == "__main__":
    debug_environment()