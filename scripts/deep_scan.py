#!/usr/bin/env python3
"""
Deep scan for remaining data in Chrono ROMs
"""

import json
import struct
from pathlib import Path
from collections import Counter

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Deep Scanning ROMs for Missed Data ===\n")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()
cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

# ============ 1. Look for compressed data we might have missed ============
print("--- Compressed Data Patterns ---")

compressed_ct = []
for i in range(0, len(ct_rom) - 16, 4096):
    region = ct_rom[i:i+16]
    # LZSS typically has header with 0x10 or 0x11
    if region[0] in [0x10, 0x11, 0x12] and region[1] > 0:
        size = region[1] << 8 | region[2]
        if 8 < size < 10000:
            compressed_ct.append({"offset": hex(i), "size": size, "header": region[:4].hex()})

print(f"CT: Found {len(compressed_ct)} compressed blocks")
print(f"  Sample: {compressed_ct[:3]}")

# ============ 2. Find all unique data structures ============
print("\n--- Data Structure Analysis ---")

# Analyze 2-byte patterns across ROM
patterns = Counter()
for i in range(0, min(len(ct_rom), 0x300000), 2):
    val = struct.unpack("<H", ct_rom[i:i+2])[0]
    if val < 10000:
        patterns[val] += 1

# Most common values might indicate data types
print("CT: Most common 2-byte values:")
for val, count in patterns.most_common(20):
    if count > 100:
        print(f"  {val}: {count}")

# ============ 3. Look for sprite/tile data ============
print("\n--- Sprite/Tile Data ---")

# SNES tiles are 8x8 or 16x16, organized in planes
sprites_ct = []
for i in range(0x200000, 0x280000, 64):
    region = ct_rom[i:i+64]
    # Check for tile-like pattern (repeating bytes that form patterns)
    zeros = region.count(0)
    if 10 < zeros < 50:
        # Might be tile data
        sprites_ct.append({"offset": hex(i), "zeros": zeros, "sample": region[:16].hex()})

print(f"CT: Found {len(sprites_ct)} potential sprite regions")

# ============ 4. Look for palette data ============
print("\n--- Palette Data ---")

# Palettes are typically sequences of 15-bit colors (2 bytes each)
palettes_ct = []
for i in range(0x100000, 0x200000, 128):
    region = ct_rom[i:i+128]
    # Count valid palette entries (0-31 for each RGB component)
    valid_colors = 0
    for j in range(0, 126, 2):
        if j+2 > len(region):
            break
        color = struct.unpack("<H", region[j:j+2])[0]
        r = color & 0x1F
        g = (color >> 5) & 0x1F
        b = (color >> 10) & 0x1F
        if r <= 31 and g <= 31 and b <= 31:
            valid_colors += 1
    
    if valid_colors > 20:
        palettes_ct.append({"offset": hex(i), "colors": valid_colors})

print(f"CT: Found {len(palettes_ct)} potential palette regions")

# ============ 5. Look for event/script data ============
print("\n--- Event/Script Data ---")

# Event scripts have specific command structure
events_ct = []
for i in range(0x100000, 0x200000, 128):
    region = ct_rom[i:i+128]
    # Count potential script commands (low bytes)
    script_cmds = sum(1 for b in region if b in [0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9, 0xCA])
    if script_cmds > 20:
        events_ct.append({"offset": hex(i), "commands": script_cmds})

print(f"CT: Found {len(events_ct)} potential event regions")

# ============ 6. Look for minimap data ============
print("\n--- Minimap Data ---")

minimaps_ct = []
for i in range(0x180000, 0x200000, 256):
    region = ct_rom[i:i+64]
    w = region[0]
    h = region[1]
    if 4 <= w <= 64 and 4 <= h <= 64:
        minimaps_ct.append({"offset": hex(i), "width": w, "height": h})

print(f"CT: Found {len(minimaps_ct)} potential minimap regions")

# ============ 7. Look for ending credits data ============
print("\n--- Ending Data ---")

ending_ct = []
for i in range(0x300000, len(ct_rom) - 1000, 512):
    region = ct_rom[i:i+128]
    # Check for credit-like patterns
    ascii_count = sum(1 for b in region if 32 <= b <= 126)
    if ascii_count > 50:
        ending_ct.append({"offset": hex(i), "ascii": ascii_count})

print(f"CT: Found {len(ending_ct)} potential ending/credit regions")

# ============ 8. Look for menu/title data ============
print("\n--- Menu/Title Data ---")

menu_ct = []
for i in range(0x100000, 0x180000, 256):
    region = ct_rom[i:i+128]
    # Menu items are typically short strings
    ascii_count = sum(1 for b in region if 65 <= b <= 90)  # A-Z
    if 20 < ascii_count < 80:
        menu_ct.append({"offset": hex(i), "letters": ascii_count})

print(f"CT: Found {len(menu_ct)} potential menu regions")

# ============ 9. Look for collision/physics data ============
print("\n--- Collision/Physics Data ---")

collision_ct = []
for i in range(0x200000, 0x280000, 64):
    region = ct_rom[i:i+64]
    # Physics data often has repeating byte patterns
    unique = len(set(region))
    if 5 < unique < 20:  # Limited variety = structured data
        collision_ct.append({"offset": hex(i), "unique": unique})

print(f"CT: Found {len(collision_ct)} potential collision regions")

# ============ 10. Look for PC (playable character) data ============
print("\n--- Playable Character Data ---")

pc_data_ct = []
for i in range(0x1C0000, 0x200000, 32):
    region = ct_rom[i:i+32]
    
    # Character data: HP, MP, Strength, Defense, etc.
    hp = struct.unpack("<H", region[0:2])[0]
    mp = struct.unpack("<H", region[2:4])[0]
    str_val = struct.unpack("<H", region[4:6])[0]
    
    if 1 <= hp <= 9999 and 1 <= mp <= 999 and str_val < 100:
        pc_data_ct.append({
            "offset": hex(i),
            "hp": hp,
            "mp": mp,
            "str": str_val,
            "sample": region[:16].hex()
        })

print(f"CT: Found {len(pc_data_ct)} potential PC data entries")

# ============ 11. Chrono Cross Deep Scan ============
print("\n--- Chrono Cross Deep Scan ---")

# CC specific: look for more compressed data
compressed_cc = []
for i in range(0, min(len(cc_bin), 0x1000000), 8192):
    region = cc_bin[i:i+16]
    if region[0] in [0x00, 0x10, 0x11] and region[1] > 0:
        size = (region[1] << 8) | region[2]
        if 8 < size < 50000:
            compressed_cc.append({"offset": hex(i), "size": size})

print(f"CC: Found {len(compressed_cc)} compressed blocks")

# CC palettes
palettes_cc = []
for i in range(0x100000, min(0x800000, len(cc_bin)), 256):
    region = cc_bin[i:i+256]
    valid_colors = 0
    for j in range(0, 254, 2):
        color = struct.unpack("<H", region[j:j+2])[0]
        r = color & 0x1F
        g = (color >> 5) & 0x1F
        b = (color >> 10) & 0x1F
        if r <= 31 and g <= 31 and b <= 31:
            valid_colors += 1
    
    if valid_colors > 30:
        palettes_cc.append({"offset": hex(i), "colors": valid_colors})

print(f"CC: Found {len(palettes_cc)} potential palette regions")

# ============ Save all findings ============
all_findings = {
    "ct_compressed": compressed_ct[:20],
    "ct_sprites": sprites_ct[:20],
    "ct_palettes": palettes_ct[:20],
    "ct_events": events_ct[:20],
    "ct_minimaps": minimaps_ct[:20],
    "ct_ending": ending_ct[:20],
    "ct_menu": menu_ct[:20],
    "ct_collision": collision_ct[:20],
    "ct_pc_data": pc_data_ct[:30],
    "cc_compressed": compressed_cc[:20],
    "cc_palettes": palettes_cc[:20]
}

with open(DATA_DIR / "deep_scan_findings.json", "w") as f:
    json.dump(all_findings, f, indent=2)

print("\n=== Deep Scan Complete ===")
print(f"Saved to {DATA_DIR}/deep_scan_findings.json")
