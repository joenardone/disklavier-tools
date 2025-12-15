import mido
import sys

def analyze_midi_deep(filepath):
    """Deep analysis of MIDI file structure."""
    mid = mido.MidiFile(filepath)
    
    print(f"\n{'='*80}")
    print(f"FILE: {filepath}")
    print(f"{'='*80}")
    print(f"Type: {mid.type}")
    print(f"Tracks: {len(mid.tracks)}")
    print(f"Ticks per beat: {mid.ticks_per_beat}")
    
    for track_idx, track in enumerate(mid.tracks):
        print(f"\n{'─'*80}")
        print(f"TRACK {track_idx} - {len(track)} messages")
        print(f"{'─'*80}")
        
        # Get all meta messages
        meta_messages = [msg for msg in track if hasattr(msg, 'type') and msg.type.startswith(('track_', 'set_', 'time_', 'key_', 'sequencer_', 'copyright', 'text', 'cue_'))]
        
        print("\nMETA MESSAGES:")
        for msg in meta_messages:
            if msg.type == 'track_name':
                print(f"  track_name: '{msg.name}'")
            elif msg.type == 'copyright':
                print(f"  copyright: '{msg.text}'")
            elif msg.type == 'text':
                print(f"  text: '{msg.text}'")
            elif msg.type == 'sequencer_specific':
                print(f"  sequencer_specific: {msg.data}")
            elif msg.type == 'cue_marker':
                print(f"  cue_marker: '{msg.text}'")
            elif msg.type == 'set_tempo':
                bpm = 60000000 / msg.tempo
                print(f"  set_tempo: {msg.tempo} ({bpm:.2f} BPM)")
            elif msg.type == 'time_signature':
                print(f"  time_signature: {msg.numerator}/{msg.denominator}")
            elif msg.type == 'key_signature':
                print(f"  key_signature: {msg.key}")
            else:
                print(f"  {msg}")
        
        # Get sysex messages
        sysex_messages = [msg for msg in track if hasattr(msg, 'type') and msg.type == 'sysex']
        if sysex_messages:
            print("\nSYSEX MESSAGES:")
            for msg in sysex_messages:
                print(f"  sysex: {msg.data}")
        
        # Count message types
        msg_types = {}
        channels = set()
        programs = set()
        
        for msg in track:
            msg_type = msg.type if hasattr(msg, 'type') else 'unknown'
            msg_types[msg_type] = msg_types.get(msg_type, 0) + 1
            
            if hasattr(msg, 'channel'):
                channels.add(msg.channel)
            if hasattr(msg, 'program'):
                programs.add(msg.program)
        
        print("\nMESSAGE TYPE SUMMARY:")
        for msg_type, count in sorted(msg_types.items()):
            print(f"  {msg_type}: {count}")
        
        if channels:
            print(f"\nCHANNELS USED: {sorted(channels)}")
        if programs:
            print(f"PROGRAMS USED: {sorted(programs)}")

if __name__ == '__main__':
    file1 = sys.argv[1] if len(sys.argv) > 1 else 'samples/midi/01 - Angel Eyes.mid'
    file2 = sys.argv[2] if len(sys.argv) > 2 else 'samples/midi/01 - Valentine.mid'
    
    analyze_midi_deep(file1)
    analyze_midi_deep(file2)
    
    # Direct comparison
    print(f"\n{'='*80}")
    print("DIRECT COMPARISON")
    print(f"{'='*80}")
    
    mid1 = mido.MidiFile(file1)
    mid2 = mido.MidiFile(file2)
    
    print(f"\nType: {mid1.type} vs {mid2.type}")
    print(f"Tracks: {len(mid1.tracks)} vs {len(mid2.tracks)}")
    print(f"Ticks per beat: {mid1.ticks_per_beat} vs {mid2.ticks_per_beat}")
    
    # Check for Yamaha-specific metadata
    print("\nYAMAHA XF METADATA:")
    
    def find_xf_metadata(mid, name):
        for track in mid.tracks:
            for msg in track:
                if hasattr(msg, 'type'):
                    if msg.type == 'text' and hasattr(msg, 'text') and ('XF' in msg.text or 'XG' in msg.text):
                        return msg.text
                    elif msg.type == 'sequencer_specific':
                        return f"sequencer_specific: {msg.data}"
        return "None"
    
    print(f"  {file1}:")
    for track in mid1.tracks:
        for msg in track:
            if hasattr(msg, 'type') and msg.type in ['text', 'sequencer_specific', 'copyright']:
                if msg.type == 'text':
                    print(f"    text: '{msg.text}'")
                elif msg.type == 'copyright':
                    print(f"    copyright: '{msg.text}'")
                elif msg.type == 'sequencer_specific':
                    print(f"    sequencer_specific: {msg.data}")
    
    print(f"\n  {file2}:")
    for track in mid2.tracks:
        for msg in track:
            if hasattr(msg, 'type') and msg.type in ['text', 'sequencer_specific', 'copyright']:
                if msg.type == 'text':
                    print(f"    text: '{msg.text}'")
                elif msg.type == 'copyright':
                    print(f"    copyright: '{msg.text}'")
                elif msg.type == 'sequencer_specific':
                    print(f"    sequencer_specific: {msg.data}")
