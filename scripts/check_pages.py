#!/usr/bin/env python3
"""Print a PDF's page count. Exits 1 if it exceeds --max.

Usage:
    python3 check_pages.py resume.pdf
    python3 check_pages.py resume.pdf --max 1
"""

import argparse
import sys


def page_count(path: str) -> int:
    try:
        from pypdf import PdfReader
    except ImportError:
        print("pypdf is not installed. Run: pip3 install pypdf", file=sys.stderr)
        raise SystemExit(2)
    return len(PdfReader(path).pages)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf")
    parser.add_argument("--max", type=int, default=1,
                        help="maximum acceptable page count (default 1)")
    args = parser.parse_args()

    pages = page_count(args.pdf)
    print(f"pages: {pages}")
    if pages > args.max:
        print(f"over budget: {pages} > {args.max}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
