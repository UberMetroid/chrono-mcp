#!/usr/bin/env python3
"""
Chrono Trigger ROM - LZSS Decompressor + Text Extractor
"""

ROM_PATH = "/home/jeryd/Code/Chrono_Series/Chrono Trigger/Chrono Trigger (USA).sfc"

def read_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

def decompress_lzss(data, offset):
    """Decompress LZSS compressed data starting at offset"""
    if offset >= len(data):
        return None, 0
    
    # Check for LZSS signature
    if data[offset] != 0x10:
        return None, 0
    
    # Get uncompressed size
    size = data[offset + 1] | (data[offset + 2] << 8)
    if size > 0x4000:  # Sanity check
        return None, 0
    
    output = bytearray()
    pos = offset + 3
    end_pos = pos + size
    
    while pos < len(data) and len(output) < size:
        flags = data[pos]
        pos += 1
        
        for bit in range(8):
            if len(output) >= size:
                break
            
            if flags & (0x80 >> bit):
                # Literal byte
                if pos < len(data):
                    output.append(data[pos])
                    pos += 1
            else:
                # Back-reference
                if pos + 1 < len(data):
                    ctrl = data[pos] | (data[pos + 1] << 8)
                    pos += 2
                    
                    length = (ctrl >> 12) + 3
                    offset_addr = ctrl & 0x0FFF
                    
                    # Copy from output buffer
                    copy_pos = len(output) - offset_addr - 1
                    for i in range(length):
                        if copy_pos >= 0 and copy_pos < len(output):
                            output.append(output[copy_pos])
                        copy_pos += 1
    
    return bytes(output), pos - offset

def decode_ct_text(compressed_data):
    """Decode Chrono Trigger's text encoding"""
    if not compressed_data:
        return ""
    
    result = []
    i = 0
    while i < len(compressed_data):
        b = compressed_data[i]
        
        if b == 0x00:
            break  # End of string
        elif b == 0x01:
            result.append('\n')
        elif b == 0x02:
            result.append(' ')
        elif 0x10 <= b <= 0x19:
            # Number
            result.append(f'#{b-0x0F}')
        elif 0x1A <= b <= 0x23:
            # Control codes
            result.append(f'[{b:02X}]')
        elif 0x30 <= b <= 0x7E:
            # ASCII-like range
            result.append(chr(b))
        elif 0x80 <= b <= 0x9F:
            # Extended Katakana
            result.append(f'[{b:02X}]')
        elif 0xA0 <= b <= 0xDF:
            # More Katakana
            result.append(f'[{b:02X}]')
        elif 0xE0 <= b <= 0xFF:
            # Kanji or special
            if b == 0xE0:
                result.append(' ')
            else:
                result.append(f'[{b:02X}]')
        else:
            result.append(f'[{b:02X}]')
        
        i += 1
    
    return ''.join(result)

def find_and_decompress_texts():
    data = read_rom()
    
    print("=== DECOMPRESSING CHRONO TRIGGER ===\n")
    
    # Find compressed text blocks - look for ones that decompress to readable text
    text_blocks = []
    
    # Search common areas where text is stored
    for offset in range(0x10000, 0x300000, 0x1000):
        if offset + 3 >= len(data):
            break
            
        if data[offset] == 0x10:
            try:
                decompressed, _ = decompress_lzss(data, offset)
                if decompressed:
                    text = decode_ct_text(decompressed[:200])
                    # Check if it looks like game text
                    if any(word in text.upper() for word in ['THE', 'AND', 'YOU', 'ARE', 'TIME', 'GATE', 'HP', 'MP', 'LVL']):
                        text_blocks.append((offset, text[:100]))
            except:
                pass
    
    print(f"Found {len(text_blocks)} text blocks:\n")
    for offset, text in text_blocks[:30]:
        print(f"  Offset {hex(offset)}:")
        print(f"    {text}")
        print()

if __name__ == "__main__":
    find_and_decompress_texts()
