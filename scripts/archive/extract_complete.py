#!/usr/bin/env python3
"""
COMPLETE extraction - literally EVERYTHING from the ROMs
"""

import sys
from pathlib import Path
import struct

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def find_all_strings(data, min_len=3):
    """Find EVERY string in the data"""
    results = []
    current = []
    
    for i, b in enumerate(data):
        if 32 <= b <= 126:
            current.append((i, chr(b)))
        else:
            if len(current) >= min_len:
                start = current[0][0]
                text = ''.join(c for _, c in current)
                results.append((start, text))
            current = []
    
    if len(current) >= min_len:
        results.append((current[0][0], ''.join(c for _, c in current)))
    
    return results

def find_data_patterns(data):
    """Find all interesting data patterns"""
    patterns = {}
    
    # Common game data signatures
    signatures = [
        (b'SAVE', 'save_data'),
        (b'SLOT', 'save_slot'),
        (b'NAME', 'name_field'),
        (b'HP', 'hp_stat'),
        (b'MP', 'mp_stat'),
        (b'LV', 'level'),
        (b'EXP', 'experience'),
        (b'GOLD', 'gold'),
        (b'GIL', 'gil'),
        (b'ATK', 'attack'),
        (b'DEF', 'defense'),
        (b'MAG', 'magic'),
        (b'SPD', 'speed'),
        (b'ITEM', 'item'),
        (b'KEY', 'key_item'),
        (b'WEAPON', 'weapon'),
        (b'ARMOR', 'armor'),
        (b'ACCESSORY', 'accessory'),
    ]
    
    for sig, name in signatures:
        count = data.count(sig)
        if count > 0:
            pos = data.find(sig)
            patterns[name] = {"count": count, "first_offset": hex(pos)}
    
    return patterns

def analyze_rom_structure(data):
    """Analyze ROM structure and find all regions"""
    info = {
        "size": len(data),
        "size_mb": len(data) / (1024*1024),
    }
    
    # Scan for data-rich regions
    regions = []
    for i in range(0, min(len(data), 0x400000), 0x10000):
        chunk = data[i:i+0x10000]
        
        # Count printable chars
        printable = sum(1 for b in chunk if 32 <= b <= 126)
        nulls = chunk.count(0x00)
        unique = len(set(chunk))
        
        if printable > 100:  # Has text
            regions.append({
                "offset": hex(i),
                "printable": printable,
                "unique_bytes": unique,
                "nulls": nulls
            })
    
    return {"info": info, "regions": regions}

# ============ COMPLETE EXTRACTION ============

def extract_complete_rd():
    """Extract EVERYTHING from Radical Dreamers"""
    rd_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    print(f"Loading Radical Dreamers ({Path(rd_path).stat().st_size / 1024 / 1024:.1f}MB)...")
    data = read_rom(rd_path)
    
    result = {
        "structure": analyze_rom_structure(data),
        "patterns": find_data_patterns(data),
    }
    
    # Extract ALL strings (grouped by length)
    print("  Finding all strings...")
    strings = find_all_strings(data, 4)
    
    # Categorize
    short = []    # 4-8 chars
    medium = []   # 9-20
    long = []     # 21+
    
    for offset, text in strings:
        if len(text) <= 8:
            short.append({"offset": hex(offset), "text": text})
        elif len(text) <= 20:
            medium.append({"offset": hex(offset), "text": text})
        else:
            long.append({"offset": hex(offset), "text": text[:100]})
    
    result["strings"] = {
        "short": short[:500],
        "medium": medium[:500], 
        "long": long[:1000]
    }
    result["string_counts"] = {
        "total": len(strings),
        "short": len(short),
        "medium": len(medium),
        "long": len(long)
    }
    
    # Find all character/location/tech mentions
    print("  Categorizing...")
    
    categories = {
        "characters": [],
        "locations": [],
        "items": [],
        "actions": [],
        "elements": []
    }
    
    # Search for key terms in the strings
    search_terms = {
        "characters": ["kid", "magil", "serge", "lynx", "harle", "viper", "guard", "ghost"],
        "locations": ["manor", "forest", "cave", "sea", "beach", "island", "castle", "tower"],
        "items": ["sword", "shield", "potion", "key", "treasure", "chest", "gem", "crystal"],
        "actions": ["attack", "defend", "magic", "heal", "use", "talk", "open", "close"],
        "elements": ["fire", "ice", "wind", "thunder", "water", "earth", "light", "dark"]
    }
    
    for cat, terms in search_terms.items():
        for offset, text in strings:
            lower = text.lower()
            for term in terms:
                if term in lower:
                    categories[cat].append({"offset": hex(offset), "text": text[:50]})
                    break
    
    # Deduplicate
    for cat in categories:
        seen = set()
        unique = []
        for item in categories[cat]:
            if item["text"] not in seen:
                seen.add(item["text"])
                unique.append(item)
        categories[cat] = unique[:200]
    
    result["categories"] = categories
    
    return result

def extract_complete_ct():
    """Extract EVERYTHING from Chrono Trigger"""
    ct_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
    print(f"Loading Chrono Trigger ({Path(ct_path).stat().st_size / 1024 / 1024:.1f}MB)...")
    data = read_rom(ct_path)
    
    result = {
        "structure": analyze_rom_structure(data),
        "patterns": find_data_patterns(data),
    }
    
    # Even though text is compressed, we can find structure
    print("  Analyzing structure...")
    
    # Look for uncompressed data
    strings = find_all_strings(data, 5)
    
    # Categorize
    result["uncompressed_strings"] = [
        {"offset": hex(o), "text": t[:60]} for o, t in strings[:1000]
    ]
    
    # Find character mentions in credits
    print("  Extracting credits...")
    credits_data = data[0x115000:0x116000]
    cred_strings = find_all_strings(credits_data, 4)
    result["credits"] = [{"offset": hex(0x115000 + o), "text": t} for o, t in cred_strings]
    
    return result

def extract_complete_cc():
    """Extract EVERYTHING from Chrono Cross"""
    cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
    print(f"Loading Chrono Cross ({Path(cc_path).stat().st_size / 1024 / 1024:.1f}MB)...")
    data = read_rom(cc_path)
    
    result = {
        "structure": analyze_rom_structure(data),
        "patterns": find_data_patterns(data),
    }
    
    # Extract all strings from key regions
    print("  Extracting strings from text regions...")
    
    all_strings = []
    regions = [
        (0x250000, 0x100000, "text_area_1"),
        (0x350000, 0x100000, "text_area_2"),
    ]
    
    for start, size, name in regions:
        strings = find_all_strings(data[start:start+size], 5)
        for offset, text in strings:
            if 5 < len(text) < 80:
                all_strings.append({"region": name, "offset": hex(start + offset), "text": text})
    
    # Deduplicate
    seen = set()
    unique = []
    for s in all_strings:
        if s["text"] not in seen:
            seen.add(s["text"])
            unique.append(s)
    
    result["strings"] = unique[:5000]
    
    return result

# ============ MAIN ============

def main():
    import json
    
    print("=" * 60)
    print("COMPLETE EXTRACTION")
    print("=" * 60)
    
    results = {}
    
    results["Radical Dreamers"] = extract_complete_rd()
    print(f"  Done! {results['Radical Dreamers']['string_counts']['total']} strings found")
    
    results["Chrono Trigger"] = extract_complete_ct()
    print("  Done!")
    
    results["Chrono Cross"] = extract_complete_cc()
    print("  Done!")
    
    # Save
    print("\nSaving...")
    with open(DATA_DIR / "complete_extraction.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSaved to data/complete_extraction.json")
    print(f"Size: {Path(DATA_DIR / 'complete_extraction.json').stat().st_size / 1024 / 1024:.1f}MB")

if __name__ == "__main__":
    main()
