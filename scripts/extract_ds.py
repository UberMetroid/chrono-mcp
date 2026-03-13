#!/usr/bin/env python3
"""
Extract data from Chrono Trigger DS (NDS)
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=== Extracting Chrono Trigger DS Data ===\n")

nds_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA) (En,Fr).nds"

if not nds_path.exists():
    print("NDS file not found!")
    exit(1)

with open(nds_path, "rb") as f:
    nds = f.read()

print(f"NDS size: {len(nds):,} bytes")

# ============ NDS Header ============
print("\n--- NDS Header ---")

# NDS header at 0x0
arm9_offset = struct.unpack("<L", nds[0x20:0x24])[0]
arm9_size = struct.unpack("<L", nds[0x24:0x28])[0]
arm7_offset = struct.unpack("<L", nds[0x28:0x2C])[0]
arm7_size = struct.unpack("<L", nds[0x2C:0x30])[0]
fnt_offset = struct.unpack("<L", nds[0x40:0x44])[0]
fnt_size = struct.unpack("<L", nds[0x44:0x48])[0]
fat_offset = struct.unpack("<L", nds[0x48:0x4C])[0]
fat_size = struct.unpack("<L", nds[0x4C:0x50])[0]

header_info = {
    "arm9_offset": hex(arm9_offset),
    "arm9_size": arm9_size,
    "arm7_offset": hex(arm7_offset),
    "arm7_size": arm7_size,
    "fnt_offset": hex(fnt_offset),
    "fnt_size": fnt_size,
    "fat_offset": hex(fat_offset),
    "fat_size": fat_size
}

print(f"  ARM9: {hex(arm9_offset)} ({arm9_size:,} bytes)")
print(f"  ARM7: {hex(arm7_offset)} ({arm7_size:,} bytes)")

with open(DATA_DIR / "ct_ds_header.json", "w") as f:
    json.dump(header_info, f, indent=2)

# ============ NDS File System ============
print("\n--- NDS File System ---")

# Extract files from FAT
files_nds = []

for i in range(0, min(1000, fat_size // 8)):
    offset = fat_offset + i * 8
    if offset + 8 > len(nds):
        break
    
    start = struct.unpack("<L", nds[offset:offset+4])[0]
    end = struct.unpack("<L", nds[offset+4:offset+8])[0]
    
    if start > 0 and end > start:
        size = end - start
        if size > 0 and size < 10000000:  # Skip unreasonable sizes
            files_nds.append({
                "index": i,
                "offset": hex(start),
                "size": size,
                "end": hex(end)
            })

print(f"Found {len(files_nds)} files in FAT")

with open(DATA_DIR / "ct_ds_files.json", "w") as f:
    json.dump(files_nds[:100], f, indent=2)

# ============ Extract Text from NDS ============
print("\n--- NDS Text Data ---")

# Search for text in the ROM
text_nds = []

for i in range(arm9_offset, min(arm9_offset + 0x1000000, len(nds) - 16), 256):
    region = nds[i:i+64]
    
    # Check for readable ASCII text
    ascii_chars = sum(1 for b in region if 32 <= b <= 126)
    if ascii_chars > 30:
        try:
            text = region[:40].decode('ascii', errors='ignore').strip()
            if len(text) > 10 and not all(c in ' \x00' for c in text):
                text_nds.append({
                    "offset": hex(i),
                    "text": text[:30]
                })
        except:
            pass

print(f"Found {len(text_nds)} text regions")

with open(DATA_DIR / "ct_ds_text.json", "w") as f:
    json.dump(text_nds[:50], f, indent=2)

# ============ NDS Save Data ============
print("\n--- NDS Save Data ---")

# NDS save data typically in last 128KB or at specific offset
save_offset = len(nds) - 0x20000
save_region = nds[save_offset:save_offset+256]

# Look for save signatures
saves_found = []
for i in range(0, 20000, 64):
    region = nds[save_offset + i:save_offset + i + 64]
    
    # Check for character HP pattern
    hp1 = struct.unpack("<H", region[0:2])[0]
    if 1 <= hp1 <= 9999:
        saves_found.append({
            "offset": hex(save_offset + i),
            "char1_hp": hp1,
            "sample": region[:16].hex()
        })

print(f"Found {len(saves_found)} potential save entries")

with open(DATA_DIR / "ct_ds_saves.json", "w") as f:
    json.dump(saves_found[:20], f, indent=2)

print("\n=== NDS Extraction Complete ===")
