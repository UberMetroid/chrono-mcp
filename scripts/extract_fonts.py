#!/usr/bin/env python3
"""
Extract font data from Chrono games
"""

import json
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Font Data ===\n")

# ============ Chrono Trigger Fonts ============
print("--- Chrono Trigger ---")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()

# Font data in SNES games is typically in 8x8 or 8x16 tile format
# Look for bitmap font patterns

# Search for character data (repeating patterns of bitmap data)
fonts_ct = []

# Font tiles are typically 8x8 or 8x16 pixels
# Each row of 8 pixels = 1 byte (1bpp) or 2 bytes (2bpp)

# Search for font-like data
for i in range(0x100000, 0x200000, 256):
    region = ct_rom[i:i+128]
    
    # Check for tile-like patterns (consistent bytes)
    non_zero = sum(1 for b in region if b != 0)
    
    # Fonts typically have 50-90% non-zero bytes
    if 60 < non_zero < 115:
        fonts_ct.append({
            "offset": hex(i),
            "non_zero_bytes": non_zero,
            "sample": region[:32].hex()
        })

print(f"Found {len(fonts_ct)} potential font locations")

# Get unique samples
unique_fonts = []
seen_samples = set()
for f in fonts_ct:
    sample = f["sample"][:8]
    if sample not in seen_samples:
        seen_samples.add(sample)
        unique_fonts.append(f)

fonts_ct = unique_fonts[:20]

with open(DATA_DIR / "ct_fonts.json", "w") as f:
    json.dump(fonts_ct, f, indent=2)

print(f"Saved {len(fonts_ct)} font locations")

# ============ Chrono Cross Fonts ============
print("\n--- Chrono Cross ---")

cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

fonts_cc = []

for i in range(0x100000, min(0x500000, len(cc_bin)), 512):
    region = cc_bin[i:i+128]
    
    non_zero = sum(1 for b in region if b != 0)
    
    if 60 < non_zero < 115:
        fonts_cc.append({
            "offset": hex(i),
            "non_zero_bytes": non_zero,
            "sample": region[:32].hex()
        })

print(f"Found {len(fonts_cc)} potential font locations")

unique_cc_fonts = []
seen_samples = set()
for f in fonts_cc:
    sample = f["sample"][:8]
    if sample not in seen_samples:
        seen_samples.add(sample)
        unique_cc_fonts.append(f)

fonts_cc = unique_cc_fonts[:20]

with open(DATA_DIR / "cc_fonts.json", "w") as f:
    json.dump(fonts_cc, f, indent=2)

print(f"Saved {len(fonts_cc)} font locations")

print("\n=== Font Extraction Complete ===")
