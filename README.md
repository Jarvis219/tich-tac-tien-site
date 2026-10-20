# Tích Tắc Tiền · Tick Tock Cash — site

Static GitHub Pages site for the Tích Tắc Tiền iOS app: landing page (`index.html` Vietnamese, `en/` English), privacy policy (`privacy/`) and support (`support/`), both bilingual with `#vi` / `#en` anchors.

Live: https://jarvis219.github.io/tich-tac-tien-site/

- No analytics, no trackers, no external JavaScript. Fonts come from Google Fonts. The landing page has one tiny inline script: the example counter (29,7 ₫/s, starts at 0, tap to change unit).
- Every link is relative so the site works under the `/tich-tac-tien-site/` sub-path. The one exception is `404.html`, which GitHub Pages serves at any missing URL, so it uses root paths (`/tich-tac-tien-site/...`).

## Rebuild

```sh
python3 scripts/build_assets.py   # images from the app repo + original art (needs Pillow with WebP)
python3 scripts/build_pages.py    # index.html, en/index.html, sitemap.xml; refreshes the CSS version on the other pages
python3 scripts/check_links.py    # every local href/src/srcset exists, no absolute site URLs in links
```

`build_assets.py` reads the app repo at `../tich-tac-tien`, the 1254px originals in `~/Downloads`, and the screenshots from the capture folders; override with `APP_DIR`, `ART_DIR`, `SHOTS_DIR`, `IPAD_DIR`, `FONT`.

Privacy and support pages are hand-written HTML. Edit the landing copy in `COPY` inside `scripts/build_pages.py`.
