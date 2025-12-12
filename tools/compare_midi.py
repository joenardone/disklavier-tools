"""Compare two MIDI files to analyze tempo and timing differences."""
import mido
import sys

def analyze_midi(filepath):
    """Analyze a MIDI file and return key information."""
    mid = mido.MidiFile(filepath)
    
    print(f"\n=== Analyzing: {filepath} ===")
    print(f"Type: {mid.type}")
    print(f"Ticks per beat: {mid.ticks_per_beat}")
    print(f"Number of tracks: {len(mid.tracks)}")
    print(f"Total length: {mid.length:.2f} seconds")
    
    # Find tempo messages
    tempos = []
    for i, track in enumerate(mid.tracks):
        for msg in track:
            if msg.type == 'set_tempo':
                bpm = mido.tempo2bpm(msg.tempo)
                tempos.append((msg.time, msg.tempo, bpm))
                print(f"Track {i}: Tempo at tick {msg.time}: {msg.tempo} µs/beat = {bpm:.2f} BPM")
    
    if not tempos:
        print("No tempo messages found (using default 120 BPM)")
    
    # Count note events
    note_count = 0
    first_notes = []
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                note_count += 1
                if len(first_notes) < 10:
                    first_notes.append((msg.time, msg.note, msg.velocity))
    
    print(f"Total note_on events: {note_count}")
    print(f"First 10 note events (time, note, velocity):")
    for note_info in first_notes:
        print(f"  {note_info}")
    
    return {
        'ticks_per_beat': mid.ticks_per_beat,
        'length': mid.length,
        'tempos': tempos,
        'note_count': note_count,
        'first_notes': first_notes
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python compare_midi.py <file1.mid> [file2.mid]")
        sys.exit(1)
    
    results = []
    for filepath in sys.argv[1:]:
        try:
            result = analyze_midi(filepath)
            results.append((filepath, result))
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
    
    # Compare if we have two files
    if len(results) == 2:
        print("\n=== COMPARISON ===")
        file1, data1 = results[0]
        file2, data2 = results[1]
        
        print(f"\nTicks per beat: {data1['ticks_per_beat']} vs {data2['ticks_per_beat']}")
        print(f"Length: {data1['length']:.2f}s vs {data2['length']:.2f}s (ratio: {data1['length']/data2['length']:.3f})")
        print(f"Note count: {data1['note_count']} vs {data2['note_count']}")
        
        if data1['tempos'] and data2['tempos']:
            tempo1_bpm = data1['tempos'][0][2]
            tempo2_bpm = data2['tempos'][0][2]
            print(f"Initial tempo: {tempo1_bpm:.2f} BPM vs {tempo2_bpm:.2f} BPM")
