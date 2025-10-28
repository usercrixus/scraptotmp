#!/usr/bin/env python3

import argparse
import datetime as dt
import random
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable, Optional


DEFAULT_URLS = [
    "https://example.com",
    "https://httpbin.org/html",
    "https://www.iana.org/domains/example",
    "https://www.python.org",
]


def pick_url(urls: Iterable[str], seed: Optional[int] = None) -> str:
    population = tuple(urls)
    if not population:
        raise ValueError("URL list is empty")
    rng = random.Random(seed)
    return rng.choice(population)


def detect_encoding(response: urllib.request.addinfourl) -> str:
    headers = response.headers
    if headers:
        ct = headers.get_content_charset()
        if ct:
            return ct
    return "utf-8"


def fetch_html(url: str, timeout: float) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CodexScraper/1.0 (+https://openai.com/)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        encoding = detect_encoding(resp)
        body = resp.read()
    return body.decode(encoding, errors="replace")


def write_html(contents: str, output_dir: Path, url: str) -> Path:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = url.replace("://", "_").replace("/", "_")
    filename = f"scrape_{timestamp}_{safe_name}.html"
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    filepath.write_text(contents, encoding="utf-8")
    return filepath


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape a random website and save the HTML to /tmp."
    )
    parser.add_argument(
        "--urls",
        nargs="*",
        default=DEFAULT_URLS,
        help="Candidate URLs to scrape. Defaults to a small curated list.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional RNG seed for reproducible URL selection.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp"),
        help="Directory where the HTML result will be written.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    try:
        url = pick_url(args.urls, seed=args.seed)
        html = fetch_html(url, timeout=args.timeout)
        path = write_html(html, args.output_dir, url=url)
    except (ValueError, urllib.error.URLError, TimeoutError) as exc:
        print(f"Scrape failed: {exc}", file=sys.stderr)
        return 1

    print(f"Scraped {url}")
    print(f"HTML saved to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
