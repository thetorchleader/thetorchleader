#!/usr/bin/env python3
"""The Torch Leader — static site generator (local prototype).

A small, simple news site in the spirit of Baptist Press, with a front
page of section "pockets" (an idea borrowed from the Christian Post) so
stories stay visible a week or two at a low publishing cadence of
2-4 new stories a day.

Reads data/*.json (one file per story) and generates:
  index.html            homepage (lead story + Must Read + six pockets)
  stories/<slug>.html   individual story pages
  robots.txt
  sitemap.xml

No dependencies beyond the Python standard library. Run:  python3 build.py
"""
import html
import json
import os
import re
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))

# Live base URL (GitHub Pages user site) — used in sitemap.xml/robots.txt.
SITE_URL = "https://thetorchleader.github.io"
SITE_NAME = "The Torch Leader"
MASTHEAD = "THE TORCH LEADER"
TAGLINE = "Global News for All People, Under the Light of Truth"
MOTTO = "HOLDING FORTH THE GOSPEL LIGHT"
LOGO_URL = "https://blackchristiannews.com/wp-content/uploads/2026/09/torchlogo.webp"
LOGO_ALT = "Flaming torch over the open Bible — the Gospel Light logo"

# The six front-page pockets, in display order. A story's "category"
# field must match one of these exactly to land in that pocket.
POCKETS = [
    "Church & Ministry",
    "U.S. & National",
    "World & the Persecuted Church",
    "Religious Liberty",
    "Family & Culture",
    "Sermons & Prayer",
]

POCKET_SIZE = 5  # headlines shown per pocket on the homepage

FLAME_SVG = (
    '<svg class="flame" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="#a61c1c" d="M12.6 2.2c.9 3.9-4.1 5-4.1 9.2a4.9 4.9 0 0 0 9.8 0c0-1.9-.9-2.9-.9-2.9s1.9 1.1 1.9 3.9a7.3 7.3 0 1 1-14.6 0C4.7 7.6 9.9 6.2 12.6 2.2z"/>'
    '<path fill="#14304d" d="M12.5 22.5a3.1 3.1 0 0 1-3.1-3.1c0-2.4 3.1-3.1 3.1-5.7 1.7 1.9 3.1 3 3.1 5.7a3.1 3.1 0 0 1-3.1 3.1z"/>'
    "</svg>"
)

# Placeholder shown when a story has no image (keeps lead/pocket layout intact).
PLACEHOLDER_IMG = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 450'%3E"
    "%3Crect width='800' height='450' fill='%2314304d'/%3E"
    "%3Cg transform='translate(368 193) scale(2.667)'%3E"
    "%3Cpath fill='%23ffffff' d='M12.6 2.2c.9 3.9-4.1 5-4.1 9.2a4.9 4.9 0 0 0 9.8 0c0-1.9-.9-2.9-.9-2.9s1.9 1.1 1.9 3.9a7.3 7.3 0 1 1-14.6 0C4.7 7.6 9.9 6.2 12.6 2.2z'/%3E"
    "%3C/g%3E"
    "%3C/svg%3E"
)


def esc(text):
    return html.escape(text or "", quote=True)


def img_url(image, prefix=""):
    """Return the image URL, prefixing only relative paths. Empty -> placeholder."""
    if not image:
        return PLACEHOLDER_IMG
    if image.startswith(("http://", "https://", "data:")):
        return image
    return prefix + image


def has_real_image(story):
    img = story.get("image") or ""
    return bool(img) and not img.startswith("data:image/svg+xml,")


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def fmt_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%B %d, %Y").replace(" 0", " ")


def load_stories():
    stories = []
    seen = set()
    data_dir = os.path.join(ROOT, "data")
    if os.path.isdir(data_dir):
        for name in sorted(os.listdir(data_dir)):
            if name.endswith(".json"):
                with open(os.path.join(data_dir, name), encoding="utf-8") as f:
                    s = json.load(f)
                if s["slug"] not in seen:
                    seen.add(s["slug"])
                    stories.append(s)
    # Newest first; slug as a stable tiebreak so same-day ordering is
    # deterministic (and the day's featured story can lead the homepage).
    stories.sort(key=lambda s: (s["published_at"], s["slug"]), reverse=True)
    return stories


def head(title, description, prefix):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | {esc(SITE_NAME)}</title>
<meta name="description" content="{esc(description)}">
<link rel="stylesheet" href="{prefix}assets/css/style.css">
</head>
<body>
"""


def utility_bar():
    return f"""<div class="utility-bar">
  <div class="container">
    <span class="dateline" id="today-date"></span>
    <span class="soli">Soli Deo Gloria</span>
  </div>
</div>
"""


def masthead(prefix):
    return f"""<header class="masthead">
  <a class="brandmark" href="{prefix}index.html" aria-label="{esc(SITE_NAME)} home">
    <img class="masthead-logo" src="{esc(LOGO_URL)}" alt="{esc(LOGO_ALT)}">
    <span class="masthead-name">{esc(MASTHEAD)}</span>
  </a>
  <p class="tagline">{esc(TAGLINE)}</p>
  <p class="motto">{esc(MOTTO)}</p>
</header>
"""


def nav(prefix, current="home"):
    items = []
    for pocket in POCKETS:
        href = f"#{slugify(pocket)}" if current == "home" else f"{prefix}index.html#{slugify(pocket)}"
        items.append(f'<li><a href="{href}">{esc(pocket)}</a></li>')
    items.append(f'<li><a href="{prefix}books.html">Books</a></li>')
    items.append(f'<li><a href="{prefix}newsletter.html">Newsletter</a></li>')
    return '<nav class="main-nav" aria-label="Sections"><ul>\n' + "\n".join(items) + "\n</ul></nav>\n"


def footer(prefix):
    pocket_links = "\n".join(
        f'<li><a href="{prefix}index.html#{slugify(p)}">{esc(p)}</a></li>' for p in POCKETS
    )
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4>{esc(SITE_NAME)}</h4>
        <p>{esc(SITE_NAME)} reports the news of the Church and the world for all people, weighed in the light of the truth of God's Word. A ministry of Gospel Light Society International.</p>
      </div>
      <div>
        <h4>Sections</h4>
        <ul class="footer-links">
{pocket_links}
        </ul>
      </div>
      <div>
        <h4>About</h4>
        <p>Editor: Daniel Whyte III, President of Gospel Light Society International and Pastor of Gospel Light House of Prayer International.</p>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 {esc(SITE_NAME)}. All rights reserved.</span>
      <span class="soli">Soli Deo Gloria</span>
    </div>
  </div>
</footer>
<script src="{prefix}assets/js/main.js"></script>
</body>
</html>
"""


def badge(category):
    return f'<span class="badge {slugify(category)}">{esc(category)}</span>'


def story_url(story, prefix=""):
    return f"{prefix}stories/{story['slug']}.html"


def meta_line(story, prefix=""):
    return (
        f'<div class="meta"><span>{fmt_date(story["published_at"])}</span>'
        f'<span>Source: <a href="{esc(story["source_url"])}" rel="noopener" target="_blank">'
        f"{esc(story['source_name'])}</a></span></div>"
    )


def build_index(stories):
    lead = stories[0]
    must_read = stories[1:6]

    if has_real_image(lead):
        lead_thumb = (
            f'<a class="lead-img" href="{story_url(lead)}">'
            f'<img src="{esc(img_url(lead["image"]))}" alt="{esc(lead["title"])}"></a>'
        )
    else:
        lead_thumb = f'<a class="lead-img lead-img-empty" href="{story_url(lead)}" aria-label="{esc(lead["title"])}"></a>'

    lead_html = f"""<section class="lead-row" aria-label="Top stories">
  <article class="lead-story">
    {lead_thumb}
    <div class="lead-text">
      {badge(lead['category'])}
      <h2><a href="{story_url(lead)}">{esc(lead['title'])}</a></h2>
      <p class="summary">{esc(lead['summary'])}</p>
      {meta_line(lead)}
    </div>
  </article>
  <aside class="must-read" aria-label="Must read">
    <h3 class="pocket-title">Must Read</h3>
    <ol class="must-read-list">
"""
    for s in must_read:
        lead_html += (
            f'      <li>{badge(s["category"])}'
            f'<a href="{story_url(s)}">{esc(s["title"])}</a>'
            f'<span class="must-read-date">{fmt_date(s["published_at"])}</span></li>\n'
        )
    lead_html += "    </ol>\n  </aside>\n</section>\n"

    pocket_sections = []
    for pocket in POCKETS:
        items = [s for s in stories if s["category"] == pocket][:POCKET_SIZE]
        if items:
            first, rest = items[0], items[1:]
            body = (
                f'<article class="pocket-lead">{badge(first["category"])}'
                f'<h4><a href="{story_url(first)}">{esc(first["title"])}</a></h4>'
                f'<p class="summary">{esc(first["summary"])}</p>{meta_line(first)}</article>'
            )
            if rest:
                lis = "\n".join(
                    f'<li><a href="{story_url(s)}">{esc(s["title"])}</a>'
                    f'<span class="pocket-date">{fmt_date(s["published_at"])}</span></li>'
                    for s in rest
                )
                body += f'\n    <ul class="pocket-list">\n{lis}\n    </ul>'
        else:
            body = '<p class="coming-soon">Stories for this section are on the way — check back soon.</p>'
        pocket_sections.append(
            f"""<section class="pocket" id="{slugify(pocket)}" aria-label="{esc(pocket)}">
    <h3 class="pocket-title">{esc(pocket)}</h3>
    {body}
  </section>"""
        )

    pockets_html = '<div class="pockets-grid">\n  ' + "\n  ".join(pocket_sections) + "\n</div>\n"

    return (
        head(f"{SITE_NAME} — {TAGLINE}", f"{SITE_NAME}: {TAGLINE}. News of the Church and the world, in the light of God's Word.", "")
        + utility_bar()
        + masthead("")
        + nav("", current="home")
        + '<main class="container">\n'
        + lead_html
        + pockets_html
        + "</main>\n"
        + footer("")
    )


def build_story_page(story, stories):
    idx = stories.index(story)
    newer = stories[idx - 1] if idx > 0 else None
    older = stories[idx + 1] if idx < len(stories) - 1 else None

    commentary_html = ""
    if story.get("commentary"):
        commentary_html = f"""<aside class="commentary-box" aria-label="Commentary">
  <p class="who">Daniel Whyte III on this story</p>
  <p>{esc(story['commentary'])}</p>
</aside>
"""

    figure_html = ""
    if has_real_image(story):
        figure_html = f"""  <figure class="story-figure">
    <img src="{esc(img_url(story['image'], '../'))}" alt="{esc(story['title'])}">
    <figcaption>{esc(story['image_credit'])}</figcaption>
  </figure>
"""

    nav_links = [f'<a class="btn ghost" href="../index.html">&larr; Back to Home</a>']
    if older:
        nav_links.append(f'<a class="btn" href="{older["slug"]}.html">Older Story &rarr;</a>')
    if newer:
        nav_links.insert(0, f'<a class="btn" href="{newer["slug"]}.html">&larr; Newer Story</a>')

    return (
        head(story["title"], story["summary"], "../")
        + utility_bar()
        + masthead("../")
        + nav("../", current="story")
        + f"""<main>
<article class="story-wrap">
  <p class="breadcrumb"><a href="../index.html">Home</a> &rsaquo; {esc(story['category'])} &rsaquo; {esc(story['title'][:60])}&hellip;</p>
  <header class="story-head">
    {badge(story['category'])}
    <h1>{esc(story['title'])}</h1>
    {meta_line(story, '../')}
  </header>
{figure_html}{commentary_html}  <div class="story-body">
{story['body_html']}
  </div>
  <aside class="takeaway-box" aria-label="Biblical worldview takeaway">
    <p class="label">Biblical Worldview Takeaway</p>
    <p>{esc(story['takeaway'])}</p>
  </aside>
  <p class="source-line">Read the original at <a href="{esc(story['source_url'])}" rel="noopener" target="_blank">{esc(story['source_name'])}</a>.</p>
  <nav class="story-nav" aria-label="Story navigation">
    {"".join(nav_links)}
  </nav>
</article>
</main>
"""
        + footer("../")
    )


def build_sitemap(stories):
    urls = [f"  <url><loc>{SITE_URL}/</loc><lastmod>{stories[0]['published_at']}</lastmod></url>"]
    for s in stories:
        urls.append(
            f"  <url><loc>{SITE_URL}/stories/{s['slug']}.html</loc>"
            f"<lastmod>{s['published_at']}</lastmod></url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def build_robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"


def write(path, content):
    os.makedirs(os.path.dirname(path) or ROOT, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    stories = load_stories()
    if not stories:
        raise SystemExit("data/ is empty — nothing to build.")

    write(os.path.join(ROOT, "index.html"), build_index(stories))
    for story in stories:
        write(
            os.path.join(ROOT, "stories", story["slug"] + ".html"),
            build_story_page(story, stories),
        )
    write(os.path.join(ROOT, "robots.txt"), build_robots())
    write(os.path.join(ROOT, "sitemap.xml"), build_sitemap(stories))

    print(f"Built {SITE_NAME}:")
    print("  index.html")
    for s in stories:
        print(f"  stories/{s['slug']}.html")
    print("  robots.txt, sitemap.xml")
    print(f"  {len(stories)} stories total.")


if __name__ == "__main__":
    main()
