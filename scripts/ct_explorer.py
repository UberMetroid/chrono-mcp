#!/usr/bin/env python3
"""
Chrono Trigger ROM Explorer
Finds and analyzes game data without decompression
"""

import sys

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

def find_ascii_sequences(data, min_len=6):
    """Find sequences of printable ASCII characters"""
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
        start = current[0][0]
        text = ''.join(c for _, c in current)
        results.append((start, text))
    
    return results

def find_4byte_text_table(data):
    """Look for 4-byte text table pointers (common in SNES)"""
    # Text tables usually have patterns: repeated offset patterns
    # Look for sequences of $XX $XX $XX $YY pointers
    pass

def analyze_rom():
    data = read_rom()
    print(f"ROM Size: {len(data)} bytes ({len(data)//1024}KB)")
    
    # Look for interesting offsets
    print("\n=== SEARCHING FOR GAME DATA ===")
    
    # Find ASCII text
    print("\n--- ASCII Text Sequences ---")
    ascii_seqs = find_ascii_sequences(data, min_len=5)
    for offset, text in ascii_seqs[:30]:
        if any(word in text.upper() for word in ['TIME', 'GATE', 'KING', 'ITEM', 'MAGIC', 'ATTACK']):
            print(f"  {hex(offset)}: {text[:40]}")
    
    # Look for item names (usually in a table)
    print("\n--- Looking for Item Data ---")
    # Items typically have: name (10-12 chars), price (2 bytes), damage (2 bytes)
    # Let's look at $C0XXXX area (common for item tables)
    for base in [0xC00000, 0xC10000, 0xC20000, 0xD00000, 0xE00000]:
        if base < len(data):
            chunk = data[base:base+256]
            printable = sum(1 for b in chunk if 32 <= b <= 126)
            if printable > 50:
                print(f"  {hex(base)}: {printable}% printable")
    
    # Look for character stats (HP, MP, Strength, etc.)
    print("\n--- Looking for Character Data ---")
    # Characters usually have stats at fixed offsets
    # Search for patterns like: HP (0x19 0x00) = 25
    # Search for "LUCCA" or similar names
    for name in [b'CRONO', b'LUCCA', b'MARLE', b'FROG', b'ROBO', b'AYLA', b'MAGUS']:
        pos = data.find(name)
        if pos != -1:
            print(f"  Found {name.decode()}: {hex(pos)}")
            # Dump surrounding bytes
            print(f"    Context: {data[pos:pos+32]}")
    
    # Look for location names (often after character data)
    print("\n--- Looking for Locations ---")
    locations = [b'ZEAL', b'KNOW', b'MEDIA', b'ANTIO', b'OCEAN', b'DWARF', b'GIANT', b'FROG', b'MANiac']
    for loc in locations:
        pos = data.find(loc)
        if pos != -1:
            print(f"  {loc.decode()}: {hex(pos)}")
    
    # Look for magic/tech names
    print("\n--- Looking for Magic/Tech Names ---")
    techs = [b'FIRE', b'ICE', b'BOLT', b'CURE', b'FLAME', b'SLASH', b'SWIRL']
    for tech in techs:
        pos = data.find(tech)
        if pos != -1:
            print(f"  {tech.decode()}: {hex(pos)}")
    
    # Analyze compression signatures (LZSS)
    print("\n--- Looking for Compressed Data ---")
    # LZSS signature: 0x10 followed by length
    # Find potential LZSS blocks
    lzss_candidates = []
    for i in range(len(data) - 4):
        # Check for LZSS header pattern
        if data[i] == 0x10 and data[i+1] > 0x10:
            length = (data[i+1] << 8) | data[i+2]
            if 4 < length < 0x1000:
                lzss_candidates.append((i, length))
    
    print(f"  Found {len(lzss_candidates)} potential compressed blocks")
    for offset, length in lzss_candidates[:10]:
        print(f"    {hex(offset)}: {length} bytes")
    
    # Look at the graphics tiles (SNES uses 2bpp/4bpp/8bpp)
    print("\n--- Looking for Tile Data ---")
    # Find 8x8 tile patterns (repeating 64-byte sequences with bit planes)
    # This is harder - let's just note tile data regions
    print("  Tile data typically at: $600000-$700000 (VRAM)")
    print("  Sprite data typically at: $7E2000-$7E3000 (RAM)")
    
    # Look for the map data (Tilemaps)
    print("\n--- Looking for Map Data ---")
    # Tilemaps are 2-byte per tile (palette + tile number)
    # Look for repeating patterns that could be tilemaps
    
    # Look for the save data structure
    print("\n--- Save Data Structure ---")
    # Check for save signature
    for sig in [b'SRRA', b'RAWR', b'SAVE', b'CT01']:
        pos = data.find(sig)
        if pos != -1:
            print(f"  Found {sig}: {hex(pos)}")

    return data

def find_text_block(data, offset, max_len=100):
    """Extract potential text from a specific offset"""
    text = []
    for i in range(max_len):
        b = data[offset + i]
        if b == 0:
            break
        if 32 <= b <= 126:
            text.append(chr(b))
    return ''.join(text)

def analyze_pointer_table(data, base_offset, count=20):
    """Analyze a potential pointer table"""
    print(f"\n=== Analyzing Pointer Table at {hex(base_offset)} ===")
    pointers = []
    for i in range(count):
        ptr_offset = base_offset + (i * 4)
        if ptr_offset + 4 > len(data):
            break
        # SNES pointer: bank << 16 | offset
        ptr = (data[ptr_offset+2] << 16) | (data[ptr_offset] << 8) | data[ptr_offset+1]
        pointers.append(ptr)
    
    # Calculate differences to find block sizes
    for i in range(len(pointers) - 1):
        diff = pointers[i+1] - pointers[i]
        if 0 < diff < 0x10000:
            text = find_text_block(data, pointers[i], 20)
            if text and len(text) > 3:
                print(f"  Entry {i}: {hex(pointers[i])} (+{diff}): {text}")

if __name__ == "__main__":
    analyze_rom()
