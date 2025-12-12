import mido
import sys

ref_file = r"samples\additional\reference\02 - KEI'S SONG.MID"
conv_file = r"samples\additional\converted\02 - Kei's Song.mid"

print("=== REFERENCE FILE ===")
mid = mido.MidiFile(ref_file)
tempo_changes = [msg for msg in mid.tracks[0] if msg.type == 'set_tempo']
print(f'Tempo changes: {len(tempo_changes)}')
for msg in tempo_changes:
    print(f'  Time {msg.time}: {mido.tempo2bpm(msg.tempo):.2f} BPM')

print("\n=== CONVERTED FILE ===")
mid = mido.MidiFile(conv_file)
tempo_changes = [msg for msg in mid.tracks[0] if msg.type == 'set_tempo']
print(f'Tempo changes: {len(tempo_changes)}')
for msg in tempo_changes:
    print(f'  Time {msg.time}: {mido.tempo2bpm(msg.tempo):.2f} BPM')
