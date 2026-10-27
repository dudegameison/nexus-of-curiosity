# Play Nexus of Curiosity in the Browser

This folder contains a web-ready version of the game using **pygbag**.

## Local test (recommended first)
```bash
pip install pygbag
cd web
pygbag .
# then open http://localhost:8000
```

## GitHub Pages (permanent link)
1. Go to repo Settings → Pages
2. Source: Deploy from branch `main` / folder `/web` (or root if you move files)
3. Save — after a few minutes the game will be at:
   `https://dudegameison.github.io/nexus-of-curiosity/`

## Notes
- Main entry must be named `main.py`
- Game loop is async and yields with `await asyncio.sleep(0)`
- Sound is stubbed for browser compatibility
- Controls are the same (WASD, Space, E, mouse)
