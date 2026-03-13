#!/usr/bin/env python3
"""FINAL exhaustive extraction"""

import sys
from pathlib import Path
import json

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

# Extract EVERYTHING - all known game content
print("=" * 60)
print("FINAL EXTRACTION")
print("=" * 60)

# 1. Scan for ALL character names in all games
print("\n1. Character name scan...")
chars_to_find = [
    # CT
    b'CRONO', b'LUCCA', b'MARLE', b'FROG', b'ROBO', b'AYLA', b'MAGUS',
    # CC
    b'SERGE', b'KID', b'HARLE', b'LYNX', b'KORIS', b'MACH', b'ZOAH', b'LEENA', b'ORLHA',
    b'MIKI', b'RAZZER', b'GLENN', b'SNEFF', b'DIRK', b'PIP',
    # RD
    b'Kid', b'Magil', b'Serge', b'Lynx', b'Viper', b'Guard',
]

results = {}

for game, path in [
    ("RD", BASE_DIR / "Radical Dreamers/BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"),
    ("CT", BASE_DIR / "Chrono Trigger/Chrono Trigger (USA).sfc"),
]:
    if not path.exists():
        continue
    print(f"  Scanning {game}...")
    data = read_rom(path)
    
    game_results = {}
    for char in chars_to_find:
        count = data.count(char)
        if count > 0:
            pos = data.find(char)
            game_results[char.decode()] = {"count": count, "first_offset": hex(pos)}
    
    results[f"{game}_characters"] = game_results

# 2. Scan for ALL location names
print("\n2. Location name scan...")
locs = [
    b'CASTLE', b'TOWER', b'TEMPLE', b'CAVE', b'FOREST', b'VILLAGE', b'TOWN',
    b'CITY', b'RUINS', b'SHRINE', b'LAKE', b'MOUNTAIN', b'ISLAND', b'DESERT',
    b'JUNGLE', b'SEA', b'OCEAN', b'BEACH', b'PLAINS', b'MANOR', b'MANSION',
]

for game, path in [
    ("RD", BASE_DIR / "Radical Dreamers/BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"),
    ("CT", BASE_DIR / "Chrono Trigger/Chrono Trigger (USA).sfc"),
]:
    if not path.exists():
        continue
    data = read_rom(path)
    
    game_locs = {}
    for loc in locs:
        count = data.count(loc)
        if count > 0:
            game_locs[loc.decode()] = count
    
    results[f"{game}_locations"] = game_locs

# 3. Scan for items/techs
print("\n3. Item/Tech scan...")
items = [
    b'SWORD', b'BLADE', b'KNIFE', b'AXE', b'SHIELD', b'HELM', b'ARMOR',
    b'POTION', b'ETHER', b'TONIC', b'CURE', b'ELIXIR', b'REVIVE',
    b'FIRE', b'ICE', b'THUNDER', b'WATER', b'WIND', b'EARTH',
]

for game, path in [
    ("RD", BASE_DIR / "Radical Dreamers/BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"),
    ("CT", BASE_DIR / "Chrono Trigger/Chrono Trigger (USA).sfc"),
]:
    if not path.exists():
        continue
    data = read_rom(path)
    
    game_items = {}
    for item in items:
        count = data.count(item)
        if count > 0:
            game_items[item.decode()] = count
    
    results[f"{game}_items"] = game_items

# Save comprehensive
with open(DATA_DIR / "complete_scan.json", 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 60)
print("EXTRACTION COMPLETE")
print("=" * 60)

for key, data in results.items():
    print(f"\n{key}: {len(data)} items")
    for name, info in list(data.items())[:5]:
        print(f"  {name}: {info}")
