#!/usr/bin/env python3
"""CLI entrypoint wrapper for normalize_coverart"""
import sys
from tools.normalize_coverart import main

if __name__ == "__main__":
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
