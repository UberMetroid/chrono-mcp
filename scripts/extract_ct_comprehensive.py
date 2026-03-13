#!/usr/bin/env python3
"""
Comprehensive Chrono Trigger extraction
- Extract all ASCII strings (uncompressed)
- Decompress and decode LZSS text blocks
- Build a proper dialog database
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, '/home/jeryd/Code/Chrono_Series')

from lib.chrono import read_rom, find_strings

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

print("Loading Chrono Trigger ROM...")
ct = read_rom('ct_snes')
print(f"ROM size: {len(ct) / (1024*1024):.2f} MB")

# 1. Extract all ASCII strings from the entire ROM
print("\n=== Extracting all ASCII strings ===")
all_strings = find_strings(ct, min_length=4)
print(f"Found {len(all_strings)} strings")

# Group strings by region
dialog_strings = []
menu_strings = []
credits_strings = []

# Credits region: 0x300000 - 0x400000 (where THANK YOU was found)
credits_start = 0x300000
credits_end = 0x400000

for pos, text in all_strings:
    if credits_start <= pos < credits_end:
        credits_strings.append({"offset": hex(pos), "text": text})
    elif len(text) >= 6:
        dialog_strings.append({"offset": hex(pos), "text": text})

# Deduplicate
seen = set()
unique_dialog = []
for s in dialog_strings:
    if s["text"] not in seen:
        seen.add(s["text"])
        unique_dialog.append(s)

print(f"Dialog strings: {len(unique_dialog)}")
print(f"Credits strings: {len(credits_strings)}")

# 2. LZSS decompression with fixed size handling
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
    window_size = 4096 if header == 0x10 else 2048
    max_length = 18 if header == 0x10 else 34
    
    while len(output) < decomp_size:
        if offset >= len(data):
            break
        flags = data[offset]
        offset += 1
        
        for bit in range(8):
            if len(output) >= decomp_size:
                break
            if offset >= len(data):
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
                if length > max_length:
                    length = max_length
                    
                for _ in range(length):
                    if len(output) >= decomp_size:
                        break
                    output.append(output[-(distance + 1)])
    
    return bytes(output), offset

# 3. Try to decode CT's custom encoding
# CT uses a SJIS-like encoding where certain byte ranges map to characters
# Let's try to find readable text in the decompressed data

def try_decode_ct_text(decompressed):
    """Try multiple decoding strategies for CT text"""
    results = []
    
    # Strategy 1: Direct ASCII (for uncompressed text)
    current = []
    for b in decompressed:
        if 32 <= b <= 126:
            current.append(chr(b))
        else:
            if len(current) >= 4:
                results.append(''.join(current))
            current = []
    if len(current) >= 4:
        results.append(''.join(current))
    
    # Strategy 2: Try Shift-JIS interpretation (for Japanese text)
    try:
        sjis_text = decompressed.decode('shift_jis', errors='ignore')
        if sjis_text.strip():
            results.append(sjis_text[:200])
    except:
        pass
    
    return results

# 4. Find and decompress text blocks
print("\n=== Decompressing LZSS text blocks ===")

# Load known text blocks or scan for them
text_blocks = []
for i in range(len(ct) - 1):
    if ct[i] in [0x10, 0x11] and ct[i+1] == 0x00:
        if i + 4 < len(ct):
            size = ct[i+2] | (ct[i+3] << 8)
            if 1000 < size < 50000:  # Likely text block sizes
                text_blocks.append((i, ct[i], size))

print(f"Found {len(text_blocks)} potential text blocks")

# Decompress first 100 blocks and extract readable content
decompressed_texts = []
for idx, (offset, header, size) in enumerate(text_blocks[:100]):
    try:
        result, next_off = lzss_decompress_ct(ct, offset)
        if len(result) > 100:
            # Look for any readable sequences
            readable_count = sum(1 for b in result if 32 <= b <= 126)
            pct = 100 * readable_count / len(result)
            if pct > 15:  # At least 15% readable
                # Extract readable strings
                strings = try_decode_ct_text(result)
                for s in strings:
                    if len(s) >= 6 and len(s) < 100:
                        decompressed_texts.append({
                            "offset": hex(offset),
                            "size": size,
                            "readable_pct": round(pct, 1),
                            "text": s[:80]
                        })
    except Exception as e:
        pass

print(f"Found {len(decompressed_texts)} decompressed text segments")

# 5. Build final database
print("\n=== Building final database ===")

# Combine all text sources
final_dialog = []

# Add uncompressed dialog
for s in unique_dialog:
    text = s["text"]
    if 6 < len(text) < 80 and any(c.isalpha() for c in text):
        final_dialog.append({
            "source": "uncompressed",
            "text": text,
            "offset": s["offset"]
        })

# Add decompressed text
for s in decompressed_texts:
    final_dialog.append({
        "source": "lzss_decompressed",
        "text": s["text"],
        "offset": s["offset"],
        "readable_pct": s["readable_pct"]
    })

# Deduplicate by text
seen_texts = set()
unique_final = []
for item in final_dialog:
    if item["text"] not in seen_texts:
        seen_texts.add(item["text"])
        unique_final.append(item)

print(f"Total unique dialog entries: {len(unique_final)}")

# Save to JSON
output = {
    "game": "Chrono Trigger",
    "total_entries": len(unique_final),
    "entries": unique_final[:2000]  # Limit for JSON size
}

with open(DATA_DIR / "chrono_trigger_dialog.json", 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nSaved to {DATA_DIR / 'chrono_trigger_dialog.json'}")

# Show some samples
print("\n=== Sample dialog ===")
for item in unique_final[:20]:
    print(f"  [{item['source']}] {item['text'][:60]}")
