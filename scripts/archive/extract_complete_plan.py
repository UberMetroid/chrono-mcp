#!/usr/bin/env python3
"""
Chrono Series Complete Extraction Plan
Priority: 1. Dialog, 2. Binary Data, 3. Audio/Video
"""

from pathlib import Path
import json
import struct

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"

# ============ PHASE 1: DIALOG EXTRACTION (HIGHEST PRIORITY) ============

def extract_ct_dialog_comprehensive():
    """Extract ALL CT dialog with full decoding"""
    print("=== Extracting Chrono Trigger Dialog ===")
    
    ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()
    
    CT_FONT = {}
    for i in range(26):
        CT_FONT[0xA0 + i] = chr(ord('A') + i)
    for i in range(26):
        CT_FONT[0xBA + i] = chr(ord('a') + i)
    for i in range(10):
        CT_FONT[0xD4 + i] = chr(ord('0') + i)
    CT_FONT[0xEF] = ' '
    CT_FONT[0xFF] = ' '
    CT_FONT[0xF0] = '♥'
    CT_FONT[0xF1] = '...'
    CT_FONT[0xF3] = '♪'
    
    CT_NAMES = {
        0x13: 'CRONO', 0x14: 'MARLE', 0x15: 'LUCCA', 0x16: 'ROBO',
        0x17: 'FROG', 0x18: 'AYLA', 0x19: 'MAGUS', 0x1A: 'CRONO',
    }
    
    # Get substring table from 0x1EC800
    subtable = []
    subtable_offset = 0x1EC800
    current = []
    while len(subtable) < 128 and subtable_offset < len(ct):
        b = ct[subtable_offset]
        if b == 0x00:
            if current:
                # Decode substring
                decoded = ""
                for byte in current:
                    if byte in CT_FONT:
                        decoded += CT_FONT[byte]
                    elif 0x41 <= byte <= 0x5A:
                        decoded += chr(byte)
                    elif 0x61 <= byte <= 0x7A:
                        decoded += chr(byte)
                    else:
                        decoded += '?'
                subtable.append(decoded)
                current = []
        else:
            current.append(b)
        subtable_offset += 1
    
    print(f"  Substring table: {len(subtable)} entries")
    
    # LZSS decompress
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
    
    # Decode text
    def decode_text(data, substrings):
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
                    result.append('?')
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
    
    # Find ALL LZSS blocks
    all_dialog = []
    for i in range(len(ct) - 1):
        if ct[i] in [0x10, 0x11] and ct[i+1] == 0x00:
            if i + 4 < len(ct):
                size = ct[i+2] | (ct[i+3] << 8)
                if 100 < size < 60000:
                    try:
                        result, _ = lzss_decompress(ct, i)
                        if len(result) > 20:
                            text = decode_text(result, subtable)
                            text = ' '.join(text.split())
                            if len(text) > 5:
                                all_dialog.append({
                                    "offset": hex(i),
                                    "size": size,
                                    "text": text[:200]
                                })
                    except:
                        pass
    
    # Dedupe
    seen = set()
    unique = []
    for item in all_dialog:
        if item["text"] not in seen:
            seen.add(item["text"])
            unique.append(item)
    
    print(f"  Extracted: {len(unique)} dialog entries")
    
    with open(DATA_DIR / "ct_dialog_complete.json", 'w') as f:
        json.dump(unique[:5000], f, indent=2)
    
    return unique


def extract_cc_dialog_comprehensive():
    """Extract ALL CC dialog"""
    print("\n=== Extracting Chrono Cross Dialog ===")
    
    cc = open(BASE_DIR / "Chrono Cross" / "Chrono Cross (Disc 1)" / "Chrono Cross (Disc 1).bin", 'rb').read()
    
    # CC uses shift-JIS like encoding, but we'll find ASCII patterns
    # Look for text in the early ROM region
    
    all_text = []
    
    # Search for readable text sequences
    for start in range(0, min(len(cc), 0x10000000), 10000):
        region = cc[start:start+10000]
        current = []
        text_start = None
        
        for i, b in enumerate(region):
            if 32 <= b <= 126:
                if text_start is None:
                    text_start = start + i
                current.append(chr(b))
            else:
                if current and text_start is not None:
                    text = ''.join(current)
                    if len(text) > 10 and ' ' in text:
                        # Filter for likely dialog
                        words = text.split()
                        if len(words) >= 3:
                            all_text.append({
                                "offset": hex(text_start),
                                "text": text[:100]
                            })
                current = []
                text_start = None
    
    # Dedupe
    seen = set()
    unique = []
    for item in all_text:
        if item["text"] not in seen:
            seen.add(item["text"])
            unique.append(item)
    
    print(f"  Extracted: {len(unique)} text segments")
    
    with open(DATA_DIR / "cc_dialog_complete.json", 'w') as f:
        json.dump(unique[:10000], f, indent=2)
    
    return unique


def extract_rd_dialog_comprehensive():
    """Extract ALL RD dialog"""
    print("\n=== Extracting Radical Dreamers Dialog ===")
    
    rd = open(BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc", 'rb').read()
    
    # RD uses 0x81 as word separator
    all_text = []
    current = []
    text_start = None
    
    for i, b in enumerate(rd):
        if 32 <= b <= 126:
            if text_start is None:
                text_start = i
            current.append(chr(b))
        elif b == 0x81:
            if current and text_start is not None:
                text = ''.join(current).strip()
                if len(text) > 5:
                    all_text.append({
                        "offset": hex(text_start),
                        "text": text
                    })
            current = []
            text_start = None
        else:
            if current and text_start is not None:
                text = ''.join(current).strip()
                if len(text) > 5:
                    all_text.append({
                        "offset": hex(text_start),
                        "text": text
                    })
            current = []
            text_start = None
    
    # Dedupe and filter
    seen = set()
    unique = []
    for item in all_text:
        text = item["text"]
        # Filter for meaningful English
        if len(text) > 10 and any(c.isalpha() for c in text):
            if text not in seen:
                seen.add(text)
                unique.append(item)
    
    print(f"  Extracted: {len(unique)} dialog entries")
    
    with open(DATA_DIR / "rd_dialog_complete.json", 'w') as f:
        json.dump(unique[:5000], f, indent=2)
    
    return unique


# ============ PHASE 2: BINARY STAT TABLES ============

def extract_ct_character_stats():
    """Extract CT character stat tables"""
    print("\n=== Extracting CT Character Stats ===")
    
    ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()
    
    # CT character data is at various offsets
    # Character stats: HP, MP, Attack, Defense, Speed, Magic (6 values per character)
    # 7 characters: Crono, Marle, Lucca, Robo, Frog, Ayla, Magus
    
    stats = []
    
    # Try common stat table locations
    for base in [0x1D0000, 0x1E0000, 0x1F0000, 0x200000, 0x2D0000]:
        if base + 100 < len(ct):
            region = ct[base:base+100]
            
            # Look for HP value pattern (typically 100-999)
            hp_values = []
            for i in range(0, len(region)-1, 2):
                val = region[i] | (region[i+1] << 8)
                if 50 <= val <= 999:
                    hp_values.append(val)
            
            if len(hp_values) >= 7:
                stats.append({
                    "offset": hex(base),
                    "potential_hp": hp_values[:7]
                })
    
    print(f"  Found {len(stats)} potential stat tables")
    
    with open(DATA_DIR / "ct_character_stats.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    return stats


def extract_ct_item_data():
    """Extract CT item data (names + prices)"""
    print("\n=== Extracting CT Item Data ===")
    
    ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()
    
    CT_FONT = {}
    for i in range(26):
        CT_FONT[0xA0 + i] = chr(ord('A') + i)
    for i in range(26):
        CT_FONT[0xBA + i] = chr(ord('a') + i)
    for i in range(10):
        CT_FONT[0xD4 + i] = chr(ord('0') + i)
    CT_FONT[0xEF] = ' '
    
    items = []
    
    # Search for item name + price patterns
    # Item data typically: name (text), price (2 bytes), stats
    for i in range(0x100000, 0x300000):
        if ct[i] in CT_FONT:
            # Potential item name start
            name_bytes = []
            j = i
            while j < min(i+20, len(ct)) and ct[j] in CT_FONT:
                name_bytes.append(ct[j])
                j += 1
            
            if len(name_bytes) >= 3:
                name = ''.join(CT_FONT[b] for b in name_bytes if b in CT_FONT)
                name = name.strip()
                
                # Check for price after name (2-byte value typically < 10000)
                if j + 2 < len(ct):
                    price = ct[j] | (ct[j+1] << 8)
                    if 1 <= price <= 99999:
                        items.append({
                            "offset": hex(i),
                            "name": name,
                            "price": price
                        })
    
    # Dedupe
    seen = set()
    unique = []
    for item in items:
        if item["name"] not in seen and len(item["name"]) > 2:
            seen.add(item["name"])
            unique.append(item)
    
    print(f"  Found {len(unique)} items with prices")
    
    with open(DATA_DIR / "ct_items_with_prices.json", 'w') as f:
        json.dump(unique[:500], f, indent=2)
    
    return unique


# ============ PHASE 3: ENEMY DATA ============

def extract_ct_enemy_data():
    """Extract CT enemy data"""
    print("\n=== Extracting CT Enemy Data ===")
    
    ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()
    
    CT_FONT = {}
    for i in range(26):
        CT_FONT[0xA0 + i] = chr(ord('A') + i)
    for i in range(26):
        CT_FONT[0xBA + i] = chr(ord('a') + i)
    for i in range(10):
        CT_FONT[0xD4 + i] = chr(ord('0') + i)
    CT_FONT[0xEF] = ' '
    
    enemies = []
    
    # Search for enemy patterns
    for i in range(0x100000, 0x300000):
        if ct[i] in CT_FONT:
            name_bytes = []
            j = i
            while j < min(i+15, len(ct)) and ct[j] in CT_FONT:
                name_bytes.append(ct[j])
                j += 1
            
            if len(name_bytes) >= 3:
                name = ''.join(CT_FONT[b] for b in name_bytes if b in CT_FONT)
                name = name.strip()
                
                # Check for HP after name
                if j + 4 < len(ct):
                    hp = ct[j] | (ct[j+1] << 8)
                    exp = ct[j+2] | (ct[j+3] << 8)
                    if 1 <= hp <= 99999 and 0 <= exp <= 99999:
                        enemies.append({
                            "offset": hex(i),
                            "name": name,
                            "hp": hp,
                            "exp": exp
                        })
    
    # Dedupe
    seen = set()
    unique = []
    for e in enemies:
        if e["name"] not in seen and len(e["name"]) > 2:
            seen.add(e["name"])
            unique.append(e)
    
    print(f"  Found {len(unique)} enemies with stats")
    
    with open(DATA_DIR / "ct_enemies_with_stats.json", 'w') as f:
        json.dump(unique[:500], f, indent=2)
    
    return unique


# ============ RUN ALL ============

if __name__ == "__main__":
    print("=== CHRONO SERIES COMPLETE EXTRACTION ===\n")
    
    # Phase 1: Dialog (most important)
    ct_dialog = extract_ct_dialog_comprehensive()
    cc_dialog = extract_cc_dialog_comprehensive()
    rd_dialog = extract_rd_dialog_comprehensive()
    
    # Phase 2: Binary data
    char_stats = extract_ct_character_stats()
    item_data = extract_ct_item_data()
    enemy_data = extract_ct_enemy_data()
    
    print("\n=== EXTRACTION COMPLETE ===")
    print(f"CT Dialog: {len(ct_dialog)}")
    print(f"CC Dialog: {len(cc_dialog)}")
    print(f"RD Dialog: {len(rd_dialog)}")
    print(f"CT Character Stats: {len(char_stats)}")
    print(f"CT Items: {len(item_data)}")
    print(f"CT Enemies: {len(enemy_data)}")
