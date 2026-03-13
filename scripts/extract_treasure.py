#!/usr/bin/env python3
"""
Extract treasure/chest data from Chrono games
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Treasure/Chest Data ===\n")

# ============ Chrono Trigger Treasure ============
print("--- Chrono Trigger ---")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()

# Treasure in CT is stored as: item_id, quantity, unknown, location_id
# Typically at fixed offsets in the ROM

treasure_ct = []

# Known treasure locations in CT - typically at specific addresses
# Let's search for treasure data patterns

# Search for treasure entries: item ID (1-2 bytes), quantity, location
for i in range(0x1C0000, 0x1E0000, 16):
    region = ct_rom[i:i+16]
    
    # Check for valid item IDs (1-99) followed by quantity (0-99)
    item_id = struct.unpack("<H", region[0:2])[0]
    qty = struct.unpack("<H", region[2:4])[0]
    
    if 1 <= item_id <= 100 and 0 <= qty <= 99:
        treasure_ct.append({
            "offset": hex(i),
            "item_id": item_id,
            "quantity": qty,
            "region": region.hex()
        })

print(f"Found {len(treasure_ct)} potential treasure entries")

# Save treasure data
with open(DATA_DIR / "ct_treasure.json", "w") as f:
    json.dump(treasure_ct[:100], f, indent=2)

# ============ Chrono Cross Treasure ============
print("\n--- Chrono Cross ---")

cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

treasure_cc = []

# CC has more items, search larger range
for i in range(0x100000, min(0x800000, len(cc_bin)), 32):
    region = cc_bin[i:i+32]
    
    item_id = struct.unpack("<H", region[0:2])[0]
    qty = struct.unpack("<H", region[2:4])[0]
    loc_id = struct.unpack("<H", region[4:6])[0]
    
    # CC items go up to ~250
    if 1 <= item_id <= 300 and 0 <= qty <= 99:
        treasure_cc.append({
            "offset": hex(i),
            "item_id": item_id,
            "quantity": qty,
            "location_id": loc_id
        })

print(f"Found {len(treasure_cc)} potential treasure entries")

# Deduplicate
unique_treasure = []
seen = set()
for t in treasure_cc:
    key = (t["item_id"], t["quantity"])
    if key not in seen:
        seen.add(key)
        unique_treasure.append(t)

treasure_cc = unique_treasure[:100]

with open(DATA_DIR / "cc_treasure.json", "w") as f:
    json.dump(treasure_cc, f, indent=2)

print(f"Saved {len(treasure_cc)} unique treasure entries")

# ============ Radical Dreamers Treasure ============
print("\n--- Radical Dreamers ---")

rd_rom = open(BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc", "rb").read()

treasure_rd = []

for i in range(0x100000, min(0x200000, len(rd_rom)), 16):
    region = rd_rom[i:i+16]
    
    item_id = struct.unpack("<H", region[0:2])[0]
    qty = struct.unpack("<H", region[2:4])[0]
    
    if 1 <= item_id <= 100 and 0 <= qty <= 99:
        treasure_rd.append({
            "offset": hex(i),
            "item_id": item_id,
            "quantity": qty
        })

print(f"Found {len(treasure_rd)} potential treasure entries")

with open(DATA_DIR / "rd_treasure.json", "w") as f:
    json.dump(treasure_rd[:50], f, indent=2)

# ============ Chrono Trigger DS (if available) ============
print("\n--- Chrono Trigger DS ---")

ds_paths = list((BASE_DIR / "Chrono Trigger").glob("*.nds"))
if ds_paths:
    print(f"Found NDS: {ds_paths[0].name}")
    # NDS has different structure - extract what we can
    nds_data = open(ds_paths[0], "rb").read()
    
    treasure_ds = []
    for i in range(0x200000, min(0x400000, len(nds_data)), 32):
        region = nds_data[i:i+32]
        item_id = struct.unpack("<H", region[0:2])[0]
        qty = struct.unpack("<H", region[2:4])[0]
        
        if 1 <= item_id <= 150 and 0 <= qty <= 99:
            treasure_ds.append({
                "offset": hex(i),
                "item_id": item_id,
                "quantity": qty
            })
    
    print(f"Found {len(treasure_ds)} potential treasure entries")
    with open(DATA_DIR / "ct_ds_treasure.json", "w") as f:
        json.dump(treasure_ds[:50], f, indent=2)
else:
    print("No NDS ROM found")

print("\n=== Treasure Extraction Complete ===")
