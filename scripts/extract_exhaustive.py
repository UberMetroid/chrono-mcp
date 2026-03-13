#!/usr/bin/env python3
"""
EXHAUSTIVE extraction - EVERY possible piece of data
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

# ============ FIND ABSOLUTELY EVERYTHING ============

def find_all_offsets(data, pattern):
    """Find ALL occurrences of a pattern"""
    offsets = []
    pos = 0
    while True:
        pos = data.find(pattern, pos)
        if pos == -1:
            break
        offsets.append(pos)
        pos += 1
    return offsets

def scan_all_2byte_patterns(data):
    """Find all 2-byte patterns that repeat"""
    from collections import Counter
    
    # Sample every 1000 bytes to not kill performance
    patterns = []
    for i in range(0, len(data) - 2, 2):
        patterns.append(data[i:i+2])
    
    counter = Counter(patterns)
    # Return most common
    return [{"pattern": p.hex(), "count": c} for p, c in counter.most_common(100)]

def find_number_sequences(data):
    """Find sequences that look like game numbers (stats, etc)"""
    numbers = []
    
    for i in range(0, min(len(data), 0x400000), 100):
        # Check for common stat values
        for offset in [i, i+1, i+2, i+3]:
            if offset + 4 > len(data):
                break
            
            # Try as 16-bit little endian
            val16 = struct.unpack('<H', data[offset:offset+2])[0]
            
            # Common game values
            if 1 <= val16 <= 9999 and val16 not in [256, 512, 1024, 2048, 4096]:
                # Check if this looks like a stat (often near other stats)
                nearby = data[max(0,offset-10):offset+20]
                if nearby.count(0) > 5:  # Has some zeros around
                    numbers.append({"offset": offset, "value": val16, "type": "u16_le"})
    
    return numbers[:50]

def extract_all_named_sections(data):
    """Extract all named sections of the ROM"""
    sections = []
    
    # Look for section markers
    markers = [
        (b'DATA', 'data'),
        (b'CODE', 'code'),
        (b'BSS', 'bss'),
        (b'HEADER', 'header'),
        (b'GRAPHICS', 'graphics'),
        (b'SPRITES', 'sprites'),
        (b'SOUND', 'sound'),
        (b'MUSIC', 'music'),
        (b'FONT', 'font'),
        (b'PALETTE', 'palette'),
        (b'MAP', 'map'),
        (b'LEVEL', 'level'),
        (b'ENEMY', 'enemy'),
        (b'ITEM', 'item'),
        (b'SCRIPT', 'script'),
        (b'DIALOG', 'dialog'),
    ]
    
    for marker, name in markers:
        offsets = find_all_offsets(data, marker)
        if offsets:
            sections.append({"name": name, "marker": marker.decode(), "offsets": [hex(o) for o in offsets[:10]]})
    
    return sections

def analyze_rom_bytes(data):
    """Analyze byte distribution"""
    from collections import Counter
    
    # Overall distribution
    total = len(data)
    
    # Sample regions
    regions_analysis = []
    
    for start in range(0, min(len(data), 0x400000), 0x100000):
        chunk = data[start:start+0x100000]
        
        # Count byte types
        nulls = chunk.count(0)
        printable = sum(1 for b in chunk if 32 <= b <= 126)
        high = sum(1 for b in chunk if b > 127)
        
        regions_analysis.append({
            "offset": hex(start),
            "null_pct": round(nulls / len(chunk) * 100, 1),
            "printable_pct": round(printable / len(chunk) * 100, 1),
            "high_pct": round(high / len(chunk) * 100, 1),
        })
    
    return regions_analysis

# ============ EXTRACT ============

def extract_exhaustive(game_name, rom_path):
    """Exhaustive extraction for one game"""
    print(f"Exhaustive: {game_name}...")
    
    data = read_rom(rom_path)
    size_mb = len(data) / 1024 / 1024
    
    result = {
        "file_size_mb": round(size_mb, 2),
        "byte_analysis": analyze_rom_bytes(data),
        "named_sections": extract_all_named_sections(data),
        "common_2byte_patterns": scan_all_2byte_patterns(data[:1000000]),
    }
    
    # Find all known game terms
    print(f"  Searching for game terms...")
    
    terms = {
        "names": ["CRONO", "LUCCA", "MARLE", "FROG", "ROBO", "AYLA", "MAGUS", "KID", "HARLE", "LYNX", "SERGE"],
        "places": ["CASTLE", "TOWER", "VILLAGE", "FOREST", "CAVE", "TEMPLE", "RUINS", "MANOR"],
        "items": ["SWORD", "SHIELD", "POTION", "ETHER", "ELIXIR", "KEY", "MAP", "TREASURE"],
        "techs": ["FIRE", "ICE", "THUNDER", "WATER", "CURE", "HEAL", "SLASH", "BLITZ"],
    }
    
    term_results = {}
    for category, words in terms.items():
        term_results[category] = []
        for word in words:
            offsets = find_all_offsets(data, word.encode())
            if offsets:
                term_results[category].append({"term": word, "count": len(offsets), "first": hex(offsets[0])})
    
    result["game_terms"] = term_results
    
    # Find any executable code patterns
    code_patterns = find_all_offsets(data, b'\x00\x00\x00\x00')
    result["null_4byte_blocks"] = len(code_patterns)
    
    return result

# ============ MAIN ============

def main():
    import json
    
    print("=" * 60)
    print("EXHAUSTIVE EXTRACTION")
    print("=" * 60)
    
    results = {}
    
    # Radical Dreamers
    rd_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    results["Radical Dreamers"] = extract_exhaustive("Radical Dreamers", rd_path)
    
    # Chrono Trigger  
    ct_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
    results["Chrono Trigger"] = extract_exhaustive("Chrono Trigger", ct_path)
    
    # Chrono Cross
    cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
    results["Chrono Cross"] = extract_exhaustive("Chrono Cross", cc_path)
    
    # Save
    with open(DATA_DIR / "exhaustive.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSaved to data/exhaustive.json")
    
    # Print summary
    for game, data in results.items():
        print(f"\n{game}:")
        print(f"  Size: {data['file_size_mb']}MB")
        terms = data.get('game_terms', {})
        for cat, items in terms.items():
            print(f"  {cat}: {len(items)} terms found")

if __name__ == "__main__":
    main()
