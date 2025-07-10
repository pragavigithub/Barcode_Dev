# Local Development Setup

This guide explains how to run the WMS application locally with MySQL database.

## Prerequisites

1. **Python 3.11+** installed
2. **MySQL Server** running locally
3. **Git** for version control

## Installation Steps

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd wms-application
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

**Option A: Windows Users (Easiest)**
```batch
setup_windows.bat
```

**Option B: Cross-Platform (Recommended)**
```bash
python install_local_deps.py
```

**Option C: Manual Installation**
```bash
pip install flask flask-sqlalchemy pymysql werkzeug email-validator pillow pyjwt qrcode requests sqlalchemy gunicorn
```

### 4. Setup MySQL Database
```sql
CREATE DATABASE wms_db;
CREATE USER 'wms_user'@'localhost' IDENTIFIED BY 'wms_password';
GRANT ALL PRIVILEGES ON wms_db.* TO 'wms_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Set Environment Variables

Create a `.env` file in the project root:
```bash
# MySQL Database Configuration
MYSQL_USER=wms_user
MYSQL_PASSWORD=wms_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=wms_db

# Session Security
SESSION_SECRET=your-secret-key-here

# Optional: SAP B1 Integration
SAP_B1_SERVER_URL=https://your-sap-server:50000/b1s/v1
SAP_B1_USERNAME=your-sap-username
SAP_B1_PASSWORD=your-sap-password
SAP_B1_COMPANY_DB=your-company-database
```

### 6. Run the Application
```bash
python main.py
```

The application will be available at: http://localhost:5000

## Default Login Credentials

- **Username:** admin
- **Password:** admin123
- **Branch ID:** MAIN (optional)

## Database Configuration

The application automatically detects the environment:

- **Local Development:** Uses MySQL with pymysql driver
- **Replit Environment:** Uses PostgreSQL with psycopg2 driver

### Manual Database Configuration

If you need to manually set the database URL:

```bash
# For MySQL
export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/wms_db"

# For PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/wms_db"
```

## Troubleshooting

### Database Connection Issues

1. **MySQL not starting:**
   - Windows: Start MySQL service from Services panel
   - Linux: `sudo systemctl start mysql`
   - macOS: `brew services start mysql`

2. **Permission denied:**
   - Check MySQL user permissions
   - Verify database exists
   - Test connection: `mysql -u wms_user -p wms_db`

3. **Port conflicts:**
   - Check if port 5000 is available
   - Change port in main.py if needed

### Package Installation Issues

1. **pymysql installation fails:**
   ```bash
   pip install --upgrade pip
   pip install pymysql
   ```

2. **Pillow installation issues:**
   - Install system dependencies first
   - Linux: `sudo apt-get install libjpeg-dev zlib1g-dev`
   - macOS: `brew install libjpeg`

## Features Available Locally

- ✅ User management with role-based access
- ✅ Purchase order management
- ✅ Goods receipt processing (GRPO)
- ✅ Quality control workflow
- ✅ QR code generation
- ✅ Barcode scanning
- ✅ Reporting and dashboard
- ⚠️ SAP B1 integration (requires configuration)

## Development Tips

1. **Debug Mode:** The application runs in debug mode locally for easier development
2. **Database Changes:** Tables are created automatically on first run
3. **Static Files:** CSS/JS files are served from the `static/` directory
4. **Templates:** HTML templates are in the `templates/` directory
5. **Logging:** Check console output for detailed application logs