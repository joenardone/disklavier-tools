#!/usr/bin/env python3
"""
Analyze MIDI metadata tags with clear explanations.
"""
import sys
import mido
from pathlib import Path

def analyze_midi_tags(filepath):
    """Analyze and explain all metadata in a MIDI file."""
    try:
        mid = mido.MidiFile(filepath)
        
        print(f"\n{'='*80}")
        print(f"File: {filepath.name}")
        print(f"{'='*80}")
        print(f"Type: {mid.type} (0=single track, 1=multi-track)")
        print(f"Tracks: {len(mid.tracks)}")
        print(f"Ticks per beat: {mid.ticks_per_beat}")
        print()
        
        # Categorize messages
        standard_midi = []
        xf_markers = []
        xg_markers = []
        text_metadata = []
        
        for track_num, track in enumerate(mid.tracks):
            for i, msg in enumerate(track):
                if not msg.is_meta:
                    continue
                    
                if msg.type == 'track_name':
                    standard_midi.append((track_num, i, 'track_name', msg.name))
                    
                elif msg.type == 'copyright':
                    standard_midi.append((track_num, i, 'copyright', msg.text))
                    
                elif msg.type == 'text':
                    text_metadata.append((track_num, i, 'text', msg.text))
                    
                elif msg.type == 'sequencer_specific':
                    data = msg.data
                    hex_str = ' '.join(f'{b:02X}' for b in data)
                    
                    # XF format markers
                    if len(data) >= 5 and data[0] == 0x43 and data[1] == 0x7B:
                        if data[3] == 0x58 and data[4] == 0x46:  # 'X' 'F'
                            xf_markers.append((track_num, i, 'XF Format Marker', hex_str, 
                                             f"Version XF{chr(data[5])}{chr(data[6])} (XF0{data[6]-48})"))
                        elif data[2] == 0x0C:  # XF extension
                            xf_markers.append((track_num, i, 'XF Extension', hex_str, 
                                             "XF extension data"))
                        else:
                            xf_markers.append((track_num, i, 'XF Other', hex_str, "Unknown XF data"))
                    
                    # XG system markers
                    elif len(data) >= 2 and data[0] == 0x43 and data[1] == 0x71:
                        xg_markers.append((track_num, i, 'XG System', hex_str, "XG system parameter"))
                    
                    else:
                        standard_midi.append((track_num, i, 'sequencer_specific', hex_str))
        
        # Display results
        print("="*80)
        print("STANDARD MIDI METADATA")
        print("="*80)
        print("(These are standard MIDI meta-events)")
        print()
        
        for track_num, pos, msg_type, content in standard_midi:
            if msg_type == 'track_name':
                print(f"Track {track_num}, Pos {pos}: TRACK_NAME")
                print(f"  Value: '{content}'")
                print(f"  Purpose: Song/track title displayed by player")
                print()
            elif msg_type == 'copyright':
                print(f"Track {track_num}, Pos {pos}: COPYRIGHT")
                print(f"  Value: '{content}'")
                print(f"  Purpose: Copyright information")
                print()
            elif msg_type == 'sequencer_specific':
                print(f"Track {track_num}, Pos {pos}: SEQUENCER_SPECIFIC")
                print(f"  Hex: {content}")
                print()
        
        if text_metadata:
            print("="*80)
            print("TEXT METADATA")
            print("="*80)
            print("(General text annotations)")
            print()
            
            for track_num, pos, msg_type, content in text_metadata:
                print(f"Track {track_num}, Pos {pos}: TEXT")
                
                # Parse common metadata patterns
                if content.startswith('Artist:'):
                    print(f"  Type: Artist tag")
                elif content.startswith('Album:'):
                    print(f"  Type: Album tag")
                elif content.startswith('Composer:'):
                    print(f"  Type: Composer tag")
                elif content.startswith('Catalog:'):
                    print(f"  Type: Catalog tag")
                else:
                    print(f"  Type: General text")
                
                print(f"  Value: '{content}'")
                print()
        
        if xf_markers:
            print("="*80)
            print("XF (eXtended Format) MARKERS")
            print("="*80)
            print("(Yamaha XF format identification - makes file show as 'Solo' or 'Plus')")
            print()
            
            for track_num, pos, marker_type, hex_str, description in xf_markers:
                print(f"Track {track_num}, Pos {pos}: {marker_type}")
                print(f"  Hex: {hex_str}")
                print(f"  Meaning: {description}")
                print()
        
        if xg_markers:
            print("="*80)
            print("XG SYSTEM MARKERS")
            print("="*80)
            print("(Yamaha XG system parameters)")
            print()
            
            for track_num, pos, marker_type, hex_str, description in xg_markers:
                print(f"Track {track_num}, Pos {pos}: {marker_type}")
                print(f"  Hex: {hex_str}")
                print(f"  Meaning: {description}")
                print()
        
        # Analysis
        print("="*80)
        print("ANALYSIS FOR DKC-900 ENSPIRE DISPLAY")
        print("="*80)
        
        track_names = [content for _, _, msg_type, content in standard_midi if msg_type == 'track_name']
        
        if len(track_names) == 0:
            print("❌ No track_name found - file will show as filename")
        elif len(track_names) == 1:
            print(f"✅ Single track_name: '{track_names[0]}'")
            print(f"   DKC-900 should display: {track_names[0]}")
        else:
            print(f"⚠️  Multiple track_name entries found: {len(track_names)}")
            for i, name in enumerate(track_names, 1):
                print(f"   {i}. '{name}'")
            print()
            print("   PROBLEM: DKC-900 may display:")
            print(f"   - First name: '{track_names[0]}'")
            print(f"   - Or combination: '{track_names[1]} - {track_names[0]}'")
            print()
            print("   FIX: Should have only ONE track_name at the start")
        
        has_xf = any('XF Format Marker' in marker_type for _, _, marker_type, _, _ in xf_markers)
        if has_xf:
            print()
            print("✅ XF format markers present - will show as 'Solo' or 'Plus' on DKC-900")
        else:
            print()
            print("❌ No XF format markers - won't show format type on DKC-900")
        
        print()
        
        return True
        
    except Exception as e:
        print(f"Error reading MIDI file: {e}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_midi_tags.py <midi_file>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    success = analyze_midi_tags(filepath)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
