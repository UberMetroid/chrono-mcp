#!/usr/bin/env python3
"""
Extract map data from Chrono games
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Map Data ===\n")

# ============ Chrono Trigger Maps ============
print("--- Chrono Trigger ---")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()

# Map data in CT is typically in compressed format
# Look for map header patterns (width, height, tile data)

map_data = []

# Search for map-like patterns
for i in range(0x100000, 0x200000, 256):
    region = ct_rom[i:i+64]
    
    # Maps typically have dimensions
    w = struct.unpack("<H", region[0:2])[0]
    h = struct.unpack("<H", region[2:4])[0]
    
    # Valid map sizes: 8x8 to 256x256
    if 8 <= w <= 256 and 8 <= h <= 256:
        # Check if following data looks like tile indices
        tile_count = sum(1 for j in range(4, 64, 2) 
                        if struct.unpack("<H", region[j:j+2])[0] < 1000)
        
        if tile_count >= 10:
            map_data.append({
                "offset": hex(i),
                "width": w,
                "height": h,
                "tile_types": tile_count
            })

print(f"Found {len(map_data)} potential map locations")

# Filter unique maps
unique_maps = []
seen_dims = set()
for m in map_data:
    dim = (m["width"], m["height"])
    if dim not in seen_dims:
        seen_dims.add(dim)
        unique_maps.append(m)

ct_maps = unique_maps[:30]
print(f"Saved {len(ct_maps)} unique map locations")

with open(DATA_DIR / "ct_maps.json", "w") as f:
    json.dump(ct_maps, f, indent=2)

# ============ Chrono Cross Maps ============
print("\n--- Chrono Cross ---")

cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

cc_maps = []

for i in range(0x100000, min(0x800000, len(cc_bin)), 512):
    region = cc_bin[i:i+64]
    
    w = struct.unpack("<H", region[0:2])[0]
    h = struct.unpack("<H", region[2:4])[0]
    
    if 8 <= w <= 512 and 8 <= h <= 512:
        tile_count = sum(1 for j in range(4, 64, 2) 
                        if struct.unpack("<H", region[j:j+2])[0] < 2000)
        
        if tile_count >= 15:
            cc_maps.append({
                "offset": hex(i),
                "width": w,
                "height": h,
                "tile_types": tile_count
            })

print(f"Found {len(cc_maps)} potential map locations")

unique_cc_maps = []
seen_dims = set()
for m in cc_maps:
    dim = (m["width"], m["height"])
    if dim not in seen_dims:
        seen_dims.add(dim)
        unique_cc_maps.append(m)

cc_maps = unique_cc_maps[:50]

with open(DATA_DIR / "cc_maps.json", "w") as f:
    json.dump(cc_maps, f, indent=2)

print(f"Saved {len(cc_maps)} unique map locations")

print("\n=== Map Extraction Complete ===")
