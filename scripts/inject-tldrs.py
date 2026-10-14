#!/usr/bin/env python3
"""Inject TL;DR cards into tongjian/story.html and re-derive the position bar.

For each chapter, insert a `<aside class="tldr">` after `<h2>`, mark every
non-class paragraph as `class="body-p"` so the drop-cap selector matches,
and stamp `data-chapter="ch-NN"` on the section. Idempotent: re-running
overwrites previous output.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads(Path("/tmp/tj-draft/tldrs.json").read_text(encoding="utf-8"))
TLDR = {int(k): v for k, v in DATA["tld"].items()}
TITLES = {int(k): v for k, v in DATA["titles"].items()}

STORY = ROOT / "tongjian/story.html"
html = STORY.read_text(encoding="utf-8")

LABELS = ["一句場景", "發生咗咩事", "咁重要係因為"]


def render_tldr(index: int) -> str:
    lines = TLDR[index]
    body = []
    for label, line in zip(LABELS, lines):
        body.append(
            f'<p><span class="tldr-label">{label}</span>{line}</p>'
        )
    return f'<aside class="tldr">{"".join(body)}</aside>'


def chapter_swap(match: re.Match) -> str:
    head = match.group(1)
    body = match.group(2)
    h2 = re.search(r"(<h2>.*?</h2>)", body).group(1)
    tail = body[h2.end():]
    body_p = re.sub(r"<p>(?!<p class=)", '<p class="body-p">', tail, count=0)
    new_body = h2 + render_tldr(int(head)) + body_p
    return f'<section class="chapter{head}"{match.group(3)}>{new_body}</section>'


# Mark sections and inject TL;DRs
out = re.sub(
    r'(<section class="chapter" id="(ch-(\d+))")>(.*?)(</section>)',
    lambda m: (
        f'{m.group(1)} data-chapter="{m.group(3)}">'
        + re.sub(
            r"(<h2>.*?</h2>)",
            lambda h: h.group(1) + render_tldr(int(m.group(3))),
            m.group(4),
        )
        + m.group(5)
    ),
    html,
    flags=re.S,
)
# Label every non-class body paragraph so the drop-cap selector can match
out = re.sub(
    r'(<section class="chapter" id="ch-(\d+)"[^>]*>)(.*?)(</section>)',
    lambda m: m.group(1)
    + re.sub(r"<p>(?!<p class=|<aside)", '<p class="body-p">', m.group(3))
    + m.group(4),
    out,
    flags=re.S,
)
STORY.write_text(out, encoding="utf-8")
print(f"tongjian/story.html: {len(re.findall(r'class=\"tldr\"', out))} tldr cards, "
      f"{len(re.findall(r'class=\"body-p\"', out))} body-p paragraphs")
