#!/usr/bin/env python3
"""
Diagnose MIDI file corruption by examining at byte level.
Specifically looks for invalid key signature messages.
"""

import sys
from pathlib import Path

def read_varlen(data, pos):
    """Read a variable-length quantity from data starting at pos."""
    value = 0
    while True:
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            break
    return value, pos

def analyze_midi_file(filepath):
    """Analyze a MIDI file and report on key signature messages."""
    print(f"\nAnalyzing: {filepath}")
    print("=" * 80)
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Check MIDI header
    if data[:4] != b'MThd':
        print("ERROR: Not a valid MIDI file (missing MThd header)")
        return
    
    header_length = int.from_bytes(data[4:8], 'big')
    format_type = int.from_bytes(data[8:10], 'big')
    num_tracks = int.from_bytes(data[10:12], 'big')
    division = int.from_bytes(data[12:14], 'big')
    
    print(f"Format: Type {format_type}")
    print(f"Tracks: {num_tracks}")
    print(f"Division: {division} ticks per quarter note\n")
    
    # Find all track chunks
    pos = 14
    track_num = 0
    
    while pos < len(data):
        # Look for MTrk chunk
        if data[pos:pos+4] != b'MTrk':
            print(f"WARNING: Expected MTrk at position {pos}, found {data[pos:pos+4]}")
            break
        
        track_num += 1
        track_length = int.from_bytes(data[pos+4:pos+8], 'big')
        print(f"Track {track_num}: {track_length} bytes")
        
        track_start = pos + 8
        track_end = track_start + track_length
        track_pos = track_start
        
        event_count = 0
        key_sig_count = 0
        
        # Parse track events
        while track_pos < track_end:
            # Read delta time
            delta, track_pos = read_varlen(data, track_pos)
            
            # Read event type
            event_byte = data[track_pos]
            
            # Check if it's a meta event (0xFF)
            if event_byte == 0xFF:
                track_pos += 1
                meta_type = data[track_pos]
                track_pos += 1
                meta_length, track_pos = read_varlen(data, track_pos)
                meta_data = data[track_pos:track_pos+meta_length]
                track_pos += meta_length
                
                # Check for key signature (meta type 0x59)
                if meta_type == 0x59:
                    key_sig_count += 1
                    if len(meta_data) >= 2:
                        # Key signature format: [sharps/flats, mode]
                        # sharps/flats: -7 to +7 (negative = flats, positive = sharps)
                        # mode: 0 = major, 1 = minor
                        sf = int.from_bytes([meta_data[0]], 'big', signed=True)
                        mode = meta_data[1]
                        
                        print(f"  Event {event_count}: Key Signature")
                        print(f"    Position in file: {track_pos - meta_length}")
                        print(f"    Sharps/Flats: {sf}")
                        print(f"    Mode: {mode} (should be 0=major or 1=minor)")
                        
                        if mode not in [0, 1]:
                            print(f"    >>> INVALID MODE: {mode} (0x{mode:02X})")
                            print(f"    >>> This is the corruption!")
                        
                event_count += 1
                
            elif event_byte >= 0x80:
                # MIDI channel message
                track_pos += 1
                # Determine message length
                if event_byte < 0xC0 or (event_byte >= 0xE0 and event_byte < 0xF0):
                    track_pos += 2  # Two data bytes
                elif event_byte < 0xE0:
                    track_pos += 1  # One data byte
                event_count += 1
            else:
                # Running status - reuse previous status
                track_pos += 1
                event_count += 1
        
        print(f"  Total events: {event_count}")
        print(f"  Key signatures: {key_sig_count}\n")
        
        pos = track_end

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python diagnose_midi_corruption.py <midi_file>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    
    analyze_midi_file(filepath)
