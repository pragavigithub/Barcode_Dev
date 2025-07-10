#!/usr/bin/env python3
"""
Test MySQL connection directly
"""

import os
import sys

def test_mysql_connection():
    """Test MySQL connection with different configurations"""
    print("MySQL Connection Test")
    print("=" * 30)
    
    # Test 1: Check if pymysql is installed
    try:
        import pymysql
        print("✓ pymysql is installed")
    except ImportError:
        print("✗ pymysql is not installed")
        print("Run: pip install pymysql")
        return False
    
    # Test 2: Get connection parameters
    configurations = [
        {
            'name': 'From Environment Variables',
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', ''),
            'database': os.environ.get('MYSQL_DATABASE', 'wms_db'),
            'port': int(os.environ.get('MYSQL_PORT', '3306'))
        },
        {
            'name': 'Default Root Configuration',
            'host': 'localhost',
            'user': 'root',
            'password': 'root@123',
            'database': 'wms_db',
            'port': 3306
        },
        {
            'name': 'Alternative Root Configuration',
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'test',
            'port': 3306
        }
    ]
    
    success = False
    
    for config in configurations:
        print(f"\n--- Testing {config['name']} ---")
        print(f"Host: {config['host']}")
        print(f"User: {config['user']}")
        print(f"Password: {'*' * len(config['password']) if config['password'] else '(empty)'}")
        print(f"Database: {config['database']}")
        print(f"Port: {config['port']}")
        
        try:
            connection = pymysql.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                port=config['port'],
                connect_timeout=5
            )
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"✓ Connection successful! MySQL version: {version[0]}")
                success = True
                break
                
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            
            # Provide specific error guidance
            if "Access denied" in str(e):
                print("  → Check username/password")
            elif "Unknown database" in str(e):
                print("  → Database doesn't exist, create it first")
            elif "Can't connect" in str(e):
                print("  → MySQL server is not running")
            elif "getaddrinfo failed" in str(e):
                print("  → Check hostname/IP address")
    
    if not success:
        print("\n❌ All MySQL connections failed!")
        print("\nNext steps:")
        print("1. Make sure MySQL is running")
        print("2. Create the database: CREATE DATABASE wms_db;")
        print("3. Check your MySQL username/password")
        print("4. The app will automatically use SQLite if MySQL fails")
        
    return success

if __name__ == "__main__":
    test_mysql_connection()