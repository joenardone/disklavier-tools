import mido
import sys

filepath = sys.argv[1] if len(sys.argv) > 1 else 'samples/midi/01 - Valentine.mid.backup'

m = mido.MidiFile(filepath)
print(f'File: {filepath}')
print(f'Type: {m.type}, Tracks: {len(m.tracks)}, Ticks per beat: {m.ticks_per_beat}')

for i, track in enumerate(m.tracks):
    print(f'\n=== Track {i}: {len(track)} messages ===')
    
    # Count message types
    msg_types = {}
    for msg in track:
        msg_type = msg.type if hasattr(msg, 'type') else 'unknown'
        msg_types[msg_type] = msg_types.get(msg_type, 0) + 1
    
    print('Message types:', msg_types)
    
    # Show first 10 messages
    print('\nFirst 10 messages:')
    for msg in track[:10]:
        print(f'  {msg}')
