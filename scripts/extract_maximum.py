#!/usr/bin/env python3
"""
ABSOLUTE MAXIMUM extraction - dump EVERYTHING
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_DIR.mkdir(exist_ok=True)

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

# ============ DUMP EVERY REGION ============

def dump_all_regions():
    """Dump ALL interesting regions as binary files"""
    
    # Radical Dreamers - dump all known text regions
    print("Dumping Radical Dreamers regions...")
    rd_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    rd = read_rom(rd_path)
    
    rd_regions = [
        (0x100000, 0x40000, "rd_bank_10"),
        (0x140000, 0x40000, "rd_bank_14"),
        (0x180000, 0x40000, "rd_bank_18"),
        (0x1C0000, 0x40000, "rd_text_dialog"),
        (0x200000, 0x40000, "rd_bank_20"),
    ]
    
    for start, size, name in rd_regions:
        if start < len(rd):
            actual_size = min(size, len(rd) - start)
            chunk = rd[start:start + actual_size]
            with open(RAW_DIR / f"{name}.bin", 'wb') as f:
                f.write(chunk)
            print(f"  Dumped {name}: {actual_size} bytes")
    
    # Chrono Trigger
    print("\nDumping Chrono Trigger regions...")
    ct_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
    ct = read_rom(ct_path)
    
    ct_regions = [
        (0x100000, 0x40000, "ct_bank_10"),
        (0xC00000, 0x40000, "ct_bank_c0"),
        (0xD00000, 0x40000, "ct_bank_d0"),
        (0xE00000, 0x40000, "ct_bank_e0"),
        (0x115000, 0x2000, "ct_credits"),
    ]
    
    for start, size, name in ct_regions:
        if start < len(ct):
            actual_size = min(size, len(ct) - start)
            chunk = ct[start:start + actual_size]
            with open(RAW_DIR / f"{name}.bin", 'wb') as f:
                f.write(chunk)
            print(f"  Dumped {name}: {actual_size} bytes")
    
    # Chrono Cross - lots of regions
    print("\nDumping Chrono Cross regions...")
    cc_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
    cc = read_rom(cc_path)
    
    cc_regions = [
        (0x250000, 0x10000, "cc_menu"),
        (0x260000, 0x10000, "cc_text_1"),
        (0x270000, 0x10000, "cc_text_2"),
        (0x280000, 0x10000, "cc_text_3"),
        (0x300000, 0x20000, "cc_strings_1"),
        (0x320000, 0x20000, "cc_strings_2"),
        (0x340000, 0x20000, "cc_strings_3"),
        (0x360000, 0x20000, "cc_strings_4"),
        (0x380000, 0x20000, "cc_strings_5"),
        (0x3A0000, 0x20000, "cc_strings_6"),
    ]
    
    for start, size, name in cc_regions:
        if start < len(cc):
            actual_size = min(size, len(cc) - start)
            chunk = cc[start:start + actual_size]
            with open(RAW_DIR / f"{name}.bin", 'wb') as f:
                f.write(chunk)
            print(f"  Dumped {name}: {actual_size} bytes")

# ============ SCAN FOR ABSOLUTELY EVERYTHING ============

def scan_everything():
    """Scan for literally every piece of information"""
    
    results = {}
    
    for game_name, rom_path in [
        ("Radical Dreamers", BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"),
        ("Chrono Trigger", BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"),
        ("Chrono Cross", BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"),
    ]:
        print(f"Scanning {game_name}...")
        
        if not rom_path.exists():
            continue
            
        data = read_rom(rom_path)
        
        # Find absolutely every unique string (including short ones)
        strings = []
        current = []
        
        for i, b in enumerate(data):
            if 32 <= b <= 126:
                current.append(chr(b))
            else:
                if len(current) >= 2:  # Even 2-char strings
                    strings.append(''.join(current))
                current = []
        
        # Count by length
        length_buckets = {
            "2": 0, "3": 0, "4": 0, "5-10": 0, "11-20": 0, "21-50": 0, "50+": 0
        }
        
        for s in strings:
            l = len(s)
            if l == 2:
                length_buckets["2"] += 1
            elif l == 3:
                length_buckets["3"] += 1
            elif l == 4:
                length_buckets["4"] += 1
            elif l <= 10:
                length_buckets["5-10"] += 1
            elif l <= 20:
                length_buckets["11-20"] += 1
            elif l <= 50:
                length_buckets["21-50"] += 1
            else:
                length_buckets["50+"] += 1
        
        results[game_name] = {
            "total_strings": len(strings),
            "by_length": length_buckets,
            "unique_strings": len(set(strings)),
        }
    
    return results

# ============ MAIN ============

if __name__ == "__main__":
    print("=" * 60)
    print("MAXIMUM EXTRACTION")
    print("=" * 60)
    
    # Dump all regions
    dump_all_regions()
    
    # Scan for everything
    print("\n" + "=" * 60)
    results = scan_everything()
    
    # Save
    with open(DATA_DIR / "string_stats.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nString statistics:")
    for game, stats in results.items():
        print(f"\n{game}:")
        print(f"  Total: {stats['total_strings']}")
        print(f"  Unique: {stats['unique_strings']}")
        print(f"  By length: {stats['by_length']}")
    
    # Count raw files
    raw_count = len(list(RAW_DIR.glob("*.bin")))
    print(f"\nDumped {raw_count} binary region files")
