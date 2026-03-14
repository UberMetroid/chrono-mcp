#!/usr/bin/env python3
"""
Chrono Series Web UI
Simple browser for Chrono game data
Run: python web_ui.py
"""

import json
import logging
import os
import re
import time
import uuid
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from flask import Flask, Response, g, jsonify, render_template_string, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Type aliases
JSON = Dict[str, Any]
JSONList = List[Any]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("chrono_web")

app = Flask(__name__)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Enable CORS with restrictions
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-Request-ID"]
    }
})

# Request ID middleware
@app.before_request
def add_request_id() -> None:
    """Add unique request ID to each request"""
    g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))

@app.after_request
def add_request_id_to_response(response: Response) -> Response:
    """Add request ID to response headers"""
    response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
    return response

# Application version
VERSION: str = "1.0.0"

# Configuration
BASE_DIR: Path = Path(os.environ.get("CHRONO_BASE", "/home/jeryd/Code/Chrono_Series"))
DATA_DIR: Path = BASE_DIR / "data"

# Optional API Authentication (disabled by default)
API_KEY: str = os.environ.get("API_KEY", "")
AUTH_ENABLED: bool = bool(API_KEY)

# Public endpoints that don't require auth
PUBLIC_ENDPOINTS: set = {'/health', '/api/ready', '/api/version', '/', '/api/games', 
                   '/api/search', '/api/export', '/data/art', '/data/audio', '/api/categories'}

# Cache globals
_data_cache: Optional[Dict[str, Any]] = None
_load_error: Optional[str] = None
_cache_hits: int = 0
_cache_misses: int = 0

# Retry configuration
MAX_RETRIES: int = 3
RETRY_DELAY: float = 0.5

# Max search results
MAX_SEARCH_RESULTS: int = 500

# Input validation
def sanitize_input(value: str, max_length: int = 100) -> str:
    """Sanitize user input"""
    if not value:
        return ""
    # Remove potentially dangerous characters
    value = re.sub(r'[<>"\';\\]', '', value)
    return value[:max_length]

def validate_game_name(name: str) -> str:
    """Validate and normalize game name"""
    name = sanitize_input(name)
    # Only allow alphanumeric, space, hyphen
    return re.sub(r'[^a-zA-Z0-9 \-]', '', name)

_data_cache = None
_load_error = None
_cache_hits = 0
_cache_misses = 0

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 0.5  # seconds

# Load data with caching and retry
def load_data(force_reload=False) -> Optional[Dict[str, Any]]:
    """Load all game data with retry logic"""
    global _data_cache, _load_error, _cache_hits, _cache_misses
    
    if _data_cache is not None and not force_reload:
        _cache_hits += 1
        return _data_cache
    
    _cache_misses += 1
    
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            data_file = DATA_DIR / "extracted/chrono_master_complete.json"
            with open(data_file) as f:
                _data_cache = json.load(f)
            _load_error = None
            logger.info(f"Data loaded successfully (attempt {attempt + 1})")
            return _data_cache
        except json.JSONDecodeError as e:
            last_error = f"JSON parse error: {e}"
            _data_cache = {"games": {}}
            logger.error(f"JSON parse error: {e}")
        except FileNotFoundError as e:
            last_error = f"File not found: {e}"
            _data_cache = {"games": {}}
            logger.error(f"File not found: {e}")
        except IOError as e:
            last_error = f"IO error: {e}"
            logger.warning(f"IO error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            # Retry for IO errors
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
        except Exception as e:
            last_error = f"Load error: {e}"
            _data_cache = {"games": {}}
            logger.error(f"Load error: {e}")
    
    _load_error = last_error
    return _data_cache

def clear_cache():
    """Clear the data cache"""
    global _data_cache
    _data_cache = None

def get_cache_stats():
    """Get cache statistics"""
    return {
        "hits": _cache_hits,
        "misses": _cache_misses,
        "size_bytes": len(str(_data_cache)) if _data_cache else 0
    }

# Cache stats endpoint
@app.route('/api/cache/stats')
def cache_stats():
    """Get cache statistics"""
    return jsonify(get_cache_stats())

@app.route('/api/cache/clear')
def cache_clear():
    """Clear the data cache"""
    clear_cache()
    logger.info("Cache cleared")
    return jsonify({"status": "ok", "message": "Cache cleared"})

# Request logging
@app.before_request
def log_request():
    """Log incoming requests"""
    logger.info(f"Request: {request.method} {request.path} [ID: {g.get('request_id', 'unknown')}]")

# Error handlers
@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500 Internal Error: {request.path}")
    return jsonify({"error": "Internal server error"}), 500

@app.route('/api/refresh')
def api_refresh():
    """Force reload data from files"""
    load_data(force_reload=True)
    return jsonify({"status": "ok", "message": "Data refreshed"})

@app.route('/health')
def health_check():
    """Health check endpoint for container orchestration"""
    health = {
        "status": "healthy",
        "version": VERSION
    }
    
    # Check data file exists and is readable
    try:
        data_file = DATA_DIR / "extracted/chrono_master_complete.json"
        if data_file.exists():
            health["data_file"] = "ok"
        else:
            health["data_file"] = "missing"
            health["status"] = "degraded"
    except Exception as e:
        health["data_file"] = str(e)
        health["status"] = "unhealthy"
    
    # Check data can be loaded
    try:
        load_data()
        health["data_load"] = "ok"
    except Exception as e:
        health["data_load"] = str(e)
        health["status"] = "unhealthy"
    
    status_code = 200 if health["status"] == "healthy" else 503
    return jsonify(health), status_code

@app.route('/api/ready')
def ready_check():
    """Readiness check - includes all dependencies"""
    return jsonify({"ready": True, "service": "chrono-mcp", "version": VERSION})

@app.route('/api/version')
def version_check():
    """Version information"""
    return jsonify({
        "version": VERSION,
        "service": "chrono-mcp",
        "web_ui": True,
        "mcp_server": True
    })

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/games')
def api_games():
    """Get all games"""
    data = load_data()
    if data is None:
        return jsonify({"error": "Data not available"})
    return jsonify(list(data.get("games", {}).keys()))

@app.route('/api/categories')
def api_categories():
    """Get all available categories across all games"""
    data = load_data()
    if data is None:
        return jsonify({"error": "Data not available"})
    all_categories = set()

    for game_data in data.get("games", {}).values():
        for key, value in game_data.items():
            if isinstance(value, list):
                all_categories.add(key)
    
    return jsonify(sorted(all_categories))

@app.route('/api/<game>')
def api_game(game):
    """Get game data"""
    # Validate input
    game = validate_game_name(game)
    if not game:
        return jsonify({"error": "Invalid game name"})

    data = load_data()
    if data is None:
        return jsonify({"error": "Data not available"})
    games = data.get("games", {})
    
    # Handle URL encoding
    game_key = game.replace("%20", " ")
    
    if game_key in games:
        return jsonify(games[game_key])
    
    # Try finding by partial match
    for g in games:
        if game.lower() in g.lower():
            return jsonify(games[g])
    
    return jsonify({"error": "Game not found"})

@app.route('/api/export/<game>')
def api_export_game_json(game):
    """Export game data as JSON"""
    game = validate_game_name(game)
    if not game:
        return jsonify({"error": "Invalid game name"})

    data = load_data()
    if data is None:
        return jsonify({"error": "Data not available"})
    games = data.get("games", {})
    
    game_key = game.replace("%20", " ")
    if game_key in games:
        return jsonify(games[game_key])
    
    for g in games:
        if game.lower() in g.lower():
            return jsonify(games[g])
    
    return jsonify({"error": "Game not found"})

@app.route('/api/export/<game>/<category>')
def api_export_category_json(game, category):
    """Export category as JSON"""
    game = validate_game_name(game)
    category = sanitize_input(category, max_length=50)

    if not game or not category:
        return jsonify({"error": "Invalid parameters"})

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
    
    if game_key in games:
        cat_data = games[game_key].get(category, [])
        return jsonify(cat_data)
    
    return jsonify({"error": "Category not found"})

@app.route('/api/export/<game>/<category>/csv')
def api_export_category_csv(game, category):
    """Export category as CSV"""
    import csv
    import io

    game = validate_game_name(game)
    category = sanitize_input(category, max_length=50)

    if not game or not category:
        return jsonify({"error": "Invalid parameters"})

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
    
    if game_key in games:
        cat_data = games[game_key].get(category, [])
        
        if not cat_data or not isinstance(cat_data, list):
            return jsonify({"error": "No data to export"})
        
        # Create CSV
        output = io.StringIO()
        if isinstance(cat_data[0], dict):
            writer = csv.DictWriter(output, fieldnames=cat_data[0].keys())
            writer.writeheader()
            writer.writerows(cat_data)
        else:
            writer = csv.writer(output)
            writer.writerow([category])
            for item in cat_data:
                writer.writerow([item])
        
        return output.getvalue(), 200, {'Content-Type': 'text/csv'}
    
    return jsonify({"error": "Category not found"})

@app.route('/api/<game>/<category>')
def api_category(game, category):
    """Get specific category (characters, items, etc.) with optional pagination"""
    # Validate inputs
    game = validate_game_name(game)
    category = sanitize_input(category, max_length=50)
    
    # Pagination parameters
    page = max(1, int(request.args.get('page', 1)))
    per_page = min(100, max(1, int(request.args.get('per_page', 20))))
    
    if not game or not category:
        return jsonify({"error": "Invalid parameters"})

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
    
    if game_key in games:
        cat_data = games[game_key].get(category, [])
        
        # Apply pagination
        total = len(cat_data)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = cat_data[start:end]
        
        return jsonify({
            "data": paginated_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    
    return jsonify({"error": "Not found"})

@app.route('/api/search')
@limiter.limit("10 per minute")
def api_search():
    """Search across all games with fuzzy matching"""
    import difflib
    
    query = request.args.get('q', '')
    game_filter = request.args.get('game', '')
    category_filter = request.args.get('category', '')
    fuzzy = request.args.get('fuzzy', 'true').lower() == 'true'
    threshold = float(request.args.get('threshold', '0.6'))
    
    # Sanitize input
    query = sanitize_input(query, max_length=50).lower()
    game_filter = sanitize_input(game_filter, max_length=50)
    category_filter = sanitize_input(category_filter, max_length=50)
    
    if not query:
        return jsonify({"query": "", "matches": [], "error": "Empty query"})
    
    data = load_data()
    if data is None:
        return jsonify({"error": "Data not available", "matches": []})
    results = {"query": query, "matches": [], "count": 0}

    for game_name, game_data in data.get("games", {}).items():
        # Filter by game if specified
        if game_filter and game_filter.lower() not in game_name.lower():
            continue
            
        for category, items in game_data.items():
            # Filter by category if specified
            if category_filter and category_filter.lower() not in category.lower():
                continue
                
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        for key, val in item.items():
                            if isinstance(val, str):
                                val_lower = val.lower()
                                if fuzzy:
                                    ratio = difflib.SequenceMatcher(None, query, val_lower).ratio()
                                    if ratio >= threshold:
                                        results["matches"].append({
                                            "game": game_name,
                                            "category": category,
                                            "field": key,
                                            "match": val,
                                            "score": round(ratio, 2)
                                        })
                                elif query in val_lower:
                                    results["matches"].append({
                                        "game": game_name,
                                        "category": category,
                                        "field": key,
                                        "match": val,
                                        "score": 1.0
                                    })
                    elif isinstance(item, str):
                        if fuzzy:
                            ratio = difflib.SequenceMatcher(None, query, item.lower()).ratio()
                            if ratio >= threshold:
                                results["matches"].append({
                                    "game": game_name,
                                    "category": category,
                                    "match": item,
                                    "score": round(ratio, 2)
                                })
                        elif query in item.lower():
                            results["matches"].append({
                                "game": game_name,
                                "category": category,
                                "match": item,
                                "score": 1.0
                            })
        
        # Limit results to prevent memory issues
        if len(results["matches"]) >= MAX_SEARCH_RESULTS:
            results["truncated"] = True
            results["matches"] = results["matches"][:MAX_SEARCH_RESULTS]
            break
    
    results["count"] = len(results["matches"])
    return jsonify(results)

@app.route('/api/images')
def api_images():
    """List available images"""
    import os
    art_dir = DATA_DIR / "art"
    if not art_dir.exists():
        return jsonify({"images": []})
    
    images = []
    for f in os.listdir(art_dir):
        if f.endswith(('.ppm', '.png', '.jpg')):
            images.append({
                "name": f,
                "path": f"/data/art/{f}"
            })
    
    return jsonify({"images": images[:100]})

@app.route('/data/art/<filename>')
def serve_image(filename):
    """Serve extracted images"""
    # Validate filename to prevent path traversal
    filename = sanitize_input(filename, max_length=200)
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({"error": "Invalid filename"})
    
    from flask import send_from_directory
    return send_from_directory(DATA_DIR / "art", filename)

@app.route('/api/audio')
def api_audio():
    """List available audio files"""
    import os
    audio_dir = DATA_DIR / "audio"
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

@app.route('/data/audio/<filename>')
def serve_audio(filename):
    """Serve audio files"""
    # Validate filename to prevent path traversal
    filename = sanitize_input(filename, max_length=200)
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({"error": "Invalid filename"})
    
    from flask import send_from_directory
    return send_from_directory(DATA_DIR / "audio", filename)

@app.route('/api/plot')
def api_plot():
    """List available plot trees"""
    import os
    extracted_dir = DATA_DIR / "extracted"
    if not extracted_dir.exists():
        return jsonify({"plots": []})
    
    plots = []
    for f in os.listdir(extracted_dir):
        if f.endswith('_plot_tree.json'):
            game_name = f.replace('_plot_tree.json', '').replace('_', ' ').title()
            if game_name == 'Ct':
                game_name = 'Chrono Trigger'
            elif game_name == 'Cc':
                game_name = 'Chrono Cross'
            elif game_name == 'Rd':
                game_name = 'Radical Dreamers'
            plots.append({
                "game": game_name,
                "file": f"/api/plot/{f.replace('.json', '')}"
            })
    
    return jsonify({"plots": plots})

@app.route('/api/plot/<plot_id>')
def api_plot_detail(plot_id):
    """Get specific plot tree"""
    import os
    import json
    
    # Sanitize and validate
    plot_id = sanitize_input(plot_id, max_length=50)
    if '..' in plot_id or '/' in plot_id:
        return jsonify({"error": "Invalid plot ID"})
    
    # Map IDs to filenames
    id_map = {
        "ct": "ct_plot_tree.json",
        "chrono_trigger": "ct_plot_tree.json",
        "cc": "cc_plot_tree.json", 
        "chrono_cross": "cc_plot_tree.json",
        "rd": "rd_plot_tree.json",
        "radical_dreamers": "rd_plot_tree.json"
    }
    
    filename = id_map.get(plot_id.lower())
    if not filename:
        return jsonify({"error": "Plot not found"})
    
    filepath = DATA_DIR / "extracted" / filename
    if not filepath.exists():
        return jsonify({"error": "Plot file not found"})
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crono MCP</title>
    <style>
        :root {
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --accent: #e94560;
            --text: #eee;
            --border: #0f3460;
        }
        .light-theme {
            --bg-primary: #f5f5f5;
            --bg-secondary: #ffffff;
            --text: #333333;
            --border: #ddd;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: var(--bg-primary); color: var(--text); padding: 20px; }
        h1 { color: var(--accent); margin-bottom: 20px; }
        .search-box { margin-bottom: 30px; }
        .search-box input { width: 100%; padding: 15px; font-size: 18px; 
                           background: var(--bg-secondary); border: 2px solid var(--accent); 
                           color: var(--text); border-radius: 8px; }
        .games { display: flex; gap: 20px; flex-wrap: wrap; }
        .game-card { background: var(--bg-secondary); padding: 20px; border-radius: 12px; 
                    min-width: 250px; flex: 1; border: 2px solid var(--border); }
        .game-card h2 { color: var(--accent); margin-bottom: 15px; }
        .game-card h3 { color: var(--text); background: var(--accent); padding: 5px 10px; 
                       border-radius: 4px; margin: 10px 0 5px; }
        .game-card ul { list-style: none; }
        .game-card li { padding: 8px; border-bottom: 1px solid var(--border); }
        .game-card li:hover { background: var(--border); }
        .section { margin: 20px 0; }
        .section h2 { color: var(--accent); margin-bottom: 15px; }
        .category-btn { background: var(--border); color: var(--text); border: none; padding: 10px 20px; 
                       margin: 5px; border-radius: 6px; cursor: pointer; }
        .category-btn:hover { background: var(--accent); }
        .clickable-item { cursor: pointer; }
        .clickable-item:hover { background: var(--accent); color: white; }
        .search-result-item { padding: 8px; border-bottom: 1px solid var(--border); cursor: pointer; }
        .search-result-item:hover { background: var(--border); }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                 background: rgba(0,0,0,0.8); z-index: 100; }
        .modal-content { background: var(--bg-secondary); margin: 50px auto; padding: 30px; 
                        max-width: 800px; border-radius: 12px; max-height: 80vh; overflow-y: auto; }
        .close { float: right; font-size: 30px; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid var(--border); }
        th { background: var(--accent); color: white; }
        tr:hover { background: var(--border); }
        .header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        .header-buttons { display: flex; gap: 10px; }
        .btn { background: var(--accent); color: #fff; border: none; padding: 10px 20px; 
                     border-radius: 6px; cursor: pointer; }
        .btn:hover { opacity: 0.9; }
        .status { font-size: 12px; color: #888; }
        
        /* Mobile responsiveness */
        @media (max-width: 600px) {
            .games { flex-direction: column; }
            .game-card { min-width: 100%; }
            .header { flex-direction: column; align-items: flex-start; }
            .header-buttons { width: 100%; }
            .btn { flex: 1; }
            .modal-content { margin: 10px; padding: 15px; max-height: 90vh; }
            table { font-size: 14px; }
            th, td { padding: 6px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Chrono MCP</h1>
        <div class="header-buttons">
            <button class="btn" onclick="toggleTheme()">🌓 Theme</button>
            <button class="btn" onclick="refreshData()">🔄 Refresh</button>
        </div>
    </div>
    <p class="status" id="status">Data loads automatically from JSON files</p>
    
    <div class="search-box">
        <input type="text" id="search" placeholder="Search all games... (e.g., 'sword', 'fire', 'crono')" 
               onkeyup="search(this.value)">
    </div>
    
    <div class="section">
        <h2 onclick="toggleSection('plots')" style="cursor:pointer">📖 Plot/Story ▾</h2>
        <div id="plots-section" style="display:none">
            <div id="plots" class="games"></div>
        </div>
    </div>
    
    <div id="results" class="games"></div>
    
    <div id="modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2 id="modal-title"></h2>
            <div id="modal-body"></div>
        </div>
    </div>

    <script>
        let gameData = {};
        
        async function loadGames() {
            const status = document.getElementById('status');
            status.textContent = 'Loading...';
            const games = await fetch('/api/games').then(r => r.json());
            const container = document.getElementById('results');
            container.innerHTML = '';  // Clear previous results
            
            for (const game of games) {
                const data = await fetch('/api/' + game).then(r => r.json());
                gameData[game] = data;
                
                const card = document.createElement('div');
                card.className = 'game-card';
                
                let categories = Object.keys(data).filter(k => Array.isArray(data[k]));
                let catsHtml = categories.map(cat => 
                    `<button class="category-btn" onclick="showCategory('${game}', '${cat}')">${cat} (${data[cat].length})</button>`
                ).join('');
                
                card.innerHTML = `
                    <h2>${game}</h2>
                    <p>Platforms: ${(data.platforms || []).join(', ')}</p>
                    <div style="margin-top:15px">${catsHtml}</div>
                `;
                container.appendChild(card);
            }
        }
        
        function showCategory(game, category) {
            const data = gameData[game][category];
            document.getElementById('modal-title').textContent = game + ' - ' + category;
            
            if (data.length === 0 || typeof data[0] === 'string') {
                document.getElementById('modal-body').innerHTML = '<ul>' + 
                    data.map(d => `<li>${d}</li>`).join('') + '</ul>';
            } else {
                // Table view
                const keys = Object.keys(data[0]);
                let html = '<table><thead><tr>' + 
                    keys.map(k => `<th>${k}</th>`).join('') + 
                    '</tr></thead><tbody>';
                html += data.map(row => '<tr>' + 
                    keys.map(k => `<td>${row[k] || '-'}</td>`).join('') + 
                    '</tr>').join('');
                html += '</tbody></table>';
                document.getElementById('modal-body').innerHTML = html;
            }
            
            document.getElementById('modal').style.display = 'block';
        }
        
        function closeModal() {
            document.getElementById('modal').style.display = 'none';
        }
        
        function toggleTheme() {
            document.body.classList.toggle('light-theme');
            localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
        }
        
        function toggleSection(id) {
            const el = document.getElementById(id + '-section');
            el.style.display = el.style.display === 'none' ? 'block' : 'none';
        }
        
        async function loadPlots() {
            try {
                const response = await fetch('/api/plot');
                const data = await response.json();
                const container = document.getElementById('plots');
                
                if (!data.plots || data.plots.length === 0) {
                    container.innerHTML = '<p>No plot data available</p>';
                    return;
                }
                
                for (const plot of data.plots) {
                    const card = document.createElement('div');
                    card.className = 'game-card';
                    const plotId = plot.file.split('/').pop().replace('_plot_tree', '');
                    card.innerHTML = `<h3>${plot.game}</h3><button class="btn" onclick="showPlot('${plotId}')">View Story</button>`;
                    container.appendChild(card);
                }
            } catch(e) {
                console.error('Failed to load plots:', e);
            }
        }
        
        async function showPlot(url) {
            const data = await fetch(url).then(r => r.json());
            let html = `<p><strong>${data.description}</strong></p>`;
            
            if (data.eras) {
                html += '<h3>Eras/Timeline</h3><ul>';
                for (const era of data.eras) {
                    html += `<li><strong>${era.name}</strong> (${era.year}): ${era.description}</li>`;
                }
                html += '</ul>';
            } else if (data.worlds) {
                html += '<h3>Worlds</h3><ul>';
                for (const world of data.worlds) {
                    html += `<li><strong>${world.name}</strong>: ${world.description}</li>`;
                }
                html += '</ul>';
            } else if (data.episodes) {
                html += '<h3>Episodes</h3><ul>';
                for (const ep of data.episodes) {
                    html += `<li><strong>${ep.name}</strong>: ${ep.description}</li>`;
                }
                html += '</ul>';
            }
            
            if (data.character_arcs) {
                html += '<h3>Character Arcs</h3><ul>';
                for (const arc of data.character_arcs) {
                    html += `<li><strong>${arc.character}</strong>: ${arc.arc}</li>`;
                }
                html += '</ul>';
            }
            
            if (data.endings) {
                html += '<h3>Endings</h3><ul>';
                for (const ending of data.endings) {
                    html += `<li><strong>${ending.name}</strong>: ${ending.description}</li>`;
                }
                html += '</ul>';
            }
            
            document.getElementById('modal-title').textContent = data.game + ' - Plot Tree';
            document.getElementById('modal-body').innerHTML = html;
            document.getElementById('modal').style.display = 'block';
        }
        
        // Load saved theme
        if (localStorage.getItem('theme') === 'light') {
            document.body.classList.add('light-theme');
        }
        
        async function refreshData() {
            gameData = {};  // Clear cache
            await fetch('/api/refresh').then(r => r.json());
            loadGames();
        }
        
        async function search(query) {
            if (query.length < 2) {
                document.getElementById('results').innerHTML = '';
                loadGames();
                return;
            }
            
            const results = await fetch('/api/search?q=' + encodeURIComponent(query)).then(r => r.json());
            const container = document.getElementById('results');
            container.innerHTML = `<h2>Search Results for "${query}"</h2>`;
            
            if (results.matches.length === 0) {
                container.innerHTML += '<p>No results found.</p>';
                return;
            }
            
            // Group by game and category
            const byGame = {};
            for (const m of results.matches) {
                const key = m.game + '|' + m.category;
                if (!byGame[key]) byGame[key] = [];
                byGame[key].push(m);
            }
            
            for (const [key, matches] of Object.entries(byGame)) {
                const [game, category] = key.split('|');
                const card = document.createElement('div');
                card.className = 'game-card';
                
                // Show individual items with clickable links
                let itemsHtml = matches.slice(0, 20).map(m => {
                    const data = m.data || {};
                    const name = data.name || data.text || data.character || JSON.stringify(data).slice(0, 30);
                    const id = data.id || data.offset || '';
                    return `<li class="clickable-item" onclick="showSearchItem('${game}', '${category}', ${JSON.stringify(data).replace(/'/g, "&#39;")})">${name}</li>`;
                }).join('');
                
                if (matches.length > 20) {
                    itemsHtml += `<li>... and ${matches.length - 20} more</li>`;
                }
                
                card.innerHTML = `
                    <h2>${game} - ${category}</h2>
                    <p>${matches.length} matches</p>
                    <ul>${itemsHtml}</ul>
                `;
                container.appendChild(card);
            }
        }
        
        function showSearchItem(game, category, data) {
            // Show clicked item in modal
            document.getElementById('modal-title').textContent = game + ' - ' + category;
            
            if (typeof data === 'object') {
                let html = '<table>';
                for (const [key, val] of Object.entries(data)) {
                    html += `<tr><th>${key}</th><td>${val}</td></tr>`;
                }
                html += '</table>';
                document.getElementById('modal-body').innerHTML = html;
            } else {
                document.getElementById('modal-body').innerHTML = '<pre>' + data + '</pre>';
            }
            
            document.getElementById('modal').style.display = 'block';
        }
        
        // Close modal on outside click
        window.onclick = function(e) {
            if (e.target.id === 'modal') closeModal();
        }
        
        loadGames();
        loadPlots();
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug, threaded=True)
