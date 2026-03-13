#!/usr/bin/env python3
"""
Chrono Trigger - SNES Text Extraction
Try multiple decompression methods
"""

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

def decompress_lzss_v(data, offset):
    """Try multiple LZSS variations"""
    if offset + 4 > len(data):
        return None
    
    if data[offset] != 0x10:
        # Try other signatures
        if data[offset] == 0x11:
            offset += 1
        else:
            return None
    
    # Get size (can be big-endian or little-endian)
    size = data[offset + 1] | (data[offset + 2] << 8)
    
    if size > 0x10000 or size < 16:
        return None
    
    output = []
    src = offset + 3
    copied = 0
    
    while copied < size and src < len(data):
        flags = data[src]
        src += 1
        
        for _ in range(8):
            if copied >= size:
                break
            
            if flags & 0x80:
                # Literal
                if src < len(data):
                    output.append(data[src])
                    src += 1
                    copied += 1
            else:
                # Compression
                if src + 1 < len(data):
                    ctrl = (data[src] << 8) | data[src + 1]
                    src += 2
                    
                    length = ((ctrl >> 12) & 0xF) + 2
                    position = ctrl & 0xFFF
                    
                    for _ in range(length):
                        if position < len(output):
                            output.append(output[position])
                            copied += 1
                        position += 1
                        if copied >= size:
                            break
    
    return bytes(output[:size])

def try_text_block(data, offset):
    """Try to extract text from a block"""
    try:
        result = decompress_lzss_v(data, offset)
        if result and len(result) > 30:
            # Count printable ASCII
            printable = sum(1 for b in result if 0x20 <= b <= 0x7E)
            if printable > len(result) * 0.6:
                return result
    except:
        pass
    return None

def main():
    data = read_rom()
    
    print("=" * 60)
    print("CHRONO TRIGGER - GAME TEXT EXTRACTION")
    print("=" * 60)
    print()
    
    # Search EVERY offset for compressed text
    print("[*] Scanning entire ROM for text blocks...")
    
    found = []
    keywords = ['TIME', 'GATE', 'LAVOS', 'FUTURE', 'PAST', 'CHRONO', 'KING', 'QUEEN', 
                'THE', 'AND', 'YOU', 'YOUR', 'HAVE', 'WILL', 'WHERE', 'WHEN',
                'BEGIN', 'START', 'STOP', 'WAIT', 'OPEN', 'CLOSE', 'LOOK', 'USE']
    
    for offset in range(0x10000, 0x380000, 50):
        try:
            result = try_text_block(data, offset)
            if result:
                text = ''.join(chr(b) if 0x20 <= b <= 0x7E else '.' for b in result[:200])
                upper = text.upper()
                
                for kw in keywords:
                    if kw in upper:
                        found.append((offset, text[:100]))
                        break
        except:
            pass
    
    print(f"Found {len(found)} blocks\n")
    
    # Print unique
    seen = set()
    count = 0
    for offset, text in found:
        key = text[:30].strip('.')
        if key and key not in seen:
            seen.add(key)
            count += 1
            print(f"[{count}] {hex(offset)}: {text[:70]}")
            
            if count >= 20:
                break
    
    # Try finding uncompressed strings directly
    print("\n" + "=" * 60)
    print("SEARCHING UNCOMPRESSED STRINGS")
    print("=" * 60)
    
    # Search for sequences of readable characters
    print("\n[*] Finding text sequences...")
    
    sequences = []
    i = 0
    current = []
    start = 0
    
    while i < len(data) - 10:
        b = data[i]
        
        if 0x30 <= b <= 0x39 or 0x41 <= b <= 0x5A or 0x61 <= b <= 0x7A or b in [0x20, 0x2E, 0x2C, 0x27]:
            if not current:
                start = i
            current.append((i, chr(b) if b < 128 else '.'))
        else:
            if len(current) >= 10:
                text = ''.join(c for _, c in current)
                sequences.append((start, text))
            current = []
        
        i += 1
    
    # Filter for game-related
    print("\n[*] Game-related strings:")
    game_words = ['TIME', 'GATE', 'LAVOS', 'KING', 'QUEEN', 'KNIGHT', 'MAGIC', 
                  'POWER', 'SWORD', 'DARK', 'LIGHT', 'FIRE', 'ICE', 'HEAL', 
                  'BEGIN', 'START', 'WORLD', 'EARTH', 'HEAVEN', 'HELL']
    
    seen = set()
    count = 0
    for offset, text in sequences:
        upper = text.upper()
        for gw in game_words:
            if gw in upper and offset > 0x10000:
                key = text[:25]
                if key not in seen:
                    seen.add(key)
                    count += 1
                    print(f"  {hex(offset)}: {text[:50]}")
                    if count >= 20:
                        break
        if count >= 20:
            break

if __name__ == "__main__":
    main()
