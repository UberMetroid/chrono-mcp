#!/usr/bin/env python3
"""
Extract NPC data and movement patterns from Chrono games
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting NPC Data ===\n")

# ============ Chrono Trigger NPCs ============
print("--- Chrono Trigger ---")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()

# NPC data typically includes: sprite_id, position, movement_type, dialog_id
npcs_ct = []

for i in range(0x1E0000, 0x220000, 32):
    region = ct_rom[i:i+32]
    
    # NPC structure: sprite_id(2), x(2), y(2), movement(2), dialog(2), etc
    sprite_id = struct.unpack("<H", region[0:2])[0]
    x = struct.unpack("<H", region[2:4])[0]
    y = struct.unpack("<H", region[4:6])[0]
    movement = struct.unpack("<H", region[6:8])[0]
    dialog = struct.unpack("<H", region[8:10])[0]
    
    # Valid NPC ranges
    if 1 <= sprite_id <= 200 and x < 1000 and y < 1000:
        npcs_ct.append({
            "offset": hex(i),
            "sprite_id": sprite_id,
            "x": x,
            "y": y,
            "movement_type": movement,
            "dialog_id": dialog
        })

print(f"Found {len(npcs_ct)} potential NPC entries")

with open(DATA_DIR / "ct_npcs.json", "w") as f:
    json.dump(npcs_ct[:200], f, indent=2)

# ============ Chrono Cross NPCs ============
print("\n--- Chrono Cross ---")

cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

npcs_cc = []

for i in range(0x200000, min(0x600000, len(cc_bin)), 48):
    region = cc_bin[i:i+48]
    
    sprite_id = struct.unpack("<H", region[0:2])[0]
    x = struct.unpack("<H", region[2:4])[0]
    y = struct.unpack("<H", region[4:6])[0]
    movement = struct.unpack("<H", region[6:8])[0]
    dialog = struct.unpack("<H", region[8:10])[0]
    
    if 1 <= sprite_id <= 500 and x < 2000 and y < 2000:
        npcs_cc.append({
            "offset": hex(i),
            "sprite_id": sprite_id,
            "x": x,
            "y": y,
            "movement_type": movement,
            "dialog_id": dialog
        })

print(f"Found {len(npcs_cc)} potential NPC entries")

unique_npcs = []
seen = set()
for n in npcs_cc:
    key = (n["sprite_id"], n["x"], n["y"])
    if key not in seen and n["sprite_id"] > 0:
        seen.add(key)
        unique_npcs.append(n)

npcs_cc = unique_npcs[:200]

with open(DATA_DIR / "cc_npcs.json", "w") as f:
    json.dump(npcs_cc, f, indent=2)

print(f"Saved {len(npcs_cc)} unique NPC entries")

# ============ Save Game Structures ============
print("\n--- Save Game Structures ---")

# CT Save format: 0x2000 bytes per save
# Contains: character stats, inventory, location, time, etc.

ct_saves = []

# Look for save data patterns
# In CT, save data starts with character data
for i in range(0x1E0000, 0x200000, 0x2000):
    region = ct_rom[i:i+64]
    
    # Check for character HP pattern (typically non-zero for valid saves)
    hp1 = struct.unpack("<H", region[0:2])[0]
    hp2 = struct.unpack("<H", region[4:6])[0]
    
    if 1 <= hp1 <= 9999 and 1 <= hp2 <= 9999:
        ct_saves.append({
            "offset": hex(i),
            "char1_hp": hp1,
            "char2_hp": hp2,
            "sample": region[:32].hex()
        })

print(f"Found {len(ct_saves)} potential save entries")

with open(DATA_DIR / "ct_save_structures.json", "w") as f:
    json.dump(ct_saves[:20], f, indent=2)

# CC Save structure
cc_saves = []

for i in range(0x100000, min(0x200000, len(cc_bin)), 0x2000):
    region = cc_bin[i:i+64]
    
    hp1 = struct.unpack("<H", region[0:2])[0]
    hp2 = struct.unpack("<H", region[4:6])[0]
    
    if 1 <= hp1 <= 9999 and 1 <= hp2 <= 9999:
        cc_saves.append({
            "offset": hex(i),
            "char1_hp": hp1,
            "char2_hp": hp2
        })

print(f"Found {len(cc_saves)} potential CC save entries")

with open(DATA_DIR / "cc_save_structures.json", "w") as f:
    json.dump(cc_saves[:20], f, indent=2)

print("\n=== NPC/Save Extraction Complete ===")
