#!/usr/bin/env python3
"""
Create sample data for local development and testing
"""

import sys
import os
from datetime import datetime, date

def create_sample_data():
    """Create sample purchase orders and users"""
    try:
        from app import app, db
        from models import User, UserRole, PurchaseOrder, PurchaseOrderLine
        
        with app.app_context():
            print("Creating sample data...")
            
            # Create sample purchase orders
            sample_pos = [
                {
                    'po_number': 'PO-2024-001',
                    'supplier_code': 'SUP001',
                    'supplier_name': 'ABC Suppliers Ltd',
                    'branch_id': 'MAIN',
                    'po_date': date(2024, 7, 1),
                    'delivery_date': date(2024, 7, 15),
                    'total_amount': 15000.00,
                    'currency': 'USD',
                    'status': 'Open',
                    'lines': [
                        {
                            'line_number': 1,
                            'item_code': 'ITEM001',
                            'item_description': 'Premium Office Chair',
                            'ordered_quantity': 10,
                            'unit_price': 250.00,
                            'unit_of_measure': 'PCS',
                            'warehouse_code': 'WH01'
                        },
                        {
                            'line_number': 2,
                            'item_code': 'ITEM002', 
                            'item_description': 'Desk Lamp LED',
                            'ordered_quantity': 20,
                            'unit_price': 45.00,
                            'unit_of_measure': 'PCS',
                            'warehouse_code': 'WH01'
                        },
                        {
                            'line_number': 3,
                            'item_code': 'ITEM003',
                            'item_description': 'Wireless Mouse',
                            'ordered_quantity': 50,
                            'unit_price': 25.00,
                            'unit_of_measure': 'PCS',
                            'warehouse_code': 'WH01'
                        }
                    ]
                },
                {
                    'po_number': 'PO-2024-002',
                    'supplier_code': 'SUP002',
                    'supplier_name': 'Tech Solutions Inc',
                    'branch_id': 'MAIN',
                    'po_date': date(2024, 7, 5),
                    'delivery_date': date(2024, 7, 20),
                    'total_amount': 8500.00,
                    'currency': 'USD',
                    'status': 'Open',
                    'lines': [
                        {
                            'line_number': 1,
                            'item_code': 'ITEM004',
                            'item_description': 'Laptop Stand Adjustable',
                            'ordered_quantity': 15,
                            'unit_price': 75.00,
                            'unit_of_measure': 'PCS',
                            'warehouse_code': 'WH01'
                        },
                        {
                            'line_number': 2,
                            'item_code': 'ITEM005',
                            'item_description': 'USB Hub 4-Port',
                            'ordered_quantity': 30,
                            'unit_price': 35.00,
                            'unit_of_measure': 'PCS',
                            'warehouse_code': 'WH01'
                        }
                    ]
                },
                {
                    'po_number': 'PO-2024-003',
                    'supplier_code': 'SUP003',
                    'supplier_name': 'Global Supplies Co',
                    'branch_id': 'MAIN',
                    'po_date': date(2024, 7, 8),
                    'delivery_date': date(2024, 7, 25),
                    'total_amount': 12000.00,
                    'currency': 'USD',
                    'status': 'Open',
                    'lines': [
                        {
                            'line_number': 1,
                            'item_code': 'ITEM006',
                            'item_description': 'Conference Table 8-Seater',
                            'ordered_quantity': 2,
                            'unit_price': 1200.00,
                            'unit_of_measure': 'PCS',
                            'warehouse_code': 'WH01'
                        },
                        {
                            'line_number': 2,
                            'item_code': 'ITEM007',
                            'item_description': 'Office Cabinet 4-Drawer',
                            'ordered_quantity': 8,
                            'unit_price': 350.00,
                            'unit_of_measure': 'PCS',
                            'warehouse_code': 'WH01'
                        },
                        {
                            'line_number': 3,
                            'item_code': 'ITEM008',
                            'item_description': 'Whiteboard Magnetic',
                            'ordered_quantity': 5,
                            'unit_price': 180.00,
                            'unit_of_measure': 'PCS',
                            'warehouse_code': 'WH01'
                        }
                    ]
                }
            ]
            
            # Create purchase orders
            for po_data in sample_pos:
                # Check if PO already exists
                existing_po = PurchaseOrder.query.filter_by(po_number=po_data['po_number']).first()
                if existing_po:
                    print(f"PO {po_data['po_number']} already exists, skipping...")
                    continue
                
                po = PurchaseOrder(
                    po_number=po_data['po_number'],
                    supplier_code=po_data['supplier_code'],
                    supplier_name=po_data['supplier_name'],
                    branch_id=po_data['branch_id'],
                    po_date=po_data['po_date'],
                    delivery_date=po_data['delivery_date'],
                    total_amount=po_data['total_amount'],
                    currency=po_data['currency'],
                    status=po_data['status']
                )
                
                db.session.add(po)
                db.session.flush()  # Get the PO ID
                
                # Add PO lines
                for line_data in po_data['lines']:
                    po_line = PurchaseOrderLine(
                        po_id=po.id,
                        line_number=line_data['line_number'],
                        item_code=line_data['item_code'],
                        item_description=line_data['item_description'],
                        ordered_quantity=line_data['ordered_quantity'],
                        unit_price=line_data['unit_price'],
                        unit_of_measure=line_data['unit_of_measure'],
                        warehouse_code=line_data['warehouse_code']
                    )
                    db.session.add(po_line)
                
                print(f"✓ Created PO: {po_data['po_number']}")
            
            # Create admin user if not exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@wms.com',
                    full_name='System Administrator',
                    role=UserRole.ADMIN,
                    branch_id='MAIN',
                    is_active=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                print("✓ Created admin user")
            
            # Create test users
            test_users = [
                {
                    'username': 'warehouse1',
                    'email': 'warehouse1@wms.com',
                    'full_name': 'Warehouse Staff 1',
                    'role': UserRole.WAREHOUSE_STAFF,
                    'password': 'warehouse123'
                },
                {
                    'username': 'qc1',
                    'email': 'qc1@wms.com',
                    'full_name': 'QC Staff 1',
                    'role': UserRole.QC_STAFF,
                    'password': 'qc123'
                },
                {
                    'username': 'manager1',
                    'email': 'manager1@wms.com',
                    'full_name': 'Warehouse Manager',
                    'role': UserRole.MANAGER,
                    'password': 'manager123'
                }
            ]
            
            for user_data in test_users:
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if not existing_user:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        full_name=user_data['full_name'],
                        role=user_data['role'],
                        branch_id='MAIN',
                        is_active=True
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    print(f"✓ Created user: {user_data['username']}")
            
            db.session.commit()
            
            print("\n" + "=" * 50)
            print("Sample data created successfully!")
            print("=" * 50)
            print("\nTest Purchase Orders:")
            for po_data in sample_pos:
                print(f"  • {po_data['po_number']} - {po_data['supplier_name']}")
            
            print("\nTest Users:")
            print("  • admin / admin123 (Administrator)")
            print("  • warehouse1 / warehouse123 (Warehouse Staff)")
            print("  • qc1 / qc123 (QC Staff)")
            print("  • manager1 / manager123 (Manager)")
            
            print("\nYou can now:")
            print("1. Login with any test user")
            print("2. Search for PO numbers: PO-2024-001, PO-2024-002, PO-2024-003")
            print("3. Create GRPOs against these purchase orders")
            
            return True
            
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return False

if __name__ == "__main__":
    print("WMS Application - Sample Data Creator")
    print("=" * 45)
    
    if create_sample_data():
        print("\nSample data creation completed!")
        print("You can now test the PO search functionality.")
    else:
        print("\nSample data creation failed!")
        print("Check the error messages above.")