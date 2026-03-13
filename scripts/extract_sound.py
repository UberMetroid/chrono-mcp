#!/usr/bin/env python3
"""
Extract music and sound data from ROMs
"""

import sys
import struct
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
ART_DIR = BASE_DIR / "data" / "art"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

# ============ SNES SPC700 SOUND DATA ============

def find_spc_data(data):
    """Find SPC sound data (SNES music)"""
    spc_files = []
    
    # SPC files start with standard header
    # "SPC700 Snapshot" or just "SNES"
    for i in range(0, min(len(data), 0x400000), 0x100):
        if i + 0x100 > len(data):
            break
            
        chunk = data[i:i+32]
        
        # Check for SPC signature
        if chunk[:4] == b'SNES' or chunk[:4] == b'SPC7':
            spc_files.append({
                "offset": i,
                "header": chunk[:16]
            })
    
    # Also look for music sequence data
    # Common music data has specific patterns
    
    return spc_files

def find_music_data(data):
    """Find music/sequence data"""
    music_areas = []
    
    # Look for common music data patterns
    # Music data often has repeating note patterns
    
    for i in range(0x100000, min(len(data), 0x300000), 0x10000):
        chunk = data[i:i+256]
        
        # Count certain byte patterns
        # Notes (0-127) followed by duration
        notes = sum(1 for b in chunk if b < 128)
        
        if notes > 50:  # High concentration of note-like bytes
            music_areas.append({
                "offset": i,
                "note_bytes": notes,
                "sample": chunk[:32].hex()
            })
    
    return music_areas

# ============ PS1 SEQ/XA DATA ============

def find_ps1_music(data):
    """Find PS1 music data"""
    music_files = []
    
    # XA audio sectors - look for sector markers
    # Also look for SEQ (sequencer) data
    
    for i in range(0, min(len(data), 0x500000), 4):
        if i + 32 > len(data):
            break
            
        # Check for common PS1 sound formats
        chunk = data[i:i+4]
        
        # Could be various sound formats
        # Most PS1 games use proprietary formats
    
    # Look for larger data blocks that might be audio
    for i in range(0x100000, min(len(data), 0x400000), 0x10000):
        chunk = data[i:i+512]
        
        # Audio data has different characteristics than graphics
        # Lower variety of bytes, patterns
        
        unique = len(set(chunk))
        
        if 10 < unique < 40:
            music_files.append({
                "offset": i,
                "unique": unique,
                "sample": chunk[:16].hex()
            })
    
    return music_files[:50]

# ============ EXTRACT ALL ============

def extract_sounds():
    """Extract sound data from all games"""
    print("Extracting sound data...")
    
    # Chrono Trigger
    print("  Chrono Trigger...")
    ct_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
    ct_data = read_rom(ct_path)
    
    ct_spc = find_spc_data(ct_data)
    ct_music = find_music_data(ct_data)
    
    import json
    with open(ART_DIR / "chrono_trigger_music.json", 'w') as f:
        json.dump({"spc": ct_spc, "music": ct_music[:20]}, f, indent=2)
    
    # Extract some music data
    for i, m in enumerate(ct_music[:10]):
        chunk = ct_data[m["offset"]:m["offset"]+4096]
        with open(ART_DIR / f"chrono_trigger_music_{i}_{hex(m['offset'])}.bin", 'wb') as f:
            f.write(chunk)
    
    # Radical Dreamers
    print("  Radical Dreamers...")
    rd_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    rd_data = read_rom(rd_path)
    
    rd_music = find_music_data(rd_data)
    
    with open(ART_DIR / "radical_dreamers_music.json", 'w') as f:
        json.dump({"music": rd_music[:20]}, f, indent=2)
    
    for i, m in enumerate(rd_music[:10]):
        chunk = rd_data[m["offset"]:m["offset"]+4096]
        with open(ART_DIR / f"radical_dreamers_music_{i}_{hex(m['offset'])}.bin", 'wb') as f:
            f.write(chunk)
    
    # Chrono Cross
    print("  Chrono Cross...")
    cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
    cc_data = read_rom(cc_path)
    
    cc_music = find_ps1_music(cc_data)
    
    with open(ART_DIR / "chrono_cross_music.json", 'w') as f:
        json.dump({"music": cc_music[:50]}, f, indent=2)
    
    for i, m in enumerate(cc_music[:20]):
        chunk = cc_data[m["offset"]:m["offset"]+8192]
        with open(ART_DIR / f"chrono_cross_music_{i}_{hex(m['offset'])}.bin", 'wb') as f:
            f.write(chunk)
    
    return len(ct_music) + len(rd_music) + len(cc_music)

if __name__ == "__main__":
    print("=" * 60)
    print("SOUND DATA EXTRACTION")
    print("=" * 60)
    
    count = extract_sounds()
    
    print(f"\nExtracted {count} potential music regions")
