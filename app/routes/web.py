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
        .header { background: var(--bg-secondary); padding: 20px; border-bottom: 2px solid var(--accent); }
        .header h1 { color: var(--accent); font-size: 2.5em; margin-bottom: 10px; }
        .header-buttons { display: flex; gap: 10px; margin-top: 15px; }
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

        loadGames();
        loadPlots();
    </script>
</body>
</html>
'''