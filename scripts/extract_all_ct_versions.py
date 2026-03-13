#!/usr/bin/env python3
"""
Extract ALL new Chrono Trigger versions
"""

import json
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"
CT_DIR = BASE_DIR / "Chrono Trigger"

print("=== Extracting ALL Chrono Trigger Versions ===\n")

# ============ MULTI-LANGUAGE SNES ============
print("--- Multi-Language SNES Versions ---")

multi_lang_dir = CT_DIR / "Chrono Trigger - SUPER NINTENDO - Multi Language"
lang_files = {
    "ct_snes_usa": "Chrono Trigger (USA) (1995).sfc",
    "ct_snes_japan": "Chrono Trigger (Japan).zip",
    "ct_snes_france": "Chrono Trigger (FR).sfc",
    "ct_snes_germany": "Chrono Trigger (DE).sfc",
    "ct_snes_arabic": "Chrono Trigger (ARAB).sfc",
    "ct_snes_finland": "Chrono Trigger (FIN).sfc",
    "ct_snes_portugal": "Chrono Trigger (PT).sfc",
    "ct_snes_romania": "Chrono Trigger (RO).sfc",
}

all_text = {}
for key, filename in lang_files.items():
    path = multi_lang_dir / filename
    if path.exists():
        print(f"  Processing: {filename}")
        with open(path, "rb") as f:
            rom = f.read()
        
        # Extract text
        text_entries = []
        for i in range(0, min(len(rom), 0x300000), 256):
            region = rom[i:i+128]
            ascii_cnt = sum(1 for b in region if 32 <= b <= 126)
            if ascii_cnt > 50:
                try:
                    text = region.decode('ascii', errors='ignore').strip()
                    if len(text) > 10:
                        text_entries.append({"offset": hex(i), "text": text[:50]})
                except:
                    pass
        
        all_text[key] = {"filename": filename, "text_count": len(text_entries), "sample": text_entries[:10]}
        print(f"    Found {len(text_entries)} text regions")

# Save
with open(DATA_DIR / "chrono_trigger/ct_snes_multilang.json", "w") as f:
    json.dump(all_text, f, indent=2)

# ============ DS JAPAN VERSION ============
print("\n--- DS Japan Version ---")

ds_jp_dir = CT_DIR / "Chrono Trigger (Jp,En,Fr) (2008) (Role Playing) (Nintendo DS)"
ds_jp_path = list(ds_jp_dir.glob("*.nds"))[0]

with open(ds_jp_path, "rb") as f:
    ds_jp = f.read()

print(f"  DS Japan size: {len(ds_jp):,} bytes")

# Extract header
arm9_off = struct.unpack("<L", ds_jp[0x20:0x24])[0]
arm9_size = struct.unpack("<L", ds_jp[0x24:0x28])[0]

# Extract text
ds_jp_text = []
for i in range(arm9_off, min(arm9_off + 0x1000000, len(ds_jp)) - 64, 256):
    region = ds_jp[i:i+128]
    ascii_cnt = sum(1 for b in region if 32 <= b <= 126)
    if ascii_cnt > 50:
        try:
            text = region.decode('ascii', errors='ignore').strip()
            if len(text) > 10:
                ds_jp_text.append({"offset": hex(i), "text": text[:50]})
        except:
            pass

print(f"  Found {len(ds_jp_text)} text regions")

# Save
with open(DATA_DIR / "chrono_trigger/ct_ds_japan.json", "w") as f:
    json.dump({
        "filename": ds_jp_path.name,
        "size": len(ds_jp),
        "arm9_offset": hex(arm9_off),
        "arm9_size": arm9_size,
        "text_entries": ds_jp_text[:50]
    }, f, indent=2)

# ============ MSU1 ORCHESTRAL ============
print("\n--- MSU1 Orchestral Version ---")

msu1_dir = CT_DIR / "Chrono Trigger (MSU1) (Audio Orchestral) (USA) (1995) (Role Playing) (Super Nes)"
msu1_sfc_path = msu1_dir / "Chrono_Trigger_(USA)_(MSU1).sfc"

if msu1_sfc_path.exists():
    with open(msu1_sfc_path, "rb") as f:
        msu1_rom = f.read()
    
    print(f"  MSU1 ROM size: {len(msu1_rom):,} bytes")
    
    # MSU1 has same text as vanilla
    msu1_text = []
    for i in range(0, min(len(msu1_rom), 0x300000), 256):
        region = msu1_rom[i:i+128]
        ascii_cnt = sum(1 for b in region if 32 <= b <= 126)
        if ascii_cnt > 50:
            try:
                text = region.decode('ascii', errors='ignore').strip()
                if len(text) > 10:
                    msu1_text.append({"offset": hex(i), "text": text[:50]})
            except:
                pass
    
    print(f"  Found {len(msu1_text)} text regions")
    
    # Get PCM track info
    pcm_files = list(msu1_dir.glob("*.pcm"))
    print(f"  Found {len(pcm_files)} audio tracks")
    
    with open(DATA_DIR / "chrono_trigger/ct_msu1.json", "w") as f:
        json.dump({
            "filename": "Chrono_Trigger_(USA)_(MSU1).sfc",
            "pcm_tracks": len(pcm_files),
            "text_entries": msu1_text[:30]
        }, f, indent=2)

# ============ PS1 VERSION ============
print("\n--- PS1 Version ---")

ps1_dir = CT_DIR / "Chrono Trigger (USA) (v1.1) (1999) (Role Playing) (Playstation)"
ps1_bin = list(ps1_dir.glob("*.bin"))[0]

with open(ps1_bin, "rb") as f:
    ps1_data = f.read()

print(f"  PS1 size: {len(ps1_data):,} bytes")

# Extract text
ps1_text = []
for i in range(0, min(len(ps1_data), 0x1000000), 512):
    region = ps1_data[i:i+128]
    ascii_cnt = sum(1 for b in region if 32 <= b <= 126)
    if ascii_cnt > 50:
        try:
            text = region.decode('ascii', errors='ignore').strip()
            if len(text) > 10:
                ps1_text.append({"offset": hex(i), "text": text[:50]})
        except:
            pass

print(f"  Found {len(ps1_text)} text regions")

# Find TIM images
ps1_tim = []
for i in range(0, min(len(ps1_data), 0x800000), 8192):
    if i + 16 > len(ps1_data):
        break
    if ps1_data[i] == 0x10:
        ps1_tim.append({"offset": hex(i)})

print(f"  Found {len(ps1_tim)} TIM images")

with open(DATA_DIR / "chrono_trigger/ct_ps1.json", "w") as f:
    json.dump({
        "filename": ps1_bin.name,
        "size": len(ps1_data),
        "text_entries": ps1_text[:30],
        "tim_images": len(ps1_tim)
    }, f, indent=2)

# ============ FAN HACKS ============
print("\n--- Fan Hacks ---")

fan_hack_dir = CT_DIR / "Chrono Trigger - SUPER NINTENDO - FAN HACK COMPLETE"

fan_hacks = {
    "ct_hack_crimson_echoes": "Chrono Trigger I - Crimson Echoes (v2004) (USA).sfc",
    "ct_hack_flames_eternity": "Chrono Trigger I - Flames of Eternity (vRC7C) (USA).sfc",
    "ct_hack_prophets_guile": "Chrono Trigger - Prophets_Guile (USA).sfc",
    "ct_hack_prophets_guile_fr": "Chrono Trigger - Prophets Guile (FR).sfc",
}

all_fan_hacks = {}

for key, filename in fan_hacks.items():
    path = fan_hack_dir / filename
    if path.exists():
        print(f"  Processing: {filename}")
        with open(path, "rb") as f:
            rom = f.read()
        
        # Extract text
        text_entries = []
        for i in range(0, min(len(rom), 0x400000), 256):
            region = rom[i:i+128]
            ascii_cnt = sum(1 for b in region if 32 <= b <= 126)
            if ascii_cnt > 50:
                try:
                    text = region.decode('ascii', errors='ignore').strip()
                    if len(text) > 10:
                        text_entries.append({"offset": hex(i), "text": text[:50]})
                except:
                    pass
        
        # Find new content (hack-specific data)
        hack_specific = []
        for i in range(0x200000, min(len(rom), 0x300000), 512):
            region = rom[i:i+64]
            # Look for unique patterns in fan hacks
            unique_bytes = len(set(region))
            if 20 < unique_bytes < 50:
                hack_specific.append({"offset": hex(i), "unique_bytes": unique_bytes})
        
        all_fan_hacks[key] = {
            "filename": filename,
            "type": "fan_hack",
            "size": len(rom),
            "text_count": len(text_entries),
            "hack_specific_regions": len(hack_specific),
            "sample_text": text_entries[:10] if text_entries else []
        }
        
        print(f"    Found {len(text_entries)} text regions, {len(hack_specific)} hack-specific regions")

# Save fan hacks
with open(DATA_DIR / "chrono_trigger/ct_fan_hacks.json", "w") as f:
    json.dump(all_fan_hacks, f, indent=2)

print("\n=== ALL EXTRACTION COMPLETE ===")
