#!/usr/bin/env python3
"""
Extract graphics from Chrono Series ROMs
"""

import sys
import struct
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
ART_DIR = BASE_DIR / "data" / "art"
ART_DIR.mkdir(parents=True, exist_ok=True)

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

# ============ PS1 TIM FORMAT (Chrono Cross) ============

def extract_tim(data, start_offset):
    """Extract PS1 TIM image format"""
    # TIM header: 0x10 = 4-bit, 0x14 = 8-bit, 0x18 = 16-bit, 0x1C = 24-bit
    if start_offset + 8 > len(data):
        return None
    
    magic = struct.unpack('<I', data[start_offset:start_offset+4])[0]
    if magic != 0x00000010:  # Not a TIM file
        # Check for variations
        tim_markers = [0x10, 0x14, 0x18, 0x1C]
        if data[start_offset] not in tim_markers:
            return None
    
    # Parse TIM header
    version = data[start_offset]
    # Skip to image data
    # For TIM: header is 8 bytes for simple, more for CLUT
    
    return {
        "offset": start_offset,
        "version": hex(version),
        "type": ["4-bit", "8-bit", "16-bit", "24-bit"][version & 0x0F]
    }

def find_tim_images(data):
    """Find all TIM images in PS1 ROM"""
    tim_images = []
    # Search for TIM magic
    for i in range(0, min(len(data), 0x500000), 16):
        if data[i:i+4] == b'\x00\x00\x00\x10' or data[i:i+4] == b'\x10\x00\x00\x00':
            # Could be TIM - check if it looks like a valid image header
            if i + 32 < len(data):
                # Try to parse dimensions
                try:
                    # Skip 8 byte header, next 4 might be width/height
                    width = struct.unpack('<H', data[i+8:i+10])[0]
                    height = struct.unpack('<H', data[i+12:i+14])[0]
                    if 1 <= width <= 1024 and 1 <= height <= 1024:
                        tim_images.append({
                            "offset": i,
                            "width": width,
                            "height": height,
                            "header": data[i:i+16].hex()
                        })
                except:
                    pass
    
    return tim_images

# ============ SNES TILE DATA ============

def find_snes_tiles(data):
    """Find potential SNES tile data"""
    tiles = []
    
    # Look for common tile patterns
    # SNES tiles are often 8x8 or 16x16
    # Plane-dependent tile data often has repeating patterns
    
    for i in range(0x10000, 0x200000, 0x1000):
        if i + 64 > len(data):
            break
        
        chunk = data[i:i+64]
        
        # Look for 8x8 tile pattern (64 bytes per tile for 4bpp)
        # Count unique bytes - tiles have variety but not too much
        unique = len(set(chunk))
        
        if 10 < unique < 60:
            # Check if surrounding area looks like tile data
            surrounding = data[i:i+0x200]
            unique_surr = len(set(surrounding))
            
            if unique_surr > 30:
                tiles.append({
                    "offset": i,
                    "unique_bytes": unique,
                    "possible_tiles": unique_surr // 10
                })
    
    return tiles[:50]

# ============ CHRONO CROSS ============

def extract_chrono_cross_art():
    """Extract graphics from Chrono Cross"""
    print("Extracting Chrono Cross art...")
    
    cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
    data = read_rom(cc_path)
    
    # Find TIM images
    tims = find_tim_images(data)
    print(f"  Found {len(tims)} potential TIM images")
    
    # Save metadata
    import json
    with open(ART_DIR / "chrono_cross_tims.json", 'w') as f:
        json.dump(tims[:100], f, indent=2)
    
    # Extract some raw TIM data
    for i, tim in enumerate(tims[:20]):
        offset = tim["offset"]
        # Save 1KB of potential TIM data for analysis
        chunk = data[offset:offset+1024]
        with open(ART_DIR / f"chrono_cross_tim_{i:03d}_{hex(offset)}.bin", 'wb') as f:
            f.write(chunk)
    
    return len(tims)

# ============ RADICAL DREAMERS ============

def extract_radical_dreamers_art():
    """Extract graphics from Radical Dreamers"""
    print("Extracting Radical Dreamers art...")
    
    rd_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    data = read_rom(rd_path)
    
    # Find potential tile data
    tiles = find_snes_tiles(data)
    print(f"  Found {len(tiles)} potential tile regions")
    
    # Save metadata
    import json
    with open(ART_DIR / "radical_dreamers_tiles.json", 'w') as f:
        json.dump(tiles, f, indent=2)
    
    # Extract some raw tile data
    for i, tile in enumerate(tiles[:30]):
        offset = tile["offset"]
        # Save 2KB of potential tile data
        chunk = data[offset:offset+2048]
        with open(ART_DIR / f"radical_dreamers_tile_{i:03d}_{hex(offset)}.bin", 'wb') as f:
            f.write(chunk)
    
    # Look for character portrait data
    # Usually at specific offsets in SNES games
    portrait_offsets = [0x100000, 0x200000, 0x300000, 0x400000]
    
    for i, offset in enumerate(portrait_offsets):
        if offset < len(data):
            chunk = data[offset:offset+4096]
            with open(ART_DIR / f"radical_dreamers_portrait_{i}_{hex(offset)}.bin", 'wb') as f:
                f.write(chunk)
    
    return len(tiles)

# ============ CHRONO TRIGGER ============

def extract_chrono_trigger_art():
    """Extract graphics from Chrono Trigger"""
    print("Extracting Chrono Trigger art...")
    
    ct_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
    data = read_rom(ct_path)
    
    # Find potential tile data
    tiles = find_snes_tiles(data)
    print(f"  Found {len(tiles)} potential tile regions")
    
    # Save metadata
    import json
    with open(ART_DIR / "chrono_trigger_tiles.json", 'w') as f:
        json.dump(tiles, f, indent=2)
    
    # Extract some raw tile data
    for i, tile in enumerate(tiles[:30]):
        offset = tile["offset"]
        chunk = data[offset:offset+2048]
        with open(ART_DIR / f"chrono_trigger_tile_{i:03d}_{hex(offset)}.bin", 'wb') as f:
            f.write(chunk)
    
    # Character portrait areas (known from ROM maps)
    portrait_areas = [
        0x100000,  # Common area for character data
        0x200000,
        0x300000,
    ]
    
    for i, offset in enumerate(portrait_areas):
        if offset < len(data):
            chunk = data[offset:offset+8192]
            with open(ART_DIR / f"chrono_trigger_char_{i}_{hex(offset)}.bin", 'wb') as f:
                f.write(chunk)
    
    return len(tiles)

# ============ MAIN ============

if __name__ == "__main__":
    print("=" * 60)
    print("CHRONO SERIES GRAPHICS EXTRACTION")
    print("=" * 60)
    
    cc_count = extract_chrono_cross_art()
    rd_count = extract_radical_dreamers_art()
    ct_count = extract_chrono_trigger_art()
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"\nArt saved to: {ART_DIR}")
    print(f"  - Chrono Cross: {cc_count} TIM regions")
    print(f"  - Radical Dreamers: {rd_count} tile regions")
    print(f"  - Chrono Trigger: {ct_count} tile regions")
