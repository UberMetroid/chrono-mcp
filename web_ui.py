#!/usr/bin/env python3
"""
Chrono Series Web UI
Simple browser for Chrono game data
Run: python web_ui.py
"""

import json
import os
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Configuration
BASE_DIR = Path(os.environ.get("CHRONO_BASE", "/home/jeryd/Code/Chrono_Series"))
DATA_DIR = BASE_DIR / "data"

_data_cache = None

# Load data
def load_data(force_reload=False):
    """Load all game data"""
    global _data_cache
    if _data_cache is None or force_reload:
        with open(DATA_DIR / "extracted/chrono_master_complete.json") as f:
            _data_cache = json.load(f)
    return _data_cache

@app.route('/api/refresh')
def api_refresh():
    """Force reload data from files"""
    load_data(force_reload=True)
    return jsonify({"status": "ok", "message": "Data refreshed"})

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/games')
def api_games():
    """Get all games"""
    data = load_data()
    return jsonify(list(data.get("games", {}).keys()))

@app.route('/api/<game>')
def api_game(game):
    """Get game data"""
    data = load_data()
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

@app.route('/api/<game>/<category>')
def api_category(game, category):
    """Get specific category (characters, items, etc.)"""
    data = load_data()
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
    
    return jsonify({"error": "Not found"})

@app.route('/api/search')
def api_search():
    """Search across all games"""
    query = request.args.get('q', '').lower()
    data = load_data()
    results = {"query": query, "matches": []}
    
    for game_name, game_data in data.get("games", {}).items():
        for category, items in game_data.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        for key, val in item.items():
                            if isinstance(val, str) and query in val.lower():
                                results["matches"].append({
                                    "game": game_name,
                                    "category": category,
                                    "data": item
                                })
                                break
                    elif isinstance(item, str) and query in item.lower():
                        results["matches"].append({
                            "game": game_name,
                            "category": category,
                            "data": item
                        })
    
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
    from flask import send_from_directory
    return send_from_directory(DATA_DIR / "audio", filename)

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Chrono ROM Tools</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: #1a1a2e; color: #eee; padding: 20px; }
        h1 { color: #e94560; margin-bottom: 20px; }
        .search-box { margin-bottom: 30px; }
        .search-box input { width: 100%; padding: 15px; font-size: 18px; 
                           background: #16213e; border: 2px solid #e94560; 
                           color: #fff; border-radius: 8px; }
        .games { display: flex; gap: 20px; flex-wrap: wrap; }
        .game-card { background: #16213e; padding: 20px; border-radius: 12px; 
                    min-width: 250px; flex: 1; border: 2px solid #0f3460; }
        .game-card h2 { color: #e94560; margin-bottom: 15px; }
        .game-card h3 { color: #0f3460; background: #e94560; padding: 5px 10px; 
                       border-radius: 4px; margin: 10px 0 5px; }
        .game-card ul { list-style: none; }
        .game-card li { padding: 8px; border-bottom: 1px solid #0f3460; }
        .game-card li:hover { background: #0f3460; }
        .category-btn { background: #0f3460; color: #fff; border: none; padding: 10px 20px; 
                       margin: 5px; border-radius: 6px; cursor: pointer; }
        .category-btn:hover { background: #e94560; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                 background: rgba(0,0,0,0.8); z-index: 100; }
        .modal-content { background: #16213e; margin: 50px auto; padding: 30px; 
                        max-width: 800px; border-radius: 12px; max-height: 80vh; overflow-y: auto; }
        .close { float: right; font-size: 30px; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { background: #e94560; }
        tr:hover { background: #0f3460; }
        .header { display: flex; justify-content: space-between; align-items: center; }
        .refresh-btn { background: #e94560; color: #fff; border: none; padding: 10px 20px; 
                     border-radius: 6px; cursor: pointer; margin-left: 20px; }
        .refresh-btn:hover { background: #ff6b8a; }
        .status { font-size: 12px; color: #888; }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚔️ Chrono ROM Tools</h1>
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
    </div>
    <p class="status" id="status">Data loads automatically from JSON files</p>
    
    <div class="search-box">
        <input type="text" id="search" placeholder="Search all games... (e.g., 'sword', 'fire', 'crono')" 
               onkeyup="search(this.value)">
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
            
            // Group by game
            const byGame = {};
            for (const m of results.matches) {
                if (!byGame[m.game]) byGame[m.game] = [];
                byGame[m.game].push(m);
            }
            
            for (const [game, matches] of Object.entries(byGame)) {
                const card = document.createElement('div');
                card.className = 'game-card';
                card.innerHTML = `<h2>${game}</h2><p>${matches.length} matches</p>`;
                container.appendChild(card);
            }
        }
        
        // Close modal on outside click
        window.onclick = function(e) {
            if (e.target.id === 'modal') closeModal();
        }
        
        loadGames();
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
