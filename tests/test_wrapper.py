import subprocess
import sys
from pathlib import Path
import tempfile


def venv_python():
    # Use the current Python executable (likely venv in tests)
    return sys.executable


def test_help_shows_preset():
    p = subprocess.run([venv_python(), 'fil2mid.py', '-h'], capture_output=True, text=True)
    assert p.returncode == 0
    assert '--preset' in p.stdout


def test_exec_with_preset_after_positional():
    sample = Path('samples/test_batch/a.fil')
    assert sample.exists()
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / 'out.mid'
        p = subprocess.run([venv_python(), 'fil2mid.py', str(sample), str(out), '--preset', 'dkc900'], capture_output=True, text=True)
        assert p.returncode == 0
        assert out.exists()
