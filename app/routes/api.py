from flask import Blueprint, jsonify, request, send_from_directory, Response
import logging
import json

logger = logging.getLogger(__name__)

from app.utils import (
    sanitize_input, validate_game_name, load_data, get_cache_stats, clear_cache
)
from app.models.database import db_service
from app.config import get_config

config = get_config()

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ============ HEALTH AND INFO ROUTES ============

@api_bp.route('/health')
def health():
    """Health check endpoint"""
    cache_stats = get_cache_stats()
    return jsonify({
        "status": "healthy",
        "timestamp": "2026-03-13T16:30:00Z",
        "version": "1.0.0",
        "cache": cache_stats
    })

@api_bp.route('/ready')
def ready():
    """Readiness check"""
    data = load_data()
    if data is None:
        return jsonify({"ready": False, "status": "not ready", "error": "Data not loaded"}), 503
    return jsonify({"ready": True, "status": "ready"})

@api_bp.route('/version')
def version():
    """Version information"""
    return jsonify({
        "version": "1.0.0",
        "name": "Chrono MCP Web UI",
        "description": "Web interface for Chrono series game data"
    })

# ============ CACHE MANAGEMENT ============

@api_bp.route('/cache/stats')
def cache_stats():
    """Get cache statistics"""
    return jsonify(get_cache_stats())

@api_bp.route('/cache/clear', methods=['POST'])
def cache_clear():
    """Clear the data cache"""
    clear_cache()
    return jsonify({"message": "Cache cleared"})

@api_bp.route('/refresh', methods=['POST'])
def refresh_data():
    """Force refresh of data"""
    data = load_data(force_reload=True)
    if data is None:
        return jsonify({"error": "Failed to refresh data"}), 500
    return jsonify({"message": "Data refreshed"})

# ============ GAME DATA ROUTES ============

@api_bp.route('/games')
def api_games():
    """Get all games"""
    try:
        games = db_service.get_games()
        return jsonify(games)
    except Exception as e:
        logger.error(f"Failed to get games: {e}")
        return jsonify({"error": "Database error"}), 500

@api_bp.route('/categories')
def api_categories():
    """Get all available categories across all games"""
    try:
        categories = db_service.get_categories()
        return jsonify(sorted(categories))
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        return jsonify({"error": "Database error"}), 500

@api_bp.route('/<game>')
def api_game(game):
    """Get game data"""
    # Validate input
    game = validate_game_name(game)
    if not game:
        return jsonify({"error": "Invalid game name"}), 400

    try:
        # Handle URL encoding
        game_key = game.replace("%20", " ")
        game_data = db_service.get_game_data(game_key)

        if game_data:
            return jsonify(game_data)

        # Try fuzzy matching
        games = db_service.get_games()
        for g in games:
            if game.lower() in g.lower():
                game_data = db_service.get_game_data(g)
                if game_data:
                    return jsonify(game_data)

        return jsonify({"error": "Game not found"}), 404
    except Exception as e:
        logger.error(f"Failed to get game {game}: {e}")
        return jsonify({"error": "Database error"}), 500

@api_bp.route('/<game>/<category>')
def api_category(game, category):
    """Get specific category (characters, items, etc.) with optional pagination"""
    # Validate inputs
    game = validate_game_name(game)
    category = sanitize_input(category, max_length=50)

    if not game or not category:
        return jsonify({"error": "Invalid parameters"}), 400

    # Pagination parameters
    page = max(1, int(request.args.get('page', 1)))
    per_page = min(config.MAX_PAGE_SIZE, max(1, int(request.args.get('per_page', config.DEFAULT_PAGE_SIZE))))

    try:
        game_key = game.replace("%20", " ")
        result = db_service.get_category_data(game_key, category, page, per_page)

        if result:
            return jsonify(result)

        return jsonify({"error": "Category not found"}), 404
    except Exception as e:
        logger.error(f"Failed to get category {game}/{category}: {e}")
        return jsonify({"error": "Database error"}), 500

# ============ PLOT ROUTES ============

@api_bp.route('/plot')
def api_plot_list():
    """Get list of available plot files"""
    try:
        # For now, return dummy data since plot extraction is not implemented
        plots = [
            {
                "file": "ct_plot_tree.json",
                "game": "Chrono Trigger",
                "description": "Complete plot tree for Chrono Trigger"
            },
            {
                "file": "cc_plot_tree.json",
                "game": "Chrono Cross",
                "description": "Complete plot tree for Chrono Cross"
            },
            {
                "file": "rd_plot_tree.json",
                "game": "Radical Dreamers",
                "description": "Complete plot tree for Radical Dreamers"
            }
        ]
        return jsonify({"plots": plots})
    except Exception as e:
        logger.error(f"Failed to get plot list: {e}")
        return jsonify({"error": "Database error"}), 500

@api_bp.route('/plot/<plot_id>')
def api_plot_detail(plot_id):
    """Get detailed plot data"""
    try:
        # Dummy data for now
        if plot_id == "ct_plot_tree":
            data = {
                "game": "Chrono Trigger",
                "description": "The complete storyline of Chrono Trigger",
                "eras": [
                    {"name": "Present", "year": "1000 AD", "description": "The story begins in the present day"},
                    {"name": "Middle Ages", "year": "600 AD", "description": "Journey to the medieval period"}
                ],
                "character_arcs": [
                    {"character": "Crono", "arc": "From ordinary boy to legendary hero"}
                ],
                "endings": [
                    {"name": "Good Ending", "description": "Save Lucca and defeat Lavos"}
                ]
            }
        elif plot_id == "cc_plot_tree":
            data = {
                "game": "Chrono Cross",
                "description": "The complex narrative of Chrono Cross",
                "worlds": [
                    {"name": "Home World", "description": "The primary timeline"}
                ],
                "character_arcs": [
                    {"character": "Serge", "arc": "Dual existence between worlds"}
                ],
                "endings": [
                    {"name": "Good Ending", "description": "Reunite the dimensions"}
                ]
            }
        else:
            data = {
                "game": "Radical Dreamers",
                "description": "The mystery adventure of Radical Dreamers",
                "episodes": [
                    {"name": "The Mansion", "description": "Investigate the mysterious mansion"}
                ]
            }

        return jsonify(data)
    except Exception as e:
        logger.error(f"Failed to get plot {plot_id}: {e}")
        return jsonify({"error": "Plot not found"}), 404

# ============ EXPORT ROUTES ============

@api_bp.route('/export/<game>')
def api_export_game(game):
    """Export game data as JSON"""
    game = validate_game_name(game)
    if not game:
        return jsonify({"error": "Invalid game name"}), 400

    data = load_data()
    if data is None:
        return jsonify({"error": "Data not available"})
    games = data.get("games", {})

    game_key = game.replace("%20", " ")
    if game_key not in games:
        for g in games:
            if game.lower() in g.lower():
                game_key = g
                break
        else:
            return jsonify({"error": "Game not found"}), 404

    response = jsonify(games[game_key])
    response.headers['Content-Disposition'] = f'attachment; filename={game_key}.json'
    return response

@api_bp.route('/export/<game>/<category>')
def api_export_category_json(game, category):
    """Export category as JSON"""
    game = validate_game_name(game)
    category = sanitize_input(category, max_length=50)

    if not game or not category:
        return jsonify({"error": "Invalid parameters"}), 400

    data = load_data()
    if data is None:
        return jsonify({"error": "Data not available"})
    games = data.get("games", {})

    game_key = game.replace("%20", " ")
    if game_key not in games:
        for g in games:
            if game.lower() in g.lower():
                game_key = g
                break
        else:
            return jsonify({"error": "Game not found"}), 404

    game_data = games[game_key]
    if category not in game_data:
        return jsonify({"error": "Category not found"}), 404

    response = jsonify(game_data[category])
    response.headers['Content-Disposition'] = f'attachment; filename={game_key}_{category}.json'
    return response

@api_bp.route('/export/<game>/<category>/csv')
def api_export_category_csv(game, category):
    """Export category as CSV"""
    import csv
    import io

    game = validate_game_name(game)
    category = sanitize_input(category, max_length=50)

    if not game or not category:
        return jsonify({"error": "Invalid parameters"}), 400

    data = load_data()
    if data is None:
        return jsonify({"error": "Data not available"})
    games = data.get("games", {})

    game_key = game.replace("%20", " ")
    if game_key not in games:
        for g in games:
            if game.lower() in g.lower():
                game_key = g
                break
        else:
            return jsonify({"error": "Game not found"}), 404

    game_data = games[game_key]
    if category not in game_data:
        return jsonify({"error": "Category not found"}), 404

    items = game_data[category]
    if not isinstance(items, list) or not items:
        return jsonify({"error": "Category must be a non-empty list"}), 400

    # Create CSV
    output = io.StringIO()
    if isinstance(items[0], dict):
        # Dict items - use keys as headers
        fieldnames = list(items[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    else:
        # Simple list
        writer = csv.writer(output)
        writer.writerow(['value'])
        for item in items:
            writer.writerow([item])

    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={game_key}_{category}.csv'
        }
    )
    return response

# ============ SEARCH ROUTES ============

@api_bp.route('/search')
def api_search():
    """Search across all games with database full-text search"""
    query = request.args.get('q', '')
    game_filter = request.args.get('game', '')
    category_filter = request.args.get('category', '')

    # Sanitize input
    query = sanitize_input(query, max_length=50)
    game_filter = sanitize_input(game_filter, max_length=50)
    category_filter = sanitize_input(category_filter, max_length=50)

    if not query:
        return jsonify({"query": "", "matches": [], "error": "Empty query"})

    try:
        matches = db_service.search_items(
            query=query,
            game_filter=game_filter or None,
            category_filter=category_filter or None,
            limit=500
        )

        return jsonify({
            "query": query,
            "matches": matches,
            "count": len(matches)
        })
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return jsonify({"error": "Search error", "matches": []}), 500

# ============ MEDIA ROUTES ============

@api_bp.route('/images')
def api_images():
    """List available images"""
    import os
    art_dir = config.DATA_DIR / "art"
    if not art_dir.exists():
        return jsonify({"images": []})

    images = []
    for f in os.listdir(art_dir):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            images.append({
                "name": f,
                "path": f"/data/art/{f}"
            })

    return jsonify({"images": images[:200]})  # Limit results

@api_bp.route('/audio')
def api_audio():
    """List available audio files"""
    import os
    audio_dir = config.DATA_DIR / "audio"
    if not audio_dir.exists():
        return jsonify({"audio": []})

    audio = []
    for f in os.listdir(audio_dir):
        if f.endswith(('.wav', '.mp3', '.ogg')):
            audio.append({
                "name": f,
                "path": f"/data/audio/{f}"
            })

    return jsonify({"audio": audio[:100]})