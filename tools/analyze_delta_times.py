import mido
import sys

ref_file = r"samples\additional\reference\02 - KEI'S SONG.MID"
conv_file = r"samples\additional\converted\02 - Kei's Song.mid"

print("=== COMPARING DELTA TIMES (first 50 events with delta > 0) ===\n")

ref_mid = mido.MidiFile(ref_file)
conv_mid = mido.MidiFile(conv_file)

# Get all events with their cumulative times
ref_events = []
ref_time = 0
for track in ref_mid.tracks:
    for msg in track:
        ref_time += msg.time
        if msg.type not in ['track_name', 'end_of_track']:
            ref_events.append((ref_time, msg))

conv_events = []
conv_time = 0
for track in conv_mid.tracks:
    for msg in track:
        conv_time += msg.time
        if msg.type not in ['track_name', 'end_of_track']:
            conv_events.append((conv_time, msg))

# Compare events with non-zero deltas
count = 0
prev_ref_time = 0
prev_conv_time = 0

print(f"{'Idx':<5} {'Ref Time':<10} {'Conv Time':<10} {'Ref Delta':<10} {'Conv Delta':<10} {'Ratio':<8} {'Event'}")
print("-" * 90)

for i in range(min(len(ref_events), len(conv_events))):
    ref_time, ref_msg = ref_events[i]
    conv_time, conv_msg = conv_events[i]
    
    ref_delta = ref_time - prev_ref_time
    conv_delta = conv_time - prev_conv_time
    
    if ref_delta > 0 or conv_delta > 0:
        ratio = conv_delta / ref_delta if ref_delta > 0 else 0
        event_str = f"{ref_msg.type}"
        if hasattr(ref_msg, 'channel'):
            event_str += f" ch{ref_msg.channel}"
        if hasattr(ref_msg, 'note'):
            event_str += f" note{ref_msg.note}"
        if hasattr(ref_msg, 'control'):
            event_str += f" cc{ref_msg.control}={ref_msg.value}"
            
        print(f"{i:<5} {ref_time:<10} {conv_time:<10} {ref_delta:<10} {conv_delta:<10} {ratio:<8.4f} {event_str}")
        
        count += 1
        if count >= 50:
            break
    
    prev_ref_time = ref_time
    prev_conv_time = conv_time

print(f"\n=== STATISTICS ===")
print(f"Total ref events: {len(ref_events)}")
print(f"Total conv events: {len(conv_events)}")
print(f"Ref total time: {ref_events[-1][0] if ref_events else 0}")
print(f"Conv total time: {conv_events[-1][0] if conv_events else 0}")
