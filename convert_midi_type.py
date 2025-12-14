"""
Wrapper script for convert_midi_type executable.
"""
import sys
from tools.convert_midi_type import main

if __name__ == '__main__':
    result = main()
    # Keep window open if not running in interactive terminal
    try:
        if sys.stdin and sys.stdin.isatty():
            pass  # Interactive terminal, let it close normally
        else:
            input("\nPress Enter to close...")
    except:
        input("\nPress Enter to close...")
    sys.exit(result)
