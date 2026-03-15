import logging
import capstone
from capstone import *
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MultiArchDisassembler:
    """Disassembler supporting SNES, PS1, NDS, and Switch architectures using Capstone."""
    
    ARCH_MAP = {
        "SNES": (CS_ARCH_MOS65XX, CS_MODE_LITTLE_ENDIAN), # 65816 subset (using 65xx)
        "PS1": (CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN), # R3000
        "NDS_ARM9": (CS_ARCH_ARM, CS_MODE_ARM | CS_MODE_LITTLE_ENDIAN), # ARM946E-S
        "NDS_THUMB": (CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN), # THUMB mode
        "SWITCH": (CS_ARCH_ARM64, CS_MODE_ARM | CS_MODE_LITTLE_ENDIAN) # ARMv8
    }

    def __init__(self):
        self.instances = {}
        # Pre-initialize architectures to speed up later calls
        for arch_name, (arch, mode) in self.ARCH_MAP.items():
            try:
                md = Cs(arch, mode)
                md.detail = True  # Enable details for register access
                self.instances[arch_name] = md
            except Exception as e:
                logger.error(f"Failed to initialize {arch_name} disassembler: {e}")

    def get_disassembler(self, platform: str) -> Optional[Cs]:
        """Get the specific Capstone instance for a platform."""
        # Normalize names
        if platform.upper() == "NDS":
            # Default to NDS ARM9 
            platform = "NDS_ARM9"
            
        # Support fallback map
        if platform.upper() not in self.instances:
            logger.warning(f"Architecture '{platform}' not mapped. Supported: {list(self.instances.keys())}")
            return None
            
        return self.instances[platform.upper()]

    def disassemble(self, data: bytes, start_address: int, platform: str, count: int = 0) -> List[Dict[str, Any]]:
        """
        Disassemble a block of raw bytes into assembly instructions.
        
        Args:
            data: Raw bytes to disassemble
            start_address: The base memory address these bytes reside at (for branching/labels)
            platform: The target architecture ("SNES", "PS1", "NDS", "SWITCH")
            count: Number of instructions to disassemble (0 = all available in buffer)
            
        Returns:
            A list of instruction dictionaries.
        """
        md = self.get_disassembler(platform)
        if not md:
            return [{"error": f"Unsupported platform: {platform}"}]
            
        instructions = []
        try:
            for insn in md.disasm(data, start_address, count):
                instructions.append({
                    "address": hex(insn.address),
                    "mnemonic": insn.mnemonic,
                    "op_str": insn.op_str,
                    "bytes": insn.bytes.hex(' ').upper(),
                    "size": insn.size
                })
        except Exception as e:
            logger.error(f"Disassembly error for {platform}: {e}")
            instructions.append({"error": str(e)})
            
        return instructions

# Global instance for MCP use
disassembler = MultiArchDisassembler()

def disasm_bytes(data: bytes, address: int, platform: str) -> str:
    """Helper formatting function to return a pretty string of assembly."""
    insts = disassembler.disassemble(data, address, platform)
    
    if not insts or "error" in insts[0]:
        return f"Error: {insts[0].get('error', 'Unknown') if insts else 'Empty data'}"
        
    output = [f"; Disassembly for {platform} at {hex(address)}"]
    for i in insts:
        # Format: 0x8000:  A9 05     LDA #$05
        byte_str = i['bytes'].ljust(15)
        output.append(f"{i['address']}:  {byte_str} {i['mnemonic'].ljust(8)} {i['op_str']}")
        
    return "\\n".join(output)
