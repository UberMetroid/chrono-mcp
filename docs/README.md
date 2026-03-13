# Chrono Series MCP Server

A comprehensive MCP server and web UI for analyzing Chrono Trigger, Chrono Cross, and Radical Dreamers ROMs.

## Features

- **Web UI** - Browse all game data at http://localhost:5000
- **MCP Server** - AI/LLM integration at http://localhost:8080/mcp
- **REST API** - Full REST API with search, pagination, export
- **Containerized** - Docker/Podman ready

## Available Games

| Game | Total Items | Categories |
|------|-------------|------------|
| **Chrono Trigger** | 9,975 | 31 |
| **Chrono Cross** | 7,623 | 21 |
| **Radical Dreamers** | 4,099 | 11 |

**Total: 21,697 items across 63 categories**

## Quick Start

```bash
# Run container
podman run -d -p 5000:5000 -p 8080:8080 chrono-mcp

# Or build locally
podman build -t chrono-mcp .
```

## Web UI (Port 5000)

- Browse all game data
- Search across games
- Dark/light theme
- Mobile responsive

## API Endpoints

- `GET /api/games` - List games
- `GET /api/<game>/<category>` - Get category data (paginated)
- `GET /api/search?q=<query>` - Fuzzy search
- `GET /api/export/<game>/<category>/csv` - Export CSV
- `GET /health` - Health check

See `/docs/SELF_HOSTING.md` for full documentation.

## MCP Tools

### Game Information
- `list_games()` - List all available games
- `get_game_info(game)` - Get extracted game data
- `get_database_stats()` - Get database statistics across all games

### Characters
- `list_characters(game)` - Get character list
- `get_all_characters(game)` - Get all characters (leave empty for all games)

### Items & Equipment
- `get_all_items(game)` - Get all items/weapons/armor
- `get_game_items(game)` - Get items for a game
- `get_game_weapons(game)` - Get weapons

### Enemies
- `get_all_enemies(game)` - Get all enemies
- `find_enemies_by_weakness(element)` - Find enemies weak to element (fire, ice, water, lightning)

### Locations
- `list_locations(game)` - Get location list
- `get_game_locations(game)` - Get locations for a game

### Text & Dialog
- `search_dialog_text(query, game)` - Search dialog
- `get_dialog_lines(game, limit)` - Get dialog lines
- `get_complete_dialog(game, limit)` - Get complete dialog

### Search
- `search_all_games(query)` - Search items, enemies, locations across ALL games
- `find_text(pattern, game)` - Search raw ROM text

### ROM Information
- `list_roms()` - List available ROMs
- `get_rom_info(game)` - Get ROM details

### Complete Data
- `get_unified_chrono_db()` - Get unified database for all games
- `get_game_master_db(game)` - Get master database for specific game
- `get_complete_ct_catalog()` - Get complete CT catalog (versions, OST, manuals)

## Data Files

### Chrono Trigger (`data/chrono_trigger/`)
- `master_complete.json` - Master database
- `ct_dialog_complete.json` - 3,414 dialog entries
- `ct_enemies_complete.json` - Enemy data
- `ct_items_complete.json` - Item data
- `ct_locations_complete.json` - Location data
- `ct_master_database.json` - Cross-referenced data

### Chrono Cross (`data/chrono_cross/`)
- `master_complete.json` - Master database
- `cc_dialog_complete.json` - 572+ dialog entries
- `cc_enemies.json` - Enemy data
- `cc_items.json` - Item data

### Radical Dreamers (`data/radical_dreamers/`)
- `master_complete.json` - Master database
- `rd_dialog_complete.json` - 1,282 dialog entries

### Extracted Media
- `data/art/` - 4,569+ images (TIM, PPM)
- `data/audio/` - Music & SFX (WAV, PCM, MSU1)
- `data/chrono_trigger/manuals/` - Extracted PDF text

## ROM Versions Available

### Chrono Trigger
- SNES (USA, Japan, FR, DE, Arabic, etc.)
- DS (USA, Japan)
- PS1
- MSU1 Orchestral
- Fan Hacks (Crimson Echoes, Flames of Eternity, Prophets Guile)

## Quick Examples

```python
# Search across all games
search_all_games("dragon")

# Find fire enemies
find_enemies_by_weakness("fire")

# Get all characters
get_all_characters()

# Get CT items
get_all_items("Chrono Trigger")
```

## Statistics

- **Total JSON files**: 150+
- **Total images**: 4,569
- **Total audio**: 110+ files
- **Total data**: 2.1GB
- **MCP Tools**: 53
