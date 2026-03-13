#!/usr/bin/env python3
"""
Comprehensive Audio Extractor for Chrono Series
Extracts all music, samples, and sound data
"""

from pathlib import Path
import json
import struct

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

print("=== Comprehensive Chrono Audio Extraction ===\n")

# ============ CHRONO TRIGGER AUDIO ============
print("--- Chrono Trigger Audio ---")

ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()

# CT Music Engine:
# - Music is stored as sequence data (MIDI-like)
# - Samples are stored as 8-bit PCM
# - There's a music engine at known offsets

# Find all music data blocks
# Look for music header patterns

def find_music_data(data, name):
    """Find music data blocks"""
    results = []
    
    # Look for common music patterns
    patterns = [
        b'\x00\x01\x00',  # Music header
        b'\x00\x02\x00',
        b'\x00\x03\x00',
        b'MUSI',  # Music marker
        b'SONG',
    ]
    
    for pattern in patterns:
        pos = 0
        while True:
            pos = data.find(pattern, pos)
            if pos == -1:
                break
            if pos > 0x100000 and pos < 0x380000:
                results.append({
                    "offset": hex(pos),
                    "pattern": pattern.hex(),
                    "name": name
                })
            pos += 1
    
    return results

ct_music = find_music_data(ct, "CT")
print(f"  Music blocks found: {len(ct_music)}")

# Find sample data (waveforms)
# Look for repeated patterns that indicate waveform data

def find_waveform_regions(data, min_size=500):
    """Find potential waveform/sample regions"""
    regions = []
    
    for start in range(0x100000, 0x380000, 1000):
        # Check if region has audio-like characteristics
        region = data[start:start+2000]
        if len(region) < 500:
            continue
        
        # Count value changes (audio has many)
        changes = sum(1 for i in range(len(region)-1) if region[i] != region[i+1])
        
        # Audio typically has 30-70% changes
        if 300 < changes < 1400:
            regions.append({
                "offset": hex(start),
                "size": 2000,
                "changes": changes
            })
    
    return regions

ct_waveforms = find_waveform_regions(ct)
print(f"  Waveform regions: {len(ct_waveforms)}")

# Extract a large audio sample
# Find best waveform region
best_waveform = None
if ct_waveforms:
    best = max(ct_waveforms, key=lambda x: x["changes"])
    print(f"  Best waveform at {best['offset']}, changes: {best['changes']}")
    best_waveform = best

# Extract the main music data
# Find the largest continuous audio region
def extract_audio_region(data, start, size):
    """Extract audio region"""
    return data[start:start+size]

# Save CT audio info
ct_audio_info = {
    "game": "Chrono Trigger",
    "music_blocks": len(ct_music),
    "waveform_regions": len(ct_waveforms),
    "sample_rate": 32000,  # SNES sample rate
    "format": "8-bit PCM (custom engine)",
    "music_offsets": [m["offset"] for m in ct_music[:20]],
    "waveform_offsets": [w["offset"] for w in ct_waveforms[:20]]
}

# Extract main audio sample (first valid waveform region)
if ct_waveforms:
    for wf in ct_waveforms[:1]:
        offset = int(wf["offset"], 16)
        audio_data = ct[offset:offset+10000]
        sample_path = AUDIO_DIR / "ct_music_sample.raw"
        with open(sample_path, 'wb') as f:
            f.write(audio_data)
        print(f"  Saved: {sample_path}")

# ============ CHRONO CROSS AUDIO ============
print("\n--- Chrono Cross Audio ---")

cc = open(BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin", 'rb').read()

# CC uses XA audio on CD-ROM sectors
# XA sectors are 2324 bytes each (2352 - sync - header)

# Find XA audio sectors
xa_sectors = []
for i in range(0, len(cc) - 2500, 2352):
    # Check for XA sync pattern
    if cc[i:i+12] == b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00':
        xa_sectors.append(i)

print(f"  XA audio sectors: {len(xa_sectors)}")

# Find ADPCM audio blocks
adpcm_blocks = []
for i in range(0, len(cc) - 1000, 100):
    # Look for ADPCM header
    if cc[i:i+4] == b'\x00\x00\x01\x00':
        # Check for audio data following
        if i + 100 < len(cc):
            non_zero = sum(1 for b in cc[i+16:i+100] if b != 0)
            if non_zero > 50:
                adpcm_blocks.append(i)

print(f"  ADPCM candidates: {len(adpcm_blocks)}")

# Extract XA audio sample
if xa_sectors:
    # Extract first XA sector
    xa_offset = xa_sectors[0]
    xa_data = cc[xa_offset:xa_offset+2324]
    sample_path = AUDIO_DIR / "cc_xa_sample.raw"
    with open(sample_path, 'wb') as f:
        f.write(xa_data)
    print(f"  Saved XA sample: {sample_path}")

# Extract ADPCM sample
if adpcm_blocks:
    adpcm_offset = adpcm_blocks[0]
    adpcm_data = cc[adpcm_offset:adpcm_offset+10000]
    sample_path = AUDIO_DIR / "cc_adpcm_sample.raw"
    with open(sample_path, 'wb') as f:
        f.write(adpcm_data)
    print(f"  Saved ADPCM sample: {sample_path}")

# Save CC audio info
cc_audio_info = {
    "game": "Chrono Cross",
    "xa_sectors": len(xa_sectors),
    "adpcm_blocks": len(adpcm_blocks),
    "format": "XA Audio / ADPCM",
    "xa_offsets": [hex(x) for x in xa_sectors[:20]],
    "adpcm_offsets": [hex(a) for a in adpcm_blocks[:20]]
}

# ============ RADICAL DREAMERS AUDIO ============
print("\n--- Radical Dreamers Audio ---")

rd = open(BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc", 'rb').read()

# RD uses similar audio engine to CT

rd_music = find_music_data(rd, "RD")
print(f"  Music blocks: {len(rd_music)}")

rd_waveforms = find_waveform_regions(rd)
print(f"  Waveform regions: {len(rd_waveforms)}")

# Extract RD audio sample
if rd_waveforms:
    wf = rd_waveforms[0]
    offset = int(wf["offset"], 16)
    audio_data = rd[offset:offset+10000]
    sample_path = AUDIO_DIR / "rd_music_sample.raw"
    with open(sample_path, 'wb') as f:
        f.write(audio_data)
    print(f"  Saved: {sample_path}")

rd_audio_info = {
    "game": "Radical Dreamers",
    "music_blocks": len(rd_music),
    "waveform_regions": len(rd_waveforms),
    "sample_rate": 32000,
    "format": "8-bit PCM (custom engine)"
}

# ============ SAVE ALL AUDIO INFO ============

all_audio = {
    "Chrono Trigger": ct_audio_info,
    "Chrono Cross": cc_audio_info,
    "Radical Dreamers": rd_audio_info
}

with open(DATA_DIR / "audio_comprehensive.json", 'w') as f:
    json.dump(all_audio, f, indent=2)

print("\n=== Audio Extraction Complete ===")
print(f"Saved audio samples to: {AUDIO_DIR}")
