import sys

def parse_fil_metadata(filepath):
    """Parse FIL file and show all metadata, especially text/XF metadata."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"\nFIL FILE: {filepath}")
    print(f"Size: {len(data)} bytes")
    print(f"\n{'='*80}")
    print("FIL HEADER (0x00-0x7B)")
    print(f"{'='*80}")
    
    # Title at offset 0x20 (16 bytes)
    title_bytes = data[0x20:0x30]
    title = title_bytes.rstrip(b'\x00').decode('latin-1', errors='replace')
    print(f"Title (0x20-0x2F): '{title}'")
    
    # Timebase at 0x1A-0x1B
    if len(data) > 0x1B:
        timebase = int.from_bytes(data[0x1A:0x1C], 'big')
        print(f"Timebase (0x1A-0x1B): {timebase}")
    
    # MIDI data starts at 0x7C
    if len(data) > 0x7C:
        print(f"\n{'='*80}")
        print("MIDI DATA (starting at 0x7C)")
        print(f"{'='*80}")
        midi_data = data[0x7C:]
        print(f"MIDI data size: {len(midi_data)} bytes")
        
        # Look for text events in MIDI data
        # Text events are: FF 01 <length> <text>
        # XF metadata uses: FF 01 for text events
        
        print("\nSearching for META TEXT events (FF 01)...")
        i = 0
        found_text = []
        while i < len(midi_data) - 3:
            if midi_data[i] == 0xFF and midi_data[i+1] == 0x01:
                # Found a text meta event
                length = midi_data[i+2]
                if i+3+length <= len(midi_data):
                    text = midi_data[i+3:i+3+length].decode('latin-1', errors='replace')
                    found_text.append((i, text))
                    print(f"  Offset 0x{i:04X}: '{text}'")
                    i += 3 + length
                else:
                    i += 1
            else:
                i += 1
        
        if not found_text:
            print("  No text meta events found")
        
        print("\nSearching for SEQUENCER_SPECIFIC events (FF 7F)...")
        i = 0
        found_seq = []
        while i < len(midi_data) - 3:
            if midi_data[i] == 0xFF and midi_data[i+1] == 0x7F:
                # Found a sequencer specific event
                length = midi_data[i+2]
                if i+3+length <= len(midi_data):
                    seq_data = midi_data[i+3:i+3+length]
                    found_seq.append((i, seq_data))
                    print(f"  Offset 0x{i:04X}: {tuple(seq_data)}")
                    i += 3 + length
                else:
                    i += 1
            else:
                i += 1
        
        if not found_seq:
            print("  No sequencer_specific events found")
        
        print("\nSearching for COPYRIGHT events (FF 02)...")
        i = 0
        while i < len(midi_data) - 3:
            if midi_data[i] == 0xFF and midi_data[i+1] == 0x02:
                # Found a copyright event
                length = midi_data[i+2]
                if i+3+length <= len(midi_data):
                    text = midi_data[i+3:i+3+length].decode('latin-1', errors='replace')
                    print(f"  Offset 0x{i:04X}: '{text}'")
                    i += 3 + length
                else:
                    i += 1
            else:
                i += 1
        
        # Show first 200 bytes of MIDI data
        print(f"\nFirst 200 bytes of MIDI data:")
        for i in range(0, min(200, len(midi_data)), 16):
            hex_str = ' '.join(f'{b:02X}' for b in midi_data[i:i+16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in midi_data[i:i+16])
            print(f"  {i:04X}: {hex_str:<48} {ascii_str}")

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'samples/midi/valentin.fil'
    parse_fil_metadata(filepath)
