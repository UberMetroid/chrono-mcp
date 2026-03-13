#!/usr/bin/env python3
"""
Fast comprehensive extraction - focus on known data regions
"""

import sys
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def find_strings_in_range(data, start, length, min_len=4):
    """Find strings in a specific range"""
    chunk = data[start:start+length]
    results = []
    current = []
    
    for i, byte in enumerate(chunk):
        if 32 <= byte <= 126:
            current.append(chr(byte))
        else:
            if len(current) >= min_len:
                results.append((start + i - len(current), ''.join(current)))
            current = []
    
    if len(current) >= min_len:
        results.append((start + length - len(current), ''.join(current)))
    
    return results

# ============ RADICAL DREAMERS ============

def extract_rd_everything():
    """Extract everything from Radical Dreamers"""
    rd_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    data = read_rom(rd_path)
    
    all_items = {}
    
    # Known text regions
    regions = [
        (0x150000, 0x10000, "menu"),
        (0x1C0000, 0x10000, "dialog1"),
        (0x1D0000, 0x10000, "dialog2"),
        (0x1E0000, 0x10000, "dialog3"),
    ]
    
    for start, length, name in regions:
        strings = find_strings_in_range(data, start, length, 4)
        
        # Filter meaningful strings
        for offset, text in strings:
            if len(text) > 5 and len(text) < 50:
                # Skip common junk
                if text.replace(' ', '').isalpha():
                    all_items[f"{name}_{offset:06x}"] = text
    
    return all_items

# ============ CHRONO TRIGGER ============

def extract_ct_everything():
    """Extract everything from Chrono Trigger"""
    ct_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
    data = read_rom(ct_path)
    
    all_items = {}
    
    # Known good regions
    regions = [
        (0x115000, 0x2000, "credits"),
        (0xE00000, 0x20000, "bank_e0"),
        (0xC00000, 0x10000, "bank_c0"),
    ]
    
    for start, length, name in regions:
        strings = find_strings_in_range(data, start, length, 4)
        
        for offset, text in strings:
            if len(text) > 5:
                if text.replace(' ', '').replace('.', '').isalpha():
                    all_items[f"{name}_{offset:06x}"] = text
    
    return all_items

# ============ CHRONO CROSS ============

def extract_cc_everything():
    """Extract everything from Chrono Cross"""
    cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
    data = read_rom(cc_path)
    
    all_items = {}
    
    # Known good regions
    regions = [
        (0x250000, 0x10000, "menu"),
        (0x300000, 0x20000, "text_a"),
        (0x320000, 0x20000, "text_b"),
    ]
    
    for start, length, name in regions:
        strings = find_strings_in_range(data, start, length, 5)
        
        for offset, text in strings:
            if len(text) > 8:
                if text.replace(' ', '').replace('.', '').isalpha():
                    all_items[f"{name}_{offset:06x}"] = text
    
    return all_items

# ============ MAIN ============

def main():
    import json
    
    print("Comprehensive extraction...")
    
    results = {
        "Radical Dreamers": extract_rd_everything(),
        "Chrono Trigger": extract_ct_everything(),
        "Chrono Cross": extract_cc_everything(),
    }
    
    # Count
    for game, data in results.items():
        print(f"  {game}: {len(data)} items")
    
    # Save
    with open(DATA_DIR / "comprehensive.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Saved to data/comprehensive.json")

if __name__ == "__main__":
    main()
