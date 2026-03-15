import logging

logger = logging.getLogger(__name__)

class TextEncoder:
    """
    Handles translation between standard UTF-8 strings and 
    custom ROM encodings (DTE for SNES, Shift-JIS for NDS, etc).
    """
    def __init__(self):
        # A simple mock DTE (Dual-Tile Encoding) dictionary for Chrono Trigger (SNES)
        # In a real scenario, this would be 100+ mappings derived from the ROM's dictionary table.
        self.dte_map = {
            0x00: "th", 0x01: "er", 0x02: "in", 0x03: "ou",
            0x04: "an", 0x05: "en", 0x06: "re", 0x07: "he",
            0x08: "on", 0x09: "st", 0x0A: "ve", 0x0B: "ll",
            # Standard ASCII offsets
            0x20: " ", 0x41: "A", 0x42: "B", 0x43: "C",
            0x61: "a", 0x62: "b", 0x63: "c", 
            # Control codes
            0x0B: "[LINE]", 0x00: "[END]" 
        }
        
        # Build reverse map
        self.reverse_dte = {v: k for k, v in self.dte_map.items() if not v.startswith("[")}

    def encode_text(self, text: str, platform: str) -> bytes:
        """Encode standard text into game-specific byte arrays."""
        platform = platform.upper()
        if platform in ["SNES", "PS1"]:
            # Perform DTE compression
            out_bytes = bytearray()
            i = 0
            while i < len(text):
                # Try to match 2-character DTE first
                if i + 1 < len(text):
                    pair = text[i:i+2]
                    if pair in self.reverse_dte:
                        out_bytes.append(self.reverse_dte[pair])
                        i += 2
                        continue
                        
                # Match single char
                char = text[i]
                if char in self.reverse_dte:
                    out_bytes.append(self.reverse_dte[char])
                else:
                    # Fallback to ascii offset or placeholder
                    out_bytes.append(0x20) # Space
                i += 1
            return bytes(out_bytes)
            
        elif platform == "NDS":
            # NDS commonly uses Shift-JIS or UTF-16LE
            try:
                return text.encode('shift_jis')
            except:
                return text.encode('utf-8')
                
        elif platform == "SWITCH":
            # Switch generally uses standard UTF-8
            return text.encode('utf-8')
            
        return text.encode('ascii', errors='ignore')

    def decode_text(self, data: bytes, platform: str) -> str:
        """Decode game-specific byte arrays into standard text."""
        platform = platform.upper()
        if platform in ["SNES", "PS1"]:
            out_str = ""
            for b in data:
                if b in self.dte_map:
                    out_str += self.dte_map[b]
                else:
                    out_str += f"[{hex(b)}]"
            return out_str
            
        elif platform == "NDS":
            try:
                return data.decode('shift_jis')
            except:
                return data.decode('utf-8', errors='ignore')
                
        elif platform == "SWITCH":
            return data.decode('utf-8', errors='ignore')
            
        return data.decode('ascii', errors='ignore')

text_encoder = TextEncoder()
