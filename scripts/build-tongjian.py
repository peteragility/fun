#!/usr/bin/env python3
"""Build a small catalogue and 294 standalone reading pages from the preserved source."""
import html
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/tongjian-source.html"
BASE = "https://peteragility.github.io/fun"


class CleanText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.paragraph = [], 0

    def handle_starttag(self, tag, attrs):
        if tag not in {"p", "h3", "div", "span", "a"}:
            raise ValueError(f"Unexpected source tag: {tag}")
        attrs = dict(attrs)
        output = []
        if attrs.get("class") in {"year", "juan-title", "src", "range"}:
            output.append(f'class="{attrs["class"]}"')
        if tag == "p":
            self.paragraph += 1
            output.append(f'id="p-{self.paragraph}"')
        if tag == "a":
            url = attrs.get("href", "")
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.netloc != "zh.wikisource.org":
                raise ValueError("Unexpected source-link host")
            output += [f'href="{html.escape(url, quote=True)}"', 'target="_blank"', 'rel="noopener noreferrer"']
        self.parts.append("<" + tag + (" " + " ".join(output) if output else "") + ">")

    def handle_endtag(self, tag):
        self.parts.append(f"</{tag}>")

    def handle_data(self, text):
        self.parts.append(html.escape(text))


def plain(text):
    return html.unescape(re.sub(r"<[^>]*>", "", text)).strip()


def shell(title, description, body, prefix, canonical):
    title, description = html.escape(title), html.escape(description, quote=True)
    return f'''<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Peter’s Fun</title><meta name="description" content="{description}">
<link rel="canonical" href="{BASE}/tongjian/{canonical}">
<meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{description}">
<meta property="og:url" content="{BASE}/tongjian/{canonical}"><meta property="og:image" content="{BASE}/assets/reading-preview.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{prefix}reader.css"><script src="{prefix}reader.js" defer></script></head><body>{body}</body></html>'''


def generate(destination):
    source = SOURCE.read_text()
    sections = [(int(n), plain(name)) for n, name in re.findall(r'<h2 class="section-title" id="sec-(\d+)">(.*?)<span', source)]
    blocks = re.findall(r'<article class="juan" id="j(\d+)">(.*?)</article>', source, re.S)
    if len(blocks) != 294 or {int(n) for n, _ in blocks} != set(range(1, 295)):
        raise ValueError("The source must contain every volume exactly once")
    volumes, cleaned = [], 0
    for number, text in blocks:
        number = int(number)
        footer = re.search(r'<p>卷[^<]*</p>\s*<p>◄</p>', text)
        if footer:
            text = text[:footer.start()]
            cleaned += 1
        if any(marker in text for marker in ("&lt;div id=&quot;", "Public domainPublic domainfalsefalse", "取自「")):
            raise ValueError(f"Unreviewed source boilerplate in volume {number}")
        title = plain(re.search(r'<h3 class="juan-title">(.*?)<a ', text, re.S).group(1))
        parser = CleanText(); parser.feed(text); parser.close()
        volumes.append((number, title, "".join(parser.parts)))
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "volumes").mkdir(exist_ok=True)
    options = "".join(f'<option value="{n:03}">{html.escape(title)}</option>' for n, title, _ in volumes)
    for number, title, text in volumes:
        previous = f'<a href="{number-1:03}.html" rel="prev">← 上一卷</a>' if number > 1 else '<span>第一卷</span>'
        following = f'<a href="{number+1:03}.html" rel="next">下一卷 →</a>' if number < 294 else '<span>全書完</span>'
        select = options.replace(f'value="{number:03}"', f'value="{number:03}" selected', 1)
        body = f'''<header class="reading-header"><a href="../../">← Fun 首頁</a><a href="../">資治通鑑 · 全卷目錄</a><span>{number} / 294</span></header>
<main data-volume="{number}"><h1>{html.escape(title)}</h1><p class="intro">司馬光 · 資治通鑑 · 維基文庫來源連結保留於卷首</p>
<nav class="reader-tools" aria-label="閱讀工具">{previous}<label>跳卷 <select id="volumeJump">{select}</select></label>{following}<a href="../">目錄</a><a href="../../">Fun</a><span class="font-controls"><button id="fontDown" type="button" aria-label="縮小字體">A−</button><button id="fontUp" type="button" aria-label="放大字體">A+</button></span></nav>
<p id="readingStatus" role="status" class="status">每卷獨立載入；可分享段落連結。</p><article class="juan">{text}</article>
<nav class="page-turn" aria-label="前後卷">{previous}<a href="../">回到目錄</a>{following}</nav></main>
<footer>原著：司馬光《資治通鑑》 · 文字取自維基文庫 · 整理與閱讀介面：Peter Chan</footer>'''
        page = shell(title, f"《資治通鑑》{title}全文閱讀。前後卷、字體調整及閱讀位置記錄。", body, "../", f"volumes/{number:03}.html")
        (destination / f"volumes/{number:03}.html").write_text(page)
    chapters = []
    for index, (start, name) in enumerate(sections):
        end = sections[index + 1][0] - 1 if index + 1 < len(sections) else 294
        links = "".join(f'<a class="volume-link" data-era="{html.escape(name, quote=True)}" data-title="{html.escape(title, quote=True)}" href="volumes/{n:03}.html"><span>卷{n:03}</span>{html.escape(title)}</a>' for n, title, _ in volumes if start <= n <= end)
        chapters.append(f'<section class="era" id="sec-{start}"><h2>{html.escape(name)} <small>卷{start}–{end}</small></h2><div class="volume-grid">{links}</div></section>')
    jump = "".join(f'<a href="#sec-{n}">{html.escape(name)}</a>' for n, name in sections)
    body = f'''<header class="reading-header"><a href="../">← Fun 首頁</a><span>Peter’s reading room / 資治通鑑</span></header>
<main class="catalogue"><p class="eyebrow">294 卷 · 16 紀 · 前403年至959年</p><h1>資治通鑑</h1><p class="intro">讀一卷，走進一段歷史。每卷獨立載入，保留全文與原文來源。</p>
<a id="resumeReading" class="resume" hidden>繼續上次閱讀</a><label class="search-label" for="volumeSearch">找一卷 / 朝代<input id="volumeSearch" type="search" placeholder="唐紀、卷185、漢紀…" autocomplete="off"></label>
<p id="searchStatus" class="status" role="status">294 卷可閱讀</p><nav class="era-nav" aria-label="各紀目錄">{jump}</nav>{''.join(chapters)}</main>
<footer>司馬光《資治通鑑》 · 文字取自維基文庫 · <a href="../">回到 Fun</a></footer>'''
    (destination / "index.html").write_text(shell("資治通鑑 · 294卷全文目錄", "司馬光《資治通鑑》全294卷：搜尋卷目、跳至各紀、獨立卷頁及繼續上次閱讀。", body, "", ""))
    print(f"Built 294 volume pages; removed {cleaned} imported navigation footers.")


if __name__ == "__main__":
    generate(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist/tongjian")
