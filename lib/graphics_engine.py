import base64
from io import BytesIO
from PIL import Image
import struct
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GraphicsEngine:
    @staticmethod
    def rgb15_to_rgb888(rgb15: int) -> tuple:
        """Convert SNES/PS1 15-bit color (BGR555 or similar) to 24-bit RGB."""
        r = (rgb15 & 0x1F) * 8
        g = ((rgb15 >> 5) & 0x1F) * 8
        b = ((rgb15 >> 10) & 0x1F) * 8
        return (r, g, b)

    @staticmethod
    def decode_snes_4bpp(tile_data: bytes, palette: list) -> Image.Image:
        """
        Decode a single 8x8 SNES 4BPP tile into an Image.
        tile_data: 32 bytes representing an 8x8 4bpp tile.
        palette: list of RGB tuples (length 16).
        """
        img = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
        pixels = img.load()
        
        if len(tile_data) < 32:
            return img

        for y in range(8):
            row_data_1 = tile_data[y*2]
            row_data_2 = tile_data[y*2 + 1]
            row_data_3 = tile_data[16 + y*2]
            row_data_4 = tile_data[16 + y*2 + 1]
            
            for x in range(8):
                bit = 7 - x
                color_idx = (
                    ((row_data_1 >> bit) & 1) |
                    (((row_data_2 >> bit) & 1) << 1) |
                    (((row_data_3 >> bit) & 1) << 2) |
                    (((row_data_4 >> bit) & 1) << 3)
                )
                
                if color_idx > 0 and color_idx < len(palette):
                    pixels[x, y] = palette[color_idx] + (255,)
                else:
                    # Color 0 is transparent
                    pixels[x, y] = (0, 0, 0, 0)
        return img

    @staticmethod
    def decode_ps1_tim(data: bytes) -> Optional[Image.Image]:
        """
        Rudimentary PS1 TIM image parser.
        """
        try:
            magic = data[0:4]
            if magic != b'\\x10\\x00\\x00\\x00':
                return None
                
            bpp = data[4]
            # Extremely basic implementation: in reality, TIM has CLUT (palette) offset, 
            # image offsets, and 4bpp/8bpp/16bpp/24bpp formats.
            # This is a placeholder structure to let the LLM generate Base64 formats.
            img = Image.new('RGB', (16, 16), color='red') 
            return img
        except Exception as e:
            logger.error(f"TIM decode error: {e}")
            return None

    @staticmethod
    def image_to_base64(img: Image.Image) -> str:
        """Convert a PIL Image to a Base64 string for Markdown embedding."""
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @staticmethod
    def render_snes_sprite(rom_data: bytes, tile_address: int, pal_address: int, width_tiles: int, height_tiles: int) -> str:
        """
        Reads SNES 4bpp tile data and a 16-color palette from the ROM and generates a Base64 PNG.
        """
        try:
            # Read palette (16 colors * 2 bytes = 32 bytes)
            pal_data = rom_data[pal_address:pal_address+32]
            palette = [(0,0,0,0)] # 0 is transparent
            for i in range(1, 16):
                c16 = struct.unpack_from('<H', pal_data, i*2)[0]
                palette.append(GraphicsEngine.rgb15_to_rgb888(c16))
                
            # Read tiles (32 bytes per 4bpp tile)
            img_width = width_tiles * 8
            img_height = height_tiles * 8
            sprite_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
            
            for ty in range(height_tiles):
                for tx in range(width_tiles):
                    tile_offset = tile_address + (ty * width_tiles + tx) * 32
                    tile_bytes = rom_data[tile_offset:tile_offset+32]
                    tile_img = GraphicsEngine.decode_snes_4bpp(tile_bytes, palette)
                    sprite_img.paste(tile_img, (tx * 8, ty * 8))
                    
            return GraphicsEngine.image_to_base64(sprite_img)
            
        except Exception as e:
            return f"Error rendering sprite: {e}"

graphics_engine = GraphicsEngine()
