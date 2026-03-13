#!/usr/bin/env python3
"""
Extract palettes, sprites, and visual data missed in earlier passes
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Visual Data (Palettes, Sprites) ===\n")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()
cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

# ============ Extract Palettes ============
print("--- Extracting Palettes ---")

# CT Palettes (15-bit BGR format)
palettes_ct = []
for i in range(0x180000, 0x200000, 128):
    region = ct_rom[i:i+256]
    colors = []
    
    for j in range(0, min(len(region), 254), 2):
        color = struct.unpack("<H", region[j:j+2])[0]
        r = color & 0x1F
        g = (color >> 5) & 0x1F
        b = (color >> 10) & 0x1F
        if r <= 31 and g <= 31 and b <= 31:
            colors.append({"r": r, "g": g, "b": b})
    
    if len(colors) >= 8:
        palettes_ct.append({
            "offset": hex(i),
            "colors": colors[:16],
            "count": len(colors)
        })

print(f"CT: Extracted {len(palettes_ct)} palette regions")

# Save
with open(DATA_DIR / "ct_palettes.json", "w") as f:
    json.dump(palettes_ct[:50], f, indent=2)

# CC Palettes
palettes_cc = []
for i in range(0x400000, 0x600000, 256):
    region = cc_bin[i:i+512]
    colors = []
    
    for j in range(0, min(len(region), 510), 2):
        color = struct.unpack("<H", region[j:j+2])[0]
        r = color & 0x1F
        g = (color >> 5) & 0x1F
        b = (color >> 10) & 0x1F
        if r <= 31 and g <= 31 and b <= 31:
            colors.append({"r": r, "g": g, "b": b})
    
    if len(colors) >= 16:
        palettes_cc.append({
            "offset": hex(i),
            "colors": colors[:32],
            "count": len(colors)
        })

print(f"CC: Extracted {len(palettes_cc)} palette regions")

with open(DATA_DIR / "cc_palettes.json", "w") as f:
    json.dump(palettes_cc[:50], f, indent=2)

# ============ Extract Sprite Data ============
print("\n--- Extracting Sprite Data ---")

# Extract SNES sprite data (tiles)
sprites_ct = []
for i in range(0x200000, 0x280000, 64):
    region = ct_rom[i:i+128]
    
    # Check for tile data (has repeating patterns)
    zeros = region.count(0)
    pattern_score = 0
    
    # Count 2-byte patterns
    for j in range(0, 120, 2):
        val = struct.unpack("<H", region[j:j+2])[0]
        if val != 0:
            pattern_score += 1
    
    if 30 < pattern_score < 100:
        sprites_ct.append({
            "offset": hex(i),
            "pattern_score": pattern_score,
            "zeros": zeros,
            "sample": region[:32].hex()
        })

print(f"CT: Found {len(sprites_ct)} sprite regions")

with open(DATA_DIR / "ct_sprite_tiles.json", "w") as f:
    json.dump(sprites_ct[:30], f, indent=2)

# ============ Extract PC Character Stats ============
print("\n--- Extracting PC Stats ---")

pc_stats_ct = []
for i in range(0x1C0000, 0x200000, 32):
    region = ct_rom[i:i+32]
    
    hp = struct.unpack("<H", region[0:2])[0]
    mp = struct.unpack("<H", region[4:6])[0]
    str_val = region[6]
    def_val = region[7]
    mag_val = region[8]
    spd_val = region[9]
    
    if 1 <= hp <= 9999 and 0 <= mp <= 999 and str_val < 100:
        pc_stats_ct.append({
            "offset": hex(i),
            "hp": hp,
            "mp": mp,
            "strength": str_val,
            "defense": def_val,
            "magic": mag_val,
            "speed": spd_val
        })

print(f"CT: Found {len(pc_stats_ct)} PC stat entries")

with open(DATA_DIR / "ct_pc_full_stats.json", "w") as f:
    json.dump(pc_stats_ct[:100], f, indent=2)

# ============ Extract Minimap Data ============
print("\n--- Extracting Minimaps ---")

minimaps_ct = []
for i in range(0x180000, 0x200000, 256):
    region = ct_rom[i:i+64]
    
    w = region[0]
    h = region[1]
    
    if 4 <= w <= 64 and 4 <= h <= 64:
        # Check for tile indices
        tile_count = sum(1 for j in range(4, 60) if region[j] < 100)
        
        if tile_count > 10:
            minimaps_ct.append({
                "offset": hex(i),
                "width": w,
                "height": h,
                "tiles": tile_count
            })

print(f"CT: Found {len(minimaps_ct)} minimap regions")

with open(DATA_DIR / "ct_minimaps.json", "w") as f:
    json.dump(minimaps_ct[:30], f, indent=2)

# ============ Extract Collision Data ============
print("\n--- Extracting Collision Data ---")

collision_ct = []
for i in range(0x200000, 0x280000, 64):
    region = ct_rom[i:i+64]
    
    # Look for tile ID patterns (0-255 range)
    tile_ids = [region[j] for j in range(64)]
    unique = len(set(tile_ids))
    
    # Collision data typically has limited variety
    if 10 < unique < 40:
        collision_ct.append({
            "offset": hex(i),
            "unique_tiles": unique,
            "sample": region[:32].hex()
        })

print(f"CT: Found {len(collision_ct)} collision regions")

with open(DATA_DIR / "ct_collision_data.json", "w") as f:
    json.dump(collision_ct[:30], f, indent=2)

print("\n=== Visual Data Extraction Complete ===")
