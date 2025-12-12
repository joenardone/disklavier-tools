#!/usr/bin/env python3
"""CLI entrypoint wrapper that delegates to tools.convert_fil_to_mid.main
This makes it easy to build a single-file executable and ensures any
CLI changes in the converter are exposed consistently.
"""
from tools.convert_fil_to_mid import main


if __name__ == "__main__":
    main()
