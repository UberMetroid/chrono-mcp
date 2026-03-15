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

from app.mcp_client import get_mcp_tools, call_mcp_tool

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Setup simple in-memory cache manually to guarantee it works without circular dependencies
_db_stats_cache = {"data": None, "timestamp": 0}
CACHE_TIMEOUT = 300 # 5 minutes

# ============ MCP ROUTES ============
@api_bp.route('/mcp/tools')
def mcp_tools():
    """Get all tools from the MCP server"""
    try:
        tools = get_mcp_tools()
        if tools is not None:
            return jsonify(tools)
        return jsonify({"error": "Failed to load tools from MCP server"}), 503
    except Exception as e:
        logger.error(f"Error fetching tools: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/mcp/tools/<tool_name>/run', methods=['POST'])
def run_mcp_tool(tool_name):
    """Execute a specific MCP tool with provided JSON arguments"""
    try:
        args = request.get_json() or {}
        # Protect against malicious commands if any exist
        result = call_mcp_tool(tool_name, args)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to run tool {tool_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============ DB STATS ============
@api_bp.route('/db_stats')
def api_db_stats():
    """Get statistics about the extracted database (Cached for 5 minutes)"""
    import time
    global _db_stats_cache
    
    current_time = time.time()
    
    # Return cached data if valid
    if _db_stats_cache["data"] and current_time - _db_stats_cache["timestamp"] < CACHE_TIMEOUT:
        return jsonify(_db_stats_cache["data"])
        
    try:
        from app.models.database import SessionLocal
        from app.models import Game, Category, Item
        from sqlalchemy import func
        
        db = SessionLocal()
        stats = {
            "total_games": db.query(Game).count(),
            "total_categories": db.query(Category).count(),
            "total_items": db.query(Item).count(),
            "games_data": []
        }
        
        games = db.query(Game).all()
        for game in games:
            game_stat = {
                "name": game.name,
                "total_categories": len(game.categories),
                "total_items": sum(c.item_count for c in game.categories),
                "categories": {c.name: c.item_count for c in game.categories}
            }
            stats["games_data"].append(game_stat)
            
        db.close()
        
        # Save to cache
        _db_stats_cache = {"data": stats, "timestamp": current_time}
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Failed to get db stats: {e}")
        return jsonify({"error": str(e)}), 500

# ============ HEALTH AND INFO ROUTES ============
def get_health_data():
    """Helper to get current health status"""
    import socket
    import datetime
    
    mcp_healthy = False
    try:
        mcp_port = int(getattr(config, 'MCP_PORT', 8080))
        with socket.create_connection(("localhost", mcp_port), timeout=1):
            mcp_healthy = True
    except OSError:
        pass

    try:
        cache_stats = get_cache_stats()
    except Exception:
        cache_stats = {"error": "Cache unavailable"}
        
    # Get Emulator Hook Status
    try:
        import urllib.request
        # We query the MCP tool directly or we just have a small helper.
        # It's easier to just try calling the MCP tool over HTTP via mcp_client.
        # But for health check we need it quickly.
        # Let's import the hook directly if possible, or just call the tool.
        from app.mcp_client import call_mcp_tool
        hook_resp = call_mcp_tool('get_live_emulator_state', {})
        if hook_resp and hook_resp.get("success"):
            import ast
            res_str = hook_resp.get("result", "{}")
            try:
                hook_state = json.loads(res_str)
            except:
                # Fallback if fastmcp stringified it as a python dict
                hook_state = ast.literal_eval(res_str)
        else:
            hook_state = {"connected": False, "error": hook_resp.get("error") if hook_resp else "Unknown"}
    except Exception as e:
        hook_state = {"connected": False, "error": str(e)}

    return {
        "status": "healthy",
        "mcp_status": "online" if mcp_healthy else "offline",
        "emulator_hook": hook_state,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "cache": cache_stats
    }

@api_bp.route('/health')
def health():
    """Health check endpoint"""
    try:
        return jsonify(get_health_data())
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/health/stream')
def health_stream():
    """Server-Sent Events stream for real-time health updates"""
    import time
    
    def generate():
        while True:
            try:
                data = get_health_data()
                # Format exactly as SSE requires
                yield f"data: {json.dumps(data)}\n\n"
            except Exception as e:
                logger.error(f"SSE error: {e}")
                # Send error but keep stream alive
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
            time.sleep(3) # Push updates every 3 seconds server-side
            
    return Response(generate(), mimetype='text/event-stream')

@api_bp.route('/lua/download')
def download_lua():
    """Download the BizHawk Lua Hook script"""
    try:
        import os
        from flask import send_file
        lua_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "lua", "bizhawk_hook.lua")
        return send_file(lua_path, as_attachment=True, download_name="chrono_mcp_hook.lua")
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@api_bp.route('/download')
def download_file():
    """Download a generated file (like IPS patches)"""
    path = request.args.get('path')
    if not path:
        return "Path required", 400
    try:
        from flask import send_file
        import os
        # Basic safety check
        if ".." in path or not os.path.exists(path):
            return "File not found or invalid path", 404
        return send_file(path, as_attachment=True)
    except Exception as e:
        return str(e), 500

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