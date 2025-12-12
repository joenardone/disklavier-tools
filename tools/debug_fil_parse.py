"""
Debug the FIL parser to see if we're parsing events correctly
"""

def analyze_fil_parse(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # MIDI data starts at 0x7C
    start = 0x7C
    i = start
    raw_events = []  # List of (status, d1, d2) without delta info
    deltas = []      # List of delta times
    last_status = None
    
    while i < len(data):
        b = data[i]
        
        # Check if this is a timing marker
        if b == 0xF3:
            if i+1 < len(data):
                delta = data[i+1]
                deltas.append(delta)
                i += 2
                continue
        elif b == 0xF4:
            if i+2 < len(data):
                lo = data[i+1]
                hi = data[i+2]
                delta = lo + (hi << 8)
                deltas.append(delta)
                i += 3
                continue
        elif b == 0xFC:
            # End marker
            print(f"Found FC end marker at offset 0x{i:05X}")
            break
        elif b >= 0x80 and b <= 0xEF:
            status = b
            last_status = status
            # determine message length
            if 0x80 <= status <= 0x8F:  # note off
                if i+2 < len(data):
                    d1 = data[i+1]
                    d2 = data[i+2]
                    if d1<128 and d2<128:
                        raw_events.append((status, d1, d2))
                    i += 3
                    continue
            if 0x90 <= status <= 0x9F:  # note on
                if i+2 < len(data):
                    d1 = data[i+1]
                    d2 = data[i+2]
                    if d1<128 and d2<128:
                        raw_events.append((status, d1, d2))
                    i += 3
                    continue
            elif 0xB0 <= status <= 0xBF:  # ctrl change
                if i+2 < len(data):
                    d1 = data[i+1]
                    d2 = data[i+2]
                    if d1 < 128 and d2 < 128:
                        raw_events.append((status, d1, d2))
                    i += 3
                    continue
            else:
                i += 1
                continue
        else:
            # Not recognized, skip
            i += 1
            continue
    
    print(f"Raw events: {len(raw_events)}")
    print(f"Deltas: {len(deltas)}")
    print(f"\nFirst 20 events:")
    for i in range(min(20, len(raw_events))):
        print(f"  {i}: {raw_events[i]}")
    print(f"\nFirst 20 deltas:")
    for i in range(min(20, len(deltas))):
        print(f"  {i}: {deltas[i]}")

if __name__ == "__main__":
    filepath = r"samples\additional\02 - Kei's Song.fil"
    analyze_fil_parse(filepath)
