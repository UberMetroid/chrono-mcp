import os
import struct
import logging

logger = logging.getLogger(__name__)

class PatchGenerator:
    """Generates standard patch files (e.g. IPS) from ROM comparisons."""
    
    @staticmethod
    def generate_ips(original_data: bytes, modified_data: bytes, out_path: str) -> bool:
        """
        Compare two byte arrays and generate a standard IPS patch.
        IPS format:
        - 5 bytes: "PATCH"
        - [Records]
            - 3 bytes: Offset
            - 2 bytes: Size
            - Size bytes: Payload
            *OR RLE Record*
            - 3 bytes: Offset
            - 2 bytes: 0x0000
            - 2 bytes: Size
            - 1 byte: RLE Value
        - 3 bytes: "EOF"
        """
        if len(original_data) != len(modified_data):
            logger.warning("Original and modified ROM sizes differ. Basic IPS generation may have issues with expansion.")
            # We can still proceed, just padding the original conceptually
        
        try:
            with open(out_path, 'wb') as f:
                f.write(b"PATCH")
                
                # Simple diffing logic
                min_len = min(len(original_data), len(modified_data))
                
                offset = 0
                while offset < min_len:
                    if original_data[offset] != modified_data[offset]:
                        # Found a difference, scan to find how long the block of differences is
                        start = offset
                        
                        # Continue until we find a match or hit EOF
                        # Optimization: allow up to a few bytes of identical data inside a diff block 
                        # to prevent massive overhead, but for simplicity we break on match.
                        # Real IPS generators allow some threshold.
                        while offset < min_len and original_data[offset] != modified_data[offset]:
                            offset += 1
                            
                        size = offset - start
                        
                        # Break up chunks > 0xFFFF
                        while size > 0:
                            chunk_size = min(size, 0xFFFF)
                            f.write(struct.pack('>I', start)[1:]) # 3-byte big-endian offset
                            f.write(struct.pack('>H', chunk_size))
                            f.write(modified_data[start:start+chunk_size])
                            start += chunk_size
                            size -= chunk_size
                    else:
                        offset += 1
                        
                # Handle expansion
                if len(modified_data) > min_len:
                    expansion_size = len(modified_data) - min_len
                    start = min_len
                    while expansion_size > 0:
                        chunk_size = min(expansion_size, 0xFFFF)
                        f.write(struct.pack('>I', start)[1:])
                        f.write(struct.pack('>H', chunk_size))
                        f.write(modified_data[start:start+chunk_size])
                        start += chunk_size
                        expansion_size -= chunk_size
                        
                f.write(b"EOF")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate IPS: {e}")
            return False

patch_generator = PatchGenerator()
