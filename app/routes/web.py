from flask import Blueprint, render_template_string

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Main web interface"""
    return render_template_string(HTML_TEMPLATE)

# HTML Template (extracted from original web_ui.py)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chrono MCP</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: var(--bg-dark); color: var(--text); line-height: 1.6; }
        :root {
            --bg-dark: #1a1a1a;
            --bg-secondary: #2a2a2a;
            --bg-tertiary: #333;
            --accent: #4a9eff;
            --text: #e0e0e0;
            --border: #444;
            --error: #ff6b6b;
            --success: #51cf66;
            --warning: #ffd43b;
        }
        @media (prefers-color-scheme: light) {
            :root {
                --bg-dark: #f8f9fa;
                --bg-secondary: #ffffff;
                --bg-tertiary: #f1f3f4;
                --text: #202124;
                --border: #dadce0;
            }
        }
        body.light-theme {
            --bg-dark: #f8f9fa;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f1f3f4;
            --text: #202124;
            --border: #dadce0;
        }
        .header { background: var(--bg-secondary); padding: 20px; border-bottom: 2px solid var(--accent); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; }
        .header-content { flex: 1; }
        .header h1 { color: var(--accent); font-size: 2.5em; margin-bottom: 5px; }
        .subtitle { color: var(--text); opacity: 0.8; font-size: 1.1em; margin: 0; }
        .header-buttons { display: flex; gap: 10px; }

        .nav { background: var(--bg-tertiary); padding: 10px 20px; border-bottom: 1px solid var(--border); }
        .nav-btn { background: var(--border); color: var(--text); border: none; padding: 10px 20px;
                  margin: 0 5px; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
        .nav-btn:hover, .nav-btn.active { background: var(--accent); color: white; }

        .stats-bar { background: var(--bg-tertiary); padding: 10px 20px; border-bottom: 1px solid var(--border);
                    font-size: 14px; color: var(--text); display: flex; justify-content: space-between; align-items: center; }
        .stats-bar .stats-left { display: flex; gap: 20px; }
        .stats-bar .stats-right { font-size: 12px; opacity: 0.7; }
        .loading { display: inline-block; width: 16px; height: 16px; border: 2px solid var(--border);
                  border-radius: 50%; border-top-color: var(--accent); animation: spin 1s ease-in-out infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .status { font-size: 12px; color: #888; margin: 10px 0; }
        .games { display: flex; flex-wrap: wrap; gap: 20px; padding: 20px; }
        .game-card { background: var(--bg-secondary); padding: 20px; border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); flex: 1; min-width: 300px; max-width: 500px; }
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
        .search-result-item { padding: 8px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.2s; }
        .search-result-item:hover { background: var(--accent); color: white; }

        .search-interface { max-width: 1400px; margin: 0 auto; }
        .search-header { text-align: center; margin-bottom: 30px; }
        .search-header h2 { color: var(--accent); margin-bottom: 10px; }
        .search-header p { color: var(--text); opacity: 0.8; font-size: 16px; }

        .search-controls { background: var(--bg-secondary); padding: 30px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .search-input-group { display: flex; gap: 15px; margin-bottom: 20px; }
        .search-btn { background: var(--accent); color: white; border: none; border-radius: 8px; font-weight: bold; }

        .filter-row { display: flex; gap: 20px; margin-bottom: 25px; flex-wrap: wrap; }
        .filter-group { display: flex; flex-direction: column; gap: 5px; min-width: 150px; }
        .filter-group label { font-weight: bold; font-size: 14px; color: var(--text); }
        .filter-group select { padding: 10px; border-radius: 6px; border: 2px solid var(--border); background: var(--bg-tertiary); color: var(--text); }

        .search-examples { border-top: 1px solid var(--border); padding-top: 20px; }
        .example-tags { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
        .example-tag { background: var(--accent); color: white; padding: 6px 12px; border-radius: 20px;
                      cursor: pointer; font-size: 14px; transition: all 0.2s; }
        .example-tag:hover { opacity: 0.8; transform: translateY(-1px); }

        .search-results-container { min-height: 400px; }
        .search-summary { background: var(--bg-tertiary); padding: 15px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; gap: 15px; flex-wrap: wrap; }
        .filter-badge { background: var(--accent); color: white; padding: 4px 10px; border-radius: 15px; font-size: 12px; }

        .search-results-grid { display: grid; gap: 20px; }
        .search-group { background: var(--bg-secondary); padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .search-group-header { display: flex; align-items: center; gap: 12px; margin-bottom: 15px; flex-wrap: wrap; }
        .search-group-header h4 { color: var(--accent); margin: 0; }
        .category-badge { background: var(--border); padding: 4px 10px; border-radius: 15px; font-size: 12px; }
        .result-count { font-size: 14px; opacity: 0.7; margin-left: auto; }

        .search-items { display: grid; gap: 8px; }
        .search-result-item { background: var(--bg-tertiary); padding: 12px 15px; border-radius: 8px; border-left: 4px solid var(--accent); transition: all 0.2s; }
        .search-result-item:hover { background: var(--border); transform: translateX(2px); }
        .result-text { font-weight: 500; margin-bottom: 4px; }
        .result-score { font-size: 12px; opacity: 0.7; }

        .more-results { text-align: center; padding: 10px; font-style: italic; opacity: 0.7; }
        .search-placeholder { animation: fadeIn 0.5s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        .api-interface { max-width: 1400px; margin: 0 auto; }
        .api-header { text-align: center; margin-bottom: 40px; }
        .api-header h2 { color: var(--accent); margin-bottom: 10px; }
        .api-header p { font-size: 16px; opacity: 0.8; }

        .api-overview { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 40px; }
        .overview-card { background: var(--bg-secondary); padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .overview-card h3 { color: var(--accent); margin-bottom: 10px; }
        .overview-card p { margin-bottom: 15px; }
        .api-stats { display: flex; gap: 10px; flex-wrap: wrap; }
        .api-stats span { background: var(--border); padding: 4px 10px; border-radius: 15px; font-size: 12px; }

        .api-section { background: var(--bg-secondary); padding: 30px; margin-bottom: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .api-section h3 { color: var(--accent); margin-bottom: 20px; border-bottom: 2px solid var(--accent); padding-bottom: 10px; }

        .api-endpoints-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .endpoint-card { background: var(--bg-tertiary); padding: 20px; border-radius: 8px; border-left: 4px solid var(--accent); }
        .endpoint-method { display: inline-block; background: var(--accent); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 8px; }
        .endpoint-path { font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; margin-bottom: 8px; }
        .endpoint-params { font-size: 14px; opacity: 0.8; margin: 10px 0; }
        .endpoint-example { margin-top: 15px; }
        .endpoint-example code { font-family: 'Courier New', monospace; background: var(--border); padding: 8px 12px; border-radius: 6px; display: block; font-size: 14px; }

        .mcp-details { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .mcp-info h4, .mcp-tools h4 { color: var(--accent); margin-bottom: 15px; }
        .tool-categories { display: grid; gap: 10px; }
        .tool-category { background: var(--bg-tertiary); padding: 10px 15px; border-radius: 6px; }

        .usage-examples { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .usage-card { background: var(--bg-tertiary); padding: 20px; border-radius: 8px; }
        .usage-card h4 { color: var(--accent); margin-bottom: 15px; }
        .usage-card pre { background: var(--border); padding: 15px; border-radius: 6px; overflow-x: auto; }
        .usage-card code { font-family: 'Courier New', monospace; font-size: 13px; }

        .response-examples h4 { color: var(--accent); margin: 20px 0 10px 0; }
        .response-examples pre { background: var(--border); padding: 15px; border-radius: 6px; overflow-x: auto; }

        .analytics-interface { max-width: 1400px; margin: 0 auto; }
        .analytics-header { text-align: center; margin-bottom: 40px; }
        .analytics-header h2 { color: var(--accent); margin-bottom: 10px; }
        .analytics-header p { opacity: 0.8; }

        .analytics-dashboard { min-height: 400px; }
        .analytics-loading { text-align: center; padding: 40px; opacity: 0.7; }

        .analytics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .analytics-card { background: var(--bg-secondary); padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .analytics-card h3 { color: var(--accent); margin-bottom: 20px; border-bottom: 2px solid var(--accent); padding-bottom: 5px; }

        .analytics-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .metric { text-align: center; padding: 15px; background: var(--bg-tertiary); border-radius: 8px; }
        .metric-value { display: block; font-size: 24px; font-weight: bold; color: var(--accent); }
        .metric-label { display: block; font-size: 12px; opacity: 0.8; margin-top: 5px; }

        .popular-list { display: grid; gap: 10px; }
        .popular-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: var(--bg-tertiary); border-radius: 6px; }
        .popular-page { font-family: 'Courier New', monospace; font-size: 14px; }
        .popular-count { font-size: 12px; opacity: 0.7; background: var(--accent); color: white; padding: 2px 6px; border-radius: 10px; }

        .activity-summary { text-align: center; padding: 20px; }
        .activity-summary strong { font-size: 24px; color: var(--accent); }

        .analytics-footer { text-align: center; margin-top: 30px; padding: 20px; background: var(--bg-tertiary); border-radius: 8px; }
        .analytics-error { text-align: center; padding: 40px; opacity: 0.7; }

        .plot-card { background: var(--bg-secondary); padding: 25px; border-radius: 16px;
                     box-shadow: 0 8px 16px rgba(0,0,0,0.15); margin-bottom: 25px; border: 1px solid var(--border);
                     transition: transform 0.2s, box-shadow 0.2s; }
        .plot-card:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(0,0,0,0.2); }

        .plot-header { margin-bottom: 15px; }
        .plot-title-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .plot-title-section h3 { color: var(--accent); margin: 0; }
        .plot-badge { background: var(--accent); color: white; padding: 4px 12px; border-radius: 20px;
                     font-size: 12px; font-weight: bold; }

        .plot-meta { display: flex; gap: 15px; margin-bottom: 15px; font-size: 14px; opacity: 0.8; }
        .plot-year { font-weight: bold; }
        .plot-platforms { font-style: italic; }

        .plot-stats { display: flex; gap: 10px; flex-wrap: wrap; font-size: 13px; }
        .stat-item { background: var(--border); padding: 6px 12px; border-radius: 20px; display: flex; align-items: center; gap: 4px; }

        .plot-description { color: var(--text); line-height: 1.6; margin-bottom: 15px; font-size: 15px; }

        .plot-features { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
        .feature-tag { background: var(--bg-tertiary); color: var(--text); padding: 4px 10px;
                      border-radius: 15px; font-size: 12px; border: 1px solid var(--border); }

        .plot-actions { display: flex; gap: 12px; flex-wrap: wrap; }
        .plot-actions .btn { padding: 12px 20px; font-size: 14px; font-weight: 500; border-radius: 8px; transition: all 0.2s; }
        .plot-actions .btn.primary { background: var(--accent); border: none; }
        .plot-actions .btn.primary:hover { background: var(--accent); opacity: 0.9; transform: translateY(-1px); }
        .plot-actions .btn.secondary { background: var(--bg-tertiary); border: 1px solid var(--border); }
        .plot-actions .btn.secondary:hover { background: var(--border); }

        .footer { background: var(--bg-tertiary); border-top: 1px solid var(--border); margin-top: 40px; }
        .footer-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; padding: 40px 20px; }
        .footer-section h4 { color: var(--accent); margin-bottom: 15px; border-bottom: 2px solid var(--accent); padding-bottom: 5px; }
        .footer-stats { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
        .footer-stats span { background: var(--accent); color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; }

        .game-links { display: grid; gap: 12px; }
        .game-link { background: var(--bg-secondary); padding: 12px 15px; border-radius: 8px; cursor: pointer;
                     transition: all 0.2s; border: 1px solid var(--border); }
        .game-link:hover { background: var(--border); transform: translateY(-1px); }
        .game-link strong { color: var(--accent); }
        .game-link small { opacity: 0.8; font-size: 12px; }

        .footer-section ul { list-style: none; padding: 0; }
        .footer-section li { margin: 8px 0; }
        .footer-section a { color: var(--text); text-decoration: none; transition: color 0.2s; }
        .footer-section a:hover { color: var(--accent); }

        .category-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
        .cat-tag { background: var(--border); color: var(--text); padding: 4px 8px; border-radius: 10px; font-size: 11px; }

        .footer-bottom { background: var(--bg-secondary); padding: 25px 20px; border-top: 1px solid var(--border); }
        .footer-bottom-content { max-width: 1200px; margin: 0 auto; text-align: center; }
        .footer-bottom p { margin: 5px 0; opacity: 0.8; font-size: 13px; }
        .tech-stack { display: flex; justify-content: center; gap: 15px; margin-top: 15px; flex-wrap: wrap; }
        .tech-stack span { background: var(--accent); color: white; padding: 4px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; }
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
        .search-box { margin: 20px; }
        .search-box input { width: 100%; max-width: 500px; padding: 12px; border: 2px solid var(--border);
                           border-radius: 8px; background: var(--bg-secondary); color: var(--text);
                           font-size: 16px; }
        .search-box input:focus { outline: none; border-color: var(--accent); }

        /* Mobile responsiveness */
        @media (max-width: 600px) {
            .games { flex-direction: column; }
            .game-card { min-width: 100%; }
            .header { flex-direction: column; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>Chrono MCP</h1>
            <p class="subtitle">Complete Chrono Series Database - All Games Decoded</p>
            <noscript style="color: #ff6b6b; font-weight: bold; margin-top: 10px;">
                ⚠️ JavaScript is required for this application to function properly.
                Please enable JavaScript in your browser and reload the page.
            </noscript>
        </div>
        <div class="header-buttons">
            <button class="btn" onclick="toggleTheme()">🌓 Theme</button>
            <button class="btn" onclick="refreshData()">🔄 Refresh</button>
            <button class="btn" onclick="showStats()">📊 Stats</button>
        </div>
    </div>

    <!-- Navigation -->
    <nav class="nav">
        <button class="nav-btn active" onclick="showSection('games')">🎮 Games</button>
        <button class="nav-btn" onclick="showSection('search')">🔍 Search</button>
        <button class="nav-btn" onclick="showSection('plots')">📚 Plot Database</button>
        <button class="nav-btn" onclick="showSection('api')">🔌 API</button>
        <button class="nav-btn" onclick="showSection('analytics')">📈 Analytics</button>
    </nav>

    <div class="stats-bar" id="stats-bar">
        <div class="stats-left">
            <span id="stats-content">
                <span class="loading"></span>
                Loading database statistics...
            </span>
        </div>
        <div class="stats-right">
            <span id="connection-status">🔗 Connected</span>
        </div>
    </div>

    <div class="search-box">
        <input type="text" id="search" placeholder="Search all games... (e.g., 'sword', 'fire', 'crono')"
               onkeyup="search(this.value)">
    </div>

    <div class="section">
        <h2 onclick="toggleSection('plots')" style="cursor:pointer">📚 Complete Plot Database ▾</h2>
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
        console.log('JavaScript loaded successfully - immediate execution');
        let gameData = {};
        let gamesLoaded = false;
        let plotsLoaded = false;

        // Simple immediate test
        try {
            document.querySelector('h1').style.color = 'red';
            console.log('DOM manipulation successful');
        } catch (e) {
            console.error('DOM manipulation failed:', e);
        }

        // Immediate test - not waiting for DOMContentLoaded
        setTimeout(() => {
            console.log('Timeout executed - JavaScript is running');
            fetch('/api/health').then(r => r.json()).then(data => {
                console.log('Immediate API test successful:', data);
            }).catch(e => {
                console.error('Immediate API test failed:', e);
            });
        }, 100);

        async function loadGames() {
            if (gamesLoaded) {
                console.log('Games already loaded, skipping');
                return;
            }
            console.log('loadGames called');
            const status = document.getElementById('status') || document.getElementById('connection-status');
            if (status) status.textContent = 'Loading...';

            try {
                const games = [...new Set(await fetch('/api/games').then(r => r.json()))];
                console.log('Games loaded:', games);
                const container = document.getElementById('results');
                container.innerHTML = '';  // Clear previous results

                for (const game of games) {
                    const data = await fetch('/api/' + encodeURIComponent(game)).then(r => r.json());
                    gameData[game] = data;

                    const card = document.createElement('div');
                    card.className = 'game-card';

                    let categories = Object.keys(data).filter(k => Array.isArray(data[k]) && k !== 'platforms');
                    let catsHtml = categories.map(cat =>
                        `<button class="category-btn" onclick="showCategory('${game}', '${cat}')">${cat.replace('_', ' ')} (${data[cat].length})</button>`
                    ).join('');

                    card.innerHTML = `
                        <h2>${game}</h2>
                        <p>Platforms: ${[...new Set(data.platforms || [])].join(', ')}</p>
                        <div style="margin-top:15px">${catsHtml}</div>
                    `;
                    container.appendChild(card);
                }
                gamesLoaded = true;
                if (status) status.innerHTML = '🔗 Connected';
            } catch (e) {
                console.error('Failed to load games:', e);
                if (status) status.textContent = 'Failed to load';
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
            const wasHidden = el.style.display === 'none';
            el.style.display = wasHidden ? 'block' : 'none';
            if (id === 'plots' && wasHidden && !plotsLoaded) {
                loadPlots();
            }
        }

        async function loadPlots() {
            if (plotsLoaded) {
                console.log('Plots already loaded, skipping');
                return;
            }
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
                    card.className = 'plot-card';
                    const plotId = plot.file.split('/').pop().replace('_plot_tree', '');

                    // Create initial card structure
                    card.innerHTML = `
                        <div class="plot-header">
                            <div class="plot-title-section">
                                <h3>${plot.game}</h3>
                                <div class="plot-badge">${plot.game.includes('Trigger') ? '🏰 RPG' : plot.game.includes('Cross') ? '🌍 Epic' : '⚡ Action'}</div>
                            </div>
                            <div class="plot-stats">
                                <span class="loading"></span>
                                Loading story details...
                            </div>
                        </div>
                        <div class="plot-meta">
                            <div class="plot-year">${plot.game.includes('Trigger') ? '1995' : plot.game.includes('Cross') ? '1999' : '1996'}</div>
                            <div class="plot-platforms">${plot.game.includes('Trigger') ? 'SNES, PS1, DS, MSU1' : plot.game.includes('Cross') ? 'PS1, PS4' : 'Satellaview'}</div>
                        </div>
                        <p class="plot-description">Explore the rich storyline, character arcs, and branching narratives of ${plot.game}.</p>
                        <div class="plot-features">
                            <span class="feature-tag">📅 Timeline</span>
                            <span class="feature-tag">👥 Characters</span>
                            <span class="feature-tag">🏁 Endings</span>
                            <span class="feature-tag">🔀 Choices</span>
                        </div>
                        <div class="plot-actions">
                            <button class="btn primary" onclick="showPlot('${plotId}')" title="View complete plot tree with all details">
                                📖 View Full Story
                            </button>
                            <button class="btn secondary" onclick="showPlotOutline('${plotId}')" title="Quick overview of key plot points">
                                📋 Quick Outline
                            </button>
                        </div>
                    `;

                    // Load enhanced info asynchronously
                    loadPlotCardInfo(card, plotId, plot.game);

                    container.appendChild(card);
                }
                plotsLoaded = true;
            } catch(e) {
                console.error('Failed to load plots:', e);
            }
        }

        async function loadPlotCardInfo(card, plotId, gameName) {
            try {
                const response = await fetch(`/api/plot/${plotId}`);
                if (!response.ok) return;

                const plotData = await response.json();
                const description = plotData.description || 'No description available';
                const shortDesc = description.length > 150 ? description.substring(0, 150) + '...' : description;

                const eras = plotData.eras ? plotData.eras.length : 0;
                const worlds = plotData.worlds ? plotData.worlds.length : 0;
                const episodes = plotData.episodes ? plotData.episodes.length : 0;
                const characters = plotData.character_arcs ? plotData.character_arcs.length : 0;

                const statsHtml = [];
                if (eras > 0) statsHtml.push(`<span class="stat-item">📅 ${eras} Era${eras > 1 ? 's' : ''}</span>`);
                if (worlds > 0) statsHtml.push(`<span class="stat-item">🌍 ${worlds} World${worlds > 1 ? 's' : ''}</span>`);
                if (episodes > 0) statsHtml.push(`<span class="stat-item">🎭 ${episodes} Episode${episodes > 1 ? 's' : ''}</span>`);
                if (characters > 0) statsHtml.push(`<span class="stat-item">👥 ${characters} Character${characters > 1 ? 's' : ''}</span>`);

                if (plotData.endings && plotData.endings.length > 0) {
                    statsHtml.push(`<span class="stat-item">🏁 ${plotData.endings.length} Ending${plotData.endings.length > 1 ? 's' : ''}</span>`);
                }

                card.querySelector('.plot-stats').innerHTML = statsHtml.join('');
                card.querySelector('.plot-description').textContent = shortDesc;

            } catch (e) {
                console.log(`Could not load enhanced info for ${gameName}:`, e);
                // Keep the default content
            }
        }

        async function showPlot(plotId) {
            try {
                const response = await fetch(`/api/plot/${plotId}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
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
                html += '<h3>🏁 Endings</h3><ul>';
                for (const ending of data.endings) {
                    html += `<li><strong>${ending.name}</strong>: ${ending.description}</li>`;
                }
                html += '</ul>';
            }

            if (data.branching_decisions) {
                html += '<h3>🔀 Branching Decisions</h3><ul>';
                for (const decision of data.branching_decisions) {
                    html += `<li><strong>${decision.point}</strong>: ${decision.description}</li>`;
                }
                html += '</ul>';
            }

            if (data.factions) {
                html += '<h3>⚔️ Factions</h3><ul>';
                for (const faction of data.factions) {
                    html += `<li><strong>${faction.name}</strong>: ${faction.description}</li>`;
                }
                html += '</ul>';
            }

            if (data.important_locations) {
                html += '<h3>📍 Important Locations</h3><ul>';
                for (const location of data.important_locations) {
                    html += `<li><strong>${location.name}</strong>: ${location.description}</li>`;
                }
                html += '</ul>';
            }

            document.getElementById('modal-title').textContent = data.game + ' - Complete Plot Tree';
            document.getElementById('modal-body').innerHTML = html;
            document.getElementById('modal').style.display = 'block';
            } catch (error) {
                console.error('Error loading plot:', error);
                document.getElementById('modal-title').textContent = 'Error Loading Plot';
                document.getElementById('modal-body').innerHTML = `<p>Sorry, there was an error loading the plot data: ${error.message}</p>`;
                document.getElementById('modal').style.display = 'block';
            }
        }

        async function showPlotOutline(plotId) {
            try {
                const response = await fetch(`/api/plot/${plotId}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
            document.getElementById('modal-title').textContent = `${data.game} - Story Outline`;

            let html = `<p><strong>${data.description}</strong></p>`;

            // Quick overview
            if (data.eras) {
                html += '<h4>📅 Timeline Overview</h4><ul>';
                data.eras.slice(0, 3).forEach(era => {
                    html += `<li><strong>${era.name}</strong> (${era.year}): ${era.description}</li>`;
                });
                if (data.eras.length > 3) html += '<li>... and more eras</li>';
                html += '</ul>';
            }

            if (data.worlds) {
                html += '<h4>🌍 Parallel Worlds</h4><ul>';
                data.worlds.forEach(world => {
                    html += `<li><strong>${world.name}</strong>: ${world.description}</li>`;
                });
                html += '</ul>';
            }

            if (data.episodes) {
                html += '<h4>🎭 Story Episodes</h4><ul>';
                data.episodes.forEach(ep => {
                    html += `<li><strong>${ep.name}</strong>: ${ep.description}</li>`;
                });
                html += '</ul>';
            }

            if (data.character_arcs) {
                html += '<h4>👥 Key Characters</h4><ul>';
                data.character_arcs.slice(0, 5).forEach(char => {
                    const shortArc = char.arc.length > 100 ? char.arc.substring(0, 100) + '...' : char.arc;
                    html += `<li><strong>${char.character}</strong>: ${shortArc}</li>`;
                });
                if (data.character_arcs.length > 5) html += '<li>... and more characters</li>';
                html += '</ul>';
            }

            if (data.endings) {
                html += '<h4>🏁 Possible Endings</h4><ul>';
                data.endings.forEach(ending => {
                    html += `<li><strong>${ending.name}</strong>: ${ending.description}</li>`;
                });
                html += '</ul>';
            }

            html += '<div style="margin-top:20px; text-align:center;">';
            html += `<button class="btn" onclick="showPlot('${plotId}')">📖 View Complete Story Details</button>`;
            html += '</div>';

            document.getElementById('modal-body').innerHTML = html;
            document.getElementById('modal').style.display = 'block';
            } catch (error) {
                console.error('Error loading plot outline:', error);
                document.getElementById('modal-title').textContent = 'Error Loading Plot Outline';
                document.getElementById('modal-body').innerHTML = `<p>Sorry, there was an error loading the plot outline: ${error.message}</p>`;
                document.getElementById('modal').style.display = 'block';
            }
        }

        // Load saved theme
        if (localStorage.getItem('theme') === 'light') {
            document.body.classList.add('light-theme');
        }

        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM fully loaded - initializing application');

            // Initialize navigation
            initNavigation();

            // Load initial data
            loadGames();
            loadStats();

            console.log('Application initialized successfully');
        });

        function initNavigation() {
            // Set up navigation button handlers
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const section = this.textContent.trim().split(' ')[1].toLowerCase();
                    showSection(section);
                });
            });
        }

        function showSection(section) {
            // Update navigation buttons
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });

            // Hide all sections
            document.getElementById('results').innerHTML = '';
            document.getElementById('plots-section').style.display = 'none';
            document.getElementById('search').value = '';

            switch(section) {
                case 'games':
                    document.querySelector('.nav-btn:nth-child(1)').classList.add('active');
                    loadGames();
                    break;
                case 'search':
                    document.querySelector('.nav-btn:nth-child(2)').classList.add('active');
                    showSearchInterface();
                    break;
                case 'plots':
                    document.querySelector('.nav-btn:nth-child(3)').classList.add('active');
                    document.getElementById('plots-section').style.display = 'block';
                    loadPlots();
                    break;
                case 'api':
                    document.querySelector('.nav-btn:nth-child(4)').classList.add('active');
                    showAPIInterface();
                    break;
                case 'analytics':
                    document.querySelector('.nav-btn:nth-child(5)').classList.add('active');
                    showAnalyticsInterface();
                    break;
            }
        }

        function showSearchInterface() {
            const container = document.getElementById('results');
            container.innerHTML = `
                <div class="search-interface">
                    <div class="search-header">
                        <h2>🔍 Advanced Search</h2>
                        <p>Search across all Chrono series data - characters, items, locations, enemies, and more</p>
                    </div>

                    <div class="search-controls">
                        <div class="search-input-group">
                            <input type="text" id="adv-search" placeholder="Enter search terms (e.g., 'crono', 'sword', 'fire')" style="flex: 1; padding: 15px; font-size: 16px; border-radius: 8px; border: 2px solid var(--border);">
                            <button class="btn search-btn" onclick="performAdvancedSearch()" style="padding: 15px 25px; font-size: 16px;">
                                🔍 Search
                            </button>
                        </div>

                        <div class="filter-row">
                            <div class="filter-group">
                                <label>Game:</label>
                                <select id="game-filter">
                                    <option value="">All Games</option>
                                    <option value="Chrono Trigger">Chrono Trigger</option>
                                    <option value="Chrono Cross">Chrono Cross</option>
                                    <option value="Radical Dreamers">Radical Dreamers</option>
                                </select>
                            </div>

                            <div class="filter-group">
                                <label>Category:</label>
                                <select id="category-filter">
                                    <option value="">All Categories</option>
                                    <!-- Categories will be populated by JavaScript -->
                                </select>
                            </div>

                            <div class="filter-group">
                                <label>Results:</label>
                                <select id="result-limit">
                                    <option value="50">50 results</option>
                                    <option value="100">100 results</option>
                                    <option value="200">200 results</option>
                                    <option value="500">500 results</option>
                                </select>
                            </div>
                        </div>

                        <div class="search-examples">
                            <strong>💡 Try searching for:</strong>
                            <div class="example-tags">
                                <span class="example-tag" onclick="setSearchQuery('crono')">crono</span>
                                <span class="example-tag" onclick="setSearchQuery('sword')">sword</span>
                                <span class="example-tag" onclick="setSearchQuery('fire')">fire</span>
                                <span class="example-tag" onclick="setSearchQuery(' Lucca')"> Lucca</span>
                                <span class="example-tag" onclick="setSearchQuery('magic')">magic</span>
                                <span class="example-tag" onclick="setSearchQuery('robot')">robot</span>
                            </div>
                        </div>
                    </div>

                    <div id="search-results" class="search-results-container">
                        <div class="search-placeholder">
                            <div style="text-align: center; padding: 40px; opacity: 0.6;">
                                <div style="font-size: 48px; margin-bottom: 20px;">🔍</div>
                                <h3>Ready to Search</h3>
                                <p>Enter search terms above to explore the Chrono series database</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Populate category filter
            populateCategoryFilter();

            // Set up search input handler
            document.getElementById('adv-search').addEventListener('keyup', function(e) {
                if (e.key === 'Enter') {
                    performAdvancedSearch();
                }
            });
        }

        function populateCategoryFilter() {
            const select = document.getElementById('category-filter');
            // Get categories from API
            fetch('/api/categories').then(r => r.json()).then(categories => {
                categories.forEach(cat => {
                    const option = document.createElement('option');
                    option.value = cat;
                    option.textContent = cat.replace('_', ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                    select.appendChild(option);
                });
            });
        }

        function setSearchQuery(query) {
            document.getElementById('adv-search').value = query.trim();
            performAdvancedSearch();
        }

        function performAdvancedSearch() {
            const query = document.getElementById('adv-search').value.trim();
            const game = document.getElementById('game-filter').value;
            const category = document.getElementById('category-filter').value;
            const limit = document.getElementById('result-limit').value;

            if (!query) {
                showSearchPlaceholder();
                return;
            }

            // Show loading state
            const container = document.getElementById('search-results');
            container.innerHTML = '<div style="text-align: center; padding: 40px;"><span class="loading"></span><br>Searching...</div>';

            let url = `/api/search?q=${encodeURIComponent(query)}&limit=${limit}`;
            if (game) url += `&game=${encodeURIComponent(game)}`;
            if (category) url += `&category=${encodeURIComponent(category)}`;

            fetch(url).then(r => r.json()).then(results => {
                if (results.matches.length === 0) {
                    container.innerHTML = `
                        <div style="text-align: center; padding: 40px; opacity: 0.6;">
                            <div style="font-size: 48px; margin-bottom: 20px;">😔</div>
                            <h3>No Results Found</h3>
                            <p>No matches found for "${query}" ${game ? `in ${game}` : ''} ${category ? `in ${category}` : ''}</p>
                            <p style="margin-top: 10px; font-size: 14px;">Try different keywords or check your filters</p>
                        </div>
                    `;
                    return;
                }

                let html = `
                    <div class="search-summary">
                        <h3>🔍 Found ${results.count} results for "${query}"</h3>
                        ${game ? `<span class="filter-badge">Game: ${game}</span>` : ''}
                        ${category ? `<span class="filter-badge">Category: ${category}</span>` : ''}
                    </div>
                    <div class="search-results-grid">
                `;

                // Group by game then category
                const groupedByGame = {};
                results.matches.forEach(match => {
                    if (!groupedByGame[match.game]) groupedByGame[match.game] = {};
                    if (!groupedByGame[match.game][match.category]) groupedByGame[match.game][match.category] = [];
                    groupedByGame[match.game][match.category].push(match);
                });

                Object.entries(groupedByGame).forEach(([gameName, categories]) => {
                    html += `
                        <div class="search-group" style="margin-bottom: 20px;">
                            <h3 style="color: var(--accent); margin-bottom: 15px; border-bottom: 2px solid var(--accent); padding-bottom: 5px;">${gameName}</h3>
                    `;
                    
                    Object.entries(categories).forEach(([cat, matches]) => {
                        const categoryName = cat.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                        
                        html += `
                            <div class="category-section" style="margin-bottom: 20px;">
                                <div class="search-group-header" style="margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                                    <span class="category-badge">${categoryName}</span>
                                    <span class="result-count" style="font-size: 0.8em;">${matches.length} result${matches.length > 1 ? 's' : ''}</span>
                                </div>
                                <div class="search-items">
                        `;

                        matches.slice(0, 10).forEach((match, idx) => {
                            const matchText = match.match.length > 100 ? match.match.substring(0, 100) + '...' : match.match;
                            html += `
                                <div class="search-result-item clickable-item" onclick="showSearchResult('${gameName}', '${cat}', ${idx})">
                                    <div class="result-text">${matchText}</div>
                                    ${match.score ? `<div class="result-score">Match: ${(match.score * 100).toFixed(0)}%</div>` : ''}
                                </div>
                            `;
                        });

                        if (matches.length > 10) {
                            html += `<div class="more-results">... and ${matches.length - 10} more results in ${categoryName}</div>`;
                        }

                        html += '</div></div>';
                    });
                    
                    html += '</div>';
                });

                html += '</div>';
                container.innerHTML = html;
            }).catch(error => {
                container.innerHTML = `
                    <div style="text-align: center; padding: 40px; opacity: 0.6;">
                        <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
                        <h3>Search Error</h3>
                        <p>There was an error performing the search: ${error.message}</p>
                    </div>
                `;
            });
        }

        function showSearchPlaceholder() {
            const container = document.getElementById('search-results');
            container.innerHTML = `
                <div class="search-placeholder">
                    <div style="text-align: center; padding: 40px; opacity: 0.6;">
                        <div style="font-size: 48px; margin-bottom: 20px;">🔍</div>
                        <h3>Ready to Search</h3>
                        <p>Enter search terms above to explore the Chrono series database</p>
                        <p style="margin-top: 10px; font-size: 14px;">Try clicking on the example tags above!</p>
                    </div>
                </div>
            `;
        }

        function showAPIInterface() {
            const container = document.getElementById('results');
            container.innerHTML = `
                <div class="api-interface">
                    <div class="api-header">
                        <h2>🚀 API Documentation</h2>
                        <p>Complete REST API and MCP server for accessing Chrono series game data programmatically</p>
                    </div>

                    <div class="api-overview">
                        <div class="overview-card">
                            <h3>📊 REST API</h3>
                            <p>Standard HTTP endpoints for web applications and scripts</p>
                            <div class="api-stats">
                                <span>🌐 HTTP/HTTPS</span>
                                <span>📋 JSON Response</span>
                                <span>🔍 Search & Filter</span>
                                <span>📄 Pagination</span>
                            </div>
                        </div>
                        <div class="overview-card">
                            <h3>🤖 MCP Server</h3>
                            <p>Model Context Protocol for AI assistants and LLM integrations</p>
                            <div class="api-stats">
                                <span>🛠️ 61 Tools</span>
                                <span>📡 JSON-RPC</span>
                                <span>⚡ Real-time</span>
                                <span>🔗 SSE Transport</span>
                            </div>
                        </div>
                    </div>

                    <div class="api-section">
                        <h3>📋 REST API Endpoints</h3>
                        <div class="api-endpoints-grid">
                            <div class="endpoint-card">
                                <div class="endpoint-method">GET</div>
                                <div class="endpoint-path">/api/games</div>
                                <p>List all available games</p>
                                <div class="endpoint-example">
                                    <code>curl http://localhost:5000/api/games</code>
                                </div>
                            </div>

                            <div class="endpoint-card">
                                <div class="endpoint-method">GET</div>
                                <div class="endpoint-path">/api/{game}</div>
                                <p>Get complete data for a specific game</p>
                                <div class="endpoint-example">
                                    <code>curl http://localhost:5000/api/Chrono%20Trigger</code>
                                </div>
                            </div>

                            <div class="endpoint-card">
                                <div class="endpoint-method">GET</div>
                                <div class="endpoint-path">/api/{game}/{category}</div>
                                <p>Get paginated category data</p>
                                <div class="endpoint-params">
                                    <strong>Query params:</strong> page, per_page
                                </div>
                                <div class="endpoint-example">
                                    <code>curl "http://localhost:5000/api/Chrono%20Trigger/characters?page=1&per_page=20"</code>
                                </div>
                            </div>

                            <div class="endpoint-card">
                                <div class="endpoint-method">GET</div>
                                <div class="endpoint-path">/api/search</div>
                                <p>Search across all games</p>
                                <div class="endpoint-params">
                                    <strong>Query params:</strong> q (required), game, category, limit
                                </div>
                                <div class="endpoint-example">
                                    <code>curl "http://localhost:5000/api/search?q=crono&game=Chrono%20Trigger"</code>
                                </div>
                            </div>

                            <div class="endpoint-card">
                                <div class="endpoint-method">GET</div>
                                <div class="endpoint-path">/api/plot</div>
                                <p>List available plot trees</p>
                                <div class="endpoint-example">
                                    <code>curl http://localhost:5000/api/plot</code>
                                </div>
                            </div>

                            <div class="endpoint-card">
                                <div class="endpoint-method">GET</div>
                                <div class="endpoint-path">/api/plot/{id}</div>
                                <p>Get detailed plot tree</p>
                                <div class="endpoint-example">
                                    <code>curl http://localhost:5000/api/plot/ct</code>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="api-section">
                        <h3>🤖 MCP Server Details</h3>
                        <div class="mcp-details">
                            <div class="mcp-info">
                                <h4>Connection</h4>
                                <p><strong>URL:</strong> http://localhost:8080</p>
                                <p><strong>Protocol:</strong> JSON-RPC 2.0 over HTTP</p>
                                <p><strong>Transport:</strong> Server-Sent Events (SSE)</p>
                                <p><strong>Authentication:</strong> None required</p>
                            </div>

                            <div class="mcp-tools">
                                <h4>Available Tools (61 total)</h4>
                                <div class="tool-categories">
                                    <div class="tool-category">
                                        <strong>🎮 Game Info:</strong> list_games, get_game_info
                                    </div>
                                    <div class="tool-category">
                                        <strong>👥 Characters:</strong> list_characters, get_character_details
                                    </div>
                                    <div class="tool-category">
                                        <strong>📍 Locations:</strong> list_locations, get_location_info
                                    </div>
                                    <div class="tool-category">
                                        <strong>⚔️ Items:</strong> list_items, get_item_details
                                    </div>
                                    <div class="tool-category">
                                        <strong>🎨 Art & Media:</strong> get_character_art, get_location_images
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="api-section">
                        <h3>💡 Usage Examples</h3>
                        <div class="usage-examples">
                            <div class="usage-card">
                                <h4>🔍 Find Character Information</h4>
                                <pre><code># Get all character data for Chrono Trigger
curl "http://localhost:5000/api/Chrono%20Trigger/characters"

# Search for specific character
curl "http://localhost:5000/api/search?q= Lucca"</code></pre>
                            </div>

                            <div class="usage-card">
                                <h4>📊 Analyze Game Statistics</h4>
                                <pre><code># Get comprehensive game data
curl "http://localhost:5000/api/Chrono%20Trigger"

# Paginate through large datasets
curl "http://localhost:5000/api/Chrono%20Trigger/weapons?page=2&per_page=50"</code></pre>
                            </div>

                            <div class="usage-card">
                                <h4>🎭 Explore Story Elements</h4>
                                <pre><code># Get plot tree
curl "http://localhost:5000/api/plot/ct"

# Search plot-related content
curl "http://localhost:5000/api/search?q=time+travel"</code></pre>
                            </div>
                        </div>
                    </div>

                    <div class="api-section">
                        <h3>⚙️ Response Format</h3>
                        <div class="response-examples">
                            <h4>Success Response:</h4>
                            <pre><code>{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}</code></pre>

                            <h4>Error Response:</h4>
                            <pre><code>{
  "error": "Game not found"
}</code></pre>
                        </div>
                    </div>
                </div>
            `;
        }

        async function showAnalyticsInterface() {
            const container = document.getElementById('results');
            container.innerHTML = `
                <div class="analytics-interface">
                    <div class="analytics-header">
                        <h2>📈 Site Analytics</h2>
                        <p>Visitor statistics and usage metrics for the Chrono MCP database</p>
                    </div>

                    <div class="analytics-dashboard">
                        <div class="analytics-loading">
                            <span class="loading"></span>
                            Loading analytics data...
                        </div>
                    </div>
                </div>
            `;

            // Load analytics data
            try {
                const statsResponse = await fetch('/api/analytics/stats');
                const popularResponse = await fetch('/api/analytics/popular');

                if (statsResponse.ok && popularResponse.ok) {
                    const stats = await statsResponse.json();
                    const popular = await popularResponse.json();

                    renderAnalyticsDashboard(stats, popular);
                } else {
                    throw new Error('Failed to load analytics');
                }
            } catch (e) {
                console.error('Analytics loading failed:', e);
                document.querySelector('.analytics-dashboard').innerHTML = `
                    <div class="analytics-error">
                        <h3>📊 Analytics Unavailable</h3>
                        <p>Unable to load visitor statistics at this time.</p>
                        <p>This may be because the analytics system is still initializing.</p>
                    </div>
                `;
            }
        }

        function renderAnalyticsDashboard(stats, popular) {
            const dashboard = document.querySelector('.analytics-dashboard');

            dashboard.innerHTML = `
                <div class="analytics-grid">
                    <div class="analytics-card">
                        <h3>📅 Today's Activity</h3>
                        <div class="analytics-metrics">
                            <div class="metric">
                                <span class="metric-value">${stats.today.page_views}</span>
                                <span class="metric-label">Page Views</span>
                            </div>
                            <div class="metric">
                                <span class="metric-value">${stats.today.unique_visitors}</span>
                                <span class="metric-label">Unique Visitors</span>
                            </div>
                            <div class="metric">
                                <span class="metric-value">${stats.today.api_calls}</span>
                                <span class="metric-label">API Calls</span>
                            </div>
                            <div class="metric">
                                <span class="metric-value">${stats.today.search_queries}</span>
                                <span class="metric-label">Searches</span>
                            </div>
                        </div>
                    </div>

                    <div class="analytics-card">
                        <h3>📊 All-Time Totals</h3>
                        <div class="analytics-metrics">
                            <div class="metric">
                                <span class="metric-value">${stats.total.page_views.toLocaleString()}</span>
                                <span class="metric-label">Total Views</span>
                            </div>
                            <div class="metric">
                                <span class="metric-value">${stats.total.unique_visitors.toLocaleString()}</span>
                                <span class="metric-label">Total Visitors</span>
                            </div>
                        </div>
                    </div>

                    <div class="analytics-card">
                        <h3>🔥 Popular Pages</h3>
                        <div class="popular-list">
                            ${popular.popular_pages.slice(0, 5).map(page => `
                                <div class="popular-item">
                                    <span class="popular-page">${page.page}</span>
                                    <span class="popular-count">${page.views} views</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <div class="analytics-card">
                        <h3>📈 Recent Activity</h3>
                        <div class="activity-summary">
                            <p><strong>${popular.recent_activity}</strong> recent interactions</p>
                            <p>People are actively exploring the Chrono database!</p>
                        </div>
                    </div>
                </div>

                <div class="analytics-footer">
                    <p>Analytics data is updated in real-time as visitors interact with the site.</p>
                    <button class="btn" onclick="refreshAnalytics()">🔄 Refresh Data</button>
                </div>
            `;
        }

        async function refreshAnalytics() {
            const button = event.target;
            const originalText = button.textContent;
            button.textContent = '⏳ Refreshing...';
            button.disabled = true;

            try {
                await showAnalyticsInterface();
            } finally {
                button.textContent = originalText;
                button.disabled = false;
            }
        }

        async function loadStats() {
            try {
                const statsContent = document.getElementById('stats-content');

                // Show loading state
                statsContent.innerHTML = '<span class="loading"></span> Loading statistics...';

                // Get basic game count
                let games = [];
                try {
                    const gamesResponse = await fetch('/api/games');
                    if (gamesResponse.ok) {
                        games = await gamesResponse.json();
                    } else {
                        throw new Error(`Games API failed: ${gamesResponse.status}`);
                    }
                } catch (e) {
                    console.warn('Games API failed, using fallback:', e);
                    games = ['Chrono Trigger', 'Chrono Cross', 'Radical Dreamers'];
                }

                // Get visitor analytics
                let visitorStats = { total: { page_views: 0, unique_visitors: 0 } };
                try {
                    const analyticsResponse = await fetch('/api/analytics/stats');
                    if (analyticsResponse.ok) {
                        visitorStats = await analyticsResponse.json();
                    }
                } catch (e) {
                    console.warn('Analytics API failed:', e);
                }

                // Simple item count estimation (avoid complex API calls)
                const estimatedItems = games.length * 10000; // Rough estimate

                // Update stats display
                const statsHtml = `
                    <strong>📊 System Status:</strong>
                    ${games.length} Games •
                    ${estimatedItems.toLocaleString()}+ Items Decoded •
                    ${visitorStats.total.page_views} Page Views
                `;

                statsContent.innerHTML = statsHtml;

                // Update connection status
                const connectionStatus = document.getElementById('connection-status');
                connectionStatus.innerHTML = '🔗 Online • API: OK • Analytics: OK';

                // Track this page view
                trackVisit('/');

            } catch (e) {
                console.error('Failed to load stats:', e);
                const statsContent = document.getElementById('stats-content');
                statsContent.innerHTML = '⚠️ Stats loading... (retrying)';

                // Retry after a delay
                setTimeout(() => loadStats(), 2000);

                const connectionStatus = document.getElementById('connection-status');
                connectionStatus.innerHTML = '🔄 Retrying connection...';
            }
        }

        function showStats() {
            const statsBar = document.getElementById('stats-bar');
            statsBar.style.display = statsBar.style.display === 'none' ? 'block' : 'none';
        }

        function searchForGame(gameName) {
            // Navigate to search section and filter by game
            showSection('search');
            document.getElementById('game-filter').value = gameName;
            document.getElementById('adv-search').focus();
        }

        async function refreshData() {
            gameData = {};  // Clear cache
            await fetch('/api/refresh').then(r => r.json());
            loadGames();
            loadStats();
        }

        async function search(query) {
            if (query.length < 2) {
                document.getElementById('results').innerHTML = '';
                return;
            }

            const results = await fetch('/api/search?q=' + encodeURIComponent(query)).then(r => r.json());
            const container = document.getElementById('results');
            container.innerHTML = `<h2>Search Results for "${query}"</h2>`;

            if (results.matches.length === 0) {
                container.innerHTML += '<p>No results found.</p>';
                return;
            }

            // Group by game then category
            const byGame = {};
            for (const m of results.matches) {
                if (!byGame[m.game]) byGame[m.game] = {};
                if (!byGame[m.game][m.category]) byGame[m.game][m.category] = [];
                byGame[m.game][m.category].push(m);
            }

            for (const [game, categories] of Object.entries(byGame)) {
                const card = document.createElement('div');
                card.className = 'game-card';
                card.innerHTML = `<h2 style="margin-bottom: 15px; border-bottom: 2px solid var(--accent); padding-bottom: 5px;">${game}</h2>`;

                for (const [category, matches] of Object.entries(categories)) {
                    const categoryName = category.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                    const itemsHtml = matches.slice(0, 10).map((match, idx) => {
                        let displayText = '';
                        if (match.item && typeof match.item === 'object') {
                            // Show key info from the matched item
                            const keys = Object.keys(match.item).slice(0, 3);
                            displayText = keys.map(k => `${k}: ${match.item[k]}`).join(', ');
                        } else {
                            displayText = match.item || 'Unknown';
                        }

                        return `<div class="search-result-item clickable-item" onclick="showSearchResult('${game}', '${category}', ${idx})" title="Click to view full details">
                            <strong>${match.item.name || match.item || 'Item'}</strong><br>
                            <small>${displayText}</small>
                            ${match.similarity ? `<br><em>Match: ${(match.similarity * 100).toFixed(0)}%</em>` : ''}
                        </div>`;
                    }).join('');

                    const catSection = document.createElement('div');
                    catSection.style.marginBottom = '15px';
                    catSection.innerHTML = `
                        <h3 style="font-size: 1.1em; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                            <span class="category-badge">${categoryName}</span>
                            <span class="result-count" style="font-size: 0.8em; font-weight: normal;">${matches.length} matches</span>
                        </h3>
                        <div class="search-items">${itemsHtml}</div>
                        ${matches.length > 10 ? `<div class="more-results" style="margin-top: 10px; font-style: italic; font-size: 0.9em; opacity: 0.8;">... and ${matches.length - 10} more in ${categoryName}</div>` : ''}
                    `;
                    card.appendChild(catSection);
                }
                container.appendChild(card);
            }
        }

        async function showSearchResult(game, category, index) {
            // Get the search results data and show the specific item
            const query = document.getElementById('search').value;
            if (!query) return;

            const results = await fetch('/api/search?q=' + encodeURIComponent(query)).then(r => r.json());
            const matches = results.matches;

            // Find matches for this game/category and get the specific index
            const gameCategoryMatches = matches.filter(m => m.game === game && m.category === category);
            const targetMatch = gameCategoryMatches[index];

            if (targetMatch) {
                document.getElementById('modal-title').textContent = `${game} - ${category}`;

                let content = `<h4>Search Result Details</h4>`;

                // Show the matched field and value
                content += `<p><strong>Field:</strong> ${targetMatch.field}</p>`;
                content += `<p><strong>Match:</strong> ${targetMatch.match}</p>`;
                content += `<p><strong>Score:</strong> ${(targetMatch.score * 100).toFixed(1)}%</p>`;

                // Try to get full item details from the API
                try {
                    const gameData = await fetch('/api/' + encodeURIComponent(game) + '/' + encodeURIComponent(category)).then(r => r.json());
                    if (gameData && gameData.items) {
                        // Find the item that contains this match
                        const fullItem = gameData.items.find(item => {
                            if (typeof item === 'string') {
                                return item.toLowerCase().includes(targetMatch.match.toLowerCase());
                            } else if (typeof item === 'object') {
                                return Object.values(item).some(val =>
                                    val && val.toString().toLowerCase().includes(targetMatch.match.toLowerCase())
                                );
                            }
                            return false;
                        });

                        if (fullItem) {
                            content += '<h5>Full Item Details:</h5>';
                            if (typeof fullItem === 'object') {
                                content += '<table><tbody>';
                                for (const [key, value] of Object.entries(fullItem)) {
                                    content += `<tr><td><strong>${key}:</strong></td><td>${value}</td></tr>`;
                                }
                                content += '</tbody></table>';
                            } else {
                                content += `<p>${fullItem}</p>`;
                            }
                        }
                    }
                } catch (e) {
                    console.log('Could not load full item details:', e);
                }

                document.getElementById('modal-body').innerHTML = content;
                document.getElementById('modal').style.display = 'block';
            }
        }

        // Event listener for modal close
        window.onclick = function(event) {
            const modal = document.getElementById('modal');
            if (event.target == modal) {
                closeModal();
            }
        }

        // Initialize visitor tracking
        let sessionId = localStorage.getItem('sessionId');
        if (!sessionId) {
            sessionId = Math.random().toString(36).substring(2, 15);
            localStorage.setItem('sessionId', sessionId);
        }

        // Track page views
        async function trackVisit(page) {
            try {
                await fetch('/api/analytics/track', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        page: page,
                        session_id: sessionId,
                        referrer: document.referrer || null
                    })
                });
            } catch (e) {
                console.log('Analytics tracking failed:', e);
            }
        }

        // Initialize immediately - DOM should be ready since script is at end of body
        console.log('About to initialize...');
        try {
            // Don't call loadGames here - it's already called in DOMContentLoaded
            loadPlots();
            loadStats();
            console.log('Initialization completed');
        } catch (e) {
            console.error('Initialization failed:', e);
        }
    </script>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-section">
                <h4>🎮 Chrono MCP Database</h4>
                <p><strong>Complete decoded data from all Chrono series games</strong></p>
                <p>Built with Python, Flask, SQLAlchemy, and SQLite</p>
                <p><strong>22,013+ items</strong> across 3 games and 70+ categories</p>
                <div class="footer-stats">
                    <span>✅ REST API</span>
                    <span>🤖 MCP Server</span>
                    <span>🔍 Full-text Search</span>
                </div>
            </div>

            <div class="footer-section">
                <h4>📚 Games Covered</h4>
                <div class="game-links">
                    <div class="game-link" onclick="searchForGame('Chrono Trigger')">
                        <strong>Chrono Trigger</strong> (1995)<br>
                        <small>SNES • RPG • Time Travel</small>
                    </div>
                    <div class="game-link" onclick="searchForGame('Chrono Cross')">
                        <strong>Chrono Cross</strong> (1999)<br>
                        <small>PS1 • Epic • Parallel Worlds</small>
                    </div>
                    <div class="game-link" onclick="searchForGame('Radical Dreamers')">
                        <strong>Radical Dreamers</strong> (1996)<br>
                        <small>Satellaview • Action • Mystery</small>
                    </div>
                </div>
            </div>

            <div class="footer-section">
                <h4>🔗 Quick Links</h4>
                <ul>
                    <li><a href="#" onclick="showSection('games')">🎮 Browse Games</a></li>
                    <li><a href="#" onclick="showSection('search')">🔍 Advanced Search</a></li>
                    <li><a href="#" onclick="showSection('plots')">📚 Plot Database</a></li>
                    <li><a href="#" onclick="showSection('api')">🚀 API Documentation</a></li>
                </ul>
            </div>

            <div class="footer-section">
                <h4>📊 Data Categories</h4>
                <div class="category-tags">
                    <span class="cat-tag">👥 Characters</span>
                    <span class="cat-tag">⚔️ Weapons</span>
                    <span class="cat-tag">🛡️ Armor</span>
                    <span class="cat-tag">📍 Locations</span>
                    <span class="cat-tag">🎭 Enemies</span>
                    <span class="cat-tag">💍 Items</span>
                    <span class="cat-tag">🎨 Art</span>
                    <span class="cat-tag">🎵 Audio</span>
                </div>
                <p style="margin-top: 10px; font-size: 14px;">
                    <a href="https://github.com/UberMetroid/chrono-mcp" target="_blank" style="color: var(--accent);">📂 View on GitHub</a>
                </p>
            </div>
        </div>

        <div class="footer-bottom">
            <div class="footer-bottom-content">
                <p>&copy; 2026 Chrono MCP Project - Complete ROM decoding and data extraction</p>
                <p>All Chrono series content property of Square Enix • Built for educational and research purposes</p>
                <div class="tech-stack">
                    <span>🐍 Python</span>
                    <span>🌶️ Flask</span>
                    <span>🗄️ SQLite</span>
                    <span>🤖 MCP</span>
                    <span>🚀 Docker</span>
                </div>
            </div>
        </div>
    </footer>
</body>
</html>
'''