# Fun — Peter’s Personal Shelf

Public reading and travel projects, separate from the professional demo lab.

- Website: [peteragility.github.io/fun](https://peteragility.github.io/fun/)
- Reading: [資治通鑑 · 294 volumes](https://peteragility.github.io/fun/tongjian/)
- Travel: [Penang family trip](https://peteragility.github.io/fun/penang-trip/)

The repository and GitHub Pages website are public. Visitors do not need to log in. The personal pages do not use the demo lab's analytics.

## Publishing

Edit `index.html`, `tongjian/index.html` or `penang-trip/index.html`, then commit and push to `main`. GitHub Actions runs `node scripts/build.mjs` and deploys only `dist/` to Pages. Repository metadata and scripts are excluded from the website artifact.

## Local viewing

Run `node scripts/build.mjs`, then `python3 -m http.server 8765 --bind 127.0.0.1 --directory dist`. Open http://127.0.0.1:8765.

## Earlier hosting

The previously created owner-private ChatGPT Site is a separate snapshot. GitHub Pages is now the public sharing address. `.openai/hosting.json` retains that Site's identifier for future maintenance; it contains no credentials.
