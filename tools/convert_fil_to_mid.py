from pathlib import Path
import base64
from collections import defaultdict
import mido
import re
import argparse

SAMPLES = Path(__file__).parent.parent / 'samples'


def sanitize_filename(name: str) -> str:
    """Clean filename by replacing Unicode quotes and illegal characters."""
    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        '\u2019': "'",  # Right single quotation mark
        '\u2018': "'",  # Left single quotation mark
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2026': '...',  # Horizontal ellipsis
    }
    
    for unicode_char, ascii_char in replacements.items():
        name = name.replace(unicode_char, ascii_char)
    
    # Replace illegal Windows filename characters
    illegal_chars = {
        '<': '', '>': '', ':': '-', '"': "'",
        '/': '-', '\\': '-', '|': '-', '?': '', '*': '',
    }
    
    for illegal_char, replacement in illegal_chars.items():
        name = name.replace(illegal_char, replacement)
    
    # Clean up multiple spaces and trim
    while '  ' in name:
        name = name.replace('  ', ' ')
    name = name.strip('. ')
    
    return name

VALID_B64_RE = re.compile(rb'[^A-Za-z0-9+/=]')

def clean_b64(data: bytes) -> bytes:
    s = VALID_B64_RE.sub(b'', data)
    rem = len(s) % 4
    if rem:
        s += b'=' * (4 - rem)
    return s


def decode_b64(src_b64: Path) -> bytes:
    b64 = clean_b64(src_b64.read_bytes())
    data = base64.b64decode(b64)
    return data


def parse_fil(data: bytes):
    """Parse Yamaha .FIL file and extract timing resolution from header."""
    # Read timing resolution from header if present (Yamaha ESEQ format)
    # Offset 0x18-0x19: target resolution (usually 16384 = 0x4000)
    # Offset 0x1A-0x1B: FIL timebase (usually 20480 = 0x5000)
    fil_timebase = None
    target_resolution = None
    title = None
    
    if len(data) > 0x1B and data[8:12] == b'OM-E':  # Check for ESEQ format
        target_resolution = data[0x18] + (data[0x19] << 8)
        fil_timebase = data[0x1A] + (data[0x1B] << 8)
        # Extract title from offset 0x57 - stop at first byte >= 0xF0 (MIDI marker)
        if len(data) >= 0x7C:
            title_bytes = []
            for b in data[0x57:0x7C]:
                if b >= 0xF0:  # Stop at MIDI markers (F0-FF)
                    break
                title_bytes.append(b)
            # Convert to ASCII (printable only), collapse multiple spaces, then strip
            title = ''.join(chr(b) if 32 <= b < 127 else ' ' for b in title_bytes)
            # Collapse multiple spaces into single space
            while '  ' in title:
                title = title.replace('  ', ' ')
            title = title.strip()
        print(f"FIL header: timebase={fil_timebase}, target_resolution={target_resolution}")
        if title:
            print(f"  Title: {title}")
    
    # For Yamaha ESEQ format, MIDI data always starts at offset 0x7C (124)
    # This is right after the header which contains song name and timing info
    start = 0x7C if len(data) > 0x7C and data[8:12] == b'OM-E' else 0
    
    # If not ESEQ format, try to find MIDI data
    if start == 0:
        # Look for first status byte pattern (note on/off or control change)
        for i in range(100, min(500, len(data)-2)):
            if 0x80 <= data[i] <= 0xEF and data[i+1] < 128:
                start = i
                # Scan backwards to include timing bytes
                back = 10
                start = max(100, start - back)
                break
    
    if start == 0:
        start = 0

    # FIL FORMAT: Events are followed by delta markers that specify the delay TO THE NEXT EVENT
    # Pattern: EVENT1 DELTA1 EVENT2 DELTA2 EVENT3...
    # The delta after EVENT1 is the time before EVENT2
    # First event has delta=0

    i = start
    events = []  # (delta, status, data1, data2)
    next_delta = 0  # Delta to apply to the next event we parse
    last_status = None
    
    while i < len(data):
        b = data[i]
        
        # Check if this is a timing marker
        if b == 0xF3:
            if i+1 < len(data):
                next_delta = data[i+1]
                i += 2
                continue
        elif b == 0xF4:
            if i+2 < len(data):
                # F4 encoding: F4 <low7bits> <high7bits>
                lo7 = data[i+1]
                hi7 = data[i+2]
                next_delta = (hi7 << 7) | lo7
                i += 3
                continue
        elif b == 0xF0:  # sys ex start
            # find F7 end
            j = i+1
            while j < len(data) and data[j] != 0xF7:
                j += 1
            # capture data bytes (i+1..j-1)
            sysex_bytes = list(data[i+1:j]) if j > i+1 else []
            events.append((next_delta, 0xF0, sysex_bytes, None))
            next_delta = 0
            i = j+1
            continue
        elif b == 0xFC or b == 0xF2:
            # End marker (FC is official, F2 also seen in some files)
            break
        elif b >= 0x80 and b <= 0xEF:
            status = b
            last_status = status
            # determine message length
            if 0x80 <= status <= 0x8F:  # note off
                if i+2 < len(data):
                    d1 = data[i+1]
                    d2 = data[i+2]
                    if d1<128 and d2<128:
                        events.append((next_delta, status, d1, d2))
                        next_delta = 0
                    i += 3
                    continue
            if 0x90 <= status <= 0x9F:  # note on
                if i+2 < len(data):
                    d1 = data[i+1]
                    d2 = data[i+2]
                    if d1<128 and d2<128:
                        events.append((next_delta, status, d1, d2))
                        next_delta = 0
                    i += 3
                    continue
            elif 0xA0 <= status <= 0xAF:  # poly aftertouch
                if i+2 < len(data):
                    d1 = data[i+1]
                    d2 = data[i+2]
                    if d1 < 128 and d2 < 128:
                        events.append((next_delta, status, d1, d2))
                        next_delta = 0
                    i += 3
                    continue
            elif 0xB0 <= status <= 0xBF:  # ctrl change
                if i+2 < len(data):
                    d1 = data[i+1]
                    d2 = data[i+2]
                    if d1 < 128 and d2 < 128:
                        events.append((next_delta, status, d1, d2))
                        next_delta = 0
                    i += 3
                    continue
            elif 0xC0 <= status <= 0xCF:  # program change
                if i+1 < len(data):
                    d1 = data[i+1]
                    if d1 < 128:
                        events.append((next_delta, status, d1, None))
                        next_delta = 0
                    i += 2
                    continue
            elif 0xD0 <= status <= 0xDF:  # channel pressure
                if i+1 < len(data):
                    d1 = data[i+1]
                    if d1 < 128:
                        events.append((next_delta, status, d1, None))
                        next_delta = 0
                    i += 2
                    continue
            elif 0xE0 <= status <= 0xEF:  # pitch bend
                if i+2 < len(data):
                    d1 = data[i+1]
                    d2 = data[i+2]
                    if d1 < 128 and d2 < 128:
                        events.append((next_delta, status, d1, d2))
                        next_delta = 0
                    i += 3
                    continue
            else:
                i += 1
                continue
        else:
            # data byte; maybe running status
            if last_status is not None:
                status = last_status
                if 0x80 <= status <= 0x8F or 0x90 <= status <= 0x9F or 0xA0 <= status <= 0xAF or 0xB0 <= status <= 0xBF or 0xE0 <= status <= 0xEF:
                    if i+1 < len(data):
                        d1 = data[i]
                        d2 = data[i+1]
                        if d1 < 128 and d2 < 128:
                            events.append((next_delta, status, d1, d2))
                            next_delta = 0
                        i += 2
                        continue
                elif 0xC0 <= status <= 0xCF or 0xD0 <= status <= 0xDF:
                    d1 = data[i]
                    if d1 < 128:
                        events.append((next_delta, status, d1, None))
                        next_delta = 0
                    i += 1
                    continue
            i += 1
            continue
    
    return events, fil_timebase, target_resolution, title


def events_to_midi(events, ticks_per_unit=1, force_channel: int | None = None, tempo: int = 500000, channel_map: dict | None = None, program_override: dict | None = None, title: str | None = None, add_xf_metadata: bool = True):
    mid = mido.MidiFile(type=0)  # Type 0 = single track (standard for Disklavier solo)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    mid.ticks_per_beat = 384
    # Add track name if available
    if title:
        track.append(mido.MetaMessage('track_name', name=title, time=0))
    # Add tempo meta to the start of the track
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    
    # Add XF Solo metadata for DKC-900 recognition (SMFSOLO format)
    # Only add for Type 0 (single track) files
    if add_xf_metadata and mid.type == 0:
        from datetime import datetime
        year = str(datetime.now().year)
        
        # Add copyright
        track.append(mido.MetaMessage('copyright', text=f'(P) {year} Yamaha Corporation', time=0))
        
        # XF format marker (XF02 signature)
        track.append(mido.MetaMessage('sequencer_specific', data=(67, 123, 0, 88, 70, 48, 50, 0, 27), time=0))
        
        # XG system marker
        track.append(mido.MetaMessage('sequencer_specific', data=(67, 113, 0, 1, 0, 1, 0), time=0))
        
        # XG system on
        track.append(mido.MetaMessage('sequencer_specific', data=(67, 113, 0, 0, 0, 65), time=0))
        
        # XF end marker
        track.append(mido.MetaMessage('sequencer_specific', data=(67, 123, 12, 1, 0), time=0))
    # If program overrides present, insert program_change at time 0 for their channel(s)
    if program_override:
        for ch, pg in program_override.items():
            track.append(mido.Message('program_change', program=pg, channel=ch, time=0))
    for delta, status, d1, d2 in events:
        # convert delta
        dt = int(delta * ticks_per_unit)
        # build mido message
        opcode = status & 0xF0
        channel = status & 0x0F
        if channel_map is not None and channel in channel_map:
            channel = channel_map[channel]
        elif force_channel is not None and opcode != 0xF0:
            channel = force_channel
        # Handle sysex special case
        if status == 0xF0:
            data_bytes = d1 if isinstance(d1, list) else []
            msg = mido.Message('sysex', data=bytes(data_bytes), time=dt)
            track.append(msg)
            continue
        if opcode == 0x90:
            if d1 is None or d2 is None or not (0 <= d1 < 128 and 0 <= d2 < 128):
                continue
            msg = mido.Message('note_on', note=d1, velocity=d2, channel=channel, time=dt)
            track.append(msg)
        elif opcode == 0x80:
            if d1 is None or d2 is None or not (0 <= d1 < 128 and 0 <= d2 < 128):
                continue
            msg = mido.Message('note_off', note=d1, velocity=d2, channel=channel, time=dt)
            track.append(msg)
        elif opcode == 0xB0:
            if d1 is None or d2 is None or not (0 <= d1 < 128 and 0 <= d2 < 128):
                continue
            msg = mido.Message('control_change', control=d1, value=d2, channel=channel, time=dt)
            track.append(msg)
        elif opcode == 0xC0:
            prog = d1
            if program_override is not None and channel in program_override:
                prog = program_override[channel]
            if prog is None or not (0 <= prog < 128):
                continue
            msg = mido.Message('program_change', program=prog, channel=channel, time=dt)
            track.append(msg)
        elif opcode == 0xA0:
            # polyphonic aftertouch (polytouch)
            if d1 is None or d2 is None or not (0 <= d1 < 128 and 0 <= d2 < 128):
                continue
            msg = mido.Message('polytouch', note=d1, value=d2, channel=channel, time=dt)
            track.append(msg)
        elif opcode == 0xD0:
            # channel pressure (aftertouch)
            if d1 is None or not (0 <= d1 < 128):
                continue
            msg = mido.Message('aftertouch', value=d1, channel=channel, time=dt)
            track.append(msg)
        elif opcode == 0xE0:
            # pitch bend: d1 = lsb, d2 = msb
            if d1 is None or d2 is None or not (0 <= d1 < 128 and 0 <= d2 < 128):
                continue
            raw = (d2 << 7) | (d1 & 0x7f)
            # convert to signed -8192..8191
            signed = raw - 8192
            msg = mido.Message('pitchwheel', pitch=signed, channel=channel, time=dt)
            track.append(msg)
        else:
            # ignore others for now
            continue
        # set subsequent times to 0 to accumulate times only in the time field for each message
        # mido uses time as delta, so keep as set
    return mid


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='fil2mid', description='Convert Yamaha .fil (base64) to .mid')
    parser.add_argument('--version', action='version', version='fil2mid 0.2')
    parser.add_argument('input', nargs='?', default='.', help='input .fil or .fil.b64 file path, or directory (default: current directory)')
    parser.add_argument('output', nargs='?', default=None, help='output .mid file path or output directory when input is a directory')
    parser.add_argument('--recursive', action='store_true', help='recurse into directories to find .fil/.fil.b64 files')
    parser.add_argument('--ticks-per-unit', type=float, default=0.82, help='scaling factor from FIL delta to MIDI ticks')
    parser.add_argument('--force-channel', type=int, default=None, help='force all MIDI channels to this channel (0-15)')
    parser.add_argument('--channel-map', type=str, default=None, help='map channels src:dst, comma delimited (e.g. 2:0,3:0)')
    parser.add_argument('--tempo-bpm', type=float, default=120.0, help='tempo in BPM for MIDI output')
    parser.add_argument('--preset', choices=['dkc900'], default=None, help='apply device preset mappings (e.g., dkc900)')
    parser.add_argument('--title-from-filename', action='store_true', help='extract title from filename (removing track number pattern NN or N-NN) instead of using FIL header')
    parser.add_argument('--output-from-title', action='store_true', help='name output .mid file using title from FIL header instead of input filename')
    return parser


def main(argv=None):
    parser = get_parser()
    args = parser.parse_args(argv)
    in_path = Path(args.input)
    out_path = Path(args.output) if args.output else None

    # Helper to derive output filename from input path
    def out_for_input(fp: Path, out_dir: Path | None, fil_title: str | None = None):
        if args.output_from_title and fil_title:
            # Use sanitized title from FIL as filename
            outname = sanitize_filename(fil_title) + '.mid'
        else:
            # Use input filename
            name = fp.name
            if name.endswith('.fil.b64'):
                outname = name[:-len('.fil.b64')] + '.mid'
            elif name.endswith('.fil'):
                outname = name[:-len('.fil')] + '.mid'
            else:
                outname = fp.stem + '.mid'
        if out_dir:
            return out_dir / outname
        return fp.with_name(outname)

    def convert_single(fp: Path, out_fp: Path | None = None):
        # Read input either as base64 file or binary fil
        if fp.name.endswith('.b64'):
            fil_data = decode_b64(fp)
        else:
            fil_data = fp.read_bytes()
        events, fil_timebase, target_resolution, title = parse_fil(fil_data)
        
        # If --output-from-title and no explicit output, derive from title
        if out_fp is None:
            out_fp = out_for_input(fp, None, title)
        
        # Determine title based on flag
        if args.title_from_filename:
            # Use filename (minus track number and extension) as title
            filename_stem = fp.stem
            # Remove track number pattern (NN or N-NN) from beginning
            track_match = re.match(r'^(\d{1,2}(?:-\d{1,2})?)\s*-?\s*(.+)$', filename_stem)
            if track_match:
                title = track_match.group(2).strip()
            else:
                title = filename_stem
        # else: use title from FIL header (already extracted by parse_fil)
        
        print('parsed events', len(events))
        
        # Calculate ticks_per_unit from FIL header if available
        calculated_ticks_per_unit = args.ticks_per_unit
        if fil_timebase and target_resolution:
            # FIL delta values are already in MIDI ticks - no conversion needed!
            calculated_ticks_per_unit = 1.0
            print(f'Using ticks_per_unit: {calculated_ticks_per_unit}')
            print(f'  (FIL timebase: {fil_timebase}, target resolution: {target_resolution})')
        
        print('first 50 events')
        for e in events[:50]:
            print(e)
        # convert to midi
        channel_map = None
        program_override = None
        if args.channel_map:
            channel_map = {}
            for pair in args.channel_map.split(','):
                if ':' in pair:
                    s,d = pair.split(':',1)
                    try:
                        channel_map[int(s)] = int(d)
                    except ValueError:
                        continue
        # Apply any presets
        if args.preset == 'dkc900':
            # DKC-900 preset: Keep original channels, set tempo to 117 BPM
            # Don't use force_channel or channel_map - preserve original channels
            # set tempo to 117 BPM (Yamaha Mark IV default)
            if args.tempo_bpm == 120.0:
                args.tempo_bpm = 117.0
            # Program override: force Acoustic Grand Piano (GM program 0) on channel 0
            program_override = {0: 0}

        # Calculate tempo AFTER preset adjustments
        tempo_us = int(60_000_000 / args.tempo_bpm)

        mid = events_to_midi(events, ticks_per_unit=calculated_ticks_per_unit, force_channel=args.force_channel, tempo=tempo_us, channel_map=channel_map, program_override=program_override, title=title)
        mid.save(out_fp)
        print('wrote', out_fp)

    # If directory, run batch mode
    if in_path.is_dir():
        files = []
        if args.recursive:
            files = list(in_path.rglob('*.fil.b64')) + list(in_path.rglob('*.fil'))
        else:
            files = list(in_path.glob('*.fil.b64')) + list(in_path.glob('*.fil'))
        if not files:
            print('No .fil or .fil.b64 files found in', in_path)
            return
        # decide output base dir
        out_dir = None
        if out_path and (out_path.exists() or str(out_path).endswith('.mid') is False):
            # treat output as directory
            out_dir = out_path
            out_dir.mkdir(parents=True, exist_ok=True)
        for fp in files:
            if args.output_from_title:
                # Need to parse FIL to get title first
                if fp.name.endswith('.b64'):
                    fil_data = decode_b64(fp)
                else:
                    fil_data = fp.read_bytes()
                _, _, _, fil_title = parse_fil(fil_data)
                out_fp = out_for_input(fp, out_dir, fil_title)
            else:
                out_fp = out_for_input(fp, out_dir)
            convert_single(fp, out_fp)
        return

    # Single-file mode
    if in_path.exists():
        if out_path:
            out_fp = out_path
        elif args.output_from_title:
            out_fp = None  # Will be determined from title in convert_single
        else:
            out_fp = out_for_input(in_path, None)
        convert_single(in_path, out_fp)

if __name__ == '__main__':
    main()
