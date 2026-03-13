#!/usr/bin/env python3
"""
Extract Audio (SPC/PSF) and Video (STR) from ROMs
"""

from pathlib import Path
import json

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()
cc = open(BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin", 'rb').read()

print("=== Audio/Video Extraction ===\n")

# CT - SPC700 audio data
# SPC files typically embedded at specific offsets
# Look for SPC header: "SPC7" or similar

print("--- Chrono Trigger Audio ---")
# CT doesn't have SPC files embedded - music is in custom format
# But we can find music data pointers
music_offsets = []
for i in range(len(ct) - 10):
    if ct[i:i+4] == b'MUSI':
        music_offsets.append(i)
print(f"  Music markers: {len(music_offsets)}")

# Look for sample data
sample_markers = []
for i in range(len(ct) - 10):
    if ct[i:i+4] == b'SMP ':
        sample_markers.append(i)
print(f"  Sample markers: {len(sample_markers)}")

# CC - PSF audio (PlayStation Sound Format)
print("\n--- Chrono Cross Audio ---")
# PSF files have header at specific offsets
# Look for PSF signatures
psf_count = 0
for i in range(0, len(cc) - 100, 1000):
    if cc[i:i+3] == b'PSF':
        psf_count += 1
print(f"  PSF signatures: {psf_count}")

# Look for BRR audio samples (common PS1 audio format)
brr_count = 0
for i in range(0, len(cc) - 100, 100):
    if cc[i:i+4] == b'BRR ':
        brr_count += 1
print(f"  BRR markers: {brr_count}")

# CC - STR video (PlayStation movies)
print("\n--- Chrono Cross Video ---")
# STR format: header at start, then audio/video data
# Look for STR file headers
str_files = []
for i in range(0, len(cc) - 100000, 50000):
    if cc[i:i+3] == b'STR':
        # Check for valid STR header
        if i + 0x100 < len(cc):
            # STR files have size at offset 0x04-0x07
            try:
                size = int.from_bytes(cc[i+4:i+8], 'little')
                if 1000 < size < 100000000:  # Reasonable size
                    str_files.append({"offset": hex(i), "size": size})
            except:
                pass

print(f"  Potential STR videos: {len(str_files)}")
if str_files:
    print(f"    First: {str_files[0]}")

# Save video locations
with open(DATA_DIR / "cc_video_files.json", 'w') as f:
    json.dump(str_files[:50], f, indent=2)

print("\n=== Summary ===")
print(f"CT: Music data (custom SNES format)")
print(f"CC: {psf_count} PSF audio blocks, {len(str_files)} potential videos")
