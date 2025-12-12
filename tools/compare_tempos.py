import mido

conv = mido.MidiFile(r"samples\additional\converted\02 - Kei's Song.mid")
ref = mido.MidiFile(r"samples\additional\reference\02 - KEI'S SONG.MID")

conv_tempo = [msg for msg in conv.tracks[0] if msg.type=='set_tempo'][0]
ref_tempo = [msg for msg in ref.tracks[0] if msg.type=='set_tempo'][0]

print(f"Converted tempo: {conv_tempo.tempo} us/qn = {mido.tempo2bpm(conv_tempo.tempo):.2f} BPM")
print(f"Reference tempo: {ref_tempo.tempo} us/qn = {mido.tempo2bpm(ref_tempo.tempo):.2f} BPM")
print(f"\nRatio: {conv_tempo.tempo / ref_tempo.tempo:.4f}")
