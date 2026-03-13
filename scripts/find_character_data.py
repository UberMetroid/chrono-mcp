#!/usr/bin/env python3
"""
Find actual character data in CT ROM
"""

from pathlib import Path
import json

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()

print("=== Finding Character Data ===\n")

# CT character names in custom encoding
# Crono = 0x13, Marle = 0x14, Lucca = 0x15, Robo = 0x16, Frog = 0x17, Ayla = 0x18, Magus = 0x19

# Search for character references
for char_code, name in [(0x13, 'CRONO'), (0x14, 'MARLE'), (0x15, 'LUCCA'), (0x16, 'ROBO'), (0x17, 'FROG'), (0x18, 'AYLA'), (0x19, 'MAGUS')]:
    pos = ct.find(bytes([char_code]))
    if pos > 0 and pos < 0x300000:
        print(f"{name}: {hex(pos)}")

# Find HP patterns near character data
# Look for small HP values (50-999) near text
print("\n=== Searching for HP Tables ===")

# Search for pattern: HP (0xHP) followed by values in range
hp_tables = []
for i in range(0x100000, 0x300000, 100):
    # Look for "HP" text followed by numeric values
    if ct[i:i+2] == b'HP':
        # Check next bytes for values
        region = ct[i:i+50]
        values = []
        for j in range(2, len(region)-1, 2):
            val = region[j] | (region[j+1] << 8)
            if 10 <= val <= 999:
                values.append(val)
        if len(values) >= 5:
            hp_tables.append((i, values))

print(f"Found {len(hp_tables)} potential HP tables")
for offset, values in hp_tables[:5]:
    print(f"  {hex(offset)}: {values[:10]}")

# Let's look for item/weapon tables differently
# Items typically have: name (text), price (2 bytes), attack (2 bytes), defense (2 bytes)

print("\n=== Searching for Item Tables ===")

# Find prices (values 10-99999 followed by text)
item_candidates = []
for i in range(0x100000, 0x300000):
    if ct[i:i+2] == b'\x00\x00':  # Null bytes might separate items
        # Check for price-like value
        price = ct[i+2] | (ct[i+3] << 8)
        if 10 <= price <= 99999:
            # Check if next bytes have text
            name_start = i+4
            if name_start < len(ct):
                # Look for readable bytes
                for j in range(name_start, min(name_start+20, len(ct))):
                    if ct[j] in range(0xA0, 0xC0):  # CT font range
                        # Found potential item
                        item_candidates.append((i, price))
                        break

print(f"Found {len(item_candidates)} potential items with prices")

# Extract tech data
print("\n=== Searching for Tech Data ===")

# Tech names are stored in text
tech_markers = [b'\x01\x00', b'\x02\x00', b'\x03\x00']  # Tech menu markers

# Search for tech power values
tech_powers = []
for i in range(0x100000, 0x300000, 50):
    val = ct[i] | (ct[i+1] << 8)
    if 1 <= val <= 999:
        # Check surrounding for text
        region = ct[max(0,i-20):i]
        # If has CT font characters, might be tech data
        tech_count = sum(1 for b in region if 0xA0 <= b <= 0xD4)
        if tech_count >= 3:
            tech_powers.append((i, val))

print(f"Found {len(tech_powers)} potential tech entries")

# Save analysis
analysis = {
    "hp_tables": [{"offset": hex(o), "values": v[:10]} for o, v in hp_tables[:10]],
    "item_candidates": len(item_candidates),
    "tech_powers": len(tech_powers),
}

with open(DATA_DIR / "ct_data_analysis.json", 'w') as f:
    json.dump(analysis, f, indent=2)

print("\n=== Analysis saved ===")
