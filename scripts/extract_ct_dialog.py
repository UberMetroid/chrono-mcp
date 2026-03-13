#!/usr/bin/env python3
"""Extract dialog from decompressed CT blocks"""

import sys
from pathlib import Path
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

def read_rom(path):
    with open(path, 'rb') as f:
        return f.read()

def decompress_lzss(data, offset):
    if offset >= len(data):
        return b'', offset
    header = data[offset]
    if header not in [0x10, 0x11]:
        return b'', offset
    output = bytearray()
    offset += 1
    while len(output) < 65536:
        if offset >= len(data):
            break
        control = data[offset]
        offset += 1
        for i in range(8):
            if offset >= len(data):
                break
            if control & (0x80 >> i):
                output.append(data[offset])
                offset += 1
            else:
                if offset + 1 >= len(data):
                    break
                match = (data[offset] << 8) | data[offset + 1]
                offset += 2
                length = ((match >> 12) & 0xF) + 3
                distance = (match & 0xFFF) + 1
                if distance > len(output):
                    break
                for _ in range(length):
                    output.append(output[-distance])
    return bytes(output), offset

ct = read_rom(BASE_DIR / "Chrono Trigger/Chrono Trigger (USA).sfc")
text_blocks = [0x127c00, 0x14e380, 0x16c750, 0x174660, 0x175c90, 0x178250, 0x17a260, 0x184d70, 0x1857d0, 0x192020]

all_dialog = []

for offset in text_blocks:
    try:
        result, _ = decompress_lzss(ct, offset)
        strings = []
        current = []
        for b in result:
            if 32 <= b <= 126:
                current.append(chr(b))
            else:
                if len(current) >= 6:
                    text = ''.join(current)
                    if text.replace(' ', '').isalpha():
                        strings.append(text)
                current = []
        for s in strings:
            if 8 < len(s) < 60:
                all_dialog.append(s)
    except:
        pass

unique = list(set(all_dialog))
print(f"Found {len(unique)} dialog lines")
for d in unique[:30]:
    print(f"  {d}")

import json
with open(DATA_DIR / "chrono_trigger_dialog.json", 'w') as f:
    json.dump(unique, f, indent=2)
