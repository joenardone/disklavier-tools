import re
from pathlib import Path
import base64
import mido

SAMPLES = Path(__file__).parent.parent / 'samples'

VALID_B64_RE = re.compile(rb'[^A-Za-z0-9+/=]')


def clean_b64(data: bytes) -> bytes:
    return VALID_B64_RE.sub(b'', data)


def decode_b64_to_file(src_b64: Path, out_path: Path):
    b64 = clean_b64(src_b64.read_bytes())
    data = base64.b64decode(b64)
    out_path.write_bytes(data)
    return data


def hexdump(data, length=512):
    lines = []
    for i in range(0, min(len(data), length), 16):
        chunk = data[i:i+16]
        hexs = ' '.join(f"{b:02X}" for b in chunk)
        chars = ''.join((chr(b) if 32 <= b < 127 else '.') for b in chunk)
        lines.append(f"{i:08X}  {hexs:<48}  {chars}")
    return '\n'.join(lines)


def find_ascii(data, minlen=4):
    results = []
    cur = bytearray()
    start = None
    for i, b in enumerate(data):
        if 32 <= b < 127:
            if start is None:
                start = i
            cur.append(b)
        else:
            if start is not None and len(cur) >= minlen:
                results.append((start, cur.decode('ascii')))
            start = None
            cur = bytearray()
    if start is not None and len(cur) >= minlen:
        results.append((start, cur.decode('ascii')))
    return results


def find_note_triplets(data):
    # find triplets that look like MIDI note-on/off: 0x8n..0x9n + note + vel
    triplets = []
    for i in range(len(data)-2):
        s, n, v = data[i], data[i+1], data[i+2]
        if 0x80 <= s <= 0x9F and 0 <= n <= 127 and 0 <= v <= 127:
            triplets.append((i, s, n, v))
    return triplets


def find_byte_histogram(data):
    from collections import Counter
    return Counter(data)


def list_midi_notes(mid_path):
    mid = mido.MidiFile(mid_path)
    notes = []
    for t_index, track in enumerate(mid.tracks):
        time_acc = 0
        for msg in track:
            time_acc += getattr(msg, 'time', 0)
            if msg.type in ('note_on','note_off'):
                notes.append((t_index,time_acc,msg.type,msg.note,msg.velocity))
    return mid, notes


def main():
    fil_b64 = SAMPLES / 'angel.fil.b64'
    fil_bin = SAMPLES / 'angel.fil'
    mid_b64 = SAMPLES / 'angel.mid.b64'
    mid_bin = SAMPLES / 'angel.mid'

    fil_data = decode_b64_to_file(fil_b64, fil_bin)
    print('FIL decoded: size', len(fil_data))
    print('\nHex dump (first 256):\n')
    print(hexdump(fil_data, 256))

    print('\nASCII strings in FIL (>=4):')
    for off, s in find_ascii(fil_data, 4):
        print(f'{off:08X}: {s}')

    print('\nByte histogram (top 20):')
    from collections import Counter
    hist = Counter(fil_data)
    for b,count in hist.most_common(20):
        print(f'{b:02X} {count}')

    print('\nLooking for MIDI-like triplets in FIL (first 100):')
    triplets = find_note_triplets(fil_data)
    for t in triplets[:100]:
        print(t)
    print('Total triplets found:', len(triplets))

    mid_data = decode_b64_to_file(mid_b64, mid_bin)
    print('\nMID decoded: size', len(mid_data))
    print('\nMID hex dump (first 256):\n')
    print(hexdump(mid_data, 256))

    mid, notes = list_midi_notes(mid_bin)
    print('\nMIDI file: type', mid.type, 'tracks', len(mid.tracks),'ticks_per_beat', mid.ticks_per_beat)
    print('First 50 note events from MIDI:')
    for n in notes[:50]:
        print(n)

if __name__ == '__main__':
    main()
