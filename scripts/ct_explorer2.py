#!/usr/bin/env python3
"""
Chrono Trigger ROM Explorer v2
More advanced analysis of SNES ROM data
"""

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

def decode_snes_text(data, offset, length=50):
    """Try to decode SNES text - uses a custom encoding
    Common in Square games: 1 byte per char, using a table
    """
    # Square's encoding often uses values 0x20-0x7F similar to ASCII
    # plus extended chars for special chars
    chars = []
    for i in range(length):
        b = data[offset + i]
        if b == 0:
            break
        # Direct ASCII range
        if 0x20 <= b <= 0x7E:
            chars.append(chr(b))
        # Extended chars - common ones
        elif b == 0x81:
            chars.append('(81)')
        elif b == 0x85:
            chars.append('.')
        elif b == 0xE0:
            chars.append(' ')
        else:
            chars.append(f'[{b:02X}]')
    return ''.join(chars)

def find_3byte_sequences(data):
    """Find sequences of printable-ish bytes (SNES text encoding)"""
    results = []
    current = []
    
    for i in range(len(data)):
        b = data[i]
        # SNES text range (extended ASCII)
        if 0x20 <= b <= 0x7E or b in [0x81, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8A, 0xE0]:
            current.append((i, b))
        else:
            if len(current) >= 8:
                start = current[0][0]
                text = decode_snes_text(data, start, len(current))
                if any(k in text.upper() for k in ['TIME', 'GATE', 'KING', 'ITEM', 'MAGIC', 'HP', 'MP', 'LVL', 'ATK']):
                    results.append((start, text))
            current = []
    
    return results

def analyze():
    data = read_rom()
    print(f"ROM Size: {len(data)} bytes")
    print(f"ROM Type: {'HiROM' if len(data) > 0x300000 else 'LoROM'}")
    
    # Check header
    print("\n=== ROM HEADER ===")
    print(f"  Title at 0xFFC0: {data[0xFFC0:0xFFE0]}")
    
    # The game text is LZSS compressed - find the decompression routine
    print("\n=== SEARCHING FOR COMPRESSED DATA ===")
    
    # Look for LZSS compressed blocks
    # LZSS format: 0x10 followed by uncompressed size (little-endian)
    lzss_blocks = []
    for i in range(0x10000, len(data) - 100):
        if data[i] == 0x10:
            size = data[i+1] | (data[i+2] << 8)
            if 0x100 < size < 0x3000:
                # Check if next byte looks like compressed data
                if data[i+3] != 0x10:
                    lzss_blocks.append((i, size))
    
    print(f"Found {len(lzss_blocks)} LZSS blocks")
    for offset, size in lzss_blocks[:10]:
        print(f"  {hex(offset)}: {size} bytes")
    
    # Look for the main script - usually in a specific bank
    print("\n=== LOOKING FOR SCRIPT ===")
    
    # Try common text banks (Square put script at different locations)
    banks_to_check = [
        0xC00000, 0xC10000, 0xC20000, 0xC30000,
        0xD00000, 0xD10000, 0xE00000, 0xE10000
    ]
    
    for bank in banks_to_check:
        if bank < len(data):
            # Look for "EVENT" or "SCRIPT" markers
            chunk = data[bank:bank+0x1000]
            # Check for pointer tables (sequences of 3-byte pointers)
            ptr_count = 0
            for i in range(0, 0x1000, 3):
                if 0x80 <= chunk[i] <= 0xFF and 0x80 <= chunk[i+1] <= 0xFF:
                    ptr_count += 1
            if ptr_count > 20:
                print(f"  Bank {hex(bank)}: {ptr_count} potential pointers")
    
    # Look for enemy data
    print("\n=== LOOKING FOR ENEMY DATA ===")
    # Enemies usually have: HP (2 bytes), Attack (2 bytes), Name pointer
    # Search for patterns
    
    # Look for monster names
    monsters = [b'MONSTER', b'SLIME', b'GOBLIN', b'BAT', b'GHOST']
    for m in monsters:
        pos = data.find(m)
        if pos != -1:
            print(f"  Found: {hex(pos)}")
    
    # Look for battle messages
    print("\n=== LOOKING FOR BATTLE TEXT ===")
    battle_text = [b'ATTACK', b'DEFEND', b'VICTORY', b'DEFEAT', b'RUN']
    for bt in battle_text:
        pos = data.find(bt)
        if pos != -1:
            print(f"  {bt.decode()}: {hex(pos)}")
            # Show context
            ctx = decode_snes_text(data, pos, 20)
            print(f"    -> {ctx}")
    
    # Character stats - usually 0xC7 bytes per character
    print("\n=== CHARACTER STATS ===")
    # Look for HP values (common: 20-99 for early game)
    # Search for sequence: HP value, MP value, strength
    
    # Let's dump the first 256 bytes of a few potential stat locations
    for base in [0x2A0000, 0x2E0000, 0x300000, 0x3A0000, 0x3E0000]:
        if base < len(data):
            print(f"\n  Dumping {hex(base)}:")
            chunk = data[base:base+128]
            # Look for stat-like values (10-99 in reasonable positions)
            stats = []
            for i in range(0, 128, 2):
                val = chunk[i] | (chunk[i+1] << 8)
                if 1 < val < 1000:
                    stats.append(f"{i}:{val}")
            if stats:
                print(f"    Possible stats: {', '.join(stats[:10])}")

    # Find all text blocks using SNES encoding
    print("\n=== ALL TEXT BLOCKS ===")
    text_blocks = find_3byte_sequences(data)
    for offset, text in text_blocks[:20]:
        if len(text) > 10:
            print(f"  {hex(offset)}: {text[:50]}")

if __name__ == "__main__":
    analyze()
