"""
Chrono Series Shared Library
Common utilities for ROM analysis across all Chrono games
"""

import os
from pathlib import Path
from typing import Optional

# Base directory for Chrono series (configurable via environment)
_BASE_DIR = os.environ.get("CHRONO_BASE", "/home/jeryd/Code/Chrono_Series")
BASE_DIR = Path(_BASE_DIR)

# Game paths
GAMES = {
    "ct": BASE_DIR / "Chrono Trigger",
    "cc": BASE_DIR / "Chrono Cross", 
    "rd": BASE_DIR / "Radical Dreamers",
}

# ROM files by game
ROMS = {
    # Chrono Trigger SNES
    "ct_snes": GAMES["ct"] / "Chrono Trigger (USA).sfc",
    "ct_snes_japan": GAMES["ct"] / "Chrono Trigger - SUPER NINTENDO - Multi Language" / "Chrono Trigger (Japan).zip",
    "ct_snes_fr": GAMES["ct"] / "Chrono Trigger - SUPER NINTENDO - Multi Language" / "Chrono Trigger (FR).sfc",
    "ct_snes_de": GAMES["ct"] / "Chrono Trigger - SUPER NINTENDO - Multi Language" / "Chrono Trigger (DE).sfc",
    # Chrono Trigger DS
    "ct_nds_usa": GAMES["ct"] / "Chrono Trigger (Jp,En,Fr) (2008) (Role Playing) (Nintendo DS)" / "Chrono Trigger (USA) (En,Fr).nds",
    "ct_nds_japan": GAMES["ct"] / "Chrono Trigger (Jp,En,Fr) (2008) (Role Playing) (Nintendo DS)" / "Chrono Trigger (Japan) (En,Ja).nds",
    # Chrono Trigger MSU1
    "ct_msu1": GAMES["ct"] / "Chrono Trigger (MSU1) (Audio Orchestral) (USA) (1995) (Role Playing) (Super Nes)" / "Chrono_Trigger_(USA)_(MSU1).sfc",
    # Chrono Trigger PS1
    "ct_ps1": GAMES["ct"] / "Chrono Trigger (USA) (v1.1) (1999) (Role Playing) (Playstation)" / "Chrono Trigger (USA) (v1.1) (1999) (Role Playing) (Playstation).bin",
    # Chrono Trigger Fan Hacks
    "ct_hack_crimson": GAMES["ct"] / "Chrono Trigger - SUPER NINTENDO - FAN HACK COMPLETE" / "Chrono Trigger I - Crimson Echoes (v2004) (USA).sfc",
    "ct_hack_flames": GAMES["ct"] / "Chrono Trigger - SUPER NINTENDO - FAN HACK COMPLETE" / "Chrono Trigger I - Flames of Eternity (vRC7C) (USA).sfc",
    "ct_hack_prophets": GAMES["ct"] / "Chrono Trigger - SUPER NINTENDO - FAN HACK COMPLETE" / "Chrono Trigger - Prophets_Guile (USA).sfc",
    # Chrono Cross (PS1)
    "cc_disc1": GAMES["cc"] / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin",
    "cc_disc2": GAMES["cc"] / "Chrono Cross (Disc 2)" / "Chrono Cross (Disc 2).bin",
    # Radical Dreamers
    "rd_snes": GAMES["rd"] / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc",
}

# Data directory
DATA_DIR = BASE_DIR / "data"


def get_rom_path(game_key: str) -> Optional[Path]:
    """Get path to ROM file"""
    return ROMS.get(game_key)


def read_rom(game_key: str) -> Optional[bytes]:
    """Read ROM file into memory"""
    path = get_rom_path(game_key)
    if path and path.exists():
        with open(path, 'rb') as f:
            return f.read()
    return None


def rom_info(data: bytes) -> dict:
    """Get basic ROM info"""
    info = {
        "size": len(data),
        "size_kb": len(data) // 1024,
        "size_mb": len(data) / (1024 * 1024),
    }
    
    # Check for SNES header
    if len(data) > 0xFFC0 + 32:
        header = data[0xFFC0:0xFFC0 + 32]
        info["header"] = header[:21].decode('ascii', errors='ignore').strip('\x00')
        info["has_header"] = b'\x00' not in header[:21]
    
    return info


def find_bytes(data: bytes, pattern: bytes) -> list:
    """Find all occurrences of pattern in data"""
    positions = []
    offset = 0
    while True:
        pos = data.find(pattern, offset)
        if pos == -1:
            break
        positions.append(pos)
        offset = pos + 1
    return positions


def find_strings(data: bytes, min_length: int = 4) -> list:
    """Find ASCII strings in binary data"""
    results = []
    current = []
    
    for i, byte in enumerate(data):
        if 32 <= byte <= 126:
            current.append((i, chr(byte)))
        else:
            if len(current) >= min_length:
                start = current[0][0]
                text = ''.join(c for _, c in current)
                results.append((start, text))
            current = []
    
    if len(current) >= min_length:
        start = current[0][0]
        text = ''.join(c for _, c in current)
        results.append((start, text))
    
    return results


# LZSS decompression (SNES variant)
def lzss_decompress(data: bytes, offset: int = 0) -> bytes:
    """
    Decompress LZSS compressed data
    Returns decompressed data and new offset
    """
    if offset >= len(data):
        return b'', offset
    
    header = data[offset]
    
    # Check for LZSS signature (usually 0x10 or 0x11)
    if header not in [0x10, 0x11, 0x12]:
        return b'', offset
    
    output = bytearray()
    offset += 1
    decompressed_size = 0
    
    # Get decompression parameters based on header
    if header == 0x10:
        window_size = 4096
        max_length = 18
    elif header == 0x11:
        window_size = 2048
        max_length = 34
    else:
        window_size = 8192
        max_length = 273
    
    while len(output) < decompressed_size or decompressed_size == 0:
        if offset >= len(data):
            break
            
        flags = data[offset]
        offset += 1
        
        for bit in range(8):
            if offset >= len(data):
                break
                
            if flags & (0x80 >> bit):
                # Literal copy
                output.append(data[offset])
                offset += 1
            else:
                # Back reference
                if offset + 1 >= len(data):
                    break
                ref = (data[offset] << 8) | data[offset + 1]
                offset += 2
                
                length = (ref >> 12) + 3
                distance = ref & 0xFFF
                
                if distance >= len(output):
                    continue
                    
                for _ in range(length):
                    output.append(output[-(distance)])
    
    return bytes(output), offset


# Data directory
DATA_DIR = BASE_DIR / "data"

# Cache for extracted data
_data_cache = {}

def load_json(filename: str) -> dict:
    """Load JSON data from data directory"""
    if filename in _data_cache:
        return _data_cache[filename]
    
    path = DATA_DIR / filename
    if path.exists():
        import json
        with open(path) as f:
            data = json.load(f)
        _data_cache[filename] = data
        return data
    return {}

def get_all_games() -> list:
    """Get list of all games"""
    return ["Chrono Trigger", "Chrono Cross", "Radical Dreamers"]

def get_game_data(game: str) -> dict:
    """Get extracted data for a game"""
    game_map = {
        "Chrono Trigger": "chrono_trigger.json",
        "Chrono Cross": "chrono_cross.json",
        "Radical Dreamers": "radical_dreamers.json",
    }
    filename = game_map.get(game)
    if filename:
        return load_json(filename)
    return {}

def get_dialog(game: str, limit: int = 100) -> list:
    """Get dialog lines for a game"""
    if game == "Radical Dreamers":
        data = load_json("radical_dreamers/radical_dreamers_dialog.json")
        if isinstance(data, list):
            return data[:limit]
        data = load_json("radical_dreamers/rd_dialog_complete.json")
        if isinstance(data, list):
            return data[:limit]
    elif game == "Chrono Trigger":
        data = load_json("chrono_trigger/ct_dialog_resolved.json")
        if isinstance(data, list):
            return data[:limit]
        data = load_json("chrono_trigger/ct_dialog_complete.json")
        if isinstance(data, list):
            return data[:limit]
    elif game == "Chrono Cross":
        data = load_json("chrono_cross/chrono_cross_dialog.json")
        if isinstance(data, list):
            return data[:limit]
    return []

def get_characters(game: str) -> dict:
    """Get character references for a game"""
    data = get_game_data(game)
    return data.get("character_references", {})

def get_locations(game: str) -> dict:
    """Get location references for a game"""
    data = get_game_data(game)
    return data.get("location_references", {})

def get_credits(game: str) -> list:
    """Get credits for a game"""
    if game in ["Chrono Trigger", "ct_snes"]:
        data = load_json("ct_credits.json")
        if isinstance(data, list):
            return data[:200]
        data = load_json("ct_credits_full.json")
        if isinstance(data, list):
            return data[:200]
    elif game in ["Chrono Cross", "cc_disc1"]:
        data = load_json("chrono_cross.json")
        if isinstance(data, dict):
            return data.get("credits", [])
    elif game in ["Radical Dreamers", "rd_snes"]:
        data = load_json("radical_dreamers.json")
        if isinstance(data, dict):
            return data.get("credits", [])
    return []

def get_index() -> dict:
    """Get master index"""
    return load_json("index.json")

def search_dialog(game: str, query: str) -> list:
    """Search dialog for a query"""
    query_lower = query.lower()
    results = []
    
    if game == "Radical Dreamers":
        data = load_json("radical_dreamers_dialog.json")
        if isinstance(data, list):
            for line in data:
                text = line if isinstance(line, str) else line.get("text", "")
                if query_lower in text.lower():
                    results.append({"text": text})
    elif game == "Chrono Trigger":
        data = load_json("ct_dialog_resolved.json")
        if isinstance(data, list):
            for line in data:
                text = line.get("text", "") if isinstance(line, dict) else str(line)
                if query_lower in text.lower():
                    results.append(line)
    elif game == "Chrono Cross":
        data = load_json("chrono_cross_readable.json")
        if isinstance(data, list):
            for line in data:
                text = line.get("text", "") if isinstance(line, dict) else str(line)
                if query_lower in text.lower():
                    results.append(line)
    
    return results[:50]

# ============ ART FUNCTIONS ============

ART_DIR = BASE_DIR / "data" / "art"

def list_art_files(game: str = None) -> list:
    """List all art files, optionally filtered by game"""
    import glob
    pattern = f"{ART_DIR}/*"
    if game:
        game_key = game.lower().replace(" ", "_")
        pattern = f"{ART_DIR}/{game_key}*"
    
    files = glob.glob(pattern)
    return [{"name": Path(f).name, "size": Path(f).stat().st_size} for f in files]

def get_art_metadata(game: str) -> dict:
    """Get art metadata for a game"""
    import json
    
    files = list_art_files(game)
    
    metadata_files = {
        "Chrono Trigger": ["chrono_trigger_tiles.json", "chrono_trigger_graphic_regions.json", "chrono_trigger_music.json"],
        "Chrono Cross": ["chrono_cross_tims.json", "chrono_cross_tim_detailed.json", "chrono_cross_music.json"],
        "Radical Dreamers": ["radical_dreamers_tiles.json", "radical_dreamers_graphic_regions.json", "radical_dreamers_music.json"],
    }
    
    result = {"files": files}
    
    for mf in metadata_files.get(game, []):
        path = ART_DIR / mf
        if path.exists():
            with open(path) as f:
                result[mf] = json.load(f)
    
    return result

def get_tim_list() -> list:
    """Get list of Chrono Cross TIM images"""
    import json
    path = DATA_DIR / "cc_tim_extracted.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    path = ART_DIR / "chrono_cross_tim_detailed.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def get_all_extracted_data() -> dict:
    """Get all extracted data summary"""
    summary = {
        "games": ["Chrono Trigger", "Chrono Cross", "Radical Dreamers"],
        "data_files": {},
    }
    
    data_files = [
        ("radical_dreamers_dialog.json", "Radical Dreamers Dialog"),
        ("chrono_cross_readable.json", "Chrono Cross Readable Text"),
        ("ct_dialog_resolved.json", "Chrono Trigger Dialog"),
        ("ct_credits.json", "Chrono Trigger Credits"),
        ("ct_substring_table.json", "Chrono Trigger Substring Table"),
    ]
    
    for filename, desc in data_files:
        path = DATA_DIR / filename
        if path.exists():
            import json
            with open(path) as f:
                data = json.load(f)
            if isinstance(data, list):
                summary["data_files"][desc] = {"type": "list", "count": len(data)}
            elif isinstance(data, dict):
                summary["data_files"][desc] = {"type": "dict", "keys": list(data.keys())[:10]}
    
    return summary


# ============ GAME DATA FUNCTIONS ============

def get_game_items(game: str) -> list:
    """Get item list for a game"""
    game_map = {
        "Chrono Trigger": "chrono_trigger/ct_items.json",
        "Chrono Cross": "chrono_cross/cc_items.json",
        "Radical Dreamers": "radical_dreamers/rd_items.json",
    }
    filename = game_map.get(game)
    if filename:
        return load_json(filename)
    return []


def get_game_weapons(game: str) -> list:
    """Get weapon list for a game"""
    game_map = {
        "Chrono Trigger": "chrono_trigger/ct_weapons.json",
        "Chrono Cross": "chrono_cross/cc_weapons.json",
    }
    filename = game_map.get(game)
    if filename:
        return load_json(filename)
    return []


def get_game_armor(game: str) -> list:
    """Get armor list for a game"""
    game_map = {
        "Chrono Trigger": "chrono_trigger/ct_armor.json",
        "Chrono Cross": "chrono_cross/cc_armor.json",
    }
    filename = game_map.get(game)
    if filename:
        return load_json(filename)
    return []


def get_game_enemies(game: str) -> list:
    """Get enemy list for a game"""
    game_map = {
        "Chrono Trigger": "chrono_trigger/ct_enemies.json",
        "Chrono Cross": "chrono_cross/cc_enemies.json",
        "Radical Dreamers": "radical_dreamers/rd_enemies.json",
    }
    filename = game_map.get(game)
    if filename:
        return load_json(filename)
    return []


def get_game_locations(game: str) -> list:
    """Get location list for a game"""
    game_map = {
        "Chrono Trigger": "chrono_trigger/ct_locations.json",
        "Chrono Cross": "chrono_cross/cc_locations.json",
        "Radical Dreamers": "radical_dreamers/rd_locations.json",
    }
    filename = game_map.get(game)
    if filename:
        return load_json(filename)
    return []


def get_game_techs(game: str) -> list:
    """Get tech/ability list for a game"""
    game_map = {
        "Chrono Trigger": "chrono_trigger/ct_techs.json",
        "Chrono Cross": "chrono_cross/cc_techs.json",
    }
    filename = game_map.get(game)
    if filename:
        return load_json(filename)
    return []


def get_master_database() -> dict:
    """Get master database summary"""
    return load_json("master_database.json")


def get_game_analysis(game: str) -> dict:
    """Get technical analysis of a game ROM"""
    game_map = {
        "Chrono Trigger": "ct_analysis.json",
        "Chrono Cross": "cc_analysis.json",
        "Radical Dreamers": "rd_analysis.json",
    }
    filename = game_map.get(game)
    if filename:
        return load_json(filename)
    return {}


def get_dialog_complete(game: str) -> list:
    """Get complete dialog for a game"""
    game_map = {
        "Chrono Trigger": "ct_dialog_complete.json",
        "Chrono Cross": "cc_dialog_complete.json",
        "Radical Dreamers": "rd_dialog_complete.json",
    }
    filename = game_map.get(game)
    if filename:
        return load_json(filename)
    return []


def get_binary_data(game: str, data_type: str = "all") -> dict:
    """Get binary data for a game (enemies, items, characters)"""
    if game != "Chrono Trigger":
        return {}
    
    result = {}
    
    if data_type in ["all", "enemies"]:
        enemies = load_json("ct_enemies_binary.json")
        if enemies:
            result["enemies"] = enemies[:100]
    
    if data_type in ["all", "items"]:
        items = load_json("ct_items_binary.json")
        if items:
            result["items"] = items[:100]
    
    if data_type in ["all", "characters"]:
        chars = load_json("ct_character_stats_binary.json")
        if chars:
            result["characters"] = chars
    
    return result


def get_audio_info(game: str) -> dict:
    """Get audio data info for a game"""
    if game == "Chrono Trigger":
        return load_json("audio_data_info.json").get("Chrono Trigger", {})
    elif game == "Chrono Cross":
        return load_json("audio_data_info.json").get("Chrono Cross", {})
    elif game == "Radical Dreamers":
        return load_json("audio_data_info.json").get("Radical Dreamers", {})
    return {}


def get_fan_hacks() -> dict:
    """Get all fan hack data"""
    return load_json("ct_fan_hacks.json")


def get_msu1_tracks() -> list:
    """Get MSU1 orchestral track info"""
    msu1_dir = BASE_DIR / "data" / "audio" / "msu1"
    if msu1_dir.exists():
        tracks = list(msu1_dir.glob("*.pcm"))
        return [{"track": t.stem, "size": t.stat().st_size} for t in tracks]
    return []


def get_all_ct_versions() -> dict:
    """Get all Chrono Trigger versions"""
    versions = {}
    
    # Multi-language
    ml = load_json("ct_snes_multilang.json")
    if ml:
        versions["multi_language"] = ml
    
    # DS Japan
    ds_jp = load_json("ct_ds_japan.json")
    if ds_jp:
        versions["ds_japan"] = ds_jp
    
    # MSU1
    msu1 = load_json("ct_msu1.json")
    if msu1:
        versions["msu1"] = msu1
    
    # PS1
    ps1 = load_json("ct_ps1.json")
    if ps1:
        versions["ps1"] = ps1
    
    # Fan hacks
    fan = load_json("ct_fan_hacks.json")
    if fan:
        versions["fan_hacks"] = fan
    
    # OST
    ost = load_json("ct_ost.json")
    if ost:
        versions["ost"] = ost
    
    # Artwork
    artwork = load_json("ct_artwork.json")
    if artwork:
        versions["artwork"] = artwork
    
    # Manuals
    manuals = load_json("ct_manuals.json")
    if manuals:
        versions["manuals"] = manuals
    
    return versions


def get_manual_text(manual_name: str = None) -> dict:
    """Get extracted manual text content"""
    manual_file = BASE_DIR / "data" / "chrono_trigger" / "manuals" / "manual_content.json"
    if manual_file.exists():
        content = load_json("manual_content.json")
        if manual_name:
            return content.get(manual_name, {})
        return content
    return {}


def get_manual_full_text() -> dict:
    """Get full text from all manuals"""
    manuals_dir = BASE_DIR / "data" / "chrono_trigger" / "manuals"
    result = {}
    for txt_file in manuals_dir.glob("*.txt"):
        if txt_file.stat().st_size > 100:
            with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            result[txt_file.stem] = content[:50000]
    return result


def get_ct_master_database() -> dict:
    """Get master database with cross-referenced items, enemies, locations, shops, techs"""
    return load_json("ct_master_database.json")


def get_unified_master() -> dict:
    """Get unified master database for all Chrono games"""
    return load_json("chrono_master.json")


def get_game_master(game: str) -> dict:
    """Get master database for a specific game (Chrono Trigger, Chrono Cross, Radical Dreamers)"""
    masters = {
        "Chrono Trigger": "ct_master_complete.json",
        "Chrono Cross": "cc_master_complete.json", 
        "Radical Dreamers": "rd_master_complete.json",
    }
    filename = masters.get(game)
    if filename:
        if game == "Chrono Trigger":
            return load_json("chrono_trigger/" + filename)
        elif game == "Chrono Cross":
            return load_json("chrono_cross/" + filename)
        elif game == "Radical Dreamers":
            return load_json("radical_dreamers/" + filename)
    return {}


# Export knowledge to JSON
def export_knowledge() -> dict:
    """Export current knowledge base"""
    return {
        "games": list(GAMES.keys()),
        "roms": {k: str(v) for k, v in ROMS.items()},
    }


if __name__ == "__main__":
    # Quick test
    rom = read_rom("ct_snes")
    if rom:
        info = rom_info(rom)
        print(f"Chrono Trigger (SNES): {info['size_mb']:.2f}MB")
        print(f"Header: {info.get('header', 'N/A')}")
