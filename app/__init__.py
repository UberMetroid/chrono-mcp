from flask import Flask, send_from_directory, jsonify, render_template_string, request
import logging
from flask_wtf.csrf import CSRFProtect
from app.config import get_config
from app.middleware import init_middleware
from app.routes.api import api_bp
from app.routes.web import web_bp
from app.routes.auth import auth_bp
from app.routes.analytics import analytics_bp
from app.routes.docs import api  # Import API documentation
from app.models.database import db_service

logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize database
    try:
        logger.info("Initializing database...")
        db_service.initialize_database()
        if not db_service.is_data_loaded():
            logger.info("Populating database with data...")
            db_service.load_data_from_json()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Continue without database - will fall back to JSON

    # Initialize middleware
    middleware = init_middleware(app)

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analytics_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Resource not found"}), 404
        return render_template_string("<h1>404 - Page Not Found</h1>"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "Internal server error"}), 500
        return render_template_string("<h1>500 - Internal Server Error</h1>"), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({"error": "An unexpected error occurred"}), 500
        return render_template_string("<h1>500 - Internal Server Error</h1>"), 500

    # Static file routes
    @app.route('/data/art/<filename>')
    def serve_image(filename):
        """Serve extracted images"""
        # Validate filename to prevent path traversal
        from app.utils import sanitize_input
        filename = sanitize_input(filename, max_length=200)
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({"error": "Invalid filename"})

        return send_from_directory(config_class.DATA_DIR / "art", filename)

    @app.route('/data/audio/<filename>')
    def serve_audio(filename):
        """Serve audio files"""
        # Validate filename to prevent path traversal
        from app.utils import sanitize_input
        filename = sanitize_input(filename, max_length=200)
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({"error": "Invalid filename"})

        return send_from_directory(config_class.DATA_DIR / "audio", filename)

    return app