#!/usr/bin/env python3
"""
Chrono MCP Server
Provides tools for analyzing Chrono series ROMs
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastmcp import FastMCP
from lib.chrono import (
    ROMS, read_rom, rom_info, find_strings, find_bytes,
    get_all_games, get_game_data, get_dialog, get_characters,
    get_locations, get_credits, get_index, search_dialog,
    list_art_files, get_art_metadata, get_tim_list, get_all_extracted_data,
    get_game_items, get_game_weapons, get_game_armor, get_game_enemies,
    get_game_locations, get_game_techs, get_master_database, get_game_analysis,
    get_dialog_complete, get_binary_data, get_audio_info
)

# Create MCP server
mcp = FastMCP("Crono MCP")

# Cache for ROM data
_rom_cache = {}


def get_rom_data(key: str):
    """Get ROM data, cached"""
    if key not in _rom_cache:
        data = read_rom(key)
        if data:
            _rom_cache[key] = data
    return _rom_cache.get(key, b'')


# ============ GAME INFO TOOLS ============

@mcp.tool()
def list_games() -> list:
    """List all Chrono games with extracted data"""
    return get_all_games()


@mcp.tool()
def get_game_info(game: str) -> dict:
    """Get extracted information for a game"""
    return get_game_data(game)


@mcp.tool()
def list_characters(game: str) -> dict:
    """Get character list and reference counts for a game"""
    return get_characters(game)


@mcp.tool()
def list_locations(game: str) -> dict:
    """Get location list and reference counts for a game"""
    return get_locations(game)


@mcp.tool()
def get_game_credits(game: str) -> list:
    """Get credits for a game"""
    game_key = {
        "Chrono Trigger": "ct_snes",
        "Chrono Cross": "cc_disc1",
        "Radical Dreamers": "rd_snes",
    }.get(game, game.lower())
    
    credits_data = get_credits(game)
    if credits_data:
        return credits_data
    
    # Fallback: try to get from extracted data
    return [{"text": "No credits found in extracted data"}]


# ============ ROM TOOLS ============

@mcp.tool()
def list_roms() -> list:
    """List all available ROMs"""
    return [
        {"key": k, "path": str(v), "exists": v.exists()}
        for k, v in ROMS.items()
    ]


@mcp.tool()
def get_rom_info(game: str = "ct_snes") -> dict:
    """Get information about a ROM"""
    data = get_rom_data(game)
    if not data:
        return {"error": f"ROM not found: {game}"}
    
    info = rom_info(data)
    return {
        "game": game,
        "size_bytes": info["size"],
        "size_mb": round(info["size_mb"], 2),
        "header": info.get("header", "N/A"),
    }


# ============ TEXT SEARCH TOOLS ============

@mcp.tool()
def search_dialog_text(query: str, game: str = "Radical Dreamers") -> list:
    """Search dialog text for a game"""
    return search_dialog(game, query)


@mcp.tool()
def get_dialog_lines(game: str = "Radical Dreamers", limit: int = 50) -> list:
    """Get dialog lines from a game"""
    return get_dialog(game, limit)


@mcp.tool()
def find_text(pattern: str, game: str = "ct_snes", min_length: int = 4) -> list:
    """Search for text patterns in raw ROM data"""
    data = get_rom_data(game)
    if not data:
        return [{"error": f"ROM not found: {game}"}]
    
    strings = find_strings(data, min_length)
    results = []
    for offset, text in strings:
        if pattern.lower() in text.lower():
            results.append({
                "offset": hex(offset),
                "text": text[:100]
            })
    
    return results[:50]


@mcp.tool()
def find_bytes_pattern(pattern: str, game: str = "ct_snes") -> list:
    """Search for byte patterns in ROM"""
    data = get_rom_data(game)
    if not data:
        return [{"error": f"ROM not found: {game}"}]
    
    try:
        pattern_bytes = bytes.fromhex(pattern.replace(" ", ""))
    except ValueError:
        return [{"error": "Invalid hex pattern"}]
    
    positions = find_bytes(data, pattern_bytes)
    return [{"offset": hex(p), "position": p} for p in positions[:20]]


# ============ DUMP TOOLS ============

@mcp.tool()
def dump_rom_region(offset: int, length: int = 256, game: str = "ct_snes") -> dict:
    """Dump a region of ROM as hex and ASCII"""
    data = get_rom_data(game)
    if not data:
        return {"error": f"ROM not found: {game}"}
    
    start = offset
    end = min(offset + length, len(data))
    
    hex_lines = []
    
    for i in range(start, end, 16):
        chunk = data[i:min(i+16, end)]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        
        hex_lines.append(f"{i:08x}: {hex_str:<48} |{ascii_str}|")
    
    return {
        "offset": hex(offset),
        "length": end - start,
        "data": '\n'.join(hex_lines)
    }


@mcp.tool()
def find_credits(game: str = "ct_snes") -> dict:
    """Find and extract credits section from ROM"""
    data = get_rom_data(game)
    if not data:
        return {"error": f"ROM not found: {game}"}
    
    search_patterns = [
        b'Producer',
        b'Director', 
        b'Character Design',
        b'Akira Toriyama',
        b'Yasunori Mitsuda',
    ]
    
    results = []
    for pattern in search_patterns:
        pos = data.find(pattern)
        if pos != -1:
            start = max(0, pos - 20)
            end = min(len(data), pos + 100)
            context = data[start:end]
            ascii_text = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in context)
            results.append({
                "pattern": pattern.decode(),
                "offset": hex(pos),
                "context": ascii_text
            })
    
    return {"credits_found": results}


# ============ DATA TOOLS ============

@mcp.tool()
def get_index() -> dict:
    """Get master index of extracted data"""
    return get_index()


@mcp.tool()
def list_game_characters(game: str = "ct_snes") -> list:
    """Find character names in raw ROM data"""
    data = get_rom_data(game)
    if not data:
        return [{"error": f"ROM not found: {game}"}]
    
    characters = ["CRONO", "LUCCA", "MARLE", "FROG", "ROBO", "AYLA", "MAGUS"]
    results = []
    
    for name in characters:
        pos = data.find(name.encode())
        if pos != -1:
            results.append({"name": name, "offset": hex(pos)})
    
    return results


# ============ ART TOOLS ============

@mcp.tool()
def list_game_art(game: str = None) -> list:
    """List all extracted art files, optionally filtered by game"""
    return list_art_files(game)


@mcp.tool()
def get_game_art_metadata(game: str) -> dict:
    """Get art metadata for a game (graphic regions, TIM info, etc)"""
    return get_art_metadata(game)


@mcp.tool()
def list_chrono_cross_tim() -> list:
    """Get list of TIM images found in Chrono Cross"""
    return get_tim_list()


@mcp.tool()
def get_extracted_data_summary() -> dict:
    """Get summary of all extracted data"""
    return get_all_extracted_data()


@mcp.tool()
def search_all_games(query: str) -> dict:
    """Search dialog across all games for a query"""
    results = {
        "query": query,
        "Chrono Trigger": search_dialog("Chrono Trigger", query),
        "Chrono Cross": search_dialog("Chrono Cross", query),
        "Radical Dreamers": search_dialog("Radical Dreamers", query),
    }
    return results


@mcp.tool()
def get_sample_dialog(game: str = "Radical Dreamers", count: int = 10) -> list:
    """Get sample dialog lines from a game"""
    return get_dialog(game, count)


# ============ GAME DATA TOOLS ============

@mcp.tool()
def get_items(game: str = "Chrono Trigger") -> list:
    """Get item list for a game"""
    return get_game_items(game)


@mcp.tool()
def get_weapons(game: str = "Chrono Trigger") -> list:
    """Get weapon list for a game"""
    return get_game_weapons(game)


@mcp.tool()
def get_armor(game: str = "Chrono Trigger") -> list:
    """Get armor list for a game"""
    return get_game_armor(game)


@mcp.tool()
def get_enemies(game: str = "Chrono Trigger") -> list:
    """Get enemy list for a game"""
    return get_game_enemies(game)


@mcp.tool()
def get_locations_list(game: str = "Chrono Trigger") -> list:
    """Get location list for a game"""
    return get_game_locations(game)


@mcp.tool()
def get_techs(game: str = "Chrono Trigger") -> list:
    """Get tech/ability list for a game"""
    return get_game_techs(game)


@mcp.tool()
def get_database_summary() -> dict:
    """Get master database summary with all counts"""
    return get_master_database()


@mcp.tool()
def get_all_game_data(game: str) -> dict:
    """Get all extracted data for a game (items, weapons, armor, enemies, locations, techs, dialog)"""
    return {
        "items": get_game_items(game)[:50],
        "weapons": get_game_weapons(game)[:50],
        "armor": get_game_armor(game)[:50],
        "enemies": get_game_enemies(game)[:50],
        "locations": get_game_locations(game)[:50],
        "techs": get_game_techs(game)[:50],
    }


@mcp.tool()
def search_game_data(game: str, query: str) -> dict:
    """Search for a term across all data types in a game"""
    query_lower = query.lower()
    
    results = {
        "query": query,
        "items": [],
        "weapons": [],
        "armor": [],
        "enemies": [],
        "locations": [],
        "techs": [],
    }
    
    for item in get_game_items(game):
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        if query_lower in text.lower():
            results["items"].append(item)
    
    for item in get_game_weapons(game):
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        if query_lower in text.lower():
            results["weapons"].append(item)
    
    for item in get_game_armor(game):
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        if query_lower in text.lower():
            results["armor"].append(item)
    
    for item in get_game_enemies(game):
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        if query_lower in text.lower():
            results["enemies"].append(item)
    
    for item in get_game_locations(game):
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        if query_lower in text.lower():
            results["locations"].append(item)
    
    for item in get_game_techs(game):
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        if query_lower in text.lower():
            results["techs"].append(item)
    
    return results


@mcp.tool()
def get_rom_analysis(game: str) -> dict:
    """Get technical analysis of a game ROM (compression, offsets, structure)"""
    return get_game_analysis(game)


@mcp.tool()
def get_complete_dialog(game: str, limit: int = 100) -> list:
    """Get complete dialog for a game (most comprehensive)"""
    return get_dialog_complete(game)[:limit]


@mcp.tool()
def get_binary_game_data(game: str, data_type: str = "all") -> dict:
    """Get binary data (enemies, items, characters) for CT"""
    return get_binary_data(game, data_type)


@mcp.tool()
def get_audio_data_info(game: str) -> dict:
    """Get audio/music info for a game"""
    return get_audio_info(game)


@mcp.tool()
def get_ct_fan_hacks() -> dict:
    """Get all Chrono Trigger fan hack data (Crimson Echoes, Flames of Eternity, Prophets Guile)"""
    from lib.chrono import get_fan_hacks
    return get_fan_hacks()


@mcp.tool()
def get_msu1_orchestral_tracks() -> list:
    """Get MSU1 orchestral audio track list"""
    from lib.chrono import get_msu1_tracks
    return get_msu1_tracks()


@mcp.tool()
def get_all_chrono_trigger_versions() -> dict:
    """Get all Chrono Trigger versions (SNES, DS, PS1, MSU1, Fan Hacks)"""
    from lib.chrono import get_all_ct_versions
    return get_all_ct_versions()


@mcp.tool()
def get_ct_multilanguage_data() -> dict:
    """Get Chrono Trigger multi-language SNES version data"""
    from lib.chrono import load_json
    return load_json("ct_snes_multilang.json")


@mcp.tool()
def get_ct_ost_tracks() -> dict:
    """Get Chrono Trigger OST (MP3) track listing"""
    from lib.chrono import load_json
    return load_json("ct_ost.json")


@mcp.tool()
def get_ct_artwork() -> list:
    """Get Chrono Trigger artwork file listing"""
    from lib.chrono import load_json
    return load_json("ct_artwork.json")


@mcp.tool()
def get_ct_manuals() -> list:
    """Get Chrono Trigger manual/guide PDFs"""
    from lib.chrono import load_json
    return load_json("ct_manuals.json")


@mcp.tool()
def get_manual_text_content(manual_name: str = None) -> dict:
    """Get extracted text from manuals (JP Manual: 5856 lines, Ultimania: 18815 lines)"""
    from lib.chrono import get_manual_text
    return get_manual_text(manual_name)


@mcp.tool()
def get_manual_full_text() -> dict:
    """Get full text content from all manuals (first 50k chars each)"""
    from lib.chrono import get_manual_full_text
    return get_manual_full_text()


@mcp.tool()
def get_ct_master_db() -> dict:
    """Get master Chrono Trigger database with items, enemies, locations, shops, techs - all properly cross-referenced"""
    from lib.chrono import get_ct_master_database
    return get_ct_master_database()


@mcp.tool()
def get_unified_chrono_db() -> dict:
    """Get unified master database for ALL Chrono games (CT, CC, RD) with cross-game references"""
    from lib.chrono import get_unified_master
    return get_unified_master()


@mcp.tool()
def get_game_master_db(game: str) -> dict:
    """Get master database for a specific game. Options: 'Chrono Trigger', 'Chrono Cross', 'Radical Dreamers'"""
    from lib.chrono import get_game_master
    return get_game_master(game)


@mcp.tool()
def get_complete_ct_catalog() -> dict:
    """Get complete Chrono Trigger catalog (all versions, OST, artwork, manuals)"""
    from lib.chrono import get_all_ct_versions
    return get_all_ct_versions()


@mcp.tool()
def search_all_games(query: str) -> dict:
    """Search for items, enemies, or locations across ALL Chrono games. Example: 'fire sword' or 'dragon'"""
    from lib.chrono import load_json
    results = {"query": query, "matches": []}
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        games = unified.get("games", {})
        
        query_lower = query.lower()
        
        for game_name, game_data in games.items():
            for item in game_data.get("items", []):
                if query_lower in str(item).lower():
                    results["matches"].append({"game": game_name, "type": "item", "data": item})
            
            for enemy in game_data.get("enemies", []):
                if query_lower in str(enemy).lower():
                    results["matches"].append({"game": game_name, "type": "enemy", "data": enemy})
            
            for loc in game_data.get("locations", []):
                if query_lower in str(loc).lower():
                    results["matches"].append({"game": game_name, "type": "location", "data": loc})
            
            for tech in game_data.get("techs", []):
                if query_lower in str(tech).lower():
                    results["matches"].append({"game": game_name, "type": "tech", "data": tech})
    
    except Exception as e:
        results["error"] = str(e)
    
    return results


@mcp.tool()
def find_enemies_by_weakness(element: str) -> dict:
    """Find all enemies weak to a specific element (fire, ice, water, lightning) across all games"""
    from lib.chrono import load_json
    
    element_lower = element.lower()
    results = {"element": element, "enemies": []}
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        games = unified.get("games", {})
        
        for game_name, game_data in games.items():
            for enemy in game_data.get("enemies", []):
                weakness = enemy.get("weakness", "").lower()
                if weakness == element_lower:
                    results["enemies"].append({"game": game_name, "enemy": enemy.get("name"), "hp": enemy.get("hp")})
    except Exception as e:
        results["error"] = str(e)
    
    return results


@mcp.tool()
def get_all_characters(game: str = None) -> dict:
    """Get all characters. Leave game empty for all games, or specify 'Chrono Trigger', 'Chrono Cross', 'Radical Dreamers'"""
    from lib.chrono import load_json
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        
        if game:
            game_key = game if game in unified["games"] else None
            if game_key:
                return {game: unified["games"][game_key].get("characters", [])}
            return {"error": f"Game not found: {game}"}
        else:
            return {g: d.get("characters", []) for g, d in unified["games"].items()}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_all_items(game: str = None) -> dict:
    """Get all items/weapons/armor. Leave game empty for all games."""
    from lib.chrono import load_json
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        
        if game:
            game_key = game if game in unified["games"] else None
            if game_key:
                return {game: unified["games"][game_key].get("items", [])}
            return {"error": f"Game not found: {game}"}
        else:
            return {g: d.get("items", []) for g, d in unified["games"].items()}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_all_enemies(game: str = None) -> dict:
    """Get all enemies. Leave game empty for all games."""
    from lib.chrono import load_json
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        
        if game:
            game_key = game if game in unified["games"] else None
            if game_key:
                return {game: unified["games"][game_key].get("enemies", [])}
            return {"error": f"Game not found: {game}"}
        else:
            return {g: d.get("enemies", []) for g, d in unified["games"].items()}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_database_stats() -> dict:
    """Get statistics on the complete database across all games"""
    from lib.chrono import load_json
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        return unified.get("stats", {})
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def find_enemies_by_hp(min_hp: int = 0, max_hp: int = 99999, game: str = None) -> dict:
    """Find enemies by HP range. Example: min_hp=1000 finds strong enemies"""
    from lib.chrono import load_json
    
    results = {"min_hp": min_hp, "max_hp": max_hp, "enemies": []}
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        games = unified.get("games", {})
        
        for game_name, game_data in games.items():
            if game and game_name != game:
                continue
            for enemy in game_data.get("enemies", []):
                hp = enemy.get("hp", 0)
                if isinstance(hp, str):
                    hp = int(hp.replace(",", ""))
                if min_hp <= hp <= max_hp:
                    results["enemies"].append({
                        "game": game_name,
                        "name": enemy.get("name"),
                        "hp": hp
                    })
    except Exception as e:
        results["error"] = str(e)
    
    return results


@mcp.tool()
def find_items_by_price(min_price: int = 0, max_price: int = 99999, game: str = None) -> dict:
    """Find items/weapons/armor by price range"""
    from lib.chrono import load_json
    
    results = {"min_price": min_price, "max_price": max_price, "items": []}
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        games = unified.get("games", {})
        
        for game_name, game_data in games.items():
            if game and game_name != game:
                continue
            
            for item in game_data.get("items", []):
                price = item.get("price", 0)
                if price and isinstance(price, (int, str)):
                    try:
                        price = int(str(price).replace(",", ""))
                        if min_price <= price <= max_price:
                            results["items"].append({
                                "game": game_name,
                                "name": item.get("name"),
                                "price": price,
                                "type": item.get("type", "item")
                            })
                    except:
                        pass
    except Exception as e:
        results["error"] = str(e)
    
    return results


@mcp.tool()
def find_techs_by_element(element: str, game: str = None) -> dict:
    """Find techs/abilities by element. Elements: fire, ice, water, lightning, earth, wind, holy, dark"""
    from lib.chrono import load_json
    
    element_lower = element.lower()
    results = {"element": element, "techs": []}
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        games = unified.get("games", {})
        
        for game_name, game_data in games.items():
            if game and game_name != game:
                continue
            for tech in game_data.get("techs", []):
                elem = tech.get("element", "").lower()
                if elem == element_lower or element_lower in elem:
                    results["techs"].append({
                        "game": game_name,
                        "name": tech.get("name"),
                        "element": tech.get("element"),
                        "damage": tech.get("damage")
                    })
    except Exception as e:
        results["error"] = str(e)
    
    return results


@mcp.tool()
def compare_characters(char_name: str) -> dict:
    """Find a character across all games and compare their stats. Example: 'Lucca' or 'Serge'"""
    from lib.chrono import load_json
    
    char_lower = char_name.lower()
    results = {"character": char_name, "games": []}
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        games = unified.get("games", {})
        
        for game_name, game_data in games.items():
            for char in game_data.get("characters", []):
                name = char.get("name", "").lower()
                if char_lower in name or name in char_lower:
                    results["games"].append({
                        "game": game_name,
                        "character": char
                    })
    except Exception as e:
        results["error"] = str(e)
    
    return results


@mcp.tool()
def find_locations_by_type(location_type: str, game: str = None) -> dict:
    """Find locations by type. Types: town, dungeon, overworld, castle, forest, cave, etc"""
    from lib.chrono import load_json
    
    type_lower = location_type.lower()
    results = {"type": location_type, "locations": []}
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        games = unified.get("games", {})
        
        for game_name, game_data in games.items():
            if game and game_name != game:
                continue
            for loc in game_data.get("locations", []):
                loc_type = loc.get("type", "").lower()
                if type_lower in loc_type:
                    results["locations"].append({
                        "game": game_name,
                        "name": loc.get("name"),
                        "type": loc.get("type")
                    })
    except Exception as e:
        results["error"] = str(e)
    
    return results


@mcp.tool()
def get_game_timeline() -> dict:
    """Get chronological timeline of all locations/events across Chrono games"""
    from lib.chrono import load_json
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        timeline = {
            "Radical Dreamers (PD)": [],
            "Chrono Trigger (1000 AD / Present)": [],
            "Chrono Trigger (Future)": [],
            "Chrono Trigger (Past / Middle Ages)": [],
            "Chrono Trigger (Prehistoric)": [],
            "Chrono Trigger (End of Time)": [],
            "Chrono Cross (PD / 1020 AD)": [],
            "Chrono Cross (DD / 1022 AD)": [],
            "Chrono Cross (Home / Nagua)": [],
        }
        
        for game_name, game_data in games.items():
            if game_name == "Chrono Trigger":
                for loc in game_data.get("locations", []):
                    era = loc.get("era", "unknown")
                    timeline.get(era, []).append(loc.get("name"))
            elif game_name == "Chrono Cross":
                for loc in game_data.get("locations", []):
                    period = loc.get("period", "unknown")
                    timeline.get(period, []).append(loc.get("name"))
        
        return timeline
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def fuzzy_search(query: str, game: str = None, threshold: float = 0.5) -> dict:
    """Fuzzy search across all data. Returns results with similarity scores."""
    from lib.chrono import load_json
    import difflib
    
    results = {"query": query, "matches": []}
    query_lower = query.lower()
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        games = unified.get("games", {})
        
        for game_name, game_data in games.items():
            if game and game_name != game:
                continue
                
            for category, items in game_data.items():
                if not isinstance(items, list):
                    continue
                    
                for item in items:
                    if isinstance(item, dict):
                        # Search in all values
                        for key, val in item.items():
                            if isinstance(val, str):
                                ratio = difflib.SequenceMatcher(None, query_lower, val.lower()).ratio()
                                if ratio >= threshold:
                                    results["matches"].append({
                                        "game": game_name,
                                        "category": category,
                                        "field": key,
                                        "value": val,
                                        "score": round(ratio, 2)
                                    })
                    elif isinstance(item, str):
                        ratio = difflib.SequenceMatcher(None, query_lower, item.lower()).ratio()
                        if ratio >= threshold:
                            results["matches"].append({
                                "game": game_name,
                                "category": category,
                                "value": item,
                                "score": round(ratio, 2)
                            })
        
        # Sort by score
        results["matches"].sort(key=lambda x: x.get("score", 0), reverse=True)
        results["matches"] = results["matches"][:50]  # Limit results
        
    except Exception as e:
        results["error"] = str(e)
    
    return results


@mcp.tool()
def advanced_filter(
    game: str = None, 
    category: str = None,
    min_stat: int = None,
    max_stat: int = None,
    stat_name: str = "hp"
) -> dict:
    """Filter items/enemies by stat range. Example: min_stat=100, stat_name='hp' finds strong enemies."""
    from lib.chrono import load_json
    
    results = {"filters": {"game": game, "category": category, f"min_{stat_name}": min_stat}, "matches": []}
    
    try:
        unified = load_json("extracted/chrono_master_complete.json")
        games = unified.get("games", {})
        
        for game_name, game_data in games.items():
            if game and game_name != game:
                continue
                
            for cat, items in game_data.items():
                if category and cat != category:
                    continue
                if not isinstance(items, list):
                    continue
                    
                for item in items:
                    if isinstance(item, dict):
                        val = item.get(stat_name, 0)
                        if isinstance(val, str):
                            try:
                                val = int(val.replace(",", ""))
                            except:
                                val = 0
                        
                        if min_stat and val and val >= min_stat:
                            results["matches"].append({
                                "game": game_name,
                                "category": cat,
                                stat_name: val,
                                "name": item.get("name", str(item)[:30])
                            })
                        elif max_stat and val and val <= max_stat:
                            results["matches"].append({
                                "game": game_name,
                                "category": cat,
                                stat_name: val,
                                "name": item.get("name", str(item)[:30])
                            })
        
    except Exception as e:
        results["error"] = str(e)
    
    return results


if __name__ == "__main__":
    import sys
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    
    if transport == "http":
        host = os.environ.get("MCP_HOST", "0.0.0.0")
        port = int(os.environ.get("MCP_PORT", "8080"))
        
        # Run MCP with HTTP transport
        # Note: MCP protocol uses streamable-http which requires
        # clients to send Accept: text/event-stream header
        # For simple health checks, use /health endpoint after server starts
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        mcp.run(transport="stdio")
