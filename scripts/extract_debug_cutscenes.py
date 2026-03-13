#!/usr/bin/env python3
"""
Extract debug data, cutscenes, and remaining game data
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Debug, Cutscenes, World Maps ===\n")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()
cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

# ============ Debug Data ============
print("--- Debug Data ---")

# Look for debug strings, test menus, developer messages
debug_ct = []
debug_strings = [b"DEBUG", b"TEST", b"CHEAT", b"DEBUG MENU", b"TEST MODE", 
                 b"DEVELOPER", b"DEV", b"TEMP", b"ALPHA", b"BETA"]

for offset in range(0, len(ct_rom) - 100, 1000):
    region = ct_rom[offset:offset+100]
    for s in debug_strings:
        if s in region:
            debug_ct.append({
                "offset": hex(offset),
                "found": s.decode('ascii', errors='ignore'),
                "context": region[max(0, region.find(s)-10):region.find(s)+len(s)+20].hex()
            })
            break

print(f"Found {len(debug_ct)} CT debug references")

# CC Debug
debug_cc = []
for offset in range(0, min(len(cc_bin), 0x1000000) - 100, 5000):
    region = cc_bin[offset:offset+100]
    for s in debug_strings:
        if s in region:
            debug_cc.append({
                "offset": hex(offset),
                "found": s.decode('ascii', errors='ignore')
            })
            break

print(f"Found {len(debug_cc)} CC debug references")

with open(DATA_DIR / "ct_debug.json", "w") as f:
    json.dump(debug_ct[:20], f, indent=2)

with open(DATA_DIR / "cc_debug.json", "w") as f:
    json.dump(debug_cc[:20], f, indent=2)

# ============ Cutscene Data ============
print("\n--- Cutscenes ---")

# Look for cutscene markers/headers
cutscenes_ct = []

# Cutscene typically has specific header or script structure
for i in range(0x100000, 0x200000, 256):
    region = ct_rom[i:i+64]
    
    # Check for common cutscene patterns
    # (sequence of commands, script-like structure)
    cmd_bytes = sum(1 for b in region if b < 0x20)
    
    if 30 < cmd_bytes < 55:
        cutscenes_ct.append({
            "offset": hex(i),
            "command_count": cmd_bytes,
            "sample": region[:32].hex()
        })

print(f"Found {len(cutscenes_ct)} potential CT cutscene entries")

# CC Cutscenes
cutscenes_cc = []
for i in range(0x200000, min(0x600000, len(cc_bin)), 512):
    region = cc_bin[i:i+64]
    cmd_bytes = sum(1 for b in region if b < 0x20)
    
    if 30 < cmd_bytes < 55:
        cutscenes_cc.append({
            "offset": hex(i),
            "command_count": cmd_bytes
        })

print(f"Found {len(cutscenes_cc)} potential CC cutscene entries")

with open(DATA_DIR / "ct_cutscenes.json", "w") as f:
    json.dump(cutscenes_ct[:30], f, indent=2)

with open(DATA_DIR / "cc_cutscenes.json", "w") as f:
    json.dump(cutscenes_cc[:30], f, indent=2)

# ============ World Map Data ============
print("\n--- World Maps ---")

# World maps are typically large tilemaps
worldmap_ct = []

for i in range(0x100000, 0x180000, 512):
    region = ct_rom[i:i+128]
    
    # World map dimensions (typically 256x256 or similar)
    w = struct.unpack("<H", region[0:2])[0]
    h = struct.unpack("<H", region[2:4])[0]
    
    # Valid world map sizes
    if 64 <= w <= 512 and 64 <= h <= 512:
        # Check for tile data
        tile_refs = sum(1 for j in range(4, 64, 2) 
                       if struct.unpack("<H", region[j:j+2])[0] < 500)
        
        if tile_refs > 20:
            worldmap_ct.append({
                "offset": hex(i),
                "width": w,
                "height": h,
                "tile_refs": tile_refs
            })

print(f"Found {len(worldmap_ct)} potential world map locations")

with open(DATA_DIR / "ct_worldmap.json", "w") as f:
    json.dump(worldmap_ct[:20], f, indent=2)

# CC World maps
worldmap_cc = []
for i in range(0x100000, min(0x400000, len(cc_bin)), 1024):
    region = cc_bin[i:i+128]
    w = struct.unpack("<H", region[0:2])[0]
    h = struct.unpack("<H", region[2:4])[0]
    
    if 64 <= w <= 1024 and 64 <= h <= 1024:
        tile_refs = sum(1 for j in range(4, 64, 2) 
                       if struct.unpack("<H", region[j:j+2])[0] < 1000)
        
        if tile_refs > 20:
            worldmap_cc.append({
                "offset": hex(i),
                "width": w,
                "height": h
            })

print(f"Found {len(worldmap_cc)} potential CC world map locations")

with open(DATA_DIR / "cc_worldmap.json", "w") as f:
    json.dump(worldmap_cc[:20], f, indent=2)

# ============ Battle Backgrounds ============
print("\n--- Battle Backgrounds ---")

# Battle BG data
battle_bg_ct = []

for i in range(0x180000, 0x200000, 256):
    region = ct_rom[i:i+64]
    
    # BG tileset reference + tilemap
    tileset = struct.unpack("<H", region[0:2])[0]
    tilemap = struct.unpack("<H", region[4:6])[0]
    
    if tileset < 100 and tilemap < 100:
        battle_bg_ct.append({
            "offset": hex(i),
            "tileset": tileset,
            "tilemap": tilemap
        })

print(f"Found {len(battle_bg_ct)} potential battle BG entries")

with open(DATA_DIR / "ct_battle_bg.json", "w") as f:
    json.dump(battle_bg_ct[:30], f, indent=2)

print("\n=== Debug/Cutscene/WorldMap Extraction Complete ===")
