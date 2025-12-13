#!/usr/bin/env python3
"""CLI entrypoint wrapper for wav_to_mp3"""
import sys
from tools.wav_to_mp3 import main

if __name__ == "__main__":
    sys.exit(main())
