import os
from pathlib import Path

class Config:
    """Application configuration"""

    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    ROMS_DIR = DATA_DIR / "roms"
    EXTRACTED_DIR = DATA_DIR / "extracted"

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False

    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))

    # Cache settings
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'redis')  # redis, simple, etc.
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '3600'))
    CACHE_KEY_PREFIX = os.getenv('CACHE_KEY_PREFIX', 'chrono:')

    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/chrono.db')

    # Rate limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '200/day;50/hour')
    RATELIMIT_SEARCH = os.getenv('RATELIMIT_SEARCH', '10/minute')

    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'chrono.log'))

    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', '20'))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', '100'))

class DevelopmentConfig(Config):
    DEBUG = True
    CACHE_TYPE = 'simple'

class ProductionConfig(Config):
    DEBUG = False
    CACHE_TYPE = 'redis'

class TestingConfig(Config):
    TESTING = True
    CACHE_TYPE = 'simple'
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])