from tools.convert_fil_to_mid import parse_fil


def test_parse_skips_invalid_ctrl_change():
    data = bytes([0x00, 0x00, 0xB2, 0x40, 0x24, 0xB2, 64, 200, 0x90, 60, 64])
    events = parse_fil(data)
    assert all((e[2] is None or (0 <= e[2] < 128)) for e in events)
    assert all((e[3] is None or (0 <= e[3] < 128)) for e in events)


def test_parse_skips_invalid_running_status_bytes():
    data = bytes([0x90, 60, 64, 61, 128])
    events = parse_fil(data)
    assert all((e[2] is None or (0 <= e[2] < 128)) for e in events)
    assert all((e[3] is None or (0 <= e[3] < 128)) for e in events)


if __name__ == '__main__':
    test_parse_skips_invalid_ctrl_change()
    print('ctrl change test OK')
    test_parse_skips_invalid_running_status_bytes()
    print('running status test OK')
