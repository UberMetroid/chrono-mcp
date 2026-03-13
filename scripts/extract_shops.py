#!/usr/bin/env python3
"""
Extract shop data from Chrono Trigger, Chrono Cross, and Radical Dreamers
"""

import json
from pathlib import Path
import struct

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Shop Data ===\n")

# ============ Chrono Trigger Shops ============
print("--- Chrono Trigger ---")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()

# Shop data in CT is typically at fixed locations
# Look for shop header patterns: item count, item IDs
shops_ct = []

# Known shop locations in CT (approximate)
shop_offsets = [
    (0x1C8000, "Guardia Shop"),
    (0x1C8200, "Frogs Shop"),
    (0x1C8400, "Guru Shop"),
    (0x1C8600, "Sewers Shop"),
    (0x1C8800, "Factory Shop"),
    (0x1C8A00, "Denadoro Shop"),
    (0x1C8C00, "Humbaba Shop"),
    (0x1C8E00, "Kashmir Shop"),
    (0x1C9000, "BlackTemple Shop"),
    (0x1C9200, "Sunken Desert Shop"),
]

# Load items for reference
ct_items = json.load(open(DATA_DIR / "ct_items_binary.json"))

for offset, name in shop_offsets:
    if offset + 20 < len(ct_rom):
        data = ct_rom[offset:offset+20]
        items = []
        for i in range(0, 16, 2):
            item_id = struct.unpack("<H", data[i:i+2])[0]
            if item_id < 100:  # Valid item ID range
                items.append(item_id)
        if items:
            shops_ct.append({"name": name, "offset": hex(offset), "items": items})

print(f"  Found {len(shops_ct)} shop locations")

# Also search for shop patterns
shop_pattern_count = 0
for i in range(0x100000, 0x200000, 16):
    region = ct_rom[i:i+16]
    # Count items in valid range
    valid_items = sum(1 for j in range(0, 16, 2) 
                     if 0 < struct.unpack("<H", region[j:j+2])[0] < 100)
    if valid_items >= 3:
        shop_pattern_count += 1

print(f"  Shop pattern matches: {shop_pattern_count}")

# Save
with open(DATA_DIR / "ct_shops.json", "w") as f:
    json.dump(shops_ct, f, indent=2)

# ============ Chrono Cross Shops ============
print("\n--- Chrono Cross ---")

cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

shops_cc = []

# Search for shop data patterns in CC
# Shops typically have item IDs followed by 0xFF or price data
for i in range(0x100000, min(0x500000, len(cc_bin)), 64):
    region = cc_bin[i:i+64]
    # Count items in valid range (CC has more items, up to 200+)
    valid_count = 0
    items_found = []
    for j in range(0, 60, 2):
        item_id = struct.unpack("<H", region[j:j+2])[0]
        if 1 <= item_id <= 250:
            valid_count += 1
            items_found.append(item_id)
    
    # A shop typically has 3-15 items
    if 3 <= valid_count <= 15:
        # Check if next byte suggests price or terminator
        if valid_count >= 4:
            shops_cc.append({
                "offset": hex(i),
                "items": items_found,
                "item_count": valid_count
            })

print(f"  Found {len(shops_cc)} potential shop locations")

# Deduplicate based on items
unique_shops = []
seen_items = set()
for shop in shops_cc:
    items_tuple = tuple(shop["items"])
    if items_tuple not in seen_items and len(items_tuple) > 3:
        seen_items.add(items_tuple)
        unique_shops.append(shop)

shops_cc = unique_shops[:50]  # Limit to top 50

with open(DATA_DIR / "cc_shops.json", "w") as f:
    json.dump(shops_cc, f, indent=2)

print(f"  Saved {len(shops_cc)} unique shops")

# ============ Radical Dreamers Shops ============
print("\n--- Radical Dreamers ---")

rd_rom = open(BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc", "rb").read()

shops_rd = []

# Search in RD area (last part of ROM)
for i in range(0x300000, min(0x400000, len(rd_rom)), 32):
    region = rd_rom[i:i+32]
    valid_count = 0
    items_found = []
    for j in range(0, 30, 2):
        item_id = struct.unpack("<H", region[j:j+2])[0]
        if 1 <= item_id <= 100:
            valid_count += 1
            items_found.append(item_id)
    
    if 2 <= valid_count <= 10:
        shops_rd.append({
            "offset": hex(i),
            "items": items_found
        })

print(f"  Found {len(shops_rd)} potential shop locations")

with open(DATA_DIR / "rd_shops.json", "w") as f:
    json.dump(shops_rd, f, indent=2)

print("\n=== Shop Extraction Complete ===")
