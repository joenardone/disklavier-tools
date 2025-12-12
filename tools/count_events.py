import mido

ref = mido.MidiFile(r"samples\additional\reference\02 - KEI'S SONG.MID")
conv = mido.MidiFile(r"samples\additional\converted\02 - Kei's Song.mid")

ref_msgs = [m for m in ref.tracks[0] if m.type not in ['end_of_track', 'track_name']]
conv_msgs = [m for m in conv.tracks[0] if m.type not in ['end_of_track']]

print(f'Ref: {len(ref_msgs)} (excluding track_name, end_of_track)')
print(f'Conv: {len(conv_msgs)} (excluding end_of_track)')
print(f'Difference: {len(conv_msgs) - len(ref_msgs)}')

# Count by type
from collections import Counter
ref_counts = Counter(m.type for m in ref_msgs)
conv_counts = Counter(m.type for m in conv_msgs)

print("\nMessage counts by type:")
all_types = set(ref_counts.keys()) | set(conv_counts.keys())
for mtype in sorted(all_types):
    r = ref_counts.get(mtype, 0)
    c = conv_counts.get(mtype, 0)
    diff = c - r
    print(f"  {mtype}: Ref={r}, Conv={c}, Diff={diff}")
