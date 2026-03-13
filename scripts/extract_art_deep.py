#!/usr/bin/env python3
"""
Deep graphics extraction - find sprites, portraits, backgrounds
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

# ============ BETTER SNES GRAPHIC FINDER ============

def find_snes_graphic_regions(data):
    """Find SNES graphic data using multiple heuristics"""
    regions = []
    
    # Common SNES palette markers (colors often start with these)
    # Look for 16-color palette blocks (32 bytes of palette data)
    # Palette data usually has gradual color transitions
    
    # Check known sprite banks (from ROM maps)
    sprite_banks = []
    for bank in range(0x10, 0x40):
        addr = bank * 0x10000
        if addr < len(data):
            # Read a chunk and check for graphic-like patterns
            chunk = data[addr:addr+0x100]
            
            # Count null bytes (compressed or empty)
            nulls = chunk.count(0x00)
            
            # Graphic data typically has variety
            if nulls < 80:
                # Check for 4bpp tile patterns (repeating every 0x40 bytes)
                variety = len(set(chunk[:0x40]))
                if variety > 20:
                    sprite_banks.append({
                        "bank": hex(bank * 0x10000),
                        "variety": variety,
                        "nulls": nulls,
                        "sample": chunk[:32].hex()
                    })
    
    return sprite_banks

# ============ CHRONO TRIGGER SPECIFIC ============

def extract_ct_deep():
    """Deep extract Chrono Trigger graphics"""
    print("Deep extracting Chrono Trigger graphics...")
    
    ct_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
    data = read_rom(ct_path)
    
    regions = find_snes_graphic_regions(data)
    
    # Save detailed region info
    import json
    with open(ART_DIR / "chrono_trigger_graphic_regions.json", 'w') as f:
        json.dump(regions, f, indent=2)
    
    # Extract from promising banks
    for i, region in enumerate(regions[:20]):
        bank = int(region["bank"].replace("0x", ""), 16)
        chunk = data[bank:bank+16384]  # 16KB chunks
        with open(ART_DIR / f"chrono_trigger_sprite_bank_{i}_{region['bank']}.bin", 'wb') as f:
            f.write(chunk)
    
    # Known character art locations from Chrono Trigger ROM map
    # Character sprites typically in these areas:
    char_areas = [
        0x1C8000,  # Common sprite area
        0x258000,
        0x268000,
        0x2D8000,
        0x318000,
    ]
    
    for i, offset in enumerate(char_areas):
        if offset < len(data):
            chunk = data[offset:offset+16384]
            with open(ART_DIR / f"chrono_trigger_char_art_{i}_{hex(offset)}.bin", 'wb') as f:
                f.write(chunk)
    
    # Battle backgrounds
    battle_areas = [0x3C0000, 0x3D0000, 0x3E0000]
    for i, offset in enumerate(battle_areas):
        if offset < len(data):
            chunk = data[offset:offset+16384]
            with open(ART_DIR / f"chrono_trigger_battle_bg_{i}_{hex(offset)}.bin", 'wb') as f:
                f.write(chunk)
    
    return len(regions)

# ============ RADICAL DREAMERS SPECIFIC ============

def extract_rd_deep():
    """Deep extract Radical Dreamers graphics"""
    print("Deep extracting Radical Dreamers graphics...")
    
    rd_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    data = read_rom(rd_path)
    
    regions = find_snes_graphic_regions(data)
    
    import json
    with open(ART_DIR / "radical_dreamers_graphic_regions.json", 'w') as f:
        json.dump(regions, f, indent=2)
    
    # Extract from banks
    for i, region in enumerate(regions[:20]):
        bank = int(region["bank"].replace("0x", ""), 16)
        chunk = data[bank:bank+16384]
        with open(ART_DIR / f"radical_dreamers_sprite_bank_{i}_{region['bank']}.bin", 'wb') as f:
            f.write(chunk)
    
    # Character art (Kid, Magil, etc)
    char_areas = [0x180000, 0x1A0000, 0x1C0000, 0x1E0000]
    for i, offset in enumerate(char_areas):
        if offset < len(data):
            chunk = data[offset:offset+16384]
            with open(ART_DIR / f"radical_dreamers_char_{i}_{hex(offset)}.bin", 'wb') as f:
                f.write(chunk)
    
    return len(regions)

# ============ CHRONO CROSS SPECIFIC ============

def extract_cc_deep():
    """Deep extract Chrono Cross graphics"""
    print("Deep extracting Chrono Cross graphics...")
    
    cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
    data = read_rom(cc_path)
    
    # PS1 uses TIM format - find more specific ones
    tim_files = []
    
    # Search with better TIM detection
    for i in range(0, min(len(data), 0x600000), 4):
        if i + 28 > len(data):
            break
            
        # Check for TIM header (various types)
        possible_tim = False
        
        # Type 1 TIM: 4-bit (16 colors)
        if data[i:i+4] == b'\x00\x00\x00\x10' or data[i:i+4] == b'\x10\x00\x00\x00':
            possible_tim = True
        # Type 2 TIM: 8-bit (256 colors) 
        elif data[i:i+4] == b'\x00\x00\x00\x14' or data[i:i+4] == b'\x14\x00\x00\x00':
            possible_tim = True
        # Type 3 TIM: 16-bit (65536 colors)
        elif data[i:i+4] == b'\x00\x00\x00\x18' or data[i:i+4] == b'\x18\x00\x00\x00':
            possible_tim = True
        # Type 4 TIM: 24-bit
        elif data[i:i+4] == b'\x00\x00\x00\x1C' or data[i:i+4] == b'\x1C\x00\x00\x00':
            possible_tim = True
            
        if possible_tim:
            # Try to get image info
            try:
                # Skip header, get dimensions
                if data[i] in [0x10, 0x14, 0x18, 0x1C]:
                    width = struct.unpack('<H', data[i+8:i+10])[0]
                    height = struct.unpack('<H', data[i+12:i+14])[0]
                    if 1 <= width <= 2048 and 1 <= height <= 2048:
                        tim_files.append({
                            "offset": i,
                            "type": hex(data[i]),
                            "width": width,
                            "height": height,
                            "data_size": len(data[i:i+100])
                        })
            except:
                pass
    
    import json
    with open(ART_DIR / "chrono_cross_tim_detailed.json", 'w') as f:
        json.dump(tim_files[:100], f, indent=2)
    
    # Extract actual TIM data (larger chunks)
    for i, tim in enumerate(tim_files[:30]):
        offset = tim["offset"]
        # Extract 32KB - typical TIM size
        chunk = data[offset:offset+32768]
        with open(ART_DIR / f"chrono_cross_tim_full_{i}_{hex(offset)}.tim", 'wb') as f:
            f.write(chunk)
    
    # Also look for character portrait data
    # These are typically at known offsets
    portrait_offsets = [0x200000, 0x300000, 0x400000, 0x500000]
    
    for i, offset in enumerate(portrait_offsets):
        if offset < len(data):
            chunk = data[offset:offset+65536]
            with open(ART_DIR / f"chrono_cross_portrait_{i}_{hex(offset)}.bin", 'wb') as f:
                f.write(chunk)
    
    return len(tim_files)

if __name__ == "__main__":
    print("=" * 60)
    print("DEEP GRAPHICS EXTRACTION")
    print("=" * 60)
    
    ct = extract_ct_deep()
    rd = extract_rd_deep()
    cc = extract_cc_deep()
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"  Chrono Trigger: {ct} graphic regions")
    print(f"  Radical Dreamers: {rd} graphic regions")
    print(f"  Chrono Cross: {cc} TIM images")
