from flask import Blueprint, request, jsonify, session, g, current_app
from app.utils import sanitize_input
from app.config import get_config

config = get_config()
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Simple admin credentials (in production, use proper user management)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "chrono2026"  # Change this!

def require_admin(f):
    """Decorator to require admin authentication"""
    def wrapper(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return jsonify({"error": "Admin authentication required"}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@auth_bp.route('/login', methods=['POST'])
def login():
    """Admin login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get('username', '')
        password = data.get('password', '')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            session['admin_username'] = username
            return jsonify({
                "message": "Admin login successful",
                "user": {"username": username, "role": "admin"}
            })
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": "Login failed"}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    session.pop('admin_username', None)
    return jsonify({"message": "Logged out successfully"})

@auth_bp.route('/status')
def status():
    """Check authentication status"""
    if session.get('admin_authenticated'):
        return jsonify({
            "authenticated": True,
            "user": {
                "username": session.get('admin_username'),
                "role": "admin"
            }
        })
    else:
        return jsonify({"authenticated": False})

# Protected routes (examples)
@auth_bp.route('/admin/stats')
@require_admin
def admin_stats():
    """Admin-only statistics"""
    # This would show detailed system stats
    return jsonify({
        "message": "Admin stats",
        "system": "Chrono MCP",
        "status": "operational"
    })

@auth_bp.route('/admin/cache/clear', methods=['POST'])
@require_admin
def admin_clear_cache():
    """Admin cache clearing"""
    from app.utils import clear_cache
    clear_cache()
    return jsonify({"message": "Admin cache cleared"})