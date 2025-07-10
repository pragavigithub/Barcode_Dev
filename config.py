import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

class DevelopmentConfig(Config):
    """Development configuration for local MySQL"""
    DEBUG = True
    
    @staticmethod
    def get_database_uri():
        # Check if DATABASE_URL is set (Replit PostgreSQL)
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            return database_url
        
        # Fallback to MySQL for local development
        mysql_user = os.environ.get("MYSQL_USER", "root")
        mysql_password = os.environ.get("MYSQL_PASSWORD", "password")
        mysql_host = os.environ.get("MYSQL_HOST", "localhost")
        mysql_port = os.environ.get("MYSQL_PORT", "3306")
        mysql_database = os.environ.get("MYSQL_DATABASE", "wms_db")
        return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    @staticmethod
    def get_database_uri():
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable must be set in production")
        return database_url

class ReplitConfig(Config):
    """Replit specific configuration"""
    DEBUG = True
    
    @staticmethod
    def get_database_uri():
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL not found in Replit environment")
        return database_url

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'replit': ReplitConfig,
    'default': DevelopmentConfig
}