import mido

ref = mido.MidiFile(r"samples\additional\reference\02 - KEI'S SONG.MID")
print(f'TPB: {ref.ticks_per_beat}')
print('\nFirst 30 events with cumulative time:')
cum = 0
for i, msg in enumerate(list(ref.tracks[0])[:30]):
    cum += msg.time
    print(f'{i:2}: cum={cum:5} delta={msg.time:3} {msg}')
