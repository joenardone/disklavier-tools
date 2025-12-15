#!/usr/bin/env python3
"""
Show detailed metadata from a MIDI file.
Displays all meta messages including XF metadata.
"""
import sys
import mido
from pathlib import Path

def show_midi_metadata(filepath):
    """Display all metadata from a MIDI file."""
    try:
        mid = mido.MidiFile(filepath)
        print(f"\n{'='*70}")
        print(f"File: {filepath}")
        print(f"{'='*70}")
        print(f"Type: {mid.type}")
        print(f"Number of tracks: {len(mid.tracks)}")
        print(f"Ticks per beat: {mid.ticks_per_beat}")
        
        # Collect all meta message types
        meta_types = set()
        for track_num, track in enumerate(mid.tracks):
            for msg in track:
                if msg.is_meta:
                    meta_types.add(msg.type)
        
        print(f"\nMeta message types found: {sorted(meta_types)}")
        
        # Show all meta messages from all tracks
        print(f"\n{'='*70}")
        print("META MESSAGES:")
        print(f"{'='*70}")
        
        for track_num, track in enumerate(mid.tracks):
            print(f"\n--- Track {track_num} ---")
            
            for msg in track:
                if msg.is_meta:
                    print(f"  {msg.type}: ", end="")
                    
                    if msg.type == 'sequencer_specific':
                        # Show bytes in both decimal and hex
                        print(f"{msg.data} (hex: {' '.join(f'{b:02X}' for b in msg.data)})")
                    elif msg.type == 'text':
                        print(f"'{msg.text}'")
                    elif msg.type == 'track_name':
                        print(f"'{msg.name}'")
                    elif msg.type == 'copyright':
                        print(f"'{msg.text}'")
                    elif msg.type == 'cue_marker':
                        print(f"'{msg.text}'")
                    elif msg.type == 'set_tempo':
                        bpm = mido.tempo2bpm(msg.tempo)
                        print(f"{msg.tempo} µs/beat ({bpm:.2f} BPM)")
                    elif msg.type == 'time_signature':
                        print(f"{msg.numerator}/{msg.denominator}")
                    elif msg.type == 'key_signature':
                        print(f"{msg.key}")
                    elif msg.type == 'marker':
                        print(f"'{msg.text}'")
                    else:
                        print(msg)
        
        print(f"\n{'='*70}\n")
        
        # Check for XF metadata specifically
        has_xf = False
        xf_messages = []
        
        for track in mid.tracks:
            for msg in track:
                if msg.is_meta:
                    if msg.type == 'sequencer_specific':
                        data = msg.data
                        # Check for XF format marker (67, 123, 0, 88, 70, ...)
                        if len(data) >= 5 and data[0] == 67 and data[1] == 123 and data[3] == 88 and data[4] == 70:
                            has_xf = True
                            xf_messages.append(f"XF format marker: {data}")
                        # Check for XG system marker (67, 113, ...)
                        elif len(data) >= 2 and data[0] == 67 and data[1] == 113:
                            xf_messages.append(f"XG system marker: {data}")
                    elif msg.type == 'text' and ('XFhd:' in msg.text or 'XFln:' in msg.text):
                        has_xf = True
                        xf_messages.append(f"XF text: '{msg.text}'")
                    elif msg.type == 'cue_marker' and '$Lyrc:' in msg.text:
                        xf_messages.append(f"XF lyric marker: '{msg.text}'")
        
        if has_xf or xf_messages:
            print(f"{'='*70}")
            print("XF METADATA DETECTED:")
            print(f"{'='*70}")
            for xf_msg in xf_messages:
                print(f"  {xf_msg}")
            print(f"{'='*70}\n")
        else:
            print(f"{'='*70}")
            print("NO XF METADATA FOUND")
            print(f"{'='*70}\n")
        
        return True
        
    except Exception as e:
        print(f"Error reading MIDI file: {e}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python show_midi_metadata.py <midi_file>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    success = show_midi_metadata(filepath)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
