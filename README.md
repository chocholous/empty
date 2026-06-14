# Stealth Content Hider

A Manifest V3 browser extension for **cosmetic content filtering**: pages load
normally (the server sees a full page view), but unwanted elements are suppressed
in your own browser via injected CSS/JS. This is the same class of technique used
by uBlock Origin's cosmetic filters — see [`docs/architecture.md`](docs/architecture.md)
for the full technical breakdown.

> Scope: this runs only in your own browser, on pages you visit, and changes only
> what *you* see. It does not attack, probe, or send data to any third party.

## Stack

- **[WXT](https://wxt.dev)** — Vite-based extension framework, TypeScript-first,
  cross-browser (Chrome / Firefox / Edge), HMR dev mode.
- **Manifest V3** with `declarativeNetRequest`, `scripting`, and `storage`.
- Two content-script layers: an **ISOLATED** cosmetic layer and an optional
  **MAIN**-world anti-detection scriptlet.

## Quick start

```bash
npm install        # installs deps and runs `wxt prepare` (generates .wxt/ types)
npm run dev        # launches Chrome with HMR
npm run dev:firefox

npm run build      # production build into .output/
npm run zip        # packaged .zip for the stores
npm run compile    # type-check only (tsc --noEmit)
```

Load the unpacked build (`.output/chrome-mv3/`) via `chrome://extensions` →
Developer mode → "Load unpacked". See [`docs/development.md`](docs/development.md).

## Project layout

```
wxt.config.ts            Manifest + build config
entrypoints/
  background.ts          MV3 service worker (seeds default settings)
  content.ts             ISOLATED world: CSS inject + MutationObserver
  main-world.content.ts  MAIN world: anti-adblock-detection scriptlet
  popup/                 Toolbar popup UI (toggle + selector editor)
lib/
  settings.ts            Typed settings, persisted to storage.sync
  hider.ts               Cosmetic filter engine (stylesheet + observer)
assets/hider.css         Static, always-on cosmetic rules
public/rules.json        declarativeNetRequest network rules (trackers)
docs/                    Architecture + development guides
```

## Roadmap

The full development lifecycle — from this scaffold through store release and
maintenance — is in [`docs/roadmap.md`](docs/roadmap.md).
