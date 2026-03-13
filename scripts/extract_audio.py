#!/usr/bin/env python3
"""
Audio Data Extractor for Chrono Series
Extracts music and sound data from ROMs
"""

from pathlib import Path
import json

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()
cc = open(BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin", 'rb').read()
rd = open(BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc", 'rb').read()

print("=== Audio Data Extraction ===\n")

# ============ CT Audio ============
# CT doesn't use SPC files - it uses a custom music engine
# Music data is stored as sequence data + sample data

# Look for music sequence markers
music_markers = []
for i in range(len(ct) - 10):
    # Look for common music-related patterns
    if ct[i:i+4] == b'MUSI':
        music_markers.append(i)
    elif ct[i:i+4] == b'SONG':
        music_markers.append(i)
    elif ct[i:i+4] == b'TRACK':
        music_markers.append(i)

print(f"CT Music markers: {len(music_markers)}")

# Look for instrument data
instrument_markers = []
for i in range(len(ct) - 10):
    if ct[i:i+4] == b'INST':
        instrument_markers.append(i)
    elif ct[i:i+4] == b'WAVE':
        instrument_markers.append(i)

print(f"CT Instrument markers: {len(instrument_markers)}")

# Look for sample data (8-bit PCM)
# Look for null-terminated PCM data patterns
sample_regions = []
for i in range(0x100000, 0x300000, 1000):
    # Look for sequences of repeated patterns (common in sample data)
    region = ct[i:i+100]
    # Count transitions (changes from high to low)
    transitions = sum(1 for j in range(len(region)-1) if (region[j] > 128) != (region[j+1] > 128))
    if transitions > 20:  # High entropy = likely sample data
        sample_regions.append(i)

print(f"CT Potential sample regions: {len(sample_regions)}")

# ============ CC Audio ============
# CC uses standard PS1 audio - XA, ADPCM, etc.

# Look for XA audio markers
xa_markers = []
for i in range(0, len(cc) - 1000, 1000):
    if cc[i:i+2] == b'XA':
        xa_markers.append(i)

print(f"\nCC XA markers: {len(xa_markers)}")

# Look for ADPCM markers
adpcm_markers = []
for i in range(0, len(cc) - 100, 100):
    # ADPCM header
    if cc[i:i+4] in [b'\x00\x00\x00\x00', b'\x01\x00\x00\x00']:
        if i + 0x20 < len(cc):
            # Check for audio-like data
            region = cc[i:i+32]
            non_zero = sum(1 for b in region if b != 0)
            if non_zero > 10:
                adpcm_markers.append(i)

print(f"CC ADPCM candidates: {len(adpcm_markers)}")

# Look for audio directory/table
audio_table = []
for i in range(0, 0x1000000, 10000):
    # Look for "SECT" markers (audio sectors)
    if cc[i:i+4] == b'SECT':
        audio_table.append(i)

print(f"CC Audio sector markers: {len(audio_table)}")

# ============ RD Audio ============
# RD also uses SPC-like audio

rd_music_markers = []
for i in range(len(rd) - 10):
    if rd[i:i+4] == b'MUSI':
        rd_music_markers.append(i)
    elif rd[i:i+4] == b'SONG':
        rd_music_markers.append(i)

print(f"\nRD Music markers: {len(rd_music_markers)}")

# Save audio info
audio_info = {
    "Chrono Trigger": {
        "music_markers": len(music_markers),
        "instrument_markers": len(instrument_markers),
        "sample_regions": len(sample_regions),
        "note": "Custom SNES SPC engine - no SPC files embedded"
    },
    "Chrono Cross": {
        "xa_markers": len(xa_markers),
        "adpcm_candidates": len(adpcm_markers),
        "audio_sectors": len(audio_table),
        "note": "PS1 uses XA/ADPCM audio in CD sectors"
    },
    "Radical Dreamers": {
        "music_markers": len(rd_music_markers),
        "note": "Custom SPC-like audio"
    }
}

with open(DATA_DIR / "audio_data_info.json", 'w') as f:
    json.dump(audio_info, f, indent=2)

# Try to extract audio sample data as raw files
print("\n=== Extracting Audio Samples ===")

# For CT - try to extract some sample data
# Find the largest continuous audio-like region

def find_audio_region(data, start, end, min_size=1000):
    """Find largest region with audio-like characteristics"""
    best_start = 0
    best_size = 0
    
    for i in range(start, end, 100):
        # Check for high entropy region
        region = data[i:i+5000]
        if len(region) < 1000:
            continue
        
        # Count non-zero bytes (audio usually has lots)
        non_zero = sum(1 for b in region if b != 0)
        if non_zero > 3000:  # 60% non-zero
            if non_zero > best_size:
                best_size = non_zero
                best_start = i
    
    return best_start, best_size

# Find CT audio region
ct_audio_start, ct_audio_size = find_audio_region(ct, 0x100000, 0x300000)
print(f"CT best audio region: {hex(ct_audio_start)}, {ct_audio_size} bytes")

# Extract a sample (first 10KB of audio-like data)
if ct_audio_size > 1000:
    sample_start = ct_audio_start
    sample_end = min(sample_start + 10000, len(ct))
    
    audio_sample = ct[sample_start:sample_end]
    
    # Save as raw PCM
    sample_path = DATA_DIR / "art" / "ct_audio_sample.raw"
    with open(sample_path, 'wb') as f:
        f.write(audio_sample)
    
    print(f"Saved CT audio sample: {sample_path}")

print("\n=== Audio Extraction Complete ===")
print("Note: Audio data needs specialized decoders (SPC700 for CT, XA decoder for CC)")
