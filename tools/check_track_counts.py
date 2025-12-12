import mido

ref = mido.MidiFile(r"samples\additional\reference\02 - KEI'S SONG.MID")
conv = mido.MidiFile(r"samples\additional\converted\02 - Kei's Song.mid")

print(f"Ref tracks: {len(ref.tracks)}")
print(f"Conv tracks: {len(conv.tracks)}\n")

for i, t in enumerate(ref.tracks):
    msgs = [m for m in t]
    print(f"Ref track {i}: {len(msgs)} messages")

for i, t in enumerate(conv.tracks):
    msgs = [m for m in t]
    print(f"Conv track {i}: {len(msgs)} messages")
