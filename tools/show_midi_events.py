"""Extract and display raw MIDI events from a file."""
import mido
import sys

def show_midi_events(filepath, max_events=50):
    mid = mido.MidiFile(filepath)
    print(f"File: {filepath}")
    print(f"Ticks per beat: {mid.ticks_per_beat}")
    print(f"Type: {mid.type}")
    print(f"\nFirst {max_events} events:")
    print("Index | Time | Type          | Details")
    print("-" * 70)
    
    count = 0
    for track_idx, track in enumerate(mid.tracks):
        for msg in track:
            if count >= max_events:
                break
            
            if msg.type in ['note_on', 'note_off', 'control_change']:
                details = f"ch={msg.channel}"
                if hasattr(msg, 'note'):
                    details += f", note={msg.note}"
                if hasattr(msg, 'velocity'):
                    details += f", vel={msg.velocity}"
                if hasattr(msg, 'control'):
                    details += f", cc={msg.control}"
                if hasattr(msg, 'value'):
                    details += f", val={msg.value}"
                    
                print(f"{count:5d} | {msg.time:4d} | {msg.type:13s} | {details}")
                count += 1
            elif msg.type == 'set_tempo':
                print(f"{count:5d} | {msg.time:4d} | {msg.type:13s} | tempo={msg.tempo} ({mido.tempo2bpm(msg.tempo):.2f} BPM)")
                count += 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python show_midi_events.py <file.mid>")
        sys.exit(1)
    
    show_midi_events(sys.argv[1])
