"""Detailed timing comparison between two MIDI files."""
import mido
import sys

def analyze_timing_detail(file1, file2):
    """Compare timing of notes between two MIDI files."""
    mid1 = mido.MidiFile(file1)
    mid2 = mido.MidiFile(file2)
    
    print(f"=== File 1: {file1} ===")
    print(f"Ticks per beat: {mid1.ticks_per_beat}")
    print(f"Type: {mid1.type}")
    
    print(f"\n=== File 2: {file2} ===")
    print(f"Ticks per beat: {mid2.ticks_per_beat}")
    print(f"Type: {mid2.type}")
    
    # Extract note events with absolute timing
    def get_notes_with_time(mid):
        notes = []
        abs_time = 0
        for track in mid.tracks:
            track_time = 0
            for msg in track:
                track_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    notes.append({
                        'abs_time': track_time,
                        'note': msg.note,
                        'velocity': msg.velocity,
                        'channel': msg.channel
                    })
        return notes
    
    notes1 = get_notes_with_time(mid1)
    notes2 = get_notes_with_time(mid2)
    
    print(f"\n=== Note Comparison (first 30 notes) ===")
    print(f"Total notes: {len(notes1)} vs {len(notes2)}")
    print()
    print("Index | File1 Time | File2 Time | Ratio  | Delta Diff | Note | Vel")
    print("-" * 75)
    
    for i in range(min(30, len(notes1), len(notes2))):
        n1 = notes1[i]
        n2 = notes2[i]
        
        ratio = n1['abs_time'] / n2['abs_time'] if n2['abs_time'] > 0 else 0
        
        # Calculate delta (time since last note)
        delta1 = n1['abs_time'] - notes1[i-1]['abs_time'] if i > 0 else n1['abs_time']
        delta2 = n2['abs_time'] - notes2[i-1]['abs_time'] if i > 0 else n2['abs_time']
        delta_ratio = delta1 / delta2 if delta2 > 0 else 0
        
        print(f"{i:5d} | {n1['abs_time']:10d} | {n2['abs_time']:10d} | {ratio:6.4f} | {delta_ratio:10.4f} | {n1['note']:3d} | {n1['velocity']:3d}")
        
        if n1['note'] != n2['note'] or n1['velocity'] != n2['velocity']:
            print(f"      *** MISMATCH: Note {n1['note']} vs {n2['note']}, Vel {n1['velocity']} vs {n2['velocity']}")
    
    # Check for systematic timing differences
    print(f"\n=== Timing Analysis ===")
    ratios = []
    for i in range(min(100, len(notes1), len(notes2))):
        if notes2[i]['abs_time'] > 0:
            ratios.append(notes1[i]['abs_time'] / notes2[i]['abs_time'])
    
    if ratios:
        avg_ratio = sum(ratios) / len(ratios)
        min_ratio = min(ratios)
        max_ratio = max(ratios)
        print(f"Average timing ratio: {avg_ratio:.6f}")
        print(f"Min ratio: {min_ratio:.6f}")
        print(f"Max ratio: {max_ratio:.6f}")
        print(f"Ratio variance: {max_ratio - min_ratio:.6f}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python analyze_timing_detailed.py <file1.mid> <file2.mid>")
        sys.exit(1)
    
    analyze_timing_detail(sys.argv[1], sys.argv[2])
