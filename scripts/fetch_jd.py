#!/usr/bin/env python3
"""Fetch a job posting from a site that blocks automated requests.

Many job boards return 403 to plain HTTP clients. Sending a browser
User-Agent usually gets through. Postings commonly embed a schema.org
JobPosting object in a <script type="application/ld+json"> tag, which is
cleaner than the rendered text, so print that first when present.

Usage:
    python3 fetch_jd.py <url> [--chars N]
"""

import argparse
import html
import json
import re
import shutil
import ssl
import subprocess
import sys
import urllib.error
import urllib.request

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _ssl_context() -> ssl.SSLContext:
    """Prefer certifi's bundle; python.org builds on macOS ship without one."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _fetch_curl(url: str, timeout: int) -> str:
    """Fallback for environments whose Python has no usable CA bundle."""
    if not shutil.which("curl"):
        raise RuntimeError("TLS verification failed and curl is unavailable")
    cmd = ["curl", "-fsSL", "--compressed", "--max-time", str(timeout)]
    for key, value in HEADERS.items():
        cmd += ["-H", f"{key}: {value}"]
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"curl exited {result.returncode}: "
            f"{result.stderr.decode('utf-8', 'replace').strip()}"
        )
    return result.stdout.decode("utf-8", errors="replace")


def fetch(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout,
                                    context=_ssl_context()) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, ssl.SSLError):
            return _fetch_curl(url, timeout)
        raise


def job_postings(page: str):
    """Yield any schema.org JobPosting objects embedded in the page."""
    pattern = r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    for match in re.finditer(pattern, page, re.S | re.I):
        try:
            data = json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            continue
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                yield item


def visible_text(page: str) -> str:
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n", text).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--chars", type=int, default=12000,
                        help="max characters of body text to print")
    args = parser.parse_args()

    try:
        page = fetch(args.url)
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code} from {args.url}", file=sys.stderr)
        print("The site refused this request. Ask the user to paste the "
              "posting text instead.", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - surface the cause to the caller
        print(f"Fetch failed: {exc}", file=sys.stderr)
        return 1

    found = False
    for posting in job_postings(page):
        found = True
        print("=== JSON-LD JobPosting ===")
        print(json.dumps(posting, indent=2, ensure_ascii=False))
        print()

    if not found:
        print("=== No JSON-LD JobPosting found; body text only ===\n")

    print("=== Page text ===")
    print(visible_text(page)[: args.chars])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
