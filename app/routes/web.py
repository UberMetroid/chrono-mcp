from flask import Blueprint, render_template_string

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Main web interface"""
    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chrono Server Status</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: #1a1a1a; color: #e0e0e0; line-height: 1.6; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #4a9eff; }
        .header h1 { color: #4a9eff; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; }
        .nav-btn { background: #333; color: #e0e0e0; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
        .nav-btn.active { background: #4a9eff; color: white; }
        .section { display: none; background: #2a2a2a; padding: 20px; border-radius: 8px; }
        .section.active { display: block; }
        pre { background: #111; padding: 15px; border-radius: 6px; overflow-x: auto; color: #51cf66; }
        .tool-card { background: #333; padding: 15px; border-radius: 6px; margin-bottom: 10px; }
        .tool-card h3 { color: #4a9eff; margin-bottom: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #444; }
        th { color: #4a9eff; }
        .btn-run { background: #4a9eff; color: white; border: none; padding: 5px 15px; border-radius: 4px; cursor: pointer; float: right; }
        .btn-run:hover { opacity: 0.9; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 100; }
        .modal-content { background: #2a2a2a; margin: 50px auto; padding: 30px; max-width: 800px; border-radius: 12px; }
        .modal-close { float: right; font-size: 24px; cursor: pointer; color: #aaa; border: none; background: none; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #4a9eff; }
        .form-group input { width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #444; background: #1a1a1a; color: white; }
    </style>
</head>
<body>
    <div id="tool-modal" class="modal">
        <div class="modal-content">
            <button class="modal-close" onclick="document.getElementById('tool-modal').style.display='none'">&times;</button>
            <h2 id="tool-modal-title" style="margin-bottom: 10px;">Run Tool</h2>
            <p id="tool-modal-desc" style="opacity: 0.8; margin-bottom: 20px;"></p>
            <div id="tool-modal-form"></div>
            <button class="nav-btn active" style="margin-top: 15px; width: 100%;" onclick="submitTool()">Execute</button>
            <div id="tool-modal-result" style="margin-top: 20px; display: none;">
                <h3 style="color: #4a9eff; margin-bottom: 10px;">Result</h3>
                <pre id="tool-modal-output" style="max-height: 400px; overflow-y: auto;"></pre>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="header">
            <h1>Chrono Mod Engine (v2)</h1>
            <p>Multi-Platform Reverse Engineering Console</p>
        </div>

        <div class="nav">
            <button class="nav-btn active" onclick="showSection('status')">System Status</button>
            <button class="nav-btn" onclick="showSection('data')">Data Details</button>
            <button class="nav-btn" onclick="showSection('api')">API & Tools</button>
        </div>

        <div id="status" class="section active">
            <h2>System Health</h2>
            <div id="health-content">Loading...</div>
        </div>

        <div id="data" class="section">
            <h2>Extracted Game Data Details</h2>
            <div id="data-content">Loading data stats...</div>
        </div>

        <div id="api" class="section">
            <h2>MCP Tools</h2>
            <div id="tools-content">Loading tools...</div>
            
            <h2 style="margin-top: 30px;">Live Emulator Hook</h2>
            <p style="margin-bottom: 15px; opacity: 0.8;">Connect your emulator (BizHawk) directly to this MCP server to read live game RAM.</p>
            <div class="tool-card" style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3>BizHawk Lua Hook Script</h3>
                    <p style="font-size: 14px;">Load this into BizHawk's Lua console. Connects to TCP 8081.</p>
                </div>
                <a href="/api/lua/download" class="nav-btn" style="text-decoration: none; font-weight: bold; background: #4a9eff; color: white;">⬇️ Download Script</a>
            </div>
            
            <h2 style="margin-top: 30px;">REST API Endpoints</h2>
            <table>
                <tr><th>Endpoint</th><th>Description</th></tr>
                <tr><td>/api/health</td><td>System health and cache stats</td></tr>
                <tr><td>/api/games</td><td>List all games</td></tr>
                <tr><td>/api/&lt;game&gt;</td><td>Get game data</td></tr>
                <tr><td>/api/db_stats</td><td>Get extracted game data statistics</td></tr>
                <tr><td>/api/mcp/tools</td><td>List available MCP tools</td></tr>
                <tr><td>/api/lua/download</td><td>Download Emulator Lua script</td></tr>
            </table>
        </div>
    </div>

    <script>
        function showSection(id) {
            document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(id).classList.add('active');
            
            if (id === 'status') document.querySelectorAll('.nav-btn')[0].classList.add('active');
            if (id === 'data') document.querySelectorAll('.nav-btn')[1].classList.add('active');
            if (id === 'api') document.querySelectorAll('.nav-btn')[2].classList.add('active');
            
            if(id === 'status') loadStatus();
            if(id === 'data') loadDataStats();
            if(id === 'api') loadTools();
        }

        // Use SSE for real-time health updates instead of polling
        let healthEventSource = null;

        function startHealthStream() {
            if (healthEventSource) {
                healthEventSource.close();
            }
            
            healthEventSource = new EventSource('/api/health/stream');
            
            healthEventSource.onmessage = function(event) {
                if (!document.getElementById('status').classList.contains('active')) {
                    return; // Don't update DOM if tab is not active
                }
                
                try {
                    const data = JSON.parse(event.data);
                    
                    if (data.error) {
                         document.getElementById('health-content').innerHTML = '<p style="color: #ff6b6b">Error in stream: ' + data.error + '</p>';
                         return;
                    }
                    
                    const mcpColor = data.mcp_status === 'online' ? '#51cf66' : '#ff6b6b';
                    const mcpIcon = data.mcp_status === 'online' ? '🟢' : '🔴';
                    
                    const hookColor = data.emulator_hook && data.emulator_hook.connected ? '#51cf66' : '#ff6b6b';
                    const hookText = data.emulator_hook && data.emulator_hook.connected ? `Connected: ${data.emulator_hook.emulator}` : 'Waiting for Emulator...';
                    const gameText = data.emulator_hook && data.emulator_hook.connected ? data.emulator_hook.game : 'N/A';
                    
                    const html = `
                        <div style="display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;">
                            <div class="tool-card" style="flex: 1; min-width: 250px;">
                                <h3>Web Server Status</h3>
                                <p style="font-size: 20px; color: #51cf66;">🟢 ${data.status.toUpperCase()}</p>
                                <p style="font-size: 14px; opacity: 0.8; margin-top: 10px;">Version: ${data.version}</p>
                                <p style="font-size: 14px; opacity: 0.8;">Time: ${data.timestamp}</p>
                            </div>
                            
                            <div class="tool-card" style="flex: 1; min-width: 250px;">
                                <h3>MCP Server Status</h3>
                                <p style="font-size: 20px; color: ${mcpColor};">${mcpIcon} ${data.mcp_status.toUpperCase()}</p>
                                <p style="font-size: 14px; opacity: 0.8; margin-top: 10px;">Port: 8080</p>
                                <p style="font-size: 14px; opacity: 0.8;">Protocol: streamable-http</p>
                            </div>
                            
                            <div class="tool-card" style="flex: 1; min-width: 250px;">
                                <h3>Emulator Hook</h3>
                                <p style="font-size: 20px; color: ${hookColor};">${data.emulator_hook && data.emulator_hook.connected ? '🟢' : '🔴'} ${hookText}</p>
                                <p style="font-size: 14px; opacity: 0.8; margin-top: 10px;">Game: ${gameText}</p>
                                <p style="font-size: 14px; opacity: 0.8;">Port: 8081</p>
                            </div>
                            
                            <div class="tool-card" style="flex: 1; min-width: 250px;">
                                <h3>Cache Health</h3>
                                <p style="font-size: 14px; margin-bottom: 5px;">Size: <strong>${data.cache.cache_size || 0} items</strong></p>
                                <p style="font-size: 14px; margin-bottom: 5px;">Hits: <strong>${data.cache.hits || 0}</strong></p>
                                <p style="font-size: 14px; margin-bottom: 5px;">Misses: <strong>${data.cache.misses || 0}</strong></p>
                                <p style="font-size: 14px; margin-bottom: 5px;">Hit Rate: <strong>${data.cache.hit_rate || 0}%</strong></p>
                            </div>
                        </div>
                        
                        <h3 style="margin-top: 20px; margin-bottom: 10px;">Raw Diagnostic Data</h3>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                    
                    document.getElementById('health-content').innerHTML = html;
                } catch (e) {
                    console.error('Error parsing SSE data:', e);
                }
            };
            
            healthEventSource.onerror = function() {
                console.error('SSE connection lost. Retrying...');
            };
        }

        async function loadStatus() {
            // Start the SSE stream if it hasn't been started
            if (!healthEventSource) {
                startHealthStream();
            }
        }

        async function loadDataStats() {
            try {
                const res = await fetch('/api/db_stats');
                const data = await res.json();
                
                if (data.error) {
                    document.getElementById('data-content').innerHTML = '<p style="color: #ff6b6b">' + data.error + '</p>';
                    return;
                }

                let html = `
                    <div style="display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;">
                        <div class="tool-card" style="flex: 1; min-width: 200px;">
                            <h3>Total Games</h3>
                            <p style="font-size: 24px;">${data.total_games}</p>
                        </div>
                        <div class="tool-card" style="flex: 1; min-width: 200px;">
                            <h3>Total Categories</h3>
                            <p style="font-size: 24px;">${data.total_categories}</p>
                        </div>
                        <div class="tool-card" style="flex: 1; min-width: 200px;">
                            <h3>Total Items Extracted</h3>
                            <p style="font-size: 24px; color: #51cf66;">${data.total_items}</p>
                        </div>
                    </div>
                `;

                if (data.games_data && data.games_data.length > 0) {
                    html += '<h3 style="margin-bottom: 15px;">Breakdown by Game</h3>';
                    data.games_data.forEach(game => {
                        html += `
                            <div class="tool-card">
                                <h3>${game.name}</h3>
                                <p><strong>Items Grabbed:</strong> ${game.total_items} across ${game.total_categories} categories</p>
                                <div style="margin-top: 10px; font-size: 0.9em; opacity: 0.8; display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 5px;">
                        `;
                        
                        Object.entries(game.categories).forEach(([cat, count]) => {
                            html += `<div>• ${cat}: ${count}</div>`;
                        });
                        
                        html += `
                                </div>
                            </div>
                        `;
                    });
                }
                
                document.getElementById('data-content').innerHTML = html;
            } catch (e) {
                document.getElementById('data-content').innerHTML = '<p style="color: #ff6b6b">Error loading data stats: ' + e.message + '</p>';
            }
        }

        let currentTools = [];

        async function loadTools() {
            try {
                const res = await fetch('/api/mcp/tools');
                const data = await res.json();
                
                if (data.error) {
                    document.getElementById('tools-content').innerHTML = '<p style="color: #ff6b6b">' + data.error + '</p>';
                    return;
                }

                let html = '';
                const toolsList = data.tools || data; 
                currentTools = toolsList;
                
                if (Array.isArray(toolsList)) {
                    toolsList.forEach(tool => {
                        html += `
                            <div class="tool-card">
                                <button class="btn-run" onclick="openToolModal('${tool.name}')">▶ Run</button>
                                <h3>${tool.name}</h3>
                                <p>${tool.description}</p>
                            </div>
                        `;
                    });
                } else {
                     html = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }
                
                document.getElementById('tools-content').innerHTML = html;
            } catch (e) {
                document.getElementById('tools-content').innerHTML = '<p style="color: #ff6b6b">Error loading tools: ' + e.message + '</p>';
            }
        }

        let activeTool = null;

        function openToolModal(toolName) {
            const tool = currentTools.find(t => t.name === toolName);
            if (!tool) return;
            
            activeTool = tool;
            document.getElementById('tool-modal-title').innerText = "Execute: " + tool.name;
            document.getElementById('tool-modal-desc').innerText = tool.description;
            document.getElementById('tool-modal-result').style.display = 'none';
            
            let formHtml = '';
            
            // Build simple form based on schema
            if (tool.schema && tool.schema.properties) {
                Object.keys(tool.schema.properties).forEach(propName => {
                    const prop = tool.schema.properties[propName];
                    const isRequired = tool.schema.required && tool.schema.required.includes(propName);
                    const label = prop.title || propName;
                    
                    formHtml += `
                        <div class="form-group">
                            <label>${label} ${isRequired ? '*' : '(Optional)'}</label>
                            <input type="${prop.type === 'integer' ? 'number' : 'text'}" 
                                   id="input-${propName}" 
                                   placeholder="${prop.description || ''}"
                                   ${isRequired ? 'required' : ''}>
                        </div>
                    `;
                });
            } else {
                formHtml = '<p style="opacity: 0.7;">This tool requires no parameters.</p>';
            }
            
            document.getElementById('tool-modal-form').innerHTML = formHtml;
            document.getElementById('tool-modal').style.display = 'block';
        }

        async function submitTool() {
            if (!activeTool) return;
            
            const args = {};
            if (activeTool.schema && activeTool.schema.properties) {
                Object.keys(activeTool.schema.properties).forEach(propName => {
                    const input = document.getElementById('input-' + propName);
                    if (input && input.value) {
                        const propType = activeTool.schema.properties[propName].type;
                        args[propName] = propType === 'integer' ? parseInt(input.value) : input.value;
                    }
                });
            }
            
            document.getElementById('tool-modal-result').style.display = 'block';
            document.getElementById('tool-modal-output').innerText = 'Executing... Please wait.';
            
            try {
                const res = await fetch('/api/mcp/tools/' + activeTool.name + '/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(args)
                });
                const data = await res.json();
                
                if (data.success) {
                    try {
                        const parsed = JSON.parse(data.result);
                        let outputHtml = '';
                        
                        if (parsed.png_base64) {
                            outputHtml += `<div style="text-align: center; margin-bottom: 15px;"><img src="data:image/png;base64,${parsed.png_base64}" style="max-width: 100%; border: 2px solid #4a9eff; border-radius: 8px; image-rendering: pixelated; width: 256px;" /></div>`;
                        }
                        
                        if (parsed.patch_path) {
                            outputHtml += `<div style="text-align: center; margin-bottom: 15px;"><a href="/api/download?path=${encodeURIComponent(parsed.patch_path)}" class="btn-run" style="float: none; display: inline-block;">⬇️ Download Patch</a></div>`;
                        }
                        
                        outputHtml += '<pre>' + JSON.stringify(parsed, null, 2) + '</pre>';
                        document.getElementById('tool-modal-output').innerHTML = outputHtml;
                    } catch (e) {
                        document.getElementById('tool-modal-output').innerText = data.result;
                    }
                } else {
                    document.getElementById('tool-modal-output').innerText = "Error: " + data.error;
                }
            } catch (e) {
                document.getElementById('tool-modal-output').innerText = "Network Error: " + e.message;
            }
        }

        // Start health stream initially
        startHealthStream();
    </script>
</body>
</html>
'''
