#!/usr/bin/env python3
"""
Chrono Trigger - Deep Lore Extraction
Find story text, dialog, item names, enemy names
"""

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

def decompress_lzss(data, offset):
    """Full LZSS decompression"""
    if offset >= len(data) or data[offset] != 0x10:
        return None
    
    size = data[offset + 1] | (data[offset + 2] << 8)
    if size > 0x8000 or size < 32:
        return None
    
    output = []
    src = offset + 3
    end = offset + 3 + size
    
    while src < len(data) and len(output) < size:
        flags = data[src]
        src += 1
        
        for _ in range(8):
            if len(output) >= size:
                break
            
            if flags & 0x80:
                if src < len(data):
                    output.append(data[src])
                    src += 1
            else:
                if src + 1 < len(data):
                    ctrl = data[src] | (data[src+1] << 8)
                    src += 2
                    length = (ctrl >> 12) + 3
                    pos = ctrl & 0xFFF
                    
                    for _ in range(length):
                        if pos < len(output):
                            output.append(output[pos])
                        pos += 1
                        if len(output) >= size:
                            break
    
    return bytes(output)[:size]

def decode_ct_text(raw):
    """Decode Chrono Trigger's text encoding"""
    result = []
    i = 0
    while i < len(raw):
        b = raw[i]
        
        if b == 0 or b == 0xFF:
            break
        # ASCII-like range
        elif 0x20 <= b <= 0x7E:
            result.append(chr(b))
        # Control codes
        elif b == 0x0A:
            result.append('\n')
        elif b == 0x09:
            result.append(' ')
        # Extended
        else:
            result.append('.')
        i += 1
    
    return ''.join(result)

def find_all_lore():
    data = read_rom()
    
    print("=" * 60)
    print("CHRONO TRIGGER - COMPLETE LORE EXTRACTION")
    print("=" * 60)
    print()
    
    # Find ALL compressed text blocks
    print("[1] SEARCHING FOR COMPRESSED TEXT BLOCKS...")
    print("-" * 40)
    
    text_blocks = []
    
    for offset in range(0x10000, 0x350000, 100):
        try:
            decompressed = decompress_lzss(data, offset)
            if decompressed and len(decompressed) > 100:
                text = decode_ct_text(decompressed)
                
                # Count readable characters
                readable = sum(1 for c in text if c.isalpha() or c.isspace())
                if readable > len(text) * 0.5 and len(text) > 50:
                    # Check for game keywords
                    keywords = [
                        'TIME', 'GATE', 'LAVOS', 'WORLD', 'FUTURE', 'PAST', 'DESTINY',
                        'PROPHECY', 'CHRONO', 'MAGIC', 'POWER', 'SWORD', 'DARK', 'LIGHT',
                        'THE', 'AND', 'YOU', 'YOUR', 'HAVE', 'WILL', 'WHEN', 'WHERE',
                        'KING', 'QUEEN', 'PRINCE', 'KNIGHT', 'GUARD', 'WIZARD',
                        'FIRE', 'ICE', 'WIND', 'WATER', 'EARTH', 'THUNDER', 'HEAL',
                        'BEGIN', 'START', 'OPEN', 'CLOSE', 'USE', 'GET', 'FIND', 'LOOK',
                        'SPEAK', 'TALK', 'WALK', 'RUN', 'STOP', 'WAIT', 'COME', 'GO'
                    ]
                    
                    upper = text.upper()
                    for kw in keywords:
                        if kw in upper:
                            text_blocks.append((offset, text[:150]))
                            break
        except:
            pass
    
    # Deduplicate and print
    print(f"Found {len(text_blocks)} text blocks with lore!\n")
    
    seen = set()
    count = 0
    for offset, text in text_blocks:
        key = text[:40].strip()
        if key and key not in seen:
            seen.add(key)
            count += 1
            print(f"[{count}] Offset {hex(offset)}:")
            # Pretty print the text
            words = text.split()
            line = ""
            for word in words:
                if len(line + " " + word) > 60:
                    print("    " + line)
                    line = word
                else:
                    line = (line + " " + word).strip()
            if line:
                print("    " + line)
            print()
            
            if count >= 15:
                break
    
    # Find specific data
    print("\n[2] CHARACTER DATA AREAS")
    print("-" * 40)
    
    # Search for character names in uncompressed areas
    for name in [b'CRONO', b'LUCCA', b'MARLE', b'FROG', b'ROBO', b'AYLA', b'MAGUS']:
        pos = data.find(name)
        if pos != -1 and pos > 0x200000:
            print(f"  {name.decode()}: {hex(pos)}")
            # Show nearby
            ctx = decode_ct_text(data[pos:pos+40])
            print(f"    Context: {ctx}")
    
    print("\n[3] ITEM/TECH DATA")  
    print("-" * 40)
    
    # Find item names
    for item in [b'POTION', b'ETHER', b'REVIVE', b'ELIXIR', b'MASAMUNE', b'RAINBOW']:
        pos = data.find(item)
        if pos != -1 and pos > 0x200000:
            print(f"  {item.decode()}: {hex(pos)}")
    
    print("\n[4] LOCATION DATA")
    print("-" * 40)
    
    # Find location names
    for loc in [b'TRESOR', b'ZEAL', b'MEDIA', b'OCEAN', b'NORTH', b'SOUTH']:
        pos = data.find(loc)
        if pos != -1 and pos > 0x200000:
            print(f"  {loc.decode()}: {hex(pos)}")

if __name__ == "__main__":
    find_all_lore()
