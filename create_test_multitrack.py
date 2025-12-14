import mido

# Create a proper multi-track Type 1 MIDI file for testing
mid = mido.MidiFile(type=1, ticks_per_beat=480)

# Track 0: Tempo and metadata
track0 = mido.MidiTrack()
track0.append(mido.MetaMessage('track_name', name='Tempo Track', time=0))
track0.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
track0.append(mido.MetaMessage('end_of_track', time=960))
mid.tracks.append(track0)

# Track 1: Piano
track1 = mido.MidiTrack()
track1.append(mido.MetaMessage('track_name', name='Piano', time=0))
track1.append(mido.Message('program_change', channel=0, program=0, time=0))
track1.append(mido.Message('note_on', channel=0, note=60, velocity=64, time=0))
track1.append(mido.Message('note_off', channel=0, note=60, velocity=64, time=480))
track1.append(mido.MetaMessage('end_of_track', time=0))
mid.tracks.append(track1)

# Track 2: Strings
track2 = mido.MidiTrack()
track2.append(mido.MetaMessage('track_name', name='Strings', time=0))
track2.append(mido.Message('program_change', channel=1, program=48, time=0))
track2.append(mido.Message('note_on', channel=1, note=64, velocity=64, time=0))
track2.append(mido.Message('note_off', channel=1, note=64, velocity=64, time=480))
track2.append(mido.MetaMessage('end_of_track', time=0))
mid.tracks.append(track2)

mid.save('samples/test_multitrack.mid')
print(f'Created test_multitrack.mid: Type {mid.type}, {len(mid.tracks)} tracks')
