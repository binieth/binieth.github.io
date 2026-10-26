#!/usr/bin/env python3
"""
build.py — turns your plain-text essays into the finished website.

HOW TO USE (you never edit this file):
  1. Write an essay as a .md text file inside the  posts-source/  folder.
  2. Double-click  build.bat  (or run:  python build.py ).
  3. Done. The styled pages and the homepage are regenerated.

Each .md file starts with a small header. Example:
  ---
  title: The Day You Were Born
  date: October 25, 2026
  excerpt: One line shown on the homepage row.
  image: images/posts/the-day-you-were-born.jpg   (optional thumbnail)
  category: Memories                               (optional, for the sidebar filter)
  ---

It uses only Python's standard library, so there is nothing to install.
"""

import os
import re
import html
import datetime

# ---- Folders (relative to this script) -------------------------------------
HERE   = os.path.dirname(os.path.abspath(__file__))
SRC    = os.path.join(HERE, "posts-source")
POSTS  = os.path.join(HERE, "posts")
INDEX  = os.path.join(HERE, "index.html")

AUTHOR = "Bini"

# Short About blurb shown in the sidebar (edit the text here if you like)
ABOUT_BLURB = ("I'm Bini. This is my notebook — letters, lessons, and memories "
               "I'm writing down for my children, one at a time.")
# Fallback thumbnail when a post has no image: of the storybook icons
DEFAULT_THUMB = "images/posts/_default.jpg"

HEAD = '''  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Security hardening (static-site friendly) -->
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
  <meta name="referrer" content="no-referrer">
  <meta http-equiv="Permissions-Policy" content="geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()">'''


# ============================================================================
#  Tiny Markdown reader (## heading, > quote, *italic*, blank line = paragraph)
# ============================================================================
def parse_front_matter(text):
    meta, body = {}, text
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            block = text[3:end].strip()
            body  = text[end + 3:].lstrip("\n")
            for line in block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
    return meta, body


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def md_to_html(body):
    lines = body.splitlines()
    out, para = [], []

    def flush():
        if para:
            joined = " ".join(l.strip() for l in para)
            if joined.strip().startswith("\u2014") and len(joined) < 40:
                out.append(f'        <p class="post-signoff">{inline(joined)}</p>')
            else:
                out.append(f"        <p>{inline(joined)}</p>")
            para.clear()

    for line in lines:
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("## "):
            flush(); out.append(f"        <h2>{inline(s[3:])}</h2>")
        elif s.startswith("> "):
            flush(); out.append(f"        <blockquote>{inline(s[2:])}</blockquote>")
        else:
            para.append(line)
    flush()
    return "\n".join(out)


# ============================================================================
#  Templates
# ============================================================================
def topbar(prefix=""):
    return f'''  <div class="topbar">
    <div class="wrap">
      <a class="brand" href="{prefix}index.html">{AUTHOR}<span>.</span></a>
      <nav class="topnav">
        <a href="{prefix}index.html">Home</a>
        <a href="{prefix}index.html#writing">Writing</a>
        <a href="{prefix}about.html">About</a>
      </nav>
    </div>
  </div>'''


def footer():
    return f'''  <footer class="site-footer">
    <div class="wrap">
      <p>\u00a9 <span id="year"></span> {AUTHOR} \u00b7 Written with <span class="heart">\u2665</span> for my children.</p>
    </div>
  </footer>'''


def article_page(meta, body_html, nav_html=""):
    title = html.escape(meta.get("title", "Untitled"))
    date  = html.escape(meta.get("date", ""))
    desc  = html.escape(meta.get("excerpt", ""))
    cat   = html.escape(meta.get("category", ""))
    cat_html = f'<div class="article-cat">{cat}</div>' if cat else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{HEAD}
  <title>{title} \u2014 {AUTHOR}</title>
  <meta name="description" content="{desc}">
  <link rel="icon" type="image/svg+xml" href="../images/icon-puppy.svg">
  <link rel="stylesheet" href="../style.css">
</head>
<body>

{topbar(prefix="../")}

  <header class="article-hero">
    <div class="wrap-read">
      {cat_html}
      <div class="date">{date}</div>
      <h1>{title}</h1>
    </div>
  </header>

  <main>
    <div class="wrap-read">
      <article class="post">

{body_html}

        <hr>
{nav_html}
        <a class="back-link" href="../index.html#writing">\u2190 Back to all writing</a>
      </article>
    </div>
  </main>

{footer()}

  <script src="../script.js"></script>
</body>
</html>
'''


def post_row(p):
    """A horizontal blog row: thumbnail left, text right (Derek-Seaman style)."""
    title = html.escape(p["title"])
    date  = html.escape(p["date"])
    exc   = html.escape(p["excerpt"])
    slug  = p["slug"]
    img   = p["image"] or DEFAULT_THUMB
    alt   = html.escape(p.get("alt") or ("Picture for: " + p["title"]))
    cat   = html.escape(p["category"]) if p["category"] else ""
    cat_tag = f'<span class="row-cat">{cat}</span>' if cat else ""
    data_cat = html.escape(p["category"].lower()) if p["category"] else "all"
    return f'''        <article class="post-row" data-category="{data_cat}">
          <a class="row-thumb" href="posts/{slug}.html">
            <img src="{img}" alt="{alt}" loading="lazy">
          </a>
          <div class="row-body">
            <div class="row-meta">{cat_tag}<span class="row-date">{date}</span></div>
            <h3 class="row-title"><a href="posts/{slug}.html">{title}</a></h3>
            <p class="row-excerpt">{exc}</p>
            <a class="row-more" href="posts/{slug}.html">Read more \u2192</a>
          </div>
        </article>'''


def sidebar(categories):
    opts = "\n".join(
        f'            <option value="{html.escape(c.lower())}">{html.escape(c)}</option>'
        for c in categories
    )
    return f'''      <aside class="sidebar">
        <div class="side-card">
          <h3 class="side-title">Browse by topic</h3>
          <select id="categoryFilter" class="cat-select" aria-label="Filter posts by category">
            <option value="all">All writing</option>
{opts}
          </select>
        </div>

        <div class="side-card">
          <h3 class="side-title">About</h3>
          <p class="side-about">{html.escape(ABOUT_BLURB)}</p>
          <a class="side-link" href="about.html">Read more \u2192</a>
        </div>
      </aside>'''


def index_page(rows_html, categories):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{HEAD}
  <title>{AUTHOR} \u2014 Letters, Lessons &amp; Memories</title>
  <meta name="description" content="A quiet place where {AUTHOR} writes down lessons learned, mistakes made, and memories \u2014 notes meant one day for the children.">
  <link rel="icon" type="image/svg+xml" href="images/icon-puppy.svg">
  <link rel="stylesheet" href="style.css">
</head>
<body>

{topbar()}

  <header class="hero">
    <img class="hero-scene" src="images/hero-scene.svg" alt="A warm storybook landscape at golden hour with a little home and a glowing window nestled in gentle hills">
    <div class="hero-inner">
      <p class="eyebrow">A notebook for my children</p>
      <h1>Letters, lessons &amp; memories</h1>
      <p class="lede">A quiet place where I write down what I've learned, the mistakes I've made, and the moments I never want to forget \u2014 one day, for my children.</p>
    </div>
  </header>

  <section class="section-writing" id="writing">
    <div class="wrap blog-layout">

      <main class="post-list-col">
{rows_html}
      </main>

{sidebar(categories)}

    </div>
  </section>

{footer()}

  <script src="script.js"></script>
</body>
</html>
'''


# ============================================================================
#  Build
# ============================================================================
def parse_date(s):
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(s.strip(), fmt)
        except ValueError:
            pass
    return datetime.datetime.min


def nav_block(newer, older):
    def link(p, label, cls):
        if not p: return '<span></span>'
        return (f'<a class="{cls}" href="{p["slug"]}.html"><span class="nav-label">{label}</span>'
                f'<span class="nav-title">{html.escape(p["title"])}</span></a>')
    return ('        <nav class="post-nav">\n          ' + link(older, "\u2190 Older letter", "nav-prev")
            + '\n          ' + link(newer, "Newer letter \u2192", "nav-next") + '\n        </nav>')


def main():
    if not os.path.isdir(SRC):
        print("No posts-source/ folder found. Nothing to build."); return
    os.makedirs(POSTS, exist_ok=True)
    posts = []
    for fn in os.listdir(SRC):
        if not fn.lower().endswith(".md"): continue
        raw = open(os.path.join(SRC, fn), encoding="utf-8").read()
        meta, body = parse_front_matter(raw)
        posts.append({"slug": os.path.splitext(fn)[0], "meta": meta, "body": body,
            "title": meta.get("title", fn), "date": meta.get("date", ""),
            "excerpt": meta.get("excerpt", ""), "image": meta.get("image", ""),
            "alt": meta.get("alt", ""), "category": meta.get("category", ""),
            "_sort": parse_date(meta.get("date", ""))})
    posts.sort(key=lambda p: p["_sort"], reverse=True)

    for i, p in enumerate(posts):
        newer = posts[i-1] if i > 0 else None
        older = posts[i+1] if i+1 < len(posts) else None
        open(os.path.join(POSTS, p["slug"] + ".html"), "w", encoding="utf-8").write(
            article_page(p["meta"], md_to_html(p["body"]), nav_block(newer, older)))
        print(f"  built  posts/{p['slug']}.html")

    cats = []
    for p in posts:
        if p["category"] and p["category"] not in cats: cats.append(p["category"])
    open(INDEX, "w", encoding="utf-8").write(index_page("\n\n".join(post_row(p) for p in posts), cats))

    site = "https://binieth.github.io/"
    urls = [site, site + "about.html"] + [site + "posts/" + p["slug"] + ".html" for p in posts]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc></url>" for u in urls] + ["</urlset>"]
    open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm) + "\n")
    print(f"  built  index.html + sitemap.xml  ({len(posts)} posts, {len(cats)} topics)")
    print("\nDone! Open index.html in your browser to see the result.")


if __name__ == "__main__":
    main()
