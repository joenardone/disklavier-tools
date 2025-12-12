from pathlib import Path
import mido
from tools.convert_fil_to_mid import main
import sys

def test_convert_sample():
    in_b64 = Path(__file__).parent.parent / 'samples' / 'angel.fil.b64'
    out_mid = Path(__file__).parent.parent / 'samples' / 'out_from_fil_test.mid'
    sys.argv = ['convert_fil_to_mid.py', str(in_b64), str(out_mid), '--ticks-per-unit', '2']
    main()
    mid = mido.MidiFile(str(out_mid))
    has_note = False
    has_cc64 = False
    for track in mid.tracks:
        for msg in track:
            if msg.type in ('note_on','note_off'):
                has_note = True
            if msg.type == 'control_change' and getattr(msg,'control',None) == 64:
                has_cc64 = True
    assert has_note, 'Converted MIDI has no note messages'
    assert has_cc64, 'Converted MIDI has no sustain pedal CC64 messages'
    print('Test passed: notes and sustain pedal present')


def test_batch_conversion(tmp_path=None):
    from pathlib import Path
    import shutil
    samples = Path(__file__).parent.parent / 'samples'
    testdir = samples / 'test_batch'
    if testdir.exists():
        shutil.rmtree(testdir)
    testdir.mkdir()
    # create 2 copies
    a = testdir / 'a.fil.b64'
    b = testdir / 'b.fil.b64'
    shutil.copy(samples / 'angel.fil.b64', a)
    shutil.copy(samples / 'angel.fil.b64', b)
    # run batch conversion
    import sys
    sys.argv = ['convert_fil_to_mid.py', str(testdir)]
    main()
    # verify outputs
    assert (testdir / 'a.mid').exists(), 'a.mid not produced'
    assert (testdir / 'b.mid').exists(), 'b.mid not produced'
    print('Test passed: batch conversion produced mids')


def test_preset_dkc900(tmp_path=None):
    from pathlib import Path
    samples = Path(__file__).parent.parent / 'samples'
    in_b64 = samples / 'angel.fil.b64'
    out_mid = samples / 'out_from_fil_preset.mid'
    import sys
    sys.argv = ['convert_fil_to_mid.py', str(in_b64), str(out_mid), '--preset', 'dkc900']
    main()
    # Verify the output program for forced channel 0
    mid = mido.MidiFile(str(out_mid))
    found_program_change_channel0 = False
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'program_change' and msg.channel == 0 and msg.program == 0:
                found_program_change_channel0 = True
    assert found_program_change_channel0, 'dkc900 preset did not set program 0 on channel 0'
    print('Test passed: dkc900 preset applied program override on channel 0')

if __name__ == '__main__':
    test_convert_sample()
