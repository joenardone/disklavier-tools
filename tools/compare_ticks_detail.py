import mido

conv = mido.MidiFile(r"samples\additional\converted\02 - Kei's Song.mid")
ref = mido.MidiFile(r"samples\additional\reference\02 - KEI'S SONG.MID")

print(f"Converted TPB: {conv.ticks_per_beat}")
print(f"Reference TPB: {ref.ticks_per_beat}")
print(f"\nConverted total ticks: {sum(msg.time for msg in conv.tracks[0])}")
print(f"Reference total ticks: {sum(msg.time for msg in ref.tracks[0])}")

# Show first 20 deltas
print("\nFirst 20 converted deltas:")
for i, msg in enumerate(list(conv.tracks[0])[:20]):
    if msg.type not in ['track_name', 'end_of_track']:
        print(f"  {i}: delta={msg.time:3} {msg.type}")

print("\nFirst 20 reference deltas:")
for i, msg in enumerate(list(ref.tracks[0])[:20]):
    if msg.type not in ['track_name', 'end_of_track']:
        print(f"  {i}: delta={msg.time:3} {msg.type}")
