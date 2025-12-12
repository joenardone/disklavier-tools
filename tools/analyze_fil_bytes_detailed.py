"""
Analyze the exact byte sequence and delta pattern
"""
with open(r"samples\additional\02 - Kei's Song.fil", 'rb') as f:
    data = f.read()

pos = 0x7C  # Start of MIDI data

print("First 50 bytes with interpretation:\n")
print(f"{'Offset':<8} {'Bytes':<20} {'Interpretation'}")
print("-" * 80)

i = 0
while pos < 0x7C + 200 and i < 50:
    b = data[pos]
    
    if b == 0xF3:
        delta = data[pos+1]
        bytes_str = f"{data[pos]:02X} {data[pos+1]:02X}"
        print(f"0x{pos:05X}  {bytes_str:<20} F3 delta={delta} (0x{delta:02X})")
        pos += 2
    elif b == 0xF4:
        lo = data[pos+1]
        hi = data[pos+2]
        delta = lo + (hi << 8)
        bytes_str = f"{data[pos]:02X} {data[pos+1]:02X} {data[pos+2]:02X}"
        print(f"0x{pos:05X}  {bytes_str:<20} F4 delta={delta} (0x{lo:02X} 0x{hi:02X})")
        pos += 3
    elif b >= 0x80 and b <= 0xEF:
        # Status byte - check what type
        if 0x80 <= b <= 0x8F or 0x90 <= b <= 0x9F or 0xA0 <= b <= 0xAF or 0xB0 <= b <= 0xBF or 0xE0 <= b <= 0xEF:
            d1 = data[pos+1]
            d2 = data[pos+2]
            bytes_str = f"{data[pos]:02X} {data[pos+1]:02X} {data[pos+2]:02X}"
            status_type = ""
            if 0x90 <= b <= 0x9F:
                status_type = f"Note On ch{b&0x0F} n{d1} v{d2}"
            elif 0xB0 <= b <= 0xBF:
                status_type = f"CC ch{b&0x0F} cc{d1}={d2}"
            print(f"0x{pos:05X}  {bytes_str:<20} {status_type}")
            pos += 3
        elif 0xC0 <= b <= 0xCF or 0xD0 <= b <= 0xDF:
            d1 = data[pos+1]
            bytes_str = f"{data[pos]:02X} {data[pos+1]:02X}"
            print(f"0x{pos:05X}  {bytes_str:<20} Status 0x{b:02X} d1={d1}")
            pos += 2
        else:
            pos += 1
    else:
        pos += 1
    i += 1
