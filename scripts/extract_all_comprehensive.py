#!/usr/bin/env python3
"""
Comprehensive extraction of ALL data from Chrono Trigger, Chrono Cross, and Radical Dreamers
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

from lib.chrono import read_rom, find_strings

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("=" * 60)
print("CHRONO SERIES COMPREHENSIVE EXTRACTION")
print("=" * 60)

# ============================================================
# RADICAL DREAMERS - Simple ASCII extraction
# ============================================================
print("\n[1/3] Extracting Radical Dreamers...")
rd_path = BASE_DIR / "Radical Dreamers/BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
rd = read_rom('rd_snes')

rd_dialog = []
# Two main text regions
for start in [0x150000, 0x1C0000]:
    chunk = rd[start:start+0x10000]
    current = []
    for b in chunk:
        if 32 <= b <= 126:
            current.append(chr(b))
        else:
            if len(current) >= 3:
                text = ''.join(current).strip()
                if text and len(text) < 80:
                    rd_dialog.append(text)
            current = []

# Dedupe
rd_unique = list(set(rd_dialog))
print(f"  Found {len(rd_unique)} dialog lines")

with open(DATA_DIR / "radical_dreamers_dialog.json", 'w') as f:
    json.dump(rd_unique, f, indent=2)

# ============================================================
# CHRONO CROSS - Text + TIM images
# ============================================================
print("\n[2/3] Extracting Chrono Cross...")
cc = read_rom('cc_disc1')

# Extract all readable strings
cc_strings = find_strings(cc, min_length=4)
print(f"  Found {len(cc_strings)} raw strings")

# Filter for meaningful text
cc_text = []
for pos, text in cc_strings:
    if len(text) > 4 and len(text) < 100:
        # Check for reasonable character content
        alpha = sum(1 for c in text if c.isalpha())
        if alpha > len(text) * 0.3:
            cc_text.append({"offset": hex(pos), "text": text[:60]})

cc_unique = list(set([t["text"] for t in cc_text]))
print(f"  Filtered to {len(cc_unique)} meaningful strings")

with open(DATA_DIR / "chrono_cross_all_text.json", 'w') as f:
    json.dump(cc_text[:10000], f, indent=2)

# ============================================================
# CHRONO TRIGGER - Everything
# ============================================================
print("\n[3/3] Extracting Chrono Trigger...")
ct = read_rom('ct_snes')

# --- CREDITS ---
print("  Extracting credits...")
credits_data = ct[0x115000:0x320000]
cred_strings = []
current = []
for b in credits_data:
    if b == 0x80:
        if len(current) >= 4:
            text = ''.join(current)
            alpha = sum(1 for c in text if c.isalpha())
            if alpha >= len(text) * 0.5:
                cred_strings.append(text)
        current = []
    elif 32 <= b <= 126:
        current.append(chr(b))
    else:
        if len(current) >= 4:
            text = ''.join(current)
            alpha = sum(1 for c in text if c.isalpha())
            if alpha >= len(text) * 0.5:
                cred_strings.append(text)
        current = []

ct_credits = list(set(cred_strings))
print(f"    Credits: {len(ct_credits)} entries")

with open(DATA_DIR / "ct_credits.json", 'w') as f:
    json.dump(ct_credits, f, indent=2)

# --- LZSS TEXT BLOCKS ---
print("  Extracting dialog from LZSS blocks...")

# Substring table
SUBTABLE_OFFSET = 0x1EC800
def extract_substrings(data, offset):
    strings = []
    current = []
    i = offset
    while len(strings) < 128 and i < len(data) - 1:
        b = data[i]
        if b == 0x00:
            if current:
                strings.append(bytes(current))
                current = []
        else:
            current.append(b)
        i += 1
    return strings

substring_bytes = extract_substrings(ct, SUBTABLE_OFFSET)
substrings = []
for s in substring_bytes:
    decoded = ""
    for byte in s:
        if 0xA0 <= byte <= 0xB9:
            decoded += chr(0x41 + (byte - 0xA0))
        elif 0xBA <= byte <= 0xD3:
            decoded += chr(0x61 + (byte - 0xBA))
        elif 0xD4 <= byte <= 0xDD:
            decoded += chr(0x30 + (byte - 0xD4))
        elif byte in [0xEF, 0xFF]:
            decoded += " "
        elif 0x20 <= byte <= 0x7F:
            decoded += chr(byte)
        else:
            decoded += "?"
    substrings.append(decoded)

# LZSS decompressor
def lzss_decompress(data, offset):
    if offset >= len(data):
        return b'', offset
    header = data[offset]
    if header not in [0x10, 0x11]:
        return b'', offset
    offset += 1
    decomp_size = data[offset] | (data[offset+1] << 8)
    offset += 2
    output = bytearray()
    max_len = 18 if header == 0x10 else 34
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
                length = min(length, max_len)
                for _ in range(length):
                    if len(output) >= decomp_size:
                        break
                    output.append(output[-(distance + 1)])
    return bytes(output), offset

# CT decoder
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
CT_FONT[0xFF] = ' '

CT_NAMES = {0x13:'CRONO', 0x14:'MARLE', 0x15:'LUCCA', 0x16:'ROBO', 
             0x17:'FROG', 0x18:'AYLA', 0x19:'MAGUS'}

def decode_ct(data, subs):
    result = []
    i = 0
    while i < len(data):
        b = data[i]
        if b == 0x00:
            break
        elif b in CT_NAMES:
            result.append(CT_NAMES[b])
        elif 0x21 <= b <= 0x9F:
            idx = b - 0x21
            if idx < len(subs):
                result.append(subs[idx])
        elif b in CT_FONT:
            result.append(CT_FONT[b])
        elif 0x20 <= b <= 0x7F:
            result.append(chr(b))
        i += 1
    return ''.join(result)

# Find and decode blocks
text_blocks = []
for i in range(len(ct) - 1):
    if ct[i] in [0x10, 0x11] and ct[i+1] == 0x00:
        if i + 4 < len(ct):
            size = ct[i+2] | (ct[i+3] << 8)
            if 500 < size < 60000:
                text_blocks.append(i)

ct_dialog = []
for offset in text_blocks[:500]:
    try:
        result, _ = lzss_decompress(ct, offset)
        if len(result) > 100:
            text = decode_ct(result, substrings)
            for chunk in text.split('\n'):
                chunk = chunk.strip()
                if 3 < len(chunk) < 60:
                    alpha = sum(1 for c in chunk if c.isalpha())
                    if alpha > len(chunk) * 0.3:
                        ct_dialog.append(chunk)
    except:
        pass

ct_dialog = list(set(ct_dialog))
print(f"    Dialog: {len(ct_dialog)} entries")

with open(DATA_DIR / "ct_dialog.json", 'w') as f:
    json.dump(ct_dialog, f, indent=2)

# --- ALL STRINGS ---
print("  Extracting all ASCII strings...")
all_strings = find_strings(ct, min_length=6)
ct_strings = [{"offset": hex(pos), "text": text} for pos, text in all_strings 
              if any(c.isalpha() for c in text) and len(text) > 5]
print(f"    Raw strings: {len(ct_strings)}")

with open(DATA_DIR / "ct_all_strings.json", 'w') as f:
    json.dump(ct_strings[:5000], f, indent=2)

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("EXTRACTION COMPLETE")
print("=" * 60)

summary = {
    "radical_dreamers": {
        "dialog_lines": len(rd_unique)
    },
    "chrono_cross": {
        "text_strings": len(cc_unique),
        "total_raw_strings": len(cc_strings)
    },
    "chrono_trigger": {
        "credits": len(ct_credits),
        "dialog": len(ct_dialog),
        "raw_strings": len(ct_strings)
    }
}

print(f"\nRadical Dreamers: {summary['radical_dreamers']['dialog_lines']} dialog lines")
print(f"Chrono Cross: {summary['chrono_cross']['text_strings']} text strings")
print(f"Chrono Trigger: {summary['chrono_trigger']['credits']} credits, {summary['chrono_trigger']['dialog']} dialog")

with open(DATA_DIR / "extraction_summary.json", 'w') as f:
    json.dump(summary, f, indent=2)

print("\nAll data saved to data/")
