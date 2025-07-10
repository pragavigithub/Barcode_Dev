#!/usr/bin/env python3
"""
Create admin user for local development
Run this script after the application starts successfully
"""

import sys
import os

def create_admin_user():
    """Create admin user in the database"""
    try:
        from app import app, db
        from models import User, UserRole
        
        with app.app_context():
            # Check if admin user already exists
            existing_admin = User.query.filter_by(username='admin').first()
            if existing_admin:
                print("✓ Admin user already exists")
                print("Username: admin")
                print("Password: admin123")
                return True
            
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@wms.com',
                full_name='Administrator',
                role=UserRole.ADMIN,
                branch_id='MAIN',
                is_active=True
            )
            admin_user.set_password('admin123')
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✓ Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
            print("Role: ADMIN")
            print("Branch ID: MAIN")
            
            return True
            
    except Exception as e:
        print(f"✗ Failed to create admin user: {e}")
        return False

if __name__ == "__main__":
    print("WMS Application - Admin User Setup")
    print("=" * 40)
    
    if create_admin_user():
        print("\nYou can now login to the application at: http://localhost:5000")
    else:
        print("\nPlease ensure the application is properly configured and try again.")