from flask import Flask, request, g, Response, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_compress import Compress
import logging
import uuid
from datetime import datetime
from app.config import get_config

config = get_config()

def setup_cors(app: Flask):
    """Configure CORS"""
    CORS(app, resources={
        r"/api/*": {
            "origins": config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Request-ID"],
            "expose_headers": ["X-Request-ID"],
            "supports_credentials": True
        }
    })

def setup_rate_limiting(app: Flask):
    """Configure rate limiting"""
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=config.RATELIMIT_STORAGE_URL,
        default_limits=[config.RATELIMIT_DEFAULT]
    )
    return limiter

def setup_sessions(app: Flask):
    """Configure Flask sessions"""
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400

def setup_caching(app: Flask):
    """Configure caching"""
    cache_config = {
        'CACHE_TYPE': config.CACHE_TYPE,
        'CACHE_REDIS_URL': config.CACHE_REDIS_URL,
        'CACHE_DEFAULT_TIMEOUT': config.CACHE_DEFAULT_TIMEOUT,
        'CACHE_KEY_PREFIX': config.CACHE_KEY_PREFIX
    }
    cache = Cache(app, config=cache_config)
    return cache

def setup_compression(app: Flask):
    """Configure response compression"""
    compress = Compress(app)
    return compress

def setup_request_logging(app: Flask):
    """Configure request logging"""
    log_dir = config.BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger("chrono_web")

    @app.before_request
    def log_request_info():
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.start_time = datetime.utcnow()
        logger.info(f"Request: {request.method} {request.path} [ID: {g.request_id}]")

    @app.after_request
    def log_response_info(response: Response) -> Response:
        duration = datetime.utcnow() - g.start_time
        duration_ms = duration.total_seconds() * 1000
        logger.info(f"Response: {response.status_code} [ID: {g.get('request_id', 'unknown')}] Duration: {duration_ms:.2f}ms")
        response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
        return response

    return logger

def init_middleware(app: Flask):
    """Initialize all middleware"""
    setup_cors(app)
    limiter = setup_rate_limiting(app)
    setup_sessions(app)
    cache = setup_caching(app)
    compress = setup_compression(app)
    logger = setup_request_logging(app)

    app.limiter = limiter
    app.cache = cache

    return {
        'limiter': limiter,
        'cache': cache,
        'compress': compress,
        'logger': logger
    }