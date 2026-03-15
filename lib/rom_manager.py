import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class RomManagerException(Exception):
    pass

class RomFile:
    """Base class for all ROM handlers."""
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.rom_data = bytearray()
        self.platform = "Unknown"
        self.is_loaded = False
        
    def load(self) -> bool:
        """Load the ROM data into memory."""
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"ROM file not found: {self.file_path}")
            
            with open(self.file_path, 'rb') as f:
                self.rom_data = bytearray(f.read())
            self.is_loaded = True
            logger.info(f"Successfully loaded {self.platform} ROM: {self.file_path.name} ({len(self.rom_data)} bytes)")
            return True
        except Exception as e:
            logger.error(f"Failed to load ROM: {e}")
            return False
            
    def save(self, output_path: Optional[str] = None) -> bool:
        """Save the modified ROM data back to disk."""
        if not self.is_loaded:
            raise RomManagerException("Cannot save: ROM is not loaded.")
            
        out_path = Path(output_path) if output_path else self.file_path
        
        try:
            with open(out_path, 'wb') as f:
                f.write(self.rom_data)
            logger.info(f"Successfully saved ROM to {out_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save ROM: {e}")
            return False
            
    def get_info(self) -> Dict[str, Any]:
        """Return basic information about the ROM."""
        info = {
            "file_name": self.file_path.name,
            "platform": self.platform,
            "size_bytes": len(self.rom_data),
            "md5": hashlib.md5(self.rom_data).hexdigest() if self.is_loaded else None
        }
        return info

class SnesRom(RomFile):
    """Handler for Super Nintendo (SFC/SMC) ROMs."""
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.platform = "SNES"
        self.has_header = False
        self.mapping = "Unknown" # LoROM or HiROM
        
    def load(self) -> bool:
        if not super().load():
            return False
            
        # Detect SMC header (512 bytes)
        # SNES ROMs without header are multiples of 32KB
        if len(self.rom_data) % 0x8000 == 512:
            self.has_header = True
            # Strip the header for easier memory mapping
            self.rom_data = self.rom_data[512:]
            logger.info("Detected and stripped 512-byte SMC header.")
            
        self._detect_mapping()
        return True
        
    def _detect_mapping(self):
        """Simple heuristic to detect LoROM vs HiROM based on internal header."""
        # SNES internal header locations
        lorom_header = 0x7FC0
        hirom_header = 0xFFC0
        
        # Check HiROM first
        if len(self.rom_data) >= hirom_header + 0x30:
            hirom_checksum = int.from_bytes(self.rom_data[hirom_header+0x2E:hirom_header+0x30], 'little')
            hirom_inverse = int.from_bytes(self.rom_data[hirom_header+0x2C:hirom_header+0x2E], 'little')
            if hirom_checksum + hirom_inverse == 0xFFFF:
                self.mapping = "HiROM"
                return
                
        # Check LoROM
        if len(self.rom_data) >= lorom_header + 0x30:
            lorom_checksum = int.from_bytes(self.rom_data[lorom_header+0x2E:lorom_header+0x30], 'little')
            lorom_inverse = int.from_bytes(self.rom_data[lorom_header+0x2C:lorom_header+0x2E], 'little')
            if lorom_checksum + lorom_inverse == 0xFFFF:
                self.mapping = "LoROM"
                return
                
        # Chrono Trigger specific check (HiROM)
        if len(self.rom_data) > hirom_header and b"CHRONO TRIGGER" in self.rom_data[hirom_header:hirom_header+21]:
            self.mapping = "HiROM"
            return
            
        # Radical Dreamers specific check (LoROM)
        if len(self.rom_data) > lorom_header and b"RADICAL DREAMERS" in self.rom_data[lorom_header:lorom_header+21]:
            self.mapping = "LoROM"
            return
            
    def read_bytes(self, snes_address: int, length: int) -> bytearray:
        """Read bytes using SNES memory mapping (e.g. $C00000)."""
        pc_offset = self.snes_to_pc(snes_address)
        if pc_offset < 0 or pc_offset + length > len(self.rom_data):
            raise ValueError(f"Address out of bounds: {hex(snes_address)}")
        return self.rom_data[pc_offset:pc_offset+length]
        
    def write_bytes(self, snes_address: int, data: bytes) -> bool:
        """Write bytes to SNES memory address."""
        pc_offset = self.snes_to_pc(snes_address)
        if pc_offset < 0 or pc_offset + len(data) > len(self.rom_data):
            raise ValueError(f"Address out of bounds: {hex(snes_address)}")
            
        self.rom_data[pc_offset:pc_offset+len(data)] = data
        self._fix_checksum()
        return True
        
    def snes_to_pc(self, snes_address: int) -> int:
        """Convert a 65816 memory address to a physical ROM file offset."""
        bank = (snes_address >> 16) & 0xFF
        offset = snes_address & 0xFFFF
        
        if self.mapping == "HiROM":
            # HiROM mapping: Bank $C0-$FF mirrors $00-$3F
            bank = bank & 0x3F
            return (bank << 16) | offset
        elif self.mapping == "LoROM":
            # LoROM mapping
            bank = bank & 0x7F
            offset = offset & 0x7FFF
            return (bank << 15) | offset
        else:
            # Fallback - assume direct map
            return snes_address
            
    def _fix_checksum(self):
        """Recalculate and fix the internal SNES checksum."""
        # Setup header location
        header_offset = 0xFFC0 if self.mapping == "HiROM" else 0x7FC0
        
        # Clear checksum and inverse before calculating
        if len(self.rom_data) >= header_offset + 0x30:
            self.rom_data[header_offset+0x2C:header_offset+0x30] = b'\\xFF\\xFF\\x00\\x00'
            
        # Calculate sum
        # SNES checksums are typically the sum of all bytes in the ROM
        # Handling powers of 2 size differences isn't fully implemented here,
        # but a simple sum works for clean 32mbit/16mbit dumps.
        total_sum = sum(self.rom_data) & 0xFFFF
        inverse = total_sum ^ 0xFFFF
        
        # Write back
        if len(self.rom_data) >= header_offset + 0x30:
            self.rom_data[header_offset+0x2C:header_offset+0x2E] = inverse.to_bytes(2, 'little')
            self.rom_data[header_offset+0x2E:header_offset+0x30] = total_sum.to_bytes(2, 'little')

    def get_info(self) -> Dict[str, Any]:
        info = super().get_info()
        info.update({
            "has_smc_header": self.has_header,
            "mapping": self.mapping
        })
        return info


class Ps1Rom(RomFile):
    """Handler for PS1 BIN/CUE/ISO files."""
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.platform = "PS1"
        self.is_bin = self.file_path.suffix.lower() in [".bin", ".img"]
        
    def extract_file(self, internal_path: str, out_path: str) -> bool:
        """Extract a file from the PS1 ISO. (Placeholder)"""
        # Normally uses pycdlib to extract files from ISO9660 filesystem
        logger.warning("PS1 extraction requires pycdlib implementation.")
        return False
        
    def inject_file(self, internal_path: str, in_path: str) -> bool:
        """Inject a file back into the PS1 ISO. (Placeholder)"""
        logger.warning("PS1 injection requires pycdlib implementation.")
        return False


class NdsRom(RomFile):
    """Handler for Nintendo DS (NDS) ROMs using ndspy."""
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.platform = "NDS"
        self.nds_obj = None
        
    def load(self) -> bool:
        try:
            import ndspy.rom
            if not self.file_path.exists():
                raise FileNotFoundError(f"NDS file not found: {self.file_path}")
            self.nds_obj = ndspy.rom.NintendoDSRom.fromFile(str(self.file_path))
            self.is_loaded = True
            logger.info(f"Successfully loaded NDS ROM: {self.nds_obj.name.decode('utf-8', 'ignore')}")
            return True
        except ImportError:
            logger.error("ndspy library not installed. Cannot load NDS ROM.")
            return False
        except Exception as e:
            logger.error(f"Failed to load NDS ROM: {e}")
            return False
            
    def save(self, output_path: Optional[str] = None) -> bool:
        if not self.is_loaded or not self.nds_obj:
            raise RomManagerException("Cannot save: NDS ROM is not loaded.")
        out_path = Path(output_path) if output_path else self.file_path
        try:
            self.nds_obj.saveToFile(str(out_path))
            logger.info(f"Successfully saved NDS ROM to {out_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save NDS ROM: {e}")
            return False
            
    def extract_file(self, internal_path: str, out_path: str) -> bool:
        """Extract a file from the NDS filesystem."""
        if not self.is_loaded: return False
        try:
            file_id = self.nds_obj.filenames.idOf(internal_path)
            data = self.nds_obj.files[file_id]
            with open(out_path, 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            logger.error(f"NDS extract error: {e}")
            return False
            
    def inject_file(self, internal_path: str, in_path: str) -> bool:
        """Inject a modified file back into the NDS filesystem."""
        if not self.is_loaded: return False
        try:
            with open(in_path, 'rb') as f:
                data = f.read()
            file_id = self.nds_obj.filenames.idOf(internal_path)
            self.nds_obj.files[file_id] = data
            return True
        except Exception as e:
            logger.error(f"NDS inject error: {e}")
            return False


class SwitchRomManager:
    """
    Manager for Nintendo Switch Mods.
    Switch modding usually avoids touching NSP/XCI directly due to encryption.
    Instead, we build a LayeredFS mod structure that the emulator/console loads.
    """
    def __init__(self, title_id: str, mod_name: str, base_dir: str = "./mods"):
        self.platform = "Switch"
        self.title_id = title_id.upper()
        self.mod_name = mod_name
        self.mod_dir = Path(base_dir) / mod_name / "contents" / self.title_id / "romfs"
        
    def init_mod_structure(self):
        """Create the LayeredFS folder structure for this mod."""
        os.makedirs(self.mod_dir, exist_ok=True)
        logger.info(f"Created LayeredFS mod structure for {self.title_id} at {self.mod_dir}")
        return str(self.mod_dir)
        
    def inject_file(self, internal_romfs_path: str, local_file_path: str) -> bool:
        """Copy a modified file into the LayeredFS mod folder, mirroring the romfs path."""
        target_path = self.mod_dir / internal_romfs_path.lstrip('/')
        os.makedirs(target_path.parent, exist_ok=True)
        try:
            shutil.copy2(local_file_path, target_path)
            logger.info(f"Injected {local_file_path} -> {target_path}")
            return True
        except Exception as e:
            logger.error(f"Switch LayeredFS inject error: {e}")
            return False


def create_rom_handler(file_path: str) -> Optional[RomFile]:
    """Factory function to instantiate the correct RomFile handler."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    ext = path.suffix.lower()
    
    if ext in [".sfc", ".smc", ".fig"]:
        return SnesRom(file_path)
    elif ext in [".bin", ".iso", ".img", ".cue"]:
        return Ps1Rom(file_path)
    elif ext in [".nds", ".srl"]:
        return NdsRom(file_path)
    else:
        logger.warning(f"Unsupported ROM extension: {ext}. Using raw fallback.")
        return RomFile(file_path)
