#!/usr/bin/env python3
"""
Chrono Trigger - Complete LZSS Decompressor + Text Extractor
"""

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

def decompress_lzss(data, offset):
    """Decompress LZSS compressed data"""
    if offset >= len(data) or data[offset] != 0x10:
        return None
    
    # Get size
    size = data[offset + 1] | (data[offset + 2] << 8)
    if size > 0x8000 or size < 4:
        return None
    
    output = []
    src = offset + 3
    dst = 0
    
    while dst < size and src < len(data):
        flag = data[src]
        src += 1
        
        for bit in range(8):
            if dst >= size:
                break
            
            if flag & (0x80 >> bit):
                # Literal
                if src < len(data):
                    output.append(data[src])
                    src += 1
                    dst += 1
            else:
                # Copy from window
                if src + 1 < len(data):
                    ctrl = data[src] | (data[src + 1] << 8)
                    src += 2
                    
                    length = ((ctrl >> 12) & 0x0F) + 3
                    position = (ctrl & 0x0FFF)
                    
                    for _ in range(length):
                        if dst >= size:
                            break
                        if position < len(output):
                            output.append(output[position])
                            position += 1
                            dst += 1
    
    return bytes(output)

def decode_text(raw_bytes):
    """Decode CT text encoding"""
    result = []
    for b in raw_bytes:
        if b == 0:
            break
        elif 0x20 <= b <= 0x7E:
            result.append(chr(b))
        elif b >= 0x81 and b <= 0x9F:
            # Katakana-ish
            result.append(chr(b - 0x40))
        elif b >= 0xA0:
            result.append(chr(b - 0x40))
        else:
            result.append('.')
    return ''.join(result)

def extract_all_text():
    data = read_rom()
    
    print("=== CHRONO TRIGGER: DECOMPRESSING LORE ===\n")
    
    # Find and decompress ALL LZSS blocks in the game data area
    text_found = []
    
    # Search in game data area (not header, not credits at end)
    for offset in range(0x10000, 0x300000, 16):
        try:
            decompressed = decompress_lzss(data, offset)
            if decompressed and len(decompressed) > 50:
                text = decode_text(decompressed[:200])
                
                # Check for game-relevant keywords
                keywords = [
                    'TIME', 'GATE', 'KING', 'QUEEN', 'PRINCE', 'LAVOS', 'QUEEN',
                    'MAGIC', 'POWER', 'SWORD', 'SHIELD', 'HELMET', 'ARMOR',
                    'YOU', 'THE', 'AND', 'ARE', 'NOT', 'BUT', 'WAS', 'WILL',
                    'YOUR', 'MYSTERY', 'SECRET', 'PROPHECY', 'DESTINY',
                    'FUTURE', 'PAST', 'PRESENT', 'WORLD', 'EARTH',
                    'CHRONO', 'LUCCA', 'MARLE', 'FROG', 'ROBO', 'AYLA', 'MAGUS',
                    'HEAL', 'FIRE', 'ICE', 'BOLT', 'WIND', 'WATER', 'DARK', 'LIGHT'
                ]
                
                upper = text.upper()
                for kw in keywords:
                    if kw in upper:
                        # Found something!
                        clean_text = decode_text(decompressed[:100])
                        text_found.append((offset, clean_text))
                        break
        except:
            pass
    
    # Print unique findings
    print(f"Found {len(text_found)} text blocks with lore:\n")
    seen = set()
    for offset, text in text_found:
        # Deduplicate
        key = text[:40]
        if key not in seen:
            seen.add(key)
            print(f"Offset {hex(offset)}:")
            # Print first 80 chars of text
            print(f"  {text[:80]}")
            print()

if __name__ == "__main__":
    extract_all_text()
