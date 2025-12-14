#!/usr/bin/env python3
"""CLI entrypoint wrapper that delegates to tools.convert_fil_to_mid.main
This makes it easy to build a single-file executable and ensures any
CLI changes in the converter are exposed consistently.
"""
import sys
from tools.convert_fil_to_mid import main


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
    sys.exit(result if result is not None else 0)
