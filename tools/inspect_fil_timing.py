"""Inspect FIL file format and compare delta timings."""
import sys
from pathlib import Path

def inspect_fil(filepath):
    """Inspect raw FIL file structure."""
    data = Path(filepath).read_bytes()
    
    print(f"\n=== Inspecting: {filepath} ===")
    print(f"File size: {len(data)} bytes")
    
    # Find MIDI pattern
    pattern = bytes([0xB2, 0x40, 0x24])
    start = data.find(pattern)
    
    if start == -1:
        print("MIDI pattern not found")
        return
    
    print(f"MIDI pattern found at offset: {start} (0x{start:X})")
    print(f"\nFirst 100 bytes from MIDI start:")
    
    # Parse events
    i = start
    events = []
    while i < len(data) and len(events) < 20:
        if data[i] >= 0x80:  # Status byte
            status = data[i]
            # Variable length delta before status
            delta = 0
            j = i - 1
            # Walk backwards to find delta
            shift = 0
            while j >= start:
                if data[j] < 0x80:
                    delta |= (data[j] & 0x7F) << shift
                    shift += 7
                    j -= 1
                else:
                    break
            
            # Get data bytes
            d1 = data[i+1] if i+1 < len(data) else None
            d2 = data[i+2] if i+2 < len(data) else None
            
            events.append({
                'offset': i,
                'delta': delta,
                'status': status,
                'd1': d1,
                'd2': d2
            })
            
            # Move past this event
            i += 3
        else:
            i += 1
    
    print(f"\nFirst 20 parsed events:")
    for e in events:
        print(f"Offset {e['offset']:5d}: delta={e['delta']:5d}, status=0x{e['status']:02X}, d1={e['d1']:3d}, d2={e['d2']:3d}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python inspect_fil_timing.py <file.fil>")
        sys.exit(1)
    
    inspect_fil(sys.argv[1])
