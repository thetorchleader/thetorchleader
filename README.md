# The Torch Leader

**Status: live on GitHub Pages at https://thetorchleader.github.io/**

Tagline: *Global News for All People, Under the Light of Truth*
Motto: *Holding Forth the Gospel Light*

## Masthead history

The masthead's deep royal red background with white lettering recalls the original *Torch* of some 30 years ago, which carried that same red masthead. The torch-over-Bible logo and the motto "Holding Forth the Gospel Light" are the ministry's own, carried for over 42 years.

## News sources

Stories are rewritten with attribution from the outlets BCNN1 and GLM follow, including **Baptist Press (baptistpress.com)** — added to the source list on October 30, 2026 — alongside the Christian Post, ChurchLeaders, Protestia, Christianity Today, Charisma News, CBN News, and Religion News Service. Every story keeps its `source_name` + `source_url` credit and a link back to the original report.

A small, simple static news site — Baptist Press simplicity in the layout, with the Christian Post's "pockets" idea for the front page — built with the same dependency-free approach as GLMOmnimedianews (plain Python standard library, one JSON file per story, generated HTML). No server, no database, nothing to overload, and no hosting bill.

## The front page (index.html)

- **Masthead** — deep royal red with the torch-over-Bible logo, THE TORCH LEADER in white, the tagline in gold italic, and the motto HOLDING FORTH THE GOSPEL LIGHT, over a simple section nav.
- **Lead story** — the newest story, large, at the top.
- **Must Read pocket** — the next 5 newest headlines beside the lead.
- **Six section pockets**, each showing its **5 most recent stories** (the newest with its summary, the rest as headline + date):
  1. Church & Ministry
  2. U.S. & National
  3. World & the Persecuted Church
  4. Religious Liberty
  5. Family & Culture
  6. Sermons & Prayer

Because stories sit in pockets instead of one fast-moving stream, the front page stays full and current for a week or two at a light cadence of **2–4 new stories a day** (~24–30 stories on the page once the pockets fill).

Every story also gets its **own page** at `stories/<slug>.html`, with the full text, a "Biblical Worldview Takeaway" box, and a link back to the original source. The publication speaks in a biblical voice and is never labeled "conservative."

## How a story is added

1. Create one small file in `data/`, named after the story's slug, e.g. `data/my-story-slug.json`, with these fields:
   - `slug` — lowercase, words joined by hyphens; also the file name and the page address
   - `title`, `summary` (2–3 sentences), `body_html` (the article, in `<p>` paragraphs)
   - `category` — must match one of the six pocket names above, exactly
   - `takeaway` — the Biblical Worldview Takeaway, with Scripture
   - `source_name` + `source_url` — attribution to the original report (always kept)
   - `image` + `image_credit` — an absolute https image URL, or `""` for the clean placeholder
   - `published_at` — `YYYY-MM-DD`
   - `commentary` — optional; only a Daniel Whyte III commentary he personally supplies
2. Run `python3 build.py` — it rebuilds `index.html`, all story pages, `robots.txt`, and `sitemap.xml`.

## Seed content

The prototype is seeded with **12 recent stories copied (not moved) from GLMOmnimedianews** (`~/workspace/glmomnimedianews/data/`), with categories remapped to the Torch pockets where needed (e.g. GLM's "Theology" → Church & Ministry; the Egypt TikTok detention → World & the Persecuted Church; the Bill Gothard prayer story → Sermons & Prayer). Source attribution fields are unchanged.

## Files

- `build.py` — the generator (adapted from GLM's, with its own simpler design)
- `data/*.json` — one file per story (13 stories as of October 30, 2026)
- `index.html`, `stories/*.html`, `sitemap.xml`, `robots.txt` — generated output
- `assets/css/style.css`, `assets/js/main.js` — the site's own plain styling (white page, royal-red masthead, serif headlines) and a tiny date script

Note: `SITE_URL` in `build.py` is `https://thetorchleader.github.io`, used inside `sitemap.xml`/`robots.txt`.
