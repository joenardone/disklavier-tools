#!/usr/bin/env python3
"""
Add minimal XF Solo metadata to test what's required.
"""
import sys
import mido
from pathlib import Path

def add_minimal_xf(input_file, output_file):
    """Add only the bare minimum XF metadata."""
    mid = mido.MidiFile(input_file)
    track = mid.tracks[0]
    
    # Find insertion point
    insert_pos = 0
    for i, msg in enumerate(track):
        if msg.type in ['set_tempo', 'time_signature', 'track_name']:
            insert_pos = i + 1
        else:
            break
    
    # Minimal XF metadata - just the three key elements
    minimal_xf = [
        # XF format marker (XF02)
        mido.MetaMessage('sequencer_specific', data=(67, 123, 0, 88, 70, 48, 50, 0, 27), time=0),
        # XF header
        mido.MetaMessage('text', text='XFhd:2025//:US:::1:no:Test Artist:::::', time=0),
        # XF line
        mido.MetaMessage('text', text='XFln:L1:Minimal Test:Test Artist::::', time=0),
    ]
    
    for msg in reversed(minimal_xf):
        track.insert(insert_pos, msg)
    
    mid.save(output_file)
    print(f"Created minimal XF test: {output_file}")

if __name__ == "__main__":
    # Create minimal test from Valentine
    add_minimal_xf(
        "samples/midi/01 - Valentine-PFBU.mid",
        "samples/midi/01 - Valentine-minimal.mid"
    )
