import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from config import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Determine configuration
    if config_name is None:
        if os.environ.get("DATABASE_URL"):
            config_name = 'replit'  # PostgreSQL on Replit
        else:
            config_name = 'development'  # MySQL for local development
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Set database URI using the config method
    config_class = config[config_name]
    app.config["SQLALCHEMY_DATABASE_URI"] = config_class.get_database_uri()
    
    # Apply ProxyFix middleware for Replit
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    db.init_app(app)
    
    return app

# Create the app instance
app = create_app()

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    
    try:
        db.create_all()
        logging.info("Database tables created successfully")
        logging.info(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        logging.info("Falling back to SQLite database...")
        
        # Force SQLite fallback
        db_path = os.path.join(os.getcwd(), 'wms_dev.db')
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        
        # Reinitialize with SQLite
        db.init_app(app)
        db.create_all()
        logging.info("SQLite database initialized successfully")
