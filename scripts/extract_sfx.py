#!/usr/bin/env python3
"""
Extract sound effects from Chrono games
"""

import json
import wave
import struct
from pathlib import Path

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"

print("=== Extracting Sound Effects ===\n")

# ============ Chrono Trigger Sound Effects ============
print("--- Chrono Trigger ---")

ct_rom = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", "rb").read()

# Sound effects in SNES are typically short, 8-bit samples
# Look for SFX-like patterns (high variation, short duration)

sfx_ct = []

# Search for SFX-like data
for i in range(0x200000, 0x300000, 256):
    region = ct_rom[i:i+256]
    
    # SFX typically has high byte variation
    unique_bytes = len(set(region))
    
    # Good SFX candidates have 100-200 unique byte values
    if 100 < unique_bytes < 200:
        # Check for audio-like patterns
        variance = sum(abs(b - 128) for b in region) / 256
        if variance > 30:  # Good audio variance
            sfx_ct.append({
                "offset": hex(i),
                "unique_bytes": unique_bytes,
                "variance": variance
            })

print(f"Found {len(sfx_ct)} potential SFX locations")

# Extract actual SFX samples
sfx_samples = []
for sfx in sfx_ct[:30]:
    offset = int(sfx["offset"], 0)
    sample_data = ct_rom[offset:offset + 2048]  # 2KB sample
    
    # Convert to WAV
    wav_data = bytearray()
    for b in sample_data:
        sample = (b - 128) * 256
        wav_data.extend(struct.pack('<h', sample))
    
    # Save
    sfx_name = f"ct_sfx_{len(sfx_samples):03d}.wav"
    sfx_path = AUDIO_DIR / sfx_name
    with wave.open(str(sfx_path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(32000)
        w.writeframes(bytes(wav_data))
    
    sfx_samples.append({"file": sfx_name, "offset": sfx["offset"]})

print(f"Saved {len(sfx_samples)} SFX samples")

# Save metadata
with open(DATA_DIR / "ct_sfx.json", "w") as f:
    json.dump(sfx_samples, f, indent=2)

# ============ Chrono Cross Sound Effects ============
print("\n--- Chrono Cross ---")

cc_bin = open(BASE_DIR / "Chrono Cross/Chrono Cross (Disc 1)/Chrono Cross (Disc 1).bin", "rb").read()

sfx_cc = []

for i in range(0x300000, min(0x500000, len(cc_bin)), 512):
    region = cc_bin[i:i+256]
    
    unique_bytes = len(set(region))
    
    if 100 < unique_bytes < 200:
        variance = sum(abs(b - 128) for b in region) / 256
        if variance > 30:
            sfx_cc.append({
                "offset": hex(i),
                "unique_bytes": unique_bytes,
                "variance": variance
            })

print(f"Found {len(sfx_cc)} potential SFX locations")

sfx_samples_cc = []
for sfx in sfx_cc[:30]:
    offset = int(sfx["offset"], 0)
    sample_data = cc_bin[offset:offset + 2048]
    
    wav_data = bytearray()
    for b in sample_data:
        sample = (b - 128) * 256
        wav_data.extend(struct.pack('<h', sample))
    
    sfx_name = f"cc_sfx_{len(sfx_samples_cc):03d}.wav"
    sfx_path = AUDIO_DIR / sfx_name
    with wave.open(str(sfx_path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(32000)
        w.writeframes(bytes(wav_data))
    
    sfx_samples_cc.append({"file": sfx_name, "offset": sfx["offset"]})

print(f"Saved {len(sfx_samples_cc)} SFX samples")

with open(DATA_DIR / "cc_sfx.json", "w") as f:
    json.dump(sfx_samples_cc, f, indent=2)

print("\n=== Sound Effect Extraction Complete ===")

# Summary
audio_files = list(AUDIO_DIR.glob("*"))
print(f"\nTotal audio files: {len(audio_files)}")
