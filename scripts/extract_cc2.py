#!/usr/bin/env python3
"""
Extract data from Chrono Cross Disc 2
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Chrono Cross Disc 2 ===\n")

cc2_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 2)" / "Chrono Cross (Disc 2).bin"

with open(cc2_path, "rb") as f:
    cc2 = f.read()

print(f"Disc 2 size: {len(cc2):,} bytes")

# ============ Find text in Disc 2 ============
print("\n--- Text Data ---")

text_cc2 = []
for i in range(0, min(len(cc2), 0x1000000), 512):
    region = cc2[i:i+128]
    ascii_count = sum(1 for b in region if 32 <= b <= 126)
    if ascii_count > 60:
        try:
            text = region[:60].decode('ascii', errors='ignore').strip()
            if len(text) > 10 and any(c.isalpha() for c in text):
                text_cc2.append({"offset": hex(i), "text": text[:40]})
        except:
            pass

print(f"Found {len(text_cc2)} text regions")

with open(DATA_DIR / "cc2_dialog.json", "w") as f:
    json.dump(text_cc2[:100], f, indent=2)

# ============ Find TIM images ============
print("\n--- TIM Images ---")

tim_cc2 = []
for i in range(0, min(len(cc2), 0x800000), 8192):
    region = cc2[i:i+16]
    if region[0] == 0x10:  # TIM signature
        tim_cc2.append({"offset": hex(i)})

print(f"Found {len(tim_cc2)} TIM images")

with open(DATA_DIR / "cc2_tim.json", "w") as f:
    json.dump(tim_cc2[:100], f, indent=2)

# ============ Find audio ============
print("\n--- Audio Sectors ---")

# XA audio sectors
xa_sectors = []
for i in range(0, min(len(cc2), 0x8000000), 2352):  # CD sector size
    region = cc2[i:i+24]
    # Check for XA sector header
    if region[0x12] == 0x01 and region[0x13] == 0x00:
        xa_sectors.append({"offset": hex(i)})

print(f"Found {len(xa_sectors)} XA audio sectors")

with open(DATA_DIR / "cc2_audio.json", "w") as f:
    json.dump({"xa_sectors": len(xa_sectors)}, f, indent=2)

# ============ Game data ============
print("\n--- Game Data ---")

# Find enemy data
enemies_cc2 = []
for i in range(0x100000, min(0x500000, len(cc2)), 32):
    region = cc2[i:i+32]
    hp = struct.unpack("<L", region[0:4])[0]
    exp = struct.unpack("<L", region[4:8])[0]
    
    if 1 <= hp <= 99999 and 0 <= exp <= 999999:
        enemies_cc2.append({"offset": hex(i), "hp": hp, "exp": exp})

print(f"Found {len(enemies_cc2)} potential enemy entries")

with open(DATA_DIR / "cc2_enemies.json", "w") as f:
    json.dump(enemies_cc2[:50], f, indent=2)

# ============ Find compressed data ============
print("\n--- Compressed Data ---")

compressed_cc2 = []
for i in range(0, min(len(cc2), 0x1000000), 8192):
    region = cc2[i:i+16]
    if region[0] in [0x00, 0x10, 0x11] and region[1] > 0:
        size = (region[1] << 8) | region[2]
        if 8 < size < 50000:
            compressed_cc2.append({"offset": hex(i), "size": size})

print(f"Found {len(compressed_cc2)} compressed blocks")

with open(DATA_DIR / "cc2_compressed.json", "w") as f:
    json.dump(compressed_cc2[:20], f, indent=2)

print("\n=== Disc 2 Extraction Complete ===")
