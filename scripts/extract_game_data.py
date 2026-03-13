#!/usr/bin/env python3
"""
Extract game data: enemies, items, techs, locations from ROMs
"""

import sys
import struct
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

# ============ ENEMY DATA ============

def find_enemy_names(data):
    """Find enemy names in ROM"""
    # Look for common enemy name patterns
    enemy_patterns = [
        b'GOBLIN', b'SLIME', b'DRAGON', b'GHOST', b'SKELETON',
        b'BAT', b'SPIDER', b'SNAKE', b'WOLF', b'BEAR',
        b'ROBOT', b'SOLDIER', b'KNIGHT', b'MAGE', b'OGRE',
        b'DEMON', b'ANGEL', b'SPIRIT', b'Golem', b'Turtle',
        b'Lizard', b'Bird', b'Fish', b'Insect', b'Plant',
    ]
    
    enemies = {}
    for pattern in enemy_patterns:
        pos = data.find(pattern)
        if pos != -1:
            # Get context around the name
            start = max(0, pos - 20)
            end = min(len(data), pos + 30)
            context = data[start:end]
            readable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in context)
            enemies[pattern.decode()] = {
                "offset": hex(pos),
                "context": readable
            }
    
    return enemies

def find_monster_stats(data):
    """Find monster stat patterns"""
    # Look for HP values near enemy names
    # HP typically 2 bytes, values like 10-9999
    stats = []
    
    # Look for common stat patterns
    for i in range(0, len(data) - 10):
        # Check for HP pattern (usually before enemy name)
        # HP bytes often have specific ranges
        b1, b2 = data[i], data[i+1]
        hp = (b2 << 8) | b1
        
        if 1 <= hp <= 9999 and hp != 0:
            # Check if nearby looks like stats
            chunk = data[i:i+20]
            # MP is often after HP
            mp = data[i+4] | (data[i+5] << 8) if i+5 < len(data) else 0
            # Attack, Defense often follow
            atk = data[i+8] if i+8 < len(data) else 0
            
            if 0 <= mp <= 999 and 0 <= atk <= 255:
                if hp > 10:  # Skip tiny values
                    stats.append({
                        "offset": i,
                        "hp": hp,
                        "mp": mp,
                        "possible": True
                    })
    
    return stats[:100]

# ============ ITEM DATA ============

def find_item_names(data):
    """Find item names in ROM"""
    item_patterns = [
        b'SWORD', b'BLADE', b'KNIFE', b'AXE', b'HAMMER',
        b'SHIELD', b'HELM', b'ARMOR', b'VEST', b'CLOAK',
        b'RING', b'BRACELET', b'PENDANT', b'CAP',
        b'POTION', b'ETHER', b'TONIC', b'CURE', b'REVIVE',
        b'ELIXIR', b'ANTIDOTE', b'HERB', b'SEED',
        b'MAP', b'KEY', b'TREASURE', b'CHEST',
    ]
    
    items = {}
    for pattern in item_patterns:
        count = data.count(pattern)
        if count > 0:
            pos = data.find(pattern)
            items[pattern.decode()] = {
                "count": count,
                "first_offset": hex(pos)
            }
    
    return items

# ============ TECH/ABILITY DATA ============

def find_tech_names(data):
    """Find technique/ability names"""
    tech_patterns = [
        b'SLASH', b'STRIKE', b'BASH', b'BLITZ', b'SWORD',
        b'FIRE', b'ICE', b'THUNDER', b'WATER', b'WIND',
        b'HEAL', b'CURE', b'PROTECT', b'SHIELD', b'AURA',
        b'CHRONO', b'TRIGGER', b'TIME', b'DREAM', b'CYCLONE',
        b'PUNCH', b'KICK', b'THROW', b'HIT', b'ATTACK',
        b'FLAME', b'FREEZE', b'SPARK', b'STORM', b'WAVE',
    ]
    
    techs = {}
    for pattern in tech_patterns:
        count = data.count(pattern)
        if count > 0:
            pos = data.find(pattern)
            techs[pattern.decode()] = {
                "count": count,
                "first_offset": hex(pos)
            }
    
    return techs

# ============ LOCATION DATA ============

def find_location_names(data):
    """Find location names"""
    loc_patterns = [
        b'CASTLE', b'TOWER', b'TEMPLE', b'CAVE', b'FOREST',
        b'VILLAGE', b'TOWN', b'CITY', b'RUINS', b'SHRINE',
        b'LAKE', b'MOUNTAIN', b'ISLAND', b'DESERT', b'JUNGLE',
        b'SEA', b'OCEAN', b'BEACH', b'PLAINS', b'MARSH',
        b'GRAVEYARD', b'DUNGEON', b'PALACE', b'MANSION', b'GATE',
    ]
    
    locs = {}
    for pattern in loc_patterns:
        count = data.count(pattern)
        if count > 0:
            pos = data.find(pattern)
            locs[pattern.decode()] = {
                "count": count,
                "first_offset": hex(pos)
            }
    
    return locs

# ============ EXTRACT ALL ============

def extract_game_data_all():
    """Extract all game data from all ROMs"""
    import json
    
    results = {}
    
    # Radical Dreamers
    print("Extracting Radical Dreamers game data...")
    rd_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    rd_data = read_rom(rd_path)
    
    results["Radical Dreamers"] = {
        "enemies": find_enemy_names(rd_data),
        "items": find_item_names(rd_data),
        "techs": find_tech_names(rd_data),
        "locations": find_location_names(rd_data),
    }
    
    # Chrono Trigger
    print("Extracting Chrono Trigger game data...")
    ct_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
    ct_data = read_rom(ct_path)
    
    results["Chrono Trigger"] = {
        "enemies": find_enemy_names(ct_data),
        "items": find_item_names(ct_data),
        "techs": find_tech_names(ct_data),
        "locations": find_location_names(ct_data),
    }
    
    # Chrono Cross
    print("Extracting Chrono Cross game data...")
    cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
    cc_data = read_rom(cc_path)
    
    results["Chrono Cross"] = {
        "enemies": find_enemy_names(cc_data),
        "items": find_item_names(cc_data),
        "techs": find_tech_names(cc_data),
        "locations": find_location_names(cc_data),
    }
    
    # Save
    with open(DATA_DIR / "game_data.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    for game, data in results.items():
        print(f"\n{game}:")
        print(f"  Enemies: {len(data['enemies'])}")
        print(f"  Items: {len(data['items'])}")
        print(f"  Techs: {len(data['techs'])}")
        print(f"  Locations: {len(data['locations'])}")
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("GAME DATA EXTRACTION")
    print("=" * 60)
    
    extract_game_data_all()
    
    print("\nSaved to data/game_data.json")
