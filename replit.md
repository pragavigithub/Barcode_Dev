# WMS Application - Warehouse Management System

## Overview

This is a Flask-based Warehouse Management System (WMS) designed to handle goods receipt processing operations (GRPO), quality control approvals, and SAP Business One integration. The system manages the complete workflow from purchase order receipt to final posting in SAP B1.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (July 2025)

- **Database Migration**: Successfully migrated to support both PostgreSQL (Replit) and MySQL (local)
- **Configuration System**: Implemented application factory pattern with environment-aware config
- **Security Updates**: Fixed session key configuration and template rendering issues  
- **Sample Data**: Added admin user (admin/admin123) and sample purchase order for testing
- **Environment Setup**: Configured dual database support with automatic detection
- **Local Development**: Created comprehensive local setup guide with MySQL integration

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM using application factory pattern
- **Database**: Dual support - PostgreSQL (Replit) and MySQL (local development)
- **Authentication**: Session-based authentication with role-based access control
- **Integration**: SAP Business One Service Layer integration for ERP connectivity
- **Configuration**: Environment-aware configuration system with automatic database detection

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **Styling**: Custom CSS built on Bootstrap with responsive design
- **JavaScript**: Vanilla JavaScript for barcode scanning and interactive features
- **Icons**: Font Awesome for consistent iconography

## Key Components

### Core Models
- **User**: Authentication and role management (Admin, Manager, Warehouse Staff, QC Staff, View Only)
- **PurchaseOrder/PurchaseOrderLine**: Purchase order data structure
- **GRPO/GRPOLine**: Goods receipt processing documents
- **QCApproval**: Quality control approval workflow
- **QRCode**: QR code generation for inventory tracking

### Authentication & Authorization
- Session-based authentication with decorator-based route protection
- Role-based permissions system with granular access control
- Branch-based data filtering for multi-location operations

### Business Logic Modules
- **SAP Integration**: RESTful API integration with SAP Business One Service Layer
- **QR Code Generation**: Automatic QR code creation for received items
- **Barcode Scanner**: JavaScript-based barcode scanning functionality

## Data Flow

1. **Purchase Order Import**: PO data imported from SAP B1 or manual entry
2. **Goods Receipt Creation**: Warehouse staff creates GRPO against PO
3. **Item Receipt Processing**: Line-by-line item receipt with batch/expiry tracking
4. **QR Code Generation**: Automatic QR code creation for inventory identification
5. **Quality Control**: QC staff approves/rejects received items
6. **SAP Posting**: Approved GRPOs posted back to SAP B1 system

## External Dependencies

### SAP Business One Integration
- Service Layer API for real-time ERP connectivity
- Purchase order synchronization
- GRPO posting automation
- Error handling and retry mechanisms

### Third-Party Libraries
- Flask ecosystem (SQLAlchemy, Werkzeug)
- PyMySQL for MySQL connectivity
- QRCode library for QR code generation
- Requests for HTTP API communication

## Database Schema

### Primary Tables
- `users`: User authentication and role management
- `purchase_orders`: PO header information
- `purchase_order_lines`: PO line item details
- `grpos`: Goods receipt document headers
- `grpo_lines`: Individual receipt line items
- `qc_approvals`: Quality control approval records
- `qr_codes`: Generated QR code tracking

### Key Relationships
- Users create and manage GRPOs
- GRPOs reference Purchase Orders
- QC approvals link to specific GRPOs
- QR codes generated for GRPO lines

## Deployment Strategy

### Environment Configuration
- Environment-based configuration for database connections
- SAP B1 connection parameters via environment variables
- Session secret key management
- Multi-environment support (development/production)

### Database Management
- SQLAlchemy automatic table creation
- Connection pooling and health monitoring
- Dual database support: PostgreSQL (Replit) and MySQL (local development)
- Environment-aware database configuration with automatic detection
- Fallback mechanisms for local development setup

### Security Considerations
- Password hashing with Werkzeug security
- Session management with secure cookies
- ProxyFix middleware for reverse proxy deployment
- Input validation and sanitization

## File Structure

### Core Application Files
- `app.py`: Flask application factory and database initialization
- `models.py`: SQLAlchemy ORM models and business logic
- `routes.py`: HTTP route handlers and view logic
- `auth.py`: Authentication decorators and user management
- `main.py`: Application entry point

### Integration Modules
- `sap_integration.py`: SAP B1 Service Layer API client
- `qr_generator.py`: QR code generation utilities

### Frontend Assets
- `templates/`: Jinja2 HTML templates with Bootstrap styling
- `static/css/`: Custom CSS for WMS-specific styling
- `static/js/`: JavaScript for barcode scanning and interactivity

### Key Features
- Responsive design with mobile support
- Real-time barcode scanning capability
- Comprehensive error handling and user feedback
- Multi-role dashboard with role-specific views
- Detailed reporting and export functionality