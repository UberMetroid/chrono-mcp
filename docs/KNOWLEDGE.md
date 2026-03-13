# Chrono Series Knowledge Base

## ROMs Available

### Chrono Trigger
- **Chrono Trigger (USA).sfc** - 4MB SNES ROM (HiROM)
  - Size: 4,194,304 bytes
  - Location: `Chrono Trigger/Chrono Trigger (USA).sfc`
  - Known: LZSS compressed text, credits at 0x115000

- **Chrono Trigger (USA) (En,Fr).nds** - NDS port
  - Size: 134,217,728 bytes

### Chrono Cross (PS1)
- **Disc 1**: Chrono Cross (Disc 1).bin - 736MB (bin/cue format)
- **Disc 2**: Chrono Cross (Disc 2).bin
- Format: PlayStation 1 CD-ROM

### Radical Dreamers (SNES)
- **BS Radical Dreamers - Le Tresor Interdit (Japan)** [T-En by Demiforce v1.4]
- Size: 2MB SNES ROM
- Note: Fan translation, Satellaview variant

---

## Technical Findings

### Chrono Trigger (SNES)

#### ROM Structure
- Type: HiROM
- Size: 4MB
- Header at: 0xFFC0 (contains "CHRONO TRIGGER")

#### Compression
- LZSS compression used extensively (~25,850 compressed blocks)
- Signature: 0x10 header bytes
- Challenge: Need to properly decompress to extract dialog

#### Found Data
- **Credits** at 0x115000:
  - Producer: Kazuhiko Aoki
  - Director: Takashi Tokita, Yoshinori Kitas
  - Character Design: Akira Toriyama
  - Story Plan: Masato Kato
  - Music: Yasunori Mitsuda, Nobuo Uematsu

- **Characters** (7 playable):
  - Crono, Lucca, Marle, Frog, Robo, Ayla, Magus

#### Text Encoding
- SNES uses custom encoding (not plain ASCII)
- Text heavily compressed with LZSS algorithm

---

## Scripts

| Script | Purpose |
|--------|---------|
| `ct_explorer.py` | Basic ROM analysis |
| `ct_explorer2.py` | Improved analysis |
| `ct_decompress.py` | LZSS decompression attempts |
| `ct_find_text.py` | Text finding |
| `ct_lore.py` | Lore exploration |
| `ct_data.py` | Game data extraction |
| `ct_extract_lore.py` | Lore extraction via decompression |
| `ct_text_final.py` | Final text extraction attempt |
| `ct_deep_lore.py` | Deep lore search |
| `ct_extract.py` | Another extraction method |
| `ct_forensic.py` | Forensic ROM analysis |

---

## Extraction Results

### Radical Dreamers - FULL DIALOG EXTRACTED ✓
- Text region: 0x1C0000-0x1D0000 (and 0x150000-0x160000)
- **6,286 dialog lines extracted**
- Characters: Kid, Magil, Frozen Flame, Serge, Lynx, Viper
- Story: Treasure hunting in Viper Manor, time-travel elements
- Locations: Viper Manor, Forest, Sea, Cave, Beach

### Chrono Cross (PS1) - Limited Extraction
- Text found at 0x25ef52: "SAVE DATA TO YOUR MEMORY CARD"
- Text at 0x9340: "CHRONOCROSS" title  
- PS1 encoding - requires different extraction method
- Characters found: Serge, Kid, Harle, Lynx, Koris, Mach, etc.
- Note: Text is encoded, not plain ASCII

### Chrono Trigger (SNES) - Limited Extraction
- Almost all text is LZSS compressed (~9,694 blocks)
- **Full credits extracted** at 0x115000: 27 entries
- Characters: Crono, Lucca, Marle, Frog, Robo, Ayla, Magus
- Need proper LZSS decompression to extract dialog

---

## Data Files

All extracted data saved to `/home/jeryd/Code/Chrono_Series/data/`:

### Text Data
| File | Contents |
|------|----------|
| `radical_dreamers.json` | Game metadata, character/location refs |
| `radical_dreamers_dialog.json` | 6,286 dialog lines |
| `chrono_trigger.json` | Credits, character refs, LZSS count |
| `chrono_cross.json` | Character/location refs |
| `chrono_cross_menu.json` | Menu text |
| `index.json` | Master index |

### Art/Graphics Data (`data/art/`)
| Category | Count |
|----------|-------|
| Chrono Cross TIM images | 202 |
| Chrono Trigger tile regions | 50 |
| Radical Dreamers tile regions | 50 |
| Music/sound regions | 43 |
| **Total art files** | **190** |

#### Art Files Include:
- `.bin` files: Raw graphic data chunks (16KB-64KB each)
- `.tim` files: PS1 TIM format images (32KB each)
- `.json` files: Metadata about found graphics

---

## Scripts Created

| Script | Purpose |
|--------|---------|
| `lib/chrono.py` | Shared library for ROM analysis |
| `mcp/src/main.py` | MCP server with FastMCP |
| `explore_all.py` | Explore all ROMs |
| `explore_radical.py` | Deep dive into Radical Dreamers |
| `extract_dialog.py` | Find dialog regions |
| `extract_rd_dialog.py` | Extract Radical Dreamers script |

---

## Next Steps

1. Extract game data (items, enemies, characters) from Radical Dreamers
2. Fix LZSS decompression for Chrono Trigger
3. Extract Chrono Cross data
4. Build MCP tools for community
