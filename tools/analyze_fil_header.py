"""Analyze Yamaha .FIL file header structure."""
import sys
from pathlib import Path

def analyze_fil_header(filepath):
    data = Path(filepath).read_bytes()
    
    print(f"\n=== Analyzing: {filepath} ===")
    print(f"File size: {len(data)} bytes\n")
    
    # Parse header
    print("Header structure:")
    print(f"Offset 0x00: {data[0]:02X} (File type marker)")
    print(f"Offset 0x01-0x03: {data[1]:02X} {data[2]:02X} {data[3]:02X}")
    
    # Check for ESEQ format
    format_id = data[8:20].decode('ascii', errors='ignore')
    print(f"Offset 0x08-0x13: '{format_id}' (Format ID)")
    
    # Look for timing-related values
    print(f"\nPotential timing values:")
    print(f"Offset 0x14: {data[0x14]:02X} = {data[0x14]} decimal")
    print(f"Offset 0x15: {data[0x15]:02X} = {data[0x15]} decimal")
    print(f"Offset 0x16-0x17: {data[0x16]:02X} {data[0x17]:02X} = {data[0x16] + (data[0x17] << 8)} (16-bit LE)")
    print(f"Offset 0x18-0x19: {data[0x18]:02X} {data[0x19]:02X} = {data[0x18] + (data[0x19] << 8)} (16-bit LE)")
    print(f"Offset 0x1A-0x1B: {data[0x1A]:02X} {data[0x1B]:02X} = {data[0x1A] + (data[0x1B] << 8)} (16-bit LE)")
    print(f"Offset 0x1C-0x1D: {data[0x1C]:02X} {data[0x1D]:02X} = {data[0x1C] + (data[0x1D] << 8)} (16-bit LE)")
    
    # Common values at 0x17 and 0x19
    val_17 = data[0x17]
    val_19 = data[0x19]
    val_1B = data[0x1B]
    
    print(f"\nKey values (both files have same values):")
    print(f"  Offset 0x17: 0x{val_17:02X} = {val_17} (could be ticks high byte)")
    print(f"  Offset 0x19: 0x{val_19:02X} = {val_19} (could be ticks high byte)")
    print(f"  Offset 0x1B: 0x{val_1B:02X} = {val_1B}")
    
    # Try to find MIDI data start
    pattern = bytes([0xB2, 0x40, 0x24])
    start = data.find(pattern)
    if start == -1:
        # Try finding first status byte
        for i in range(100, len(data)):
            if data[i] >= 0x80 and data[i] <= 0xEF:
                start = i
                break
    
    print(f"\nMIDI data appears to start at offset: 0x{start:04X} ({start} decimal)")
    print(f"Header size: {start} bytes")
    
    # Show bytes just before MIDI data
    if start > 10:
        print(f"\nBytes before MIDI data start:")
        for i in range(max(0, start-20), start):
            print(f"  Offset 0x{i:04X}: 0x{data[i]:02X} = {data[i]:3d} {'(F3 timing)' if data[i] == 0xF3 else '(F4 timing)' if data[i] == 0xF4 else ''}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_fil_header.py <file.fil>")
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        analyze_fil_header(filepath)
