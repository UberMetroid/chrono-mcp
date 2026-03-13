#!/usr/bin/env python3
"""
Extract EVERY possible data structure from ROMs
"""

import sys
import struct
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

# ============ FIND STAT TABLES ============

def find_stat_tables(data):
    """Find potential character/enemy stat tables"""
    stats = []
    
    # Look for HP patterns (common RPG stats)
    # HP usually 2 bytes, little endian
    for i in range(0, min(len(data), 0x400000), 16):
        if i + 20 > len(data):
            break
            
        chunk = data[i:i+20]
        
        # Check for HP (0-9999), MP (0-999), then stats
        try:
            hp = struct.unpack('<H', chunk[0:2])[0]
            mp = struct.unpack('<H', chunk[2:4])[0]
            atk = struct.unpack('<H', chunk[4:6])[0]
            def_val = struct.unpack('<H', chunk[6:8])[0]
            
            # Valid stat ranges
            if 1 <= hp <= 9999 and 0 <= mp <= 999 and 0 <= atk <= 999 and 0 <= def_val <= 999:
                if hp > 10:  # Skip tiny values
                    stats.append({
                        "offset": hex(i),
                        "hp": hp,
                        "mp": mp,
                        "atk": atk,
                        "def": def_val,
                        "chunk": chunk[:16].hex()
                    })
        except:
            pass
    
    return stats[:100]

# ============ FIND ITEM TABLES ============

def find_item_tables(data):
    """Find item/weapon/armor data tables"""
    items = []
    
    # Items usually have: name pointer, price, effect, description
    # Look for price patterns (2 bytes, usually multiples of 10)
    
    for i in range(0, min(len(data), 0x300000), 32):
        if i + 32 > len(data):
            break
            
        chunk = data[i:i+32]
        
        # Look for price-like values
        for j in range(0, 24, 2):
            if j + 2 > len(chunk):
                break
            price = struct.unpack('<H', chunk[j:j+2])[0]
            
            # Common item prices
            if price in [10, 20, 30, 50, 100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000]:
                items.append({
                    "offset": hex(i + j),
                    "price": price,
                    "data": chunk[j:j+16].hex()
                })
                break
    
    return items[:50]

# ============ FIND POINTER TABLES ============

def find_pointer_tables(data):
    """Find pointer tables (addresses to other data)"""
    pointers = []
    
    # SNES pointers are typically 3 bytes (bank:offset)
    # Look for sequential offsets
    
    for i in range(0, min(len(data), 0x200000), 4):
        if i + 4 > len(data):
            break
            
        # Check for incrementing pattern
        p1 = data[i] | (data[i+1] << 8) | (data[i+2] << 16)
        p2 = data[i+4] | (data[i+5] << 8) | (data[i+6] << 16) if i + 7 < len(data) else 0
        
        # If they're close together (valid pointer table)
        if 0 < p2 - p1 < 10000 and p1 > 0x8000:
            pointers.append({
                "offset": hex(i),
                "ptr1": hex(p1),
                "ptr2": hex(p2)
            })
    
    return pointers[:30]

# ============ FIND PALETTE DATA ============

def find_palettes(data):
    """Find color palette data"""
    palettes = []
    
    # Palettes are sequences of 2-byte colors (5-5-5 or 6-6-6 RGB)
    for i in range(0, min(len(data), 0x400000), 2):
        if i + 32 > len(data):
            break
            
        # Check for valid palette colors
        colors = []
        valid = True
        
        for j in range(0, 32, 2):
            if i + j + 2 > len(data):
                break
            color = struct.unpack('<H', data[i+j:i+j+2])[0]
            
            # Check if valid RGB component ranges
            r = (color >> 10) & 0x1F
            g = (color >> 5) & 0x1F
            b = color & 0x1F
            
            if r > 31 or g > 31 or b > 31:
                valid = False
                break
            colors.append(color)
        
        if valid and len(colors) == 16:
            palettes.append({
                "offset": hex(i),
                "colors": colors[:8]
            })
    
    return palettes[:30]

# ============ FIND MAP DATA ============

def find_map_data(data):
    """Find tile map data"""
    maps = []
    
    # Map data often has repeating patterns of tile indices
    # Look for sequences of similar 16-bit values
    
    for i in range(0, min(len(data), 0x300000), 256):
        if i + 256 > len(data):
            break
            
        chunk = data[i:i+256]
        
        # Count tile-like values (0-1023 typical for SNES)
        tiles = 0
        for j in range(0, 256, 2):
            if j + 2 > len(chunk):
                break
            tile = struct.unpack('<H', chunk[j:j+2])[0]
            if tile < 2048:
                tiles += 1
        
        if tiles > 100:  # Mostly tile indices
            maps.append({
                "offset": hex(i),
                "tile_count": tiles,
                "sample": chunk[:32].hex()
            })
    
    return maps[:20]

# ============ EXTRACT ALL ============

def extract_all_structures():
    """Extract all data structures"""
    
    results = {}
    
    # Radical Dreamers
    print("Extracting Radical Dreamers structures...")
    rd_path = BASE_DIR / "Radical Dreamers/BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    rd = read_rom(rd_path)
    
    results["Radical Dreamers"] = {
        "stat_tables": find_stat_tables(rd),
        "item_tables": find_item_tables(rd),
        "pointer_tables": find_pointer_tables(rd),
        "palettes": find_palettes(rd),
        "map_data": find_map_data(rd),
    }
    
    # Chrono Trigger
    print("Extracting Chrono Trigger structures...")
    ct_path = BASE_DIR / "Chrono Trigger/Chrono Trigger (USA).sfc"
    ct = read_rom(ct_path)
    
    results["Chrono Trigger"] = {
        "stat_tables": find_stat_tables(ct),
        "item_tables": find_item_tables(ct),
        "pointer_tables": find_pointer_tables(ct),
        "palettes": find_palettes(ct),
        "map_data": find_map_data(ct),
    }
    
    # Save
    import json
    with open(DATA_DIR / "data_structures.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults:")
    for game, data in results.items():
        print(f"\n{game}:")
        for key, items in data.items():
            print(f"  {key}: {len(items)} found")

if __name__ == "__main__":
    extract_all_structures()
