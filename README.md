# Fun — Peter’s Personal Shelf

Public reading and travel projects, separate from the professional demo lab.

- Website: [peteragility.github.io/fun](https://peteragility.github.io/fun/)
- Reading: [資治通鑑 · 294 volumes](https://peteragility.github.io/fun/tongjian/)
- Travel: [Penang family trip](https://peteragility.github.io/fun/penang-trip/)

The repository and GitHub Pages website are public. Visitors do not need to log in. The personal pages do not use the demo lab's analytics.

## Publishing

Edit `index.html`, `penang-trip/index.html`, the reader assets in `tongjian/`, or `scripts/build-tongjian.py`, then commit and push to `main`. GitHub Actions builds, validates links and scripts, runs mobile browser regressions, and deploys only `dist/` to Pages. Repository metadata, scripts and the original reading source are excluded from the website artifact.

## Reading source and generated pages

`data/tongjian-source.html` preserves the original 294-volume source. `scripts/build-tongjian.py` generates a lightweight catalogue and 294 independent volume pages. It removes the 146 imported Wikisource navigation/footer remnants while retaining historical text and each volume's source link. The importer accepts only the expected text markup and source-link host; unexpected markup fails the build.

The reader supports dynasty/volume filtering, previous/next navigation, volume selection, bounded font sizes and browser-local resume links. Storage failures leave reading and navigation usable. Old `tongjian/#j185` links redirect to the matching volume, and dynasty anchors such as `#sec-185` remain available in the catalogue.

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
