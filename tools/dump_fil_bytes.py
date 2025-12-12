"""
Dump raw FIL file structure around events to understand timing encoding
"""

def dump_fil_structure(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # MIDI data starts at 0x7C
    pos = 0x7C
    
    print("=== RAW FIL STRUCTURE (first 200 bytes from 0x7C) ===\n")
    
    # Show in 16-byte rows
    for offset in range(0x7C, min(0x7C + 200, len(data)), 16):
        hex_bytes = ' '.join(f'{b:02X}' for b in data[offset:offset+16])
        ascii_repr = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[offset:offset+16])
        print(f"0x{offset:05X}: {hex_bytes:<48} {ascii_repr}")

if __name__ == "__main__":
    filepath = r"samples\additional\02 - Kei's Song.fil"
    dump_fil_structure(filepath)
