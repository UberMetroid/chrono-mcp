#!/usr/bin/env python3
"""
Extract and convert Chrono audio to playable formats
"""

from pathlib import Path
import json
import wave
import struct

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"

print("=== Converting Audio to WAV ===\n")

# ============ CT Audio ============
print("--- Chrono Trigger ---")

ct_raw = AUDIO_DIR / "ct_music_sample.raw"
if ct_raw.exists():
    # Read raw 8-bit PCM
    with open(ct_raw, 'rb') as f:
        raw_data = f.read()
    
    # Convert 8-bit PCM to 16-bit PCM WAV
    wav_data = bytearray()
    
    for b in raw_data:
        # Convert 0-255 to signed 16-bit
        sample = (b - 128) * 256
        wav_data.extend(struct.pack('<h', sample))
    
    # Write WAV file
    ct_wav = AUDIO_DIR / "ct_music_sample.wav"
    with wave.open(str(ct_wav), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(32000)
        w.writeframes(bytes(wav_data))
    
    print(f"  Created: {ct_wav}")
    print(f"  Size: {len(wav_data)} bytes")

# ============ RD Audio ============
print("\n--- Radical Dreamers ---")

rd_raw = AUDIO_DIR / "rd_music_sample.raw"
if rd_raw.exists():
    with open(rd_raw, 'rb') as f:
        raw_data = f.read()
    
    wav_data = bytearray()
    for b in raw_data:
        sample = (b - 128) * 256
        wav_data.extend(struct.pack('<h', sample))
    
    rd_wav = AUDIO_DIR / "rd_music_sample.wav"
    with wave.open(str(rd_wav), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(32000)
        w.writeframes(bytes(wav_data))
    
    print(f"  Created: {rd_wav}")

# ============ Extract Multiple CT Tracks ============
print("\n--- Extracting Multiple CT Tracks ---")

ct = open(BASE_DIR / "Chrono Trigger" / "Chrono Trigger (USA).sfc", 'rb').read()

# Find multiple music tracks by looking for music header patterns
# Music tracks typically have sequence data

def find_music_tracks(data, count=20):
    """Find potential music track locations"""
    tracks = []
    
    # Look for music sequence headers
    for i in range(0x100000, 0x380000, 1000):
        # Check for music-like patterns
        # Sequence data typically has repeating note patterns
        region = data[i:i+500]
        
        # Count value diversity (music has good variety)
        unique = len(set(region))
        if 50 < unique < 200:
            tracks.append(i)
        
        if len(tracks) >= count:
            break
    
    return tracks

ct_tracks = find_music_tracks(ct, 20)
print(f"  Found {len(ct_tracks)} potential tracks")

# Extract and save multiple tracks
for idx, track_offset in enumerate(ct_tracks[:10]):
    # Extract 5 seconds of audio
    audio = ct[track_offset:track_offset + 32000 * 5]  # 5 sec at 32kHz
    
    if len(audio) > 1000:
        # Convert to WAV
        wav_data = bytearray()
        for b in audio:
            sample = (b - 128) * 256
            wav_data.extend(struct.pack('<h', sample))
        
        track_wav = AUDIO_DIR / f"ct_track_{idx:02d}.wav"
        with wave.open(str(track_wav), 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(32000)
            w.writeframes(bytes(wav_data))

print(f"  Saved 10 tracks to {AUDIO_DIR}")

# ============ List All Audio Files ============
print("\n=== Audio Files ===")
audio_files = list(AUDIO_DIR.glob("*"))
print(f"Total files: {len(audio_files)}")
for f in audio_files:
    size = f.stat().st_size
    print(f"  {f.name}: {size:,} bytes")

print("\n=== Conversion Complete ===")
