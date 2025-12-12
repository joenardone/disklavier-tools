#!/usr/bin/env python3
"""Trace through FIL parser to see what events it's creating."""

def parse_fil_traced(data):
    """Parse FIL format with detailed tracing."""
    # Check format
    if not (len(data) > 0x1B and data[8:12] == b'OM-E'):
        raise ValueError("Not a valid ESEQ/FIL file")
    
    # Extract header info (correct offsets from convert_fil_to_mid.py)
    target_resolution = data[0x18] + (data[0x19] << 8)
    fil_timebase = data[0x1A] + (data[0x1B] << 8)
    
    print(f"Header: fil_timebase={fil_timebase}, target_resolution={target_resolution}")
    
    # MIDI data starts at fixed offset 0x7C
    midi_data = data[0x7C:]
    
    events = []
    i = 0
    next_delta = 0  # Delta time to apply to the NEXT event
    last_status = None
    
    event_counts = {}
    f3_count = 0
    f4_count = 0
    fc_count = 0
    
    while i < len(midi_data):
        byte = midi_data[i]
        
        # F3: single-byte delta time marker
        if byte == 0xF3:
            if i + 1 >= len(midi_data):
                break
            next_delta = midi_data[i + 1]
            f3_count += 1
            i += 2
            continue
            
        # F4: two-byte delta time marker (7-bit encoding)
        elif byte == 0xF4:
            if i + 2 >= len(midi_data):
                break
            lo7 = midi_data[i + 1]
            hi7 = midi_data[i + 2]
            next_delta = (hi7 << 7) | lo7
            f4_count += 1
            i += 3
            continue
            
        # FC: end of track
        elif byte == 0xFC:
            fc_count += 1
            break
            
        # Status byte (0x80-0xEF)
        elif byte >= 0x80 and byte < 0xF0:
            last_status = byte
            status = byte
            
            # Determine how many data bytes we need
            if status >= 0xC0 and status < 0xE0:
                # Program change or channel pressure: 1 data byte
                if i + 1 >= len(midi_data):
                    break
                d1 = midi_data[i + 1]
                d2 = None
                i += 2
            else:
                # Note on/off, CC, pitch bend, etc.: 2 data bytes
                if i + 2 >= len(midi_data):
                    break
                d1 = midi_data[i + 1]
                d2 = midi_data[i + 2]
                i += 3
            
            events.append((next_delta, status, d1, d2))
            
            # Count event types
            msg_type = (status >> 4) & 0x0F
            type_names = {
                0x8: 'note_off',
                0x9: 'note_on',
                0xA: 'polytouch',
                0xB: 'control_change',
                0xC: 'program_change',
                0xD: 'aftertouch',
                0xE: 'pitchwheel'
            }
            type_name = type_names.get(msg_type, f'unknown_{msg_type:X}')
            event_counts[type_name] = event_counts.get(type_name, 0) + 1
            
            next_delta = 0
            
        # Data byte - should use running status
        elif byte < 0x80:
            if last_status is None:
                print(f"WARNING: Data byte 0x{byte:02X} at position {i} with no running status!")
                i += 1
                continue
                
            status = last_status
            
            # Determine how many data bytes we need
            if status >= 0xC0 and status < 0xE0:
                # Program change or channel pressure: 1 data byte
                d1 = byte
                d2 = None
                i += 1
            else:
                # Note on/off, CC, pitch bend, etc.: 2 data bytes
                if i + 1 >= len(midi_data):
                    break
                d1 = byte
                d2 = midi_data[i + 1]
                i += 2
            
            events.append((next_delta, status, d1, d2))
            
            # Count event types
            msg_type = (status >> 4) & 0x0F
            type_names = {
                0x8: 'note_off',
                0x9: 'note_on',
                0xA: 'polytouch',
                0xB: 'control_change',
                0xC: 'program_change',
                0xD: 'aftertouch',
                0xE: 'pitchwheel'
            }
            type_name = type_names.get(msg_type, f'unknown_{msg_type:X}')
            event_counts[type_name] = event_counts.get(type_name, 0) + 1
            
            next_delta = 0
            
        else:
            print(f"WARNING: Unexpected byte 0x{byte:02X} at position {i}")
            i += 1
    
    print(f"\nMarker counts: F3={f3_count}, F4={f4_count}, FC={fc_count}")
    print(f"Total events parsed: {len(events)}")
    print(f"\nEvent counts by type:")
    for event_type in sorted(event_counts.keys()):
        print(f"  {event_type}: {event_counts[event_type]}")
    
    return events, fil_timebase, target_resolution

# Test with Kei's Song
data = open(r"samples\additional\02 - Kei's Song.fil", 'rb').read()
events, _, _ = parse_fil_traced(data)
