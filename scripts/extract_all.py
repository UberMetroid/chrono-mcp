#!/usr/bin/env python3
"""
Comprehensive Data Extraction from Chrono Series ROMs
Saves structured data for MCP use
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def find_all_strings(data, min_len=3):
    """Find all ASCII strings"""
    results = []
    current = []
    for i, byte in enumerate(data):
        if 32 <= byte <= 126:
            current.append((i, chr(byte)))
        else:
            if len(current) >= min_len:
                start = current[0][0]
                text = ''.join(c for _, c in current)
                results.append((start, text))
            current = []
    if len(current) >= min_len:
        results.append((current[0][0], ''.join(c for _, c in current)))
    return results

def find_bytes(data, pattern):
    """Find all occurrences of pattern"""
    positions = []
    offset = 0
    while True:
        pos = data.find(pattern, offset)
        if pos == -1:
            break
        positions.append(pos)
        offset = pos + 1
    return positions

def extract_radical_dreamers():
    """Extract everything from Radical Dreamers"""
    print("Extracting Radical Dreamers...")
    rom_path = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
    data = read_rom(rom_path)
    
    result = {
        "game": "Radical Dreamers",
        "version": "Demiforce v1.4 translation",
        "size": len(data),
        "header": data[0xFFC0:0xFFC0+32].decode('ascii', errors='ignore').strip('\x00'),
    }
    
    # Find all strings
    strings = find_all_strings(data, 4)
    result["total_strings"] = len(strings)
    
    # Categorize strings
    characters = {
        "Kid": find_bytes(data, b'Kid'),
        "Magil": find_bytes(data, b'Magil'),
        "Serge": find_bytes(data, b'Serge'),
        "Frozen": find_bytes(data, b'Frozen'),
        "Flame": find_bytes(data, b'Flame'),
        "Lynx": find_bytes(data, b'Lynx'),
        "Viper": find_bytes(data, b'Viper'),
        "Guards": find_bytes(data, b'Guards'),
    }
    result["character_references"] = {k: len(v) for k, v in characters.items()}
    
    # Locations
    locations = {
        "Viper Manor": find_bytes(data, b'Manor'),
        "Forest": find_bytes(data, b'Forest'),
        "Sea": find_bytes(data, b'Sea'),
        "Cave": find_bytes(data, b'Cave'),
        "Beach": find_bytes(data, b'Beach'),
        "Castle": find_bytes(data, b'Castle'),
    }
    result["location_references"] = {k: len(v) for k, v in locations.items()}
    
    # Menu text regions
    menu_region = data[0x150000:0x160000]
    menu_strings = find_all_strings(menu_region, 3)
    result["menu_strings"] = [{"offset": hex(s[0] + 0x150000), "text": s[1][:50]} for s in menu_strings[:100]]
    
    # Dialog region
    dialog_region = data[0x1C0000:0x1D0000]
    dialog_strings = find_all_strings(dialog_region, 3)
    result["dialog_sample"] = [{"offset": hex(s[0] + 0x1C0000), "text": s[1][:80]} for s in dialog_strings[:50]]
    
    # Full dialog (save to separate file)
    full_dialog = []
    for offset, text in dialog_strings:
        if len(text) > 3:
            full_dialog.append({"offset": hex(offset + 0x1C0000), "text": text})
    
    with open(OUTPUT_DIR / "radical_dreamers_dialog.json", 'w') as f:
        json.dump(full_dialog, f, indent=2)
    result["dialog_lines"] = len(full_dialog)
    
    # Save to file
    with open(OUTPUT_DIR / "radical_dreamers.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"  Found {len(characters)} character references")
    print(f"  Found {len(locations)} location references")
    print(f"  Extracted {len(full_dialog)} dialog lines")
    
    return result

def extract_chrono_trigger():
    """Extract everything from Chrono Trigger"""
    print("\nExtracting Chrono Trigger...")
    rom_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
    data = read_rom(rom_path)
    
    result = {
        "game": "Chrono Trigger",
        "version": "USA",
        "size": len(data),
        "header": data[0xFFC0:0xFFC0+32].decode('ascii', errors='ignore').strip('\x00'),
    }
    
    # Character references
    characters = {
        "Crono": find_bytes(data, b'CRONO'),
        "Lucca": find_bytes(data, b'LUCCA'),
        "Marle": find_bytes(data, b'MARLE'),
        "Frog": find_bytes(data, b'FROG'),
        "Robo": find_bytes(data, b'ROBO'),
        "Ayla": find_bytes(data, b'AYLA'),
        "Magus": find_bytes(data, b'MAGUS'),
    }
    result["character_references"] = {k: len(v) for k, v in characters.items()}
    
    # LZSS blocks
    lzss_count = 0
    for i in range(len(data) - 1):
        if data[i] == 0x10 and data[i+1] in [0, 1, 2, 3]:
            lzss_count += 1
    result["lzss_blocks"] = lzss_count
    
    # Credits
    credits_region = data[0x115000:0x116000]
    credits_strings = find_all_strings(credits_region, 4)
    result["credits"] = [{"offset": hex(s[0] + 0x115000), "text": s[1][:60]} for s in credits_strings[:30]]
    
    # Look for any uncompressed text
    # Check common SNES text regions
    for bank_name, bank_addr in [("C0", 0xC00000), ("C1", 0xC10000), ("D0", 0xD00000), ("E0", 0xE00000)]:
        if bank_addr < len(data):
            chunk = data[bank_addr:bank_addr+256]
            printable = sum(1 for b in chunk if 32 <= b <= 126)
            if printable > 50:
                strings = find_all_strings(data[bank_addr:bank_addr+0x10000], 5)
                if strings:
                    result[f"bank_{bank_name}_strings"] = len(strings)
    
    with open(OUTPUT_DIR / "chrono_trigger.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"  Found {len(characters)} characters")
    print(f"  Found {lzss_count} LZSS compressed blocks")
    
    return result

def extract_chrono_cross():
    """Extract everything from Chrono Cross"""
    print("\nExtracting Chrono Cross...")
    rom_path = BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin"
    data = read_rom(rom_path)
    
    result = {
        "game": "Chrono Cross",
        "version": "PS1 Disc 1",
        "size": len(data),
    }
    
    # Character references
    characters = {
        "Serge": find_bytes(data, b'SERGE'),
        "Kid": find_bytes(data, b'KID'),
        "Harle": find_bytes(data, b'HARLE'),
        "Lynx": find_bytes(data, b'LYNX'),
        "Koris": find_bytes(data, b'KORIS'),
        "Mach": find_bytes(data, b'MACH'),
        "Razzer": find_bytes(data, b'RAZZER'),
        "Zoah": find_bytes(data, b'ZOAH'),
        "Leena": find_bytes(data, b'LEENA'),
        "Orlha": find_bytes(data, b'ORLHA'),
        "Miki": find_bytes(data, b'MIKI'),
    }
    result["character_references"] = {k: len(v) for k, v in characters.items()}
    
    # Location references
    locations = {
        "Home": find_bytes(data, b'HOME'),
        "Arnel": find_bytes(data, b'ARNEL'),
        "Marbule": find_bytes(data, b'MARBULE'),
        "Guldove": find_bytes(data, b'GULDOVE'),
        "Dead Sea": find_bytes(data, b'DEADSEA'),
    }
    result["location_references"] = {k: len(v) for k, v in locations.items()}
    
    # Menu text (known to be uncompressed in PS1 games)
    menu_search = b"SAVE DATA TO YOUR MEMORY CARD"
    pos = data.find(menu_search)
    if pos != -1:
        result["menu_region"] = hex(pos)
        # Extract surrounding text
        region = data[pos:pos+500]
        strings = find_all_strings(region, 4)
        result["menu_strings"] = [{"text": s[1]} for s in strings]
    
    # Title
    title_search = b"CHRONOCROSS"
    pos = data.find(title_search)
    if pos != -1:
        result["title_offset"] = hex(pos)
    
    with open(OUTPUT_DIR / "chrono_cross.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"  Found {len(characters)} characters")
    print(f"  Found {len(locations)} locations")
    
    return result

def create_master_index():
    """Create master index of all data"""
    index = {
        "games": ["Chrono Trigger", "Chrono Cross", "Radical Dreamers"],
        "data_files": [
            "radical_dreamers.json",
            "radical_dreamers_dialog.json", 
            "chrono_trigger.json",
            "chrono_cross.json",
        ],
        "extracted_offsets": {
            "Chrono Trigger": {
                "credits": "0x115000",
                "header": "0xFFC0",
            },
            "Chrono Cross": {
                "menu": "0x25ef52",
                "title": "0x9340",
            },
            "Radical Dreamers": {
                "dialog": "0x1C0000-0x1D0000",
                "menu": "0x150000-0x160000",
                "header": "0xFFC0",
            }
        }
    }
    
    with open(OUTPUT_DIR / "index.json", 'w') as f:
        json.dump(index, f, indent=2)
    
    return index

if __name__ == "__main__":
    print("=" * 60)
    print("CHRONO SERIES DATA EXTRACTION")
    print("=" * 60)
    
    rd = extract_radical_dreamers()
    ct = extract_chrono_trigger()
    cc = extract_chrono_cross()
    idx = create_master_index()
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"\nData saved to: {OUTPUT_DIR}")
    print(f"  - radical_dreamers.json ({rd.get('total_strings', 0)} strings)")
    print(f"  - radical_dreamers_dialog.json ({rd.get('dialog_lines', 0)} lines)")
    print(f"  - chrono_trigger.json")
    print(f"  - chrono_cross.json")
    print(f"  - index.json")
