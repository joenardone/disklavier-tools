"""
Analyze timing markers in .FIL file to understand delta time encoding
"""

def analyze_fil_timing(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # MIDI data starts at 0x7C
    pos = 0x7C
    event_count = 0
    
    print("=== FIRST 100 TIMING EVENTS IN .FIL ===\n")
    print(f"{'Evt#':<5} {'Pos':<8} {'Marker':<8} {'Delta':<10} {'Bytes':<20} {'Next Event'}")
    print("-" * 100)
    
    while pos < len(data) and event_count < 100:
        if data[pos] == 0xF3:
            # 1-byte delta
            if pos + 1 < len(data):
                delta = data[pos + 1]
                next_bytes = data[pos+2:pos+6].hex(' ')
                print(f"{event_count:<5} 0x{pos:05X}  F3       {delta:<10} {data[pos:pos+2].hex(' '):<20} {next_bytes}")
                pos += 2
                event_count += 1
        elif data[pos] == 0xF4:
            # 2-byte delta (lo, hi)
            if pos + 2 < len(data):
                delta_lo = data[pos + 1]
                delta_hi = data[pos + 2]
                delta = delta_lo + (delta_hi << 8)
                next_bytes = data[pos+3:pos+7].hex(' ')
                print(f"{event_count:<5} 0x{pos:05X}  F4       {delta:<10} {data[pos:pos+3].hex(' '):<20} {next_bytes}")
                pos += 3
                event_count += 1
        elif data[pos] == 0xFC:
            # End marker
            print(f"\nFound end marker FC at 0x{pos:05X}")
            break
        else:
            # Skip to next potential timing marker
            pos += 1
    
    print(f"\nTotal timing markers found: {event_count}")

if __name__ == "__main__":
    filepath = r"samples\additional\02 - Kei's Song.fil"
    analyze_fil_timing(filepath)
