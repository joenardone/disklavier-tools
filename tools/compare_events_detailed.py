import mido
import sys

ref_file = r"samples\additional\reference\02 - KEI'S SONG.MID"
conv_file = r"samples\additional\converted\02 - Kei's Song.mid"

ref_mid = mido.MidiFile(ref_file)
conv_mid = mido.MidiFile(conv_file)

print(f"Reference TPB: {ref_mid.ticks_per_beat}")
print(f"Converted TPB: {conv_mid.ticks_per_beat}\n")

# Get all events with their cumulative times
ref_events = []
ref_time = 0
for track in ref_mid.tracks:
    for msg in track:
        if msg.type not in ['track_name', 'end_of_track']:
            ref_events.append((ref_time, msg.time, msg))
            ref_time += msg.time

conv_events = []
conv_time = 0
for track in conv_mid.tracks:
    for msg in track:
        if msg.type not in ['track_name', 'end_of_track']:
            conv_events.append((conv_time, msg.time, msg))
            conv_time += msg.time

print(f"First 100 events comparison:\n")
print(f"{'#':<4} {'RefCum':<8} {'RefΔ':<6} {'ConvCum':<8} {'ConvΔ':<6} {'Match':<6} {'Event'}")
print("-" * 100)

for i in range(min(100, len(ref_events), len(conv_events))):
    ref_cum, ref_delta, ref_msg = ref_events[i]
    conv_cum, conv_delta, conv_msg = conv_events[i]
    
    # Check if events match
    match = "✓" if (ref_msg.type == conv_msg.type and 
                     getattr(ref_msg, 'note', None) == getattr(conv_msg, 'note', None) and
                     getattr(ref_msg, 'control', None) == getattr(conv_msg, 'control', None)) else "✗"
    
    event_str = f"{ref_msg.type}"
    if hasattr(ref_msg, 'channel'):
        event_str += f" ch{ref_msg.channel}"
    if hasattr(ref_msg, 'note'):
        event_str += f" n{ref_msg.note}"
    if hasattr(ref_msg, 'control'):
        event_str += f" cc{ref_msg.control}={ref_msg.value}"
    if hasattr(ref_msg, 'velocity'):
        event_str += f" v{ref_msg.velocity}"
        
    print(f"{i:<4} {ref_cum:<8} {ref_delta:<6} {conv_cum:<8} {conv_delta:<6} {match:<6} {event_str}")
