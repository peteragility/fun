#!/usr/bin/env python3
"""Re-import the 294 Tongjian volumes from Wikisource into data/tongjian-source.html.

The committed source kept only part of each volume, which silently dropped
chapters and whole years (Guandu in 200, Xuanwu Gate in 626, the Langjuxu campaign
in 119 BC). This script rebuilds every volume body from the MediaWiki parse API
while keeping the existing file's titles, section headings and page chrome.

    python3 scripts/fetch-tongjian.py [--check]

`--check` re-fetches and reports coverage without writing.
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/tongjian-source.html"
API = "https://zh.wikisource.org/w/api.php"
USER_AGENT = "fun-repo/1.0 (personal reading site; re-imports public-domain Tongjian text)"
VOLUMES = 294
DELAY = 1.2

HEADING = re.compile(
    r'<div class="mw-heading[^"]*"><h(?P<level>[23])[^>]*>(?P<text>.*?)</h(?P=level)>[\s\S]*?</div>', re.S)
PARAGRAPH = re.compile(r"<p(?:\s[^>]*)?>(.*?)</p>", re.S)
# Some volumes carry their 臣光曰 essays and notes as list items or definition terms rather
# than paragraphs; dropping these silently loses a few thousand characters per volume.
ITEM = re.compile(r"<li(?:\s[^>]*)?>(.*?)</li>|<dd(?:\s[^>]*)?>(.*?)</dd>", re.S)
BOILERPLATE = re.compile(
    r"^(.*資治通鑑 第.*|【.+?】.*$|此.*公有领域.*$|.*Public domain.*$|起.+，盡.+，凡.+$|.*►.*|卷[一二三四五六七八九十百零〇第]+)")
VOLUME_BLOCK = re.compile(r'<article class="juan" id="j(\d+)">(.*?)</article>', re.S)
TITLE = re.compile(r'<h3 class="juan-title">(.*?)<a ', re.S)
# Wikisource tags year headings h3 in some volumes and h2 in others, and writes years as either
# Chinese numerals (公元前三二〇年) or Arabic digits (前314年), so classify by content, not tag.
YEAR_LABEL = re.compile(r"(?:[公西]元[前後]?|[前後])[〇一二三四五六七八九十百千\d]+年")


def fetch(number, retries=5):
    page = f"資治通鑑/卷{number:03d}"
    query = urllib.parse.urlencode({
        "action": "parse", "format": "json", "formatversion": 2,
        "prop": "text", "page": page,
    })
    for attempt in range(retries):
        try:
            request = urllib.request.Request(f"{API}?{query}", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))["parse"]["text"]
        except urllib.error.HTTPError as error:
            if error.code not in (429, 503) or attempt == retries - 1:
                raise SystemExit(f"卷{number:03d} failed: HTTP {error.code}")
            wait = int(error.headers.get("Retry-After") or 0) or 30 * (attempt + 1)
            print(f"    {error.code} on 卷{number:03d}, waiting {wait}s", flush=True)
            time.sleep(wait)
        except Exception as error:  # noqa: BLE001 - retry any transport failure
            if attempt == retries - 1:
                raise SystemExit(f"卷{number:03d} failed after {retries} tries: {error}")
            time.sleep(5 * (attempt + 1))


def strip_tables(markup):
    """Remove whole table elements, honouring nesting. A non-greedy match would stop at the
    first inner </table> and leave the wrapper behind, or delete real body text."""
    pieces, cursor, opener = [], 0, re.compile(r"<table\b", re.I)
    while True:
        found = opener.search(markup, cursor)
        if not found:
            pieces.append(markup[cursor:])
            return "".join(pieces)
        pieces.append(markup[cursor:found.start()])
        depth, end = 0, None
        for tag in re.finditer(r"</?table\b", markup[found.start():], re.I):
            depth += -1 if tag.group(0).startswith("</") else 1
            if depth == 0:
                end = found.start() + tag.end()
                break
        if end is None:  # unclosed table: drop the remainder rather than guess
            return "".join(pieces)
        cursor = end


def text_of(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def convert(markup, title, number):
    """Turn one Wikisource page into the markup shape the reader expects."""
    # Tables are deliberately left in place: stripping them naively deletes body text, because
    # the page body is itself nested inside a wrapper table. Anything inside a table that is not
    # a paragraph or a heading is simply not emitted below.
    for junk in ("<style", "<script", "<noscript", "<figure", "<sup", "<pre"):
        while junk in markup:
            tag = junk[1:]
            markup = re.sub(rf"<{tag}[\s\S]*?</{tag}>", "", markup, count=1)
    # The <li> items inside the reference list are the editor's collation notes, not the book.
    # Without this they leak into the reading text as inline 「據《史記》⋯⋯改」 clauses.
    markup = re.sub(r'<div class="references-small">[\s\S]*?</ol>\s*</div>', "", markup)
    # Some volumes lay the text out as long blocks broken by <br> rather than paragraphs;
    # turn each line break into a paragraph boundary so nothing is lost.
    markup = re.sub(r"<br\s*/?>", "</p><p>", markup)
    body = [
        f'<h3 class="juan-title">{html.escape(title)}'
        f'<a class="src" href="https://zh.wikisource.org/wiki/{urllib.parse.quote(f"資治通鑑/卷{number:03d}")}"'
        ' target="_blank">原文 ↗</a></h3>'
    ]
    pattern = re.compile(
        f"(?P<head>{HEADING.pattern})"
        r"|(?P<para><p(?:\s[^>]*)?>(?P<paratext>[\s\S]*?)</p>)"
        r"|<li(?:\s[^>]*)?>(?P<listext>[\s\S]*?)</li>"
        r"|<dd(?:\s[^>]*)?>(?P<defext>[\s\S]*?)</dd>", re.S)
    for match in pattern.finditer(markup):
        if match.group("head") is not None:
            found = HEADING.match(match.group("head"))
            heading = text_of(found.group("text"))
            if not heading or BOILERPLATE.match(heading):
                continue
            # Year headings get the accent style; reign lines stay ordinary text.
            body.append(f'<h3 class="year">{html.escape(heading)}</h3>' if YEAR_LABEL.search(heading)
                        else f"<p>{html.escape(heading)}</p>")
            continue
        fragment = match.group("paratext") or match.group("listext") or match.group("defext")
        if not fragment:
            continue
        paragraph = text_of(fragment)
        if paragraph and re.search(r"[一-鿿]", paragraph) and not BOILERPLATE.match(paragraph):
            body.append(f"<p>{html.escape(paragraph)}</p>")
    return "".join(body)


def year_of(heading):
    match = re.search(r"[公西]元([前後]?)([〇一二三四五六七八九十百千\d]+)年", heading)
    if not match:
        match = re.search(r"([前後])([〇一二三四五六七八九十百千\d]+)年", heading)
    if not match:
        return None
    body = match.group(2)
    if body.isdigit():
        total = int(body)
    else:
        digits = {"零": 0, "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
                  "六": 6, "七": 7, "八": 8, "九": 9}
        total, current = 0, 0
        for character in body:
            if character in digits:
                current = current * 10 + digits[character]
            elif character in "十百千":
                scale = {"十": 10, "百": 100, "千": 1000}[character]
                total += (current or 1) * scale
                current = 0
        total += current
    return -total if match.group(1) == "前" else total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="report coverage without writing")
    arguments = parser.parse_args()

    current = SOURCE.read_text(encoding="utf-8")
    titles = {int(n): html.unescape(re.sub(r"<[^>]*>", "", t)).strip()
              for n, t in ((n, TITLE.search(b).group(1)) for n, b in VOLUME_BLOCK.findall(current))}
    if len(titles) != VOLUMES:
        raise SystemExit(f"expected {VOLUMES} volume titles, found {len(titles)}")

    rebuilt, years = {}, set()
    year_label = re.compile(r"[公西]元[前後]?[〇一二三四五六七八九十百千\d]+年|[前後][〇一二三四五六七八九十百千\d]+年")
    for number in range(1, VOLUMES + 1):
        markup = convert(fetch(number), titles[number], number)
        rebuilt[number] = markup
        # Many volumes carry a year label inline inside a paragraph rather than as its own
        # heading, so coverage must be measured against the whole text, not just the headings.
        plain = re.sub(r"<[^>]+>", "", markup)
        years.update(filter(None, (year_of(label) for label in year_label.findall(plain))))
        if number % 25 == 0 or number == VOLUMES:
            print(f"  fetched {number}/{VOLUMES}", flush=True)
        time.sleep(DELAY)

    expected = set(range(-403, 0)) | set(range(1, 960))
    missing = sorted(expected - years)
    print(f"years covered: {len(years & expected)}/{len(expected)}  missing: {len(missing)}")
    if missing:
        print("  missing:", ", ".join(str(y) for y in missing[:20]), "..." if len(missing) > 20 else "")
    if arguments.check:
        return

    updated = VOLUME_BLOCK.sub(lambda m: f'<article class="juan" id="j{m.group(1)}">{rebuilt[int(m.group(1))]}</article>', current)
    SOURCE.write_text(updated, encoding="utf-8")
    print(f"Wrote {SOURCE.relative_to(ROOT)} ({len(updated):,} bytes)")


if __name__ == "__main__":
    main()