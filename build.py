#!/usr/bin/env python3
"""
build.py — turns your plain-text essays into the finished website.

HOW TO USE (you never edit this file):
  1. Write an essay as a .md text file inside the  posts-source/  folder.
  2. Double-click  build.bat  (or run:  python build.py ).
  3. Done. The styled pages and the homepage are regenerated.

It uses only Python's standard library, so there is nothing to install.
"""

import os
import re
import html
import datetime

# ---- Folders (relative to this script) -------------------------------------
HERE   = os.path.dirname(os.path.abspath(__file__))
SRC    = os.path.join(HERE, "posts-source")   # where you write .md files
POSTS  = os.path.join(HERE, "posts")          # generated article pages
INDEX  = os.path.join(HERE, "index.html")     # generated homepage

AUTHOR = "Bini"

# ---- The security + head block shared by every page ------------------------
HEAD = '''  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Security hardening (static-site friendly) -->
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
  <meta name="referrer" content="no-referrer">
  <meta http-equiv="Permissions-Policy" content="geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()">'''


# ============================================================================
#  A tiny Markdown reader.  Supports exactly what you need:
#    ## Heading      -> <h2>
#    > quote         -> <blockquote>
#    *word*          -> <em>word</em>
#    blank line      -> new paragraph
#  Everything is HTML-escaped first, so your text is always safe.
# ============================================================================
def parse_front_matter(text):
    """Pull the title/date/excerpt block from the top of the file."""
    meta = {}
    body = text
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
    """Escape HTML, then turn *italics* into <em>."""
    text = html.escape(text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def md_to_html(body):
    """Convert the essay body into clean HTML paragraphs/headings/quotes."""
    lines = body.splitlines()
    out = []
    para = []

    def flush():
        if para:
            joined = " ".join(l.strip() for l in para)
            # sign-off line (— Dad) gets a special style
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
            flush()
            out.append(f"        <h2>{inline(s[3:])}</h2>")
        elif s.startswith("> "):
            flush()
            out.append(f"        <blockquote>{inline(s[2:])}</blockquote>")
        else:
            para.append(line)
    flush()
    return "\n".join(out)


# ============================================================================
#  Page templates
# ============================================================================
def article_page(meta, body_html):
    title = html.escape(meta.get("title", "Untitled"))
    date  = html.escape(meta.get("date", ""))
    desc  = html.escape(meta.get("excerpt", ""))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{HEAD}
  <title>{title} \u2014 {AUTHOR}</title>
  <meta name="description" content="{desc}">
  <link rel="stylesheet" href="../style.css">
</head>
<body>

  <div class="topbar">
    <div class="wrap">
      <a class="brand" href="../index.html">{AUTHOR}<span>.</span></a>
      <nav class="topnav">
        <a href="../index.html">Home</a>
        <a href="../index.html#writing">Writing</a>
        <a href="../about.html">About</a>
      </nav>
    </div>
  </div>

  <header class="article-hero">
    <div class="wrap-read">
      <div class="date">{date}</div>
      <h1>{title}</h1>
    </div>
  </header>

  <main>
    <div class="wrap-read">
      <article class="post">

{body_html}

        <hr>
        <a class="back-link" href="../index.html#writing">\u2190 Back to all writing</a>
      </article>
    </div>
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <p>\u00a9 <span id="year"></span> {AUTHOR} \u00b7 Written with <span class="heart">\u2665</span> for my children.</p>
    </div>
  </footer>

  <script src="../script.js"></script>
</body>
</html>
'''


def card_html(p, featured=False):
    title = html.escape(p["title"])
    date  = html.escape(p["date"])
    exc   = html.escape(p["excerpt"])
    slug  = p["slug"]
    if featured:
        tag = html.escape(p.get("tag", "\u2605 Start here"))
        return f'''        <article class="card card-featured">
          <span class="tag">{tag}</span>
          <div class="date">{date}</div>
          <h3><a href="posts/{slug}.html">{title}</a></h3>
          <p>{exc}</p>
          <a class="more" href="posts/{slug}.html">Read the letter \u2192</a>
        </article>'''
    return f'''        <article class="card">
          <div class="date">{date}</div>
          <h3><a href="posts/{slug}.html">{title}</a></h3>
          <p>{exc}</p>
          <a class="more" href="posts/{slug}.html">Read the letter \u2192</a>
        </article>'''


def index_page(cards_html):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{HEAD}
  <title>{AUTHOR} \u2014 Letters, Lessons &amp; Memories</title>
  <meta name="description" content="A quiet place where {AUTHOR} writes down lessons learned, mistakes made, and memories \u2014 notes meant one day for the children.">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <div class="topbar">
    <div class="wrap">
      <a class="brand" href="index.html">{AUTHOR}<span>.</span></a>
      <nav class="topnav">
        <a href="index.html">Home</a>
        <a href="#writing">Writing</a>
        <a href="about.html">About</a>
      </nav>
    </div>
  </div>

  <header class="hero">
    <div class="hero-inner">
      <p class="eyebrow">A notebook for my children</p>
      <h1>Letters, lessons &amp; memories</h1>
      <p class="lede">A quiet place where I write down what I've learned, the mistakes I've made, and the moments I never want to forget \u2014 one day, for my children.</p>
      <a class="cta" href="#writing">Start reading</a>
    </div>
  </header>

  <section class="section-writing" id="writing">
    <div class="wrap">
      <div class="heading">
        <span class="kicker">The Writing</span>
        <h2>Pages from my binder</h2>
      </div>

      <div class="post-grid">

{cards_html}

      </div>
    </div>
  </section>

  <footer class="site-footer">
    <div class="wrap">
      <p>\u00a9 <span id="year"></span> {AUTHOR} \u00b7 Written with <span class="heart">\u2665</span> for my children.</p>
    </div>
  </footer>

  <script src="script.js"></script>
</body>
</html>
'''


# ============================================================================
#  Main build
# ============================================================================
def parse_date(s):
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(s.strip(), fmt)
        except ValueError:
            pass
    return datetime.datetime.min  # unknown dates sort last


def main():
    if not os.path.isdir(SRC):
        print("No posts-source/ folder found. Nothing to build.")
        return
    os.makedirs(POSTS, exist_ok=True)

    posts = []
    for fn in os.listdir(SRC):
        if not fn.lower().endswith(".md"):
            continue
        slug = os.path.splitext(fn)[0]
        raw  = open(os.path.join(SRC, fn), encoding="utf-8").read()
        meta, body = parse_front_matter(raw)

        body_html = md_to_html(body)
        page = article_page(meta, body_html)
        open(os.path.join(POSTS, slug + ".html"), "w", encoding="utf-8").write(page)

        posts.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "date": meta.get("date", ""),
            "excerpt": meta.get("excerpt", ""),
            "featured": meta.get("featured", "").lower() == "true",
            "tag": meta.get("tag", ""),
            "_sort": parse_date(meta.get("date", "")),
        })
        print(f"  built  posts/{slug}.html")

    # newest first
    posts.sort(key=lambda p: p["_sort"], reverse=True)

    # featured posts go last in the grid (they render full-width as an anchor);
    # everything else newest-first on top.
    normal   = [p for p in posts if not p["featured"]]
    featured = [p for p in posts if p["featured"]]
    cards = [card_html(p) for p in normal] + [card_html(p, featured=True) for p in featured]

    open(INDEX, "w", encoding="utf-8").write(index_page("\n\n".join(cards)))
    print(f"  built  index.html  ({len(posts)} post(s) total)")
    print("\nDone! Open index.html in your browser to see the result.")


if __name__ == "__main__":
    main()
