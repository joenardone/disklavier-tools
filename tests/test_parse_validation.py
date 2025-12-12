from tools.convert_fil_to_mid import parse_fil


def test_parse_skips_invalid_ctrl_change():
    # Create a base64 or binary-like fil starting with known pattern and a ctrl change
    # 0xB2 0x40 0x24 pattern then 0xB2 (ctrl change) with d1=64, d2=200 (>127 should be skipped)
    data = bytes([0x00, 0x00, 0xB2, 0x40, 0x24, 0xB2, 64, 200, 0x90, 60, 64])
    events = parse_fil(data)
    # All events should have data bytes < 128
    assert all((e[2] is None or (0 <= e[2] < 128)) for e in events)
    assert all((e[3] is None or (0 <= e[3] < 128)) for e in events)


def test_parse_skips_invalid_running_status_bytes():
    # Note on (0x90) then running status data with second byte >=128
    data = bytes([0x90, 60, 64, 61, 128])
    events = parse_fil(data)
    assert all((e[2] is None or (0 <= e[2] < 128)) for e in events)
    assert all((e[3] is None or (0 <= e[3] < 128)) for e in events)


def test_events_to_midi_skips_invalid_values():
    from tools.convert_fil_to_mid import events_to_midi
    # Create an event list with a control_change event with invalid value 200
    events = [(0, 0xB2, 64, 200), (0, 0x90, 60, 64)]
    # This should not raise and should produce a MidiFile
    mid = events_to_midi(events, ticks_per_unit=2.0)
    assert hasattr(mid, 'tracks')
