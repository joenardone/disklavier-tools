#!/usr/bin/env python3
"""
Analyze a .fil file to extract header information and search for any metadata.
"""
import sys
from pathlib import Path

def parse_fil_file(filepath):
    """Parse a .fil file and extract metadata."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print("="*80)
    print(f"File: {filepath}")
    print(f"Total size: {len(data)} bytes")
    print("="*80)
    
    # FIL header is at 0x00-0x7B (123 bytes)
    if len(data) < 124:
        print("File too small to contain FIL header")
        return
    
    # Parse header
    print("\nFIL HEADER (first 124 bytes):")
    print("-"*80)
    
    # Title is at offset 0x2C (44) for 64 bytes
    title_bytes = data[0x2C:0x2C+64]
    # Find null terminator
    null_idx = title_bytes.find(b'\x00')
    if null_idx != -1:
        title = title_bytes[:null_idx].decode('ascii', errors='replace')
    else:
        title = title_bytes.decode('ascii', errors='replace').rstrip()
    print(f"  Title (offset 0x2C): '{title}'")
    
    # Timebase at offset 0x10 (16) - 2 bytes, little endian
    timebase = int.from_bytes(data[0x10:0x12], 'little')
    print(f"  Timebase (offset 0x10): {timebase}")
    
    # Print hex dump of header
    print("\n  Header hex dump (first 124 bytes):")
    for i in range(0, 124, 16):
        hex_str = ' '.join(f'{b:02X}' for b in data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"    {i:04X}: {hex_str:<48} | {ascii_str}")
    
    # MIDI data starts at 0x7C (124)
    midi_data = data[124:]
    print(f"\nMIDI DATA (from offset 0x7C, {len(midi_data)} bytes):")
    print("-"*80)
    
    # Search for text-like metadata patterns in MIDI data
    print("\nSearching for text metadata in MIDI data:")
    
    # Look for common meta event markers
    # FF 01 = text event
    # FF 02 = copyright
    # FF 03 = track name
    # FF 7F = sequencer specific
    
    text_events = []
    copyright_events = []
    seq_specific = []
    
    i = 0
    while i < len(midi_data) - 1:
        if midi_data[i] == 0xFF:
            meta_type = midi_data[i+1]
            if meta_type == 0x01:  # Text event
                # Try to read length and text
                if i + 2 < len(midi_data):
                    length = midi_data[i+2]
                    if i + 3 + length <= len(midi_data):
                        text = midi_data[i+3:i+3+length].decode('ascii', errors='replace')
                        text_events.append((i, text))
            elif meta_type == 0x02:  # Copyright
                if i + 2 < len(midi_data):
                    length = midi_data[i+2]
                    if i + 3 + length <= len(midi_data):
                        text = midi_data[i+3:i+3+length].decode('ascii', errors='replace')
                        copyright_events.append((i, text))
            elif meta_type == 0x7F:  # Sequencer specific
                if i + 2 < len(midi_data):
                    length = midi_data[i+2]
                    if i + 3 + length <= len(midi_data):
                        seq_data = midi_data[i+3:i+3+length]
                        seq_specific.append((i, seq_data))
        i += 1
    
    if text_events:
        print(f"\n  Found {len(text_events)} text event(s):")
        for offset, text in text_events:
            print(f"    Offset {offset:04X}: '{text}'")
    else:
        print("\n  No text events found")
    
    if copyright_events:
        print(f"\n  Found {len(copyright_events)} copyright event(s):")
        for offset, text in copyright_events:
            print(f"    Offset {offset:04X}: '{text}'")
    else:
        print("\n  No copyright events found")
    
    if seq_specific:
        print(f"\n  Found {len(seq_specific)} sequencer_specific event(s):")
        for offset, data in seq_specific[:5]:  # Show first 5
            hex_str = ' '.join(f'{b:02X}' for b in data[:20])
            print(f"    Offset {offset:04X}: {hex_str}...")
    else:
        print("\n  No sequencer_specific events found")
    
    # Search for any ASCII strings longer than 10 chars
    print("\n\nSearching for ASCII strings in MIDI data (length > 10):")
    print("-"*80)
    current_string = []
    start_offset = 0
    
    for i, byte in enumerate(midi_data):
        if 32 <= byte < 127:  # Printable ASCII
            if not current_string:
                start_offset = i
            current_string.append(chr(byte))
        else:
            if len(current_string) > 10:
                text = ''.join(current_string)
                print(f"  Offset {start_offset:04X}: '{text}'")
            current_string = []
    
    # Check last string
    if len(current_string) > 10:
        text = ''.join(current_string)
        print(f"  Offset {start_offset:04X}: '{text}'")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_fil_metadata.py <file.fil>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    parse_fil_file(filepath)
