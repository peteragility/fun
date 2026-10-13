# Fun — Peter’s Personal Shelf

Public reading and travel projects, separate from the professional demo lab.

- Website: [peteragility.github.io/fun](https://peteragility.github.io/fun/)
- Reading: [資治通鑑 · 故事版 + 294 卷全文](https://peteragility.github.io/fun/tongjian/)
- Travel: [Penang family trip](https://peteragility.github.io/fun/penang-trip/)

The repository and GitHub Pages website are public. Visitors do not need to log in. The personal pages do not use the demo lab's analytics.

## Publishing

Edit `index.html`, `penang-trip/index.html`, the story chapters in `tongjian/story.html`, the reader assets in `tongjian/`, or `scripts/build-tongjian.py`, then commit and push to `main`. GitHub Actions builds, validates links and scripts, runs mobile browser regressions, and deploys only `dist/` to Pages. Repository metadata, scripts and the original reading source are excluded from the website artifact.

## Reading source and generated pages

`data/tongjian-source.html` preserves the original 294-volume source. `scripts/build-tongjian.py` generates a lightweight catalogue and 294 independent volume pages. It removes the 146 imported Wikisource navigation/footer remnants while retaining historical text and each volume's source link. The importer accepts only the expected text markup and source-link host; unexpected markup fails the build.

The reader supports dynasty/volume filtering, previous/next navigation, volume selection, bounded font sizes and browser-local resume links. Storage failures leave reading and navigation usable. Old `tongjian/#j185` links redirect to the matching volume, and dynasty anchors such as `#sec-185` remain available in the catalogue.

The catalogue is a single-line grid per chronicle (four columns on desktop, two on a phone) with a sticky dynasty jump bar, so all 294 volumes stay scannable instead of scrolling through full-height cards. Volume pages show the title once; the Wikisource link sits beside it rather than repeating the heading inside the text panel.

`tongjian/index.html` is one page: the sixteen-chapter retelling, then the full 294-volume catalogue. `tongjian/story.html` holds the story chapters and is inlined by the build, so the prose stays hand-editable while the catalogue stays generated.

## Re-importing the source

`data/tongjian-source.html` was originally missing roughly half of each volume — the Guandu campaign, the Xuanwu Gate incident and the Langjuxu expedition were all absent. `python3 scripts/fetch-tongjian.py` re-fetches all 294 volumes from the Wikisource parse API and rewrites the source, keeping the existing titles and page chrome. It requests politely (1.2 s apart, exponential backoff on 429) and takes about 20 minutes. Use `--check` to report coverage without writing.

The importer has to cope with Wikisource being inconsistent: year headings are `<h3>` in some volumes and `<h2>` in others, years are written as either Chinese numerals or Arabic digits, some volumes lay text out with `<br>` instead of paragraphs, and others bury the 臣光曰 essays in list items. It classifies headings by content rather than tag, treats `<br>` as a paragraph break, and drops the editor's collation notes, which otherwise leak into the reading text as inline 「據《史記》⋯⋯改」 clauses. The committed source now carries about 12% more text than the previous version with no volume shorter than before.

`tongjian/story/index.html` is a hand-written retelling of the same 1,362 years: 15 selected moments, each chapter linking back to the volume it came from. It is plain HTML and shares `reader.css`; it loads no reader script, so storage failures cannot affect it.

```sh
node scripts/build.mjs
node scripts/check-site.mjs dist
node scripts/browser-smoke.mjs
```

The build clears `dist/` first so deleted files cannot linger. Browser checks require Google Chrome and use a temporary profile. Set `CHROME_PATH` if needed. No package installation is required.

`preview-cards.json` supplies the committed sharing-image text. Run `node scripts/preview-images.mjs` after editing it, then rebuild. The images and page metadata use the public GitHub Pages addresses.

## Local viewing

Run `node scripts/build.mjs`, then `python3 -m http.server 8765 --bind 127.0.0.1 --directory dist`. Open http://127.0.0.1:8765.

## Earlier hosting

The previously created owner-private ChatGPT Site is a separate snapshot. GitHub Pages is now the public sharing address. `.openai/hosting.json` retains that Site's identifier for future maintenance; it contains no credentials.
