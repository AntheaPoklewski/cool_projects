# my-website

Personal portfolio **Anthea Poklewski-Koziell** — university projects, ongoing builds, electronic hobbies, UP-Robotics club!.

## How this site is structured

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

## Preview locally

From this folder:

```bash
python3 -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000).

## Colour scheme

Teal / soft greenhouse tones in `style.css` (`:root` variables). Change `--accent`, `--bg`, and `--brass` to restyle the whole site.
