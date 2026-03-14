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
                    font-size: 14px; color: var(--text); }
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

        .search-interface, .api-interface { max-width: 1200px; margin: 0 auto; }
        .search-controls { background: var(--bg-secondary); padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .search-results-grid { display: grid; gap: 20px; }
        .search-group { background: var(--bg-secondary); padding: 15px; border-radius: 8px; }
        .search-items { margin-top: 10px; }

        .api-section { background: var(--bg-secondary); padding: 20px; margin-bottom: 20px; border-radius: 8px; }
        .endpoint { background: var(--bg-tertiary); padding: 10px; margin: 10px 0; border-radius: 4px; }
        .endpoint code { font-family: 'Courier New', monospace; background: var(--border); padding: 2px 4px; border-radius: 3px; }
        .code-examples { margin-top: 15px; }
        .code-block { background: var(--bg-tertiary); padding: 15px; margin: 10px 0; border-radius: 4px; }
        .code-block code { font-family: 'Courier New', monospace; background: var(--border); padding: 2px 4px; border-radius: 3px; display: block; margin-top: 5px; }

        .plot-card { background: var(--bg-secondary); padding: 20px; border-radius: 12px;
                     box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .plot-header { margin-bottom: 15px; }
        .plot-header h3 { color: var(--accent); margin-bottom: 8px; }
        .plot-stats { display: flex; gap: 15px; flex-wrap: wrap; font-size: 14px; opacity: 0.8; }
        .plot-stats span { background: var(--border); padding: 4px 8px; border-radius: 4px; }
        .plot-description { color: var(--text); line-height: 1.5; margin-bottom: 15px; }
        .plot-actions { display: flex; gap: 10px; flex-wrap: wrap; }
        .plot-actions .btn.primary { background: var(--accent); }
        .plot-actions .btn.secondary { background: var(--border); }

        .footer { background: var(--bg-tertiary); border-top: 1px solid var(--border); margin-top: 40px; }
        .footer-content { display: flex; justify-content: space-between; padding: 30px 20px; flex-wrap: wrap; gap: 20px; }
        .footer-section { flex: 1; min-width: 200px; }
        .footer-section h4 { color: var(--accent); margin-bottom: 10px; }
        .footer-section ul { list-style: none; }
        .footer-section li { margin: 5px 0; }
        .footer-section a { color: var(--text); text-decoration: none; }
        .footer-section a:hover { color: var(--accent); }
        .footer-bottom { text-align: center; padding: 15px 20px; border-top: 1px solid var(--border); color: var(--text); opacity: 0.7; font-size: 14px; }
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
    </nav>

    <div class="stats-bar" id="stats-bar" style="display:none">
        <span id="stats-content">Loading stats...</span>
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
                    card.className = 'plot-card';
                    const plotId = plot.file.split('/').pop().replace('_plot_tree', '');

                    // Get basic plot info
                    fetch(`/api/plot/${plotId}`).then(r => r.json()).then(plotData => {
                        const description = plotData.description || 'No description available';
                        const shortDesc = description.length > 150 ? description.substring(0, 150) + '...' : description;

                        const eras = plotData.eras ? plotData.eras.length : 0;
                        const worlds = plotData.worlds ? plotData.worlds.length : 0;
                        const episodes = plotData.episodes ? plotData.episodes.length : 0;
                        const characters = plotData.character_arcs ? plotData.character_arcs.length : 0;

                        card.innerHTML = `
                            <div class="plot-header">
                                <h3>${plot.game}</h3>
                                <div class="plot-stats">
                                    ${eras > 0 ? `<span>📅 ${eras} Era${eras > 1 ? 's' : ''}</span>` : ''}
                                    ${worlds > 0 ? `<span>🌍 ${worlds} World${worlds > 1 ? 's' : ''}</span>` : ''}
                                    ${episodes > 0 ? `<span>🎭 ${episodes} Episode${episodes > 1 ? 's' : ''}</span>` : ''}
                                    ${characters > 0 ? `<span>👥 ${characters} Character${characters > 1 ? 's' : ''}</span>` : ''}
                                </div>
                            </div>
                            <p class="plot-description">${shortDesc}</p>
                            <div class="plot-actions">
                                <button class="btn primary" onclick="showPlot('${plotId}')">📖 View Full Story</button>
                                <button class="btn secondary" onclick="showPlotOutline('${plotId}')">📋 Quick Outline</button>
                            </div>
                        `;
                    }).catch(e => {
                        card.innerHTML = `<h3>${plot.game}</h3><p>Error loading plot data</p><button class="btn" onclick="showPlot('${plotId}')">View Story</button>`;
                    });

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
        }

        async function showPlotOutline(plotId) {
            const data = await fetch(`/api/plot/${plotId}`).then(r => r.json());
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
        }

        // Load saved theme
        if (localStorage.getItem('theme') === 'light') {
            document.body.classList.add('light-theme');
        }

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
                    break;
                case 'api':
                    document.querySelector('.nav-btn:nth-child(4)').classList.add('active');
                    showAPIInterface();
                    break;
            }
        }

        function showSearchInterface() {
            const container = document.getElementById('results');
            container.innerHTML = `
                <div class="search-interface">
                    <h2>Advanced Search</h2>
                    <div class="search-controls">
                        <input type="text" id="adv-search" placeholder="Search all games..." style="width: 100%; padding: 12px; margin-bottom: 10px;">
                        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                            <select id="game-filter">
                                <option value="">All Games</option>
                                <option value="Chrono Trigger">Chrono Trigger</option>
                                <option value="Chrono Cross">Chrono Cross</option>
                                <option value="Radical Dreamers">Radical Dreamers</option>
                            </select>
                            <select id="category-filter">
                                <option value="">All Categories</option>
                            </select>
                        </div>
                        <button class="btn" onclick="performAdvancedSearch()">🔍 Search</button>
                    </div>
                    <div id="search-results"></div>
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
                    option.textContent = cat.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                    select.appendChild(option);
                });
            });
        }

        function performAdvancedSearch() {
            const query = document.getElementById('adv-search').value;
            const game = document.getElementById('game-filter').value;
            const category = document.getElementById('category-filter').value;

            if (!query) return;

            let url = `/api/search?q=${encodeURIComponent(query)}`;
            if (game) url += `&game=${encodeURIComponent(game)}`;
            if (category) url += `&category=${encodeURIComponent(category)}`;

            fetch(url).then(r => r.json()).then(results => {
                const container = document.getElementById('search-results');
                if (results.matches.length === 0) {
                    container.innerHTML = '<p>No results found.</p>';
                    return;
                }

                let html = `<h3>Found ${results.count} results</h3>`;
                html += '<div class="search-results-grid">';

                // Group by game and category
                const grouped = {};
                results.matches.forEach(match => {
                    const key = `${match.game}|${match.category}`;
                    if (!grouped[key]) grouped[key] = [];
                    grouped[key].push(match);
                });

                Object.entries(grouped).forEach(([key, matches]) => {
                    const [game, cat] = key.split('|');
                    html += `
                        <div class="search-group">
                            <h4>${game} - ${cat.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} (${matches.length})</h4>
                            <div class="search-items">
                    `;

                    matches.slice(0, 5).forEach((match, idx) => {
                        html += `<div class="search-result-item clickable-item" onclick="showSearchResult('${game}', '${cat}', ${idx})">${match.match}</div>`;
                    });

                    if (matches.length > 5) {
                        html += `<p>... and ${matches.length - 5} more</p>`;
                    }

                    html += '</div></div>';
                });

                html += '</div>';
                container.innerHTML = html;
            });
        }

        function showAPIInterface() {
            const container = document.getElementById('results');
            container.innerHTML = `
                <div class="api-interface">
                    <h2>API Documentation</h2>
                    <div class="api-section">
                        <h3>REST API Endpoints</h3>
                        <div class="api-endpoints">
                            <div class="endpoint">
                                <code>GET /api/games</code>
                                <p>List all available games</p>
                            </div>
                            <div class="endpoint">
                                <code>GET /api/{game}</code>
                                <p>Get all data for a specific game</p>
                            </div>
                            <div class="endpoint">
                                <code>GET /api/{game}/{category}</code>
                                <p>Get category data with pagination</p>
                            </div>
                            <div class="endpoint">
                                <code>GET /api/search?q={query}</code>
                                <p>Search across all games</p>
                            </div>
                            <div class="endpoint">
                                <code>GET /api/plot</code>
                                <p>List available plot trees</p>
                            </div>
                        </div>
                    </div>

                    <div class="api-section">
                        <h3>MCP Server</h3>
                        <p>The MCP (Model Context Protocol) server provides 61 tools for AI assistants to query Chrono game data programmatically.</p>
                        <div class="endpoint">
                            <code>HTTP: localhost:8080</code>
                            <p>JSON-RPC over HTTP with Server-Sent Events</p>
                        </div>
                    </div>

                    <div class="api-section">
                        <h3>Example API Calls</h3>
                        <div class="code-examples">
                            <div class="code-block">
                                <strong>Get all games:</strong><br>
                                <code>curl http://localhost:5000/api/games</code>
                            </div>
                            <div class="code-block">
                                <strong>Search for characters:</strong><br>
                                <code>curl "http://localhost:5000/api/search?q=crono"</code>
                            </div>
                            <div class="code-block">
                                <strong>Get character data:</strong><br>
                                <code>curl http://localhost:5000/api/Chrono%20Trigger/characters</code>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        async function loadStats() {
            try {
                const games = await fetch('/api/games').then(r => r.json());
                let totalItems = 0;
                let totalCategories = 0;

                for (const game of games) {
                    const gameData = await fetch('/api/' + encodeURIComponent(game)).then(r => r.json());
                    const categories = Object.keys(gameData).filter(k => Array.isArray(gameData[k]));
                    totalCategories += categories.length;

                    for (const cat of categories) {
                        totalItems += gameData[cat].length;
                    }
                }

                const stats = document.getElementById('stats-content');
                stats.innerHTML = `📊 ${games.length} Games • ${totalCategories} Categories • ${totalItems.toLocaleString()} Items Decoded`;
            } catch (e) {
                console.error('Failed to load stats:', e);
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

                card.innerHTML = `
                    <h3>${game} - ${category}</h3>
                    <p>${matches.length} matches</p>
                    <div>${itemsHtml}</div>
                    ${matches.length > 10 ? `<p>... and ${matches.length - 10} more</p>` : ''}
                `;
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

        // Initialize navigation
        initNavigation();

        loadGames();
        loadPlots();
        loadStats();
    </script>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-section">
                <h4>Chrono MCP Database</h4>
                <p>Complete decoded data from all Chrono series games</p>
                <p>Built with Python, Flask, and SQLite</p>
            </div>
            <div class="footer-section">
                <h4>Games Covered</h4>
                <ul>
                    <li><a href="#" onclick="showSection('games'); searchForGame('Chrono Trigger')">Chrono Trigger (1995)</a></li>
                    <li><a href="#" onclick="showSection('games'); searchForGame('Chrono Cross')">Chrono Cross (1999)</a></li>
                    <li><a href="#" onclick="showSection('games'); searchForGame('Radical Dreamers')">Radical Dreamers (1996)</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>Links</h4>
                <ul>
                    <li><a href="#" onclick="showSection('api')">API Documentation</a></li>
                    <li><a href="#" onclick="showSection('plots')">Plot Trees</a></li>
                    <li><a href="https://github.com/UberMetroid/chrono-mcp" target="_blank">GitHub</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2026 Chrono MCP Project - All Chrono series content property of Square Enix</p>
        </div>
    </footer>
</body>
</html>
'''