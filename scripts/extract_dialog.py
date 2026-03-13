#!/usr/bin/env python3
"""
Extract actual game dialog and data from ROMs
"""

import sys
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

def dump_raw_text(data, start, length=512):
    """Extract readable text from a region"""
    chunk = data[start:start+length]
    result = []
    for b in chunk:
        if 32 <= b <= 126:
            result.append(chr(b))
        else:
            result.append('.')
    return ''.join(result)

# Open Radical Dreamers
rd_path = "/home/jeryd/Code/Chrono_Series/Radical Dreamers/BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
rd = open(rd_path, 'rb').read()

print("=== RADICAL DREAMERS - TEXT REGIONS ===\n")

# Look at specific regions that seem to have text
regions = [
    (0x150000, "Dialog region?"),
    (0x1C0000, "More dialog"),
    (0x10000, "Start of ROM"),
]

for addr, desc in regions:
    print(f"--- {desc} (0x{addr:06x}) ---")
    print(dump_raw_text(rd, addr, 200))
    print()

# Open Chrono Cross - looking for text
print("\n=== CHRONO CROSS - SEARCHING FOR TEXT ===\n")

cc_path = "/home/jeryd/Code/Chrono_Series/Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin"
cc = open(cc_path, 'rb').read()

# PS1 games use different encoding. Let's look for uncompressed text.
# Try finding some known strings
searches = [
    b'SERGE',
    b'KID',
    b'HARLE',
    b'LYNX',
    b'CHRONO',
    b'CROSS',
    b'BEGIN',
    b'STATUS',
    b'ITEM',
    b'EQUIP',
    b'SAVE',
    b'LOAD',
]

for s in searches:
    pos = cc.find(s)
    if pos != -1:
        context = dump_raw_text(cc, max(0, pos-20), 80)
        print(f"{s.decode()}: {hex(pos)}")
        print(f"  {context}")
        print()
