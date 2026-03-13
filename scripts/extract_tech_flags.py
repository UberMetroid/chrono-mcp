#!/usr/bin/env python3
"""
Extract tech learning trees, game flags, and animation data
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Tech Trees & Game Data ===\n")

# ============ Tech Learning Trees ============
print("--- Tech Learning Trees ---")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()

# Tech trees: character_id -> tech_id -> level_learned
# Typically: tech_id, level, mp_cost, etc.

tech_trees_ct = []

# Search for tech learning patterns
for i in range(0x200000, 0x240000, 16):
    region = ct_rom[i:i+16]
    
    # Pattern: char_id, tech_id, level, mp
    char_id = region[0]
    tech_id = region[2]
    level = region[4]
    mp = region[6]
    
    if 1 <= char_id <= 8 and 1 <= tech_id <= 50 and level <= 99:
        tech_trees_ct.append({
            "offset": hex(i),
            "character": char_id,
            "tech_id": tech_id,
            "level": level,
            "mp_cost": mp
        })

print(f"Found {len(tech_trees_ct)} potential tech tree entries")

with open(DATA_DIR / "ct_tech_trees.json", "w") as f:
    json.dump(tech_trees_ct[:100], f, indent=2)

# ============ Game Flags ============
print("\n--- Game Flags ---")

# Game flags track story progress, chest opened, events, etc.
# Typically stored as bitfields

flags_ct = []

# Look for flag patterns (0x00 or 0x01 bytes)
for i in range(0x1C0000, 0x1E0000, 64):
    region = ct_rom[i:i+64]
    
    # Count 0x00 and 0x01 bytes (typical flag values)
    flag_bytes = sum(1 for b in region if b in [0x00, 0x01, 0xFF])
    
    if flag_bytes >= 50:  # Mostly flag-like bytes
        flags_ct.append({
            "offset": hex(i),
            "flag_count": flag_bytes,
            "sample": region[:32].hex()
        })

print(f"Found {len(flags_ct)} potential flag regions")

with open(DATA_DIR / "ct_game_flags.json", "w") as f:
    json.dump(flags_ct[:30], f, indent=2)

# ============ Animation Data ============
print("\n--- Animation Data ---")

# Sprite animation frames: sprite_id, frame_count, frame_data
animations_ct = []

for i in range(0x240000, 0x280000, 32):
    region = ct_rom[i:i+32]
    
    # Animation header: frame_count, speed, loop, etc.
    frame_count = region[0]
    speed = region[2]
    
    # Valid animation ranges
    if 1 <= frame_count <= 20 and speed > 0:
        animations_ct.append({
            "offset": hex(i),
            "frame_count": frame_count,
            "speed": speed,
            "sample": region[:16].hex()
        })

print(f"Found {len(animations_ct)} potential animation entries")

with open(DATA_DIR / "ct_animations.json", "w") as f:
    json.dump(animations_ct[:50], f, indent=2)

# ============ Chrono Cross Additional Data ============
print("\n--- Chrono Cross ---")

cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

# CC Tech trees
cc_techs = []
for i in range(0x300000, 0x400000, 16):
    region = cc_bin[i:i+16]
    char_id = region[0]
    tech_id = region[2]
    level = region[4]
    
    if 1 <= char_id <= 8 and 1 <= tech_id <= 80:
        cc_techs.append({
            "offset": hex(i),
            "character": char_id,
            "tech_id": tech_id,
            "level": level
        })

print(f"Found {len(cc_techs)} potential CC tech entries")

with open(DATA_DIR / "cc_tech_trees.json", "w") as f:
    json.dump(cc_techs[:100], f, indent=2)

# CC Flags
cc_flags = []
for i in range(0x200000, 0x400000, 64):
    region = cc_bin[i:i+64]
    flag_bytes = sum(1 for b in region if b in [0x00, 0x01, 0xFF])
    
    if flag_bytes >= 50:
        cc_flags.append({
            "offset": hex(i),
            "flag_count": flag_bytes
        })

print(f"Found {len(cc_flags)} potential CC flag regions")

with open(DATA_DIR / "cc_game_flags.json", "w") as f:
    json.dump(cc_flags[:30], f, indent=2)

# CC Animations
cc_anims = []
for i in range(0x400000, 0x500000, 32):
    region = cc_bin[i:i+32]
    frame_count = region[0]
    speed = region[2]
    
    if 1 <= frame_count <= 30 and speed > 0:
        cc_anims.append({
            "offset": hex(i),
            "frames": frame_count,
            "speed": speed
        })

print(f"Found {len(cc_anims)} potential CC animation entries")

with open(DATA_DIR / "cc_animations.json", "w") as f:
    json.dump(cc_anims[:50], f, indent=2)

print("\n=== Tech Trees & Game Data Complete ===")
