# Bini — Personal Blog

A warm, personal blog for writing letters, lessons, and memories.
Plain HTML + CSS + a tiny bit of JavaScript. No build step. Works directly on GitHub Pages.

## Files
- `index.html` — homepage (welcome note + list of articles)
- `about.html` — about page
- `404.html` — "page not found" page
- `style.css` — all the styling 
- `script.js` — tiny script that keeps the footer year current automatically
- `robots.txt` — basic search-engine crawl rules
- `posts/` — each article is one HTML file in here
- `.nojekyll` — tells GitHub Pages to serve files as-is

## How to add a new article
1. Copy `posts/a-letter-to-my-children.html` to a new file, e.g. `posts/my-new-story.html`.
2. Change the title, date, and the writing inside the `<article>` section.
3. Open `index.html` and add a new `<li class="post-item">` block at the TOP of the
   list (newest first), pointing to your new file. Copy the existing block as a template.
4. Commit and push.

## Security notes
This site is hardened as much as a GitHub Pages static site allows:


