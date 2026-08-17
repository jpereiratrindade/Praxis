#!/usr/bin/env python3
"""Validate optional Praxis governed licensing state without mutating it."""

from __future__ import annotations

import argparse
from pathlib import Path

from governed_licensing import STATE_RELATIVE, validate_licensing


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", nargs="?", default=".")
    root = Path(parser.parse_args().workspace).resolve()
    status, errors = validate_licensing(root)

    if errors:
        for error in errors:
            print(f"FAIL  governed licensing — {error}")
        return 1

    if status == "legacy":
        print("PASS  governed licensing — legacy/not constituted; no mutation")
    elif status == "pending":
        print("PASS  governed licensing — initial constitution pending")
    else:
        print(f"PASS  governed licensing state — {STATE_RELATIVE}")
        print("PASS  governed licensing provenance and policy coherence")
        print("PASS  governed LICENSE identity and referential integrity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
