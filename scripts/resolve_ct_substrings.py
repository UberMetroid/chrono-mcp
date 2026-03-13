#!/usr/bin/env python3
"""
Chrono Trigger - Substring Table Resolution (Safe Iterative)
"""

import sys
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

ct_rom_path = BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc"
ct = open(ct_rom_path, 'rb').read()

SUBTABLE_OFFSET = 0x1EC800

CT_FONT = {}
for i in range(26):
    CT_FONT[0xA0 + i] = chr(ord('A') + i)
for i in range(26):
    CT_FONT[0xBA + i] = chr(ord('a') + i)
for i in range(10):
    CT_FONT[0xD4 + i] = chr(ord('0') + i)

for i, sym in enumerate("!\"#%&'()*+,-./:;<=>?@[\\]^_`{|}~"):
    CT_FONT[0xDE + i] = sym

CT_FONT[0xEF] = ' '
CT_FONT[0xF0] = '♥'
CT_FONT[0xF1] = '...'
CT_FONT[0xF3] = '♪'
CT_FONT[0xFF] = ' '

CT_NAMES = {
    0x13: 'CRONO', 0x14: 'MARLE', 0x15: 'LUCCA', 0x16: 'ROBO',
    0x17: 'FROG', 0x18: 'AYLA', 0x19: 'MAGUS', 0x1A: 'CRONO',
}

def byte_to_char(b):
    if b == 0x00:
        return ''
    if b in [0x05, 0x0A]:
        return ' '
    if b in CT_FONT:
        return CT_FONT[b]
    if 0x41 <= b <= 0x5A:
        return chr(b)
    if 0x61 <= b <= 0x7A:
        return chr(b)
    return None

def extract_raw_substrings(rom_data, offset):
    strings = []
    current = []
    i = offset
    max_strings = 150
    while len(strings) < max_strings and i < len(rom_data) - 1:
        b = rom_data[i]
        if b == 0x00:
            if current:
                strings.append(bytes(current))
                current = []
        else:
            current.append(b)
        i += 1
    if current:
        strings.append(bytes(current))
    return strings

raw_substrings = extract_raw_substrings(ct, SUBTABLE_OFFSET)
print(f"Found {len(raw_substrings)} raw substrings")

def resolve_substrings_safe(raw_strings):
    """Safely resolve substring references with max expansion limit"""
    result = []
    for raw in raw_strings:
        decoded = ""
        for b in raw:
            c = byte_to_char(b)
            if c:
                decoded += c
            elif 0x21 <= b <= 0x9F:
                decoded += f'@{(b - 0x21):02X}@'
            else:
                decoded += '?'
        result.append(decoded)
    
    MAX_LEN = 200
    for _ in range(5):
        changed = False
        for i in range(len(result)):
            s = result[i]
            if len(s) > MAX_LEN:
                continue
            new = s
            for ref_idx in range(len(result)):
                marker = f'@{ref_idx:02X}@'
                if marker in new and len(new) < MAX_LEN:
                    new = new.replace(marker, result[ref_idx])
                    changed = True
            if new != s:
                result[i] = new[:MAX_LEN]
        if not changed:
            break
    
    result = [s.replace('@', '') for s in result]
    return result

resolved_substrings = resolve_substrings_safe(raw_substrings)

print("\nResolved substring table (first 30):")
for i, s in enumerate(resolved_substrings[:30]):
    print(f"  [{i+0x21:02X}]: {s[:50]}")

import json

def lzss_decompress_ct(data, offset):
    if offset >= len(data):
        return b'', offset
    header = data[offset]
    if header not in [0x10, 0x11]:
        return b'', offset
    offset += 1
    decomp_size = data[offset] | (data[offset+1] << 8)
    offset += 2
    output = bytearray()
    max_length = 18 if header == 0x10 else 34
    while len(output) < decomp_size:
        if offset >= len(data):
            break
        flags = data[offset]
        offset += 1
        for bit in range(8):
            if len(output) >= decomp_size or offset >= len(data):
                break
            if flags & (0x80 >> bit):
                output.append(data[offset])
                offset += 1
            else:
                if offset + 1 >= len(data):
                    break
                ref = (data[offset+1] << 8) | data[offset]
                offset += 2
                length = (ref >> 12) + 3
                distance = ref & 0xFFF
                if distance >= len(output):
                    continue
                length = min(length, max_length)
                for _ in range(length):
                    if len(output) >= decomp_size:
                        break
                    output.append(output[-(distance + 1)])
    return bytes(output), offset

def decode_ct_dialog(data, substrings):
    result = []
    i = 0
    while i < len(data):
        b = data[i]
        if b == 0x00:
            break
        if b in [0x05, 0x0A, 0x0B, 0x0C]:
            result.append(' ')
        elif b in CT_NAMES:
            result.append(CT_NAMES[b])
        elif 0x21 <= b <= 0x9F:
            idx = b - 0x21
            if idx < len(substrings):
                result.append(substrings[idx])
            else:
                result.append(f'[{b:02X}]')
        elif b in CT_FONT:
            result.append(CT_FONT[b])
        elif 0x41 <= b <= 0x5A:
            result.append(chr(b))
        elif 0x61 <= b <= 0x7A:
            result.append(chr(b))
        else:
            result.append(' ')
        i += 1
    return ''.join(result)

text_blocks = []
for i in range(len(ct) - 1):
    if ct[i] in [0x10, 0x11] and ct[i+1] == 0x00:
        if i + 4 < len(ct):
            size = ct[i+2] | (ct[i+3] << 8)
            if 200 < size < 60000:
                text_blocks.append((i, ct[i], size))

print(f"\nFound {len(text_blocks)} text blocks, decoding...")

decoded_dialog = []
for offset, header, size in text_blocks[:600]:
    try:
        result, _ = lzss_decompress_ct(ct, offset)
        if len(result) > 50:
            text = decode_ct_dialog(result, resolved_substrings)
            text = ' '.join(text.split())
            if len(text) > 5:
                decoded_dialog.append({
                    "offset": hex(offset),
                    "text": text[:80]
                })
    except:
        pass

seen = set()
unique = []
for item in decoded_dialog:
    if item["text"] not in seen:
        seen.add(item["text"])
        unique.append(item)

print(f"Decoded {len(unique)} unique dialog entries")

with open(DATA_DIR / "ct_dialog_resolved.json", 'w') as f:
    json.dump(unique[:2000], f, indent=2)

with open(DATA_DIR / "ct_substring_table.json", 'w') as f:
    json.dump(resolved_substrings, f, indent=2)

print("\n=== Sample decoded dialog ===")
for item in unique[:40]:
    print(f"  {item['text']}")
