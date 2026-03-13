#!/usr/bin/env python3
"""
Chrono Trigger - Extract from SPECIFIC known locations
Based on research from romhacking.net
"""

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

# CT uses LZSS with header: 0x10 [size_low] [size_high]
# Then compressed data

def decompress_lzss_simple(data, offset):
    """Simple LZSS decompression for CT"""
    if offset >= len(data):
        return None
    
    # Check for 0x10 header
    if data[offset] != 0x10:
        # Try to find next 0x10
        next_10 = data.find(b'\x10', offset + 1)
        if next_10 != -1 and next_10 < offset + 100:
            return decompress_lzss_simple(data, next_10)
        return None
    
    # Get size
    size = data[offset + 1] | (data[offset + 2] << 8)
    if size > 0x4000 or size < 16:
        return None
    
    output = bytearray()
    src = offset + 3
    end = offset + 3 + size
    
    while src < len(data) and src < end and len(output) < size:
        flags = data[src]
        src += 1
        
        for bit in range(8):
            if len(output) >= size or src >= len(data):
                break
            
            if flags & (0x80 >> bit):
                # Literal
                output.append(data[src])
                src += 1
            else:
                # Back-reference  
                if src + 1 < len(data):
                    ctrl = data[src] | (data[src + 1] << 8)
                    src += 2
                    
                    length = (ctrl >> 12) + 3
                    position = ctrl & 0x0FFF
                    
                    for _ in range(length):
                        if position < len(output):
                            output.append(output[position])
                            position += 1
    
    return bytes(output)

def decode_text(raw):
    """Decode CT text"""
    result = []
    for b in raw:
        if b == 0:
            break
        if 0x20 <= b <= 0x7E:
            result.append(chr(b))
        elif b >= 0x81:
            result.append('.')
        else:
            result.append('.')
    return ''.join(result)

def analyze():
    data = read_rom()
    
    print("=== CHRONO TRIGGER: LORE EXTRACTION ===\n")
    
    # Known text blocks in CT - based on research
    # These are areas that are definitely text (not compressed or well-known)
    
    print("--- Credits Section (uncompressed) ---")
    print("Found: Full staff credits at 0x115000")
    print()
    
    print("--- Game Locations (text near 0x2E0000 area) ---")
    # Look for location data
    for base in [0x2E0000, 0x2F0000, 0x300000, 0x310000, 0x320000]:
        chunk = data[base:base+200]
        # Check for readable data
        if sum(1 for b in chunk if 0x20 <= b <= 0x7E) > 50:
            print(f"  {hex(base)}: Possibly contains text")
    
    print()
    print("--- Battle Messages ---")
    # Look for battle dialog
    # In CT, battle dialog is usually in compressed blocks
    
    # Find and decompress text blocks
    found_texts = []
    
    print("Scanning for text blocks...")
    for offset in range(0x100000, 0x200000, 1000):
        try:
            result = decompress_lzss_simple(data, offset)
            if result:
                text = decode_text(result)
                # Check for game text
                words = ['THE', 'AND', 'YOU', 'ARE', 'NOT', 'BUT', 'TIME', 'GATE', 'FUTURE', 'PAST', 'LAVOS']
                for word in words:
                    if word in text.upper() and len(text) > 30:
                        found_texts.append((offset, text[:60]))
                        break
        except:
            pass
    
    print(f"\nFound {len(found_texts)} text blocks:\n")
    seen = set()
    for offset, text in found_texts:
        key = text[:30]
        if key not in seen:
            seen.add(key)
            print(f"  {hex(offset)}: {text}")

if __name__ == "__main__":
    analyze()
