# my-website

Personal portfolio for **Anthea Poklewski-Koziell** — university projects, ongoing builds, and HTML/CSS experiments.

## How this site is structured

Same idea as many research portfolios (home → clickable project cards → article pages), kept as plain HTML/CSS:

```
my_website/
  index.html              ← home (intro + featured cards)
  style.css               ← shared look & colour scheme
  images/                 ← photos used across pages
  university_projects/    ← original media
  projects/
    index.html            ← full project grid
    coffee-stabiliser/index.html
    line-following-robot/index.html
    outdoor-slam/index.html
    ...
```

## Add a new project article

1. Create a folder: `projects/my-new-project/`
2. Copy any existing `projects/*/index.html` into it
3. Edit the title, summary, images, and body text
4. Add a card on **both**:
   - `index.html` (featured, optional)
   - `projects/index.html` (full list)
5. Point the card’s `href` to `projects/my-new-project/index.html`

Card pattern:

```html
<a class="project-card" href="projects/my-new-project/index.html">
  <div class="project-card-media">
    <img src="images/your-cover.jpg" alt="Short description">
  </div>
  <div class="project-card-body">
    <span class="project-card-date">2026</span>
    <h3>Project title</h3>
    <p>One or two sentences for the preview.</p>
  </div>
</a>
```

## Preview locally

From this folder:

```bash
python3 -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000).

## Colour scheme

Teal / soft greenhouse tones in `style.css` (`:root` variables). Change `--accent`, `--bg`, and `--brass` to restyle the whole site.

## Safe inspiration note

Gilbert Tanner’s site uses Hugo + PaperMod. This site borrows the *interaction pattern* (cards → articles), not his theme files, assets, or copy.
