#!/usr/bin/env python3
"""
Deep extraction - find EVERYTHING in the ROMs
"""

import sys
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def find_all_text_patterns(data, min_count=2):
    """Find ALL text patterns that appear multiple times"""
    from collections import Counter
    
    # Find all 4+ char sequences
    strings = []
    for i in range(len(data) - 4):
        chunk = data[i:i+4]
        # Check if all bytes are printable ASCII
        if all(32 <= b <= 126 for b in chunk):
            strings.append(chunk.decode('ascii'))
    
    # Count occurrences
    counter = Counter(strings)
    
    # Filter and return
    return {k: v for k, v in counter.items() if v >= min_count and len(k) >= 5}

# ============ RADICAL DREAMERS DEEP ============

def extract_rd_deep():
    """Deep extract Radical Dreamers"""
    print("Deep extracting Radical Dreamers...")
    
    rd_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    rd_data = read_rom(rd_path)
    
    # Find ALL repeated strings
    repeated = find_all_text_patterns(rd_data, min_count=3)
    
    # Categorize
    important = {}
    for text, count in sorted(repeated.items(), key=lambda x: -x[1]):
        upper = text.upper()
        
        # Character names
        if any(n in upper for n in ['KID', 'MAGIL', 'SERGE', 'FLAME', 'LYNX', 'VIPER', 'GUARD']):
            important[f"CHAR_{text}"] = count
        
        # Actions/verbs
        elif any(n in upper for n in ['SAY', 'TELL', 'LOOK', 'WALK', 'RUN', 'TURN', 'TAKE', 'USE', 'GET']):
            important[f"VERB_{text}"] = count
        
        # Places
        elif any(n in upper for n in ['MANOR', 'CASTLE', 'FOREST', 'SEA', 'CAVE', 'BEACH', 'ISLAND']):
            important[f"LOC_{text}"] = count
        
        # Items
        elif any(n in upper for n in ['ITEM', 'KEY', 'GATE', 'DOOR', 'BOX', 'CHEST']):
            important[f"ITEM_{text}"] = count
        
        # Techs
        elif any(n in upper for n in ['FIRE', 'ICE', 'WIND', 'THUNDER', 'WATER', 'HEAL']):
            important[f"TECH_{text}"] = count
    
    return important

# ============ CHRONO TRIGGER DEEP ============

def extract_ct_deep():
    """Deep extract Chrono Trigger"""
    print("Deep extracting Chrono Trigger...")
    
    ct_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
    ct_data = read_rom(ct_path)
    
    repeated = find_all_text_patterns(ct_data, min_count=2)
    
    important = {}
    for text, count in sorted(repeated.items(), key=lambda x: -x[1]):
        upper = text.upper()
        
        if any(n in upper for n in ['CRONO', 'LUCCA', 'MARLE', 'FROG', 'ROBO', 'AYLA', 'MAGUS']):
            important[f"CHAR_{text}"] = count
        
        elif any(n in upper for n in ['GATE', 'TIME', 'LAVOS', 'KING', 'QUEEN']):
            important[f"STORY_{text}"] = count
        
        elif any(n in upper for n in ['FIRE', 'ICE', 'THUNDER', 'WATER', 'CURE', 'HEAL']):
            important[f"ELEM_{text}"] = count
    
    return important

# ============ CHRONO CROSS DEEP ============

def extract_cc_deep():
    """Deep extract Chrono Cross"""
    print("Deep extracting Chrono Cross...")
    
    cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
    cc_data = read_rom(cc_path)
    
    repeated = find_all_text_patterns(cc_data, min_count=3)
    
    important = {}
    for text, count in sorted(repeated.items(), key=lambda x: -x[1]):
        upper = text.upper()
        
        if any(n in upper for n in ['SERGE', 'KID', 'HARLE', 'LYNX', 'KORIS', 'MACH', 'ZOAH']):
            important[f"CHAR_{text}"] = count
        
        elif any(n in upper for n in ['HOME', 'ARGELO', 'MARBULE', 'DEAD', 'GULDOVE']):
            important[f"LOC_{text}"] = count
        
        elif any(n in upper for n in ['ELEM', 'FIRE', 'ICE', 'WIND', 'WATER']):
            important[f"ELEM_{text}"] = count
    
    return important

# ============ SAVE DATA STRUCTURE ============

def find_save_data(data):
    """Find save data structure"""
    # Look for save file signatures
    # Common: "SAVE", "SLOT", or checksum patterns
    
    save_areas = []
    
    # Search for common save patterns
    for i in range(0, min(len(data), 0x200000), 0x1000):
        chunk = data[i:i+128]
        
        # Look for patterns that might be save data
        # Like character stats, money, etc.
        
        # Check for repeating patterns (common in empty save slots)
        unique = len(set(chunk))
        
        if unique > 10 and unique < 50:
            save_areas.append({
                "offset": i,
                "unique": unique,
                "sample": chunk[:32].hex()
            })
    
    return save_areas[:20]

# ============ MAIN ============

def main():
    import json
    
    print("=" * 60)
    print("DEEP DATA EXTRACTION")
    print("=" * 60)
    
    results = {}
    
    results["Radical Dreamers"] = extract_rd_deep()
    print(f"  Found {len(results['Radical Dreamers'])} important patterns")
    
    results["Chrono Trigger"] = extract_ct_deep()
    print(f"  Found {len(results['Chrono Trigger'])} important patterns")
    
    results["Chrono Cross"] = extract_cc_deep()
    print(f"  Found {len(results['Chrono Cross'])} important patterns")
    
    # Save
    with open(DATA_DIR / "deep_data.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Also look for save data
    print("\nSearching for save data structures...")
    
    rd_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    rd_data = read_rom(rd_path)
    saves = find_save_data(rd_data)
    
    with open(DATA_DIR / "save_data.json", 'w') as f:
        json.dump(saves, f, indent=2)
    
    print(f"  Found {len(saves)} potential save areas")
    
    print("\nSaved to data/deep_data.json and data/save_data.json")

if __name__ == "__main__":
    main()
