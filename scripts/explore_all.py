#!/usr/bin/env python3
"""
Comprehensive ROM Explorer
Finds text, data, and structure in Chrono series ROMs
"""

import sys
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

from lib.chrono import read_rom, rom_info, find_strings, find_bytes

def explore_ct():
    """Explore Chrono Trigger SNES ROM"""
    print("=" * 60)
    print("CHRONO TRIGGER (SNES) EXPLORATION")
    print("=" * 60)
    
    data = read_rom("ct_snes")
    info = rom_info(data)
    print(f"\nROM Info: {info['size_mb']:.2f}MB, Header: '{info['header']}'")
    
    # Find all meaningful strings
    print("\n--- Searching for Text Patterns ---")
    strings = find_strings(data, min_length=5)
    
    # Categorize findings
    locations = []
    items = []
    characters = []
    misc = []
    
    location_names = ["NORTH", "SOUTH", "EAST", "WEST", "CASTLE", "TOWER", "CAVE", "TEMPLE", 
                      "FOREST", "LAKE", "MOUNTAIN", "VILLAGE", "TOWN", "CITY", "RUINS",
                      "GUARDIA", "ZEAL", "OCEAN", "DESERT", "ISLAND", "LABO", "FROG"]
    
    item_names = ["SWORD", "SHIELD", "HELM", "ARMOR", "POTION", "ETHER", "TONIC",
                  "CURE", "REVEAL", "MAP", "KEY", "SEED", "FEATHER", "CLOTH"]
    
    char_names = ["CRONO", "LUCCA", "MARLE", "FROG", "ROBO", "AYLA", "MAGUS",
                  "FROB", "NARR", "JOHNY", "ROUND", "SAY", "LALLAP", "DOS"]
    
    for offset, text in strings:
        upper = text.upper()
        found = False
        
        for loc in location_names:
            if loc in upper and len(text) > 4:
                locations.append((offset, text))
                found = True
                break
        
        if not found:
            for item in item_names:
                if item in upper:
                    items.append((offset, text))
                    found = True
                    break
        
        if not found:
            for char in char_names:
                if char in upper:
                    characters.append((offset, text))
                    found = True
                    break
    
    print(f"\nFound {len(locations)} location references:")
    for offset, text in locations[:15]:
        print(f"  {hex(offset)}: {text[:40]}")
    
    print(f"\nFound {len(characters)} character references:")
    for offset, text in characters[:15]:
        print(f"  {hex(offset)}: {text[:40]}")
    
    print(f"\nFound {len(items)} item references:")
    for offset, text in items[:15]:
        print(f"  {hex(offset)}: {text[:40]}")
    
    # Look for specific story elements
    print("\n--- Story Elements ---")
    story_patterns = [
        b'LAVOS', b'GATE', b'PROPHECY', b'DESTINY', b'TIME',
        b'CHRONO', b'TRIGGER', b'DREAM', b'ROOF', b'CITY',
        b'KING', b'QUEEN', b'PRINCESS', b'KNIGHT', b'GUARD'
    ]
    
    for pattern in story_patterns:
        pos = data.find(pattern)
        if pos != -1:
            context = data[max(0,pos-10):pos+30]
            readable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in context)
            print(f"  {pattern.decode()}: {hex(pos)} - ...{readable}...")
    
    # Look for compressed blocks (LZSS signature)
    print("\n--- LZSS Compression Blocks ---")
    lzss_sig = bytes([0x10])
    count = 0
    positions = []
    for i in range(len(data) - 1):
        if data[i] == 0x10 and data[i+1] in [0, 1, 2, 3]:
            count += 1
            if len(positions) < 10:
                positions.append(i)
    print(f"  Found ~{count} potential LZSS blocks")
    print(f"  Sample positions: {[hex(p) for p in positions[:10]]}")
    
    # Look at ROM bank structure
    print("\n--- ROM Bank Analysis ---")
    banks = [(0xC00000, "Bank C0"), (0xC10000, "Bank C1"), (0xC20000, "Bank C2"),
             (0xD00000, "Bank D0"), (0xE00000, "Bank E0")]
    
    for addr, name in banks:
        if addr < len(data):
            chunk = data[addr:addr+256]
            printable = sum(1 for b in chunk if 32 <= b <= 126)
            ratio = printable / 256 * 100
            print(f"  {name} ({hex(addr)}): {ratio:.1f}% printable")


def explore_rd():
    """Explore Radical Dreamers ROM"""
    print("\n" + "=" * 60)
    print("RADICAL DREAMERS EXPLORATION")
    print("=" * 60)
    
    data = read_rom("rd_snes")
    print(f"\nROM Size: {len(data)} bytes ({len(data)//1024}KB)")
    
    # Header
    if len(data) > 0xFFC0:
        header = data[0xFFC0:0xFFC0+32]
        print(f"Header: {header[:21]}")
    
    # Find text
    strings = find_strings(data, min_length=4)
    print(f"\nFound {len(strings)} string sequences")
    
    # Look for names
    names = ["KID", "HARLE", "NORMAN", "NIKOLAI", "GUARD", "KING", "RADICAL", "DREAM", "TREASURE"]
    for name in names:
        pos = data.find(name.encode())
        if pos != -1:
            context = data[max(0,pos-5):pos+25]
            readable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in context)
            print(f"  {name}: {hex(pos)} - {readable}")


def explore_cc():
    """Explore Chrono Cross (PS1)"""
    print("\n" + "=" * 60)
    print("CHRONO CROSS EXPLORATION (Disc 1)")
    print("=" * 60)
    
    data = read_rom("cc_disc1")
    print(f"\nROM Size: {len(data)} bytes ({len(data)//1024//1024}MB)")
    
    # PS1 executables usually start with bootstrap
    print(f"  First bytes: {data[:16].hex()}")
    
    # Find strings
    strings = find_strings(data, min_length=6)
    print(f"\nFound {len(strings)} string sequences")
    
    # Look for character names
    cc_chars = ["SERGE", "KID", "HARLE", "LYNX", "FUZ", "KORIS", "MACH", "RONAN",
                "HARLE", "CHRIS", "MEL", "DIRK", "SNEFF", "LEAH", "MAX"]
    
    print("\n--- Character Search ---")
    for name in cc_chars:
        pos = data.find(name.encode())
        if pos != -1:
            context = data[max(0,pos-5):pos+25]
            readable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in context)
            print(f"  {name}: {hex(pos)} - {readable}")
    
    # Look for locations
    cc_locs = ["HOME", "ARGELO", "MARBULE", "TOMAHAWK", "DEATH", "DENADORO",
               "WATERFALL", "FOREST", "VINCENT", "ISLAND"]
    
    print("\n--- Location Search ---")
    for name in cc_locs:
        pos = data.find(name.encode())
        if pos != -1:
            context = data[max(0,pos-5):pos+25]
            readable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in context)
            print(f"  {name}: {hex(pos)} - {readable}")


if __name__ == "__main__":
    explore_ct()
    explore_rd()
    explore_cc()
