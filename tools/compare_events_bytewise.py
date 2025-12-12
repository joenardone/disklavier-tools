import mido

ref_file = r"samples\additional\reference\02 - KEI'S SONG.MID"
conv_file = r"samples\additional\converted\02 - Kei's Song.mid"

ref_mid = mido.MidiFile(ref_file)
conv_mid = mido.MidiFile(conv_file)

print(f"=== FILE COMPARISON ===")
print(f"Reference: {ref_file}")
print(f"Converted: {conv_file}\n")

print(f"Reference tracks: {len(ref_mid.tracks)}, TPB: {ref_mid.ticks_per_beat}")
print(f"Converted tracks: {len(conv_mid.tracks)}, TPB: {conv_mid.ticks_per_beat}\n")

# Get all events
ref_events = []
ref_time = 0
for track in ref_mid.tracks:
    for msg in track:
        ref_events.append((ref_time, msg.time, msg))
        ref_time += msg.time

conv_events = []
conv_time = 0
for track in conv_mid.tracks:
    for msg in track:
        conv_events.append((conv_time, msg.time, msg))
        conv_time += msg.time

print(f"Reference events: {len(ref_events)}")
print(f"Converted events: {len(conv_events)}\n")

# Find first divergence
print("=== EVENT-BY-EVENT COMPARISON (first divergence) ===\n")
print(f"{'#':<5} {'RefCum':<8} {'RefD':<6} {'ConvCum':<8} {'ConvD':<6} {'Match':<6} {'Reference Event':<50} {'Converted Event'}")
print("-" * 160)

divergence_found = False
for i in range(min(len(ref_events), len(conv_events))):
    ref_cum, ref_delta, ref_msg = ref_events[i]
    conv_cum, conv_delta, conv_msg = conv_events[i]
    
    # Check if events match
    events_match = (
        ref_msg.type == conv_msg.type and
        ref_delta == conv_delta and
        getattr(ref_msg, 'note', None) == getattr(conv_msg, 'note', None) and
        getattr(ref_msg, 'control', None) == getattr(conv_msg, 'control', None) and
        getattr(ref_msg, 'value', None) == getattr(conv_msg, 'value', None) and
        getattr(ref_msg, 'velocity', None) == getattr(conv_msg, 'velocity', None) and
        getattr(ref_msg, 'channel', None) == getattr(conv_msg, 'channel', None)
    )
    
    match = "Y" if events_match else "N"
    
    # Show all events until we find several divergences
    if not events_match or i < 30:
        ref_str = str(ref_msg)[:50]
        conv_str = str(conv_msg)[:50]
        print(f"{i:<5} {ref_cum:<8} {ref_delta:<6} {conv_cum:<8} {conv_delta:<6} {match:<6} {ref_str:<50} {conv_str}")
        
        if not events_match and not divergence_found:
            print(f"      ^^^ FIRST DIVERGENCE at event {i}")
            divergence_found = True
            
        if divergence_found and i > 40:
            break

print(f"\n=== SUMMARY ===")
if len(ref_events) != len(conv_events):
    print(f"Event count mismatch: {len(ref_events)} vs {len(conv_events)}")
print(f"Total time: {ref_events[-1][0]} vs {conv_events[-1][0]}")
