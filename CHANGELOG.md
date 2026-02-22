# Changelog — FPKGi Manager (Python Edition)

All notable changes are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

Repository: [github.com/RastaFairy/FPKGi-for-PY](https://github.com/RastaFairy/FPKGi-for-PY)

---

## Version history at a glance

| Version | Key milestone |
|---------|---------------|
| v1.0 | First working prototype — tkinter UI, dark theme, JSON loader |
| v2.0 | Persistent icon cache + real PKG download to disk |
| v3.3 | PSN Update XML API (HMAC) + SerialStation scraper |
| v4.2 | Dual JSON format + OrbisPatches replaces SerialStation |
| v5.2 | Multilingual UI (9 languages) + HTTP availability check |
| v5.3 | Internal refactor and stability improvements |
| v5.4 | Thread-safe icon queue + external `lang/*.json` files |
| v5.5 | Icon progress bar |
| v5.6 | **Playwright** — Cloudflare bypass for OrbisPatches |
| v5.7 | Scraper robustness improvements |
| v5.8 | `UpdatesWindow` + `DownloadManager` floating windows |
| v5.9 | Hardened HTML parser + two-tier fetch strategy |
| v5.10 | Session persistence (geometry, language, last JSON) |
| v5.11 | Anthropic AI patch-note translation + formal author credits |
| v5.11-FTP | **FTP transfer** to PS4 + `FTPConfigWindow` |
| v5.12 | Persistent `_PlaywrightPool` singleton — faster patch queries |
| v5.12-FTP | FTP + Playwright pool + animated PS4 background · **current** |

---

## [v5.12-FTP] — Current release

### Added
- **Animated PS4-style background**: 32-band deep-navy → PS-blue gradient canvas with 36 floating △○×□ particles at ~25 fps
- `_build_background()` — particle system with per-particle drift, speed and vertical wrap
- `_draw_bg_gradient()` — gradient repaints on every window resize (`<Configure>`)
- `_bg_canvas.lower()` via `tk.Misc.lower()` (see Fixed below)

### Fixed
- **`_bg_canvas.lower()` crash on Python 3.13** — `Canvas.lower()` in Python 3.13 requires a `tagOrId` argument; replaced with `tk.Misc.lower(self._bg_canvas)` to correctly lower the widget in the stacking order without touching canvas items

### Changed
- CI workflow updated: Python 3.13 added to lint matrix
- PyInstaller build command uses `fpkgi_manager_with_ftp.py` directly (no `.spec` file needed)

---

## [v5.12] — Persistent Playwright pool

### Added
- `_PlaywrightPool` as a **persistent singleton**: Chromium launched once at app startup, reused for every OrbisPatches request — eliminates the cold-start delay on each query
- Pool API: `start()` at boot · `fetch(url)` from any thread · `stop()` on close
- Animated PS4-style background (same implementation as 5.12-FTP)

### Changed
- OrbisPatches fetching is now 3–5× faster thanks to the persistent browser pool
- `_pw_fetch()` delegates to the pool instead of spawning Chromium per request

---

## [v5.11-FTP] — FTP transfer to PS4

### Added
- **FTP transfer mode** via Python `ftplib` — no intermediate local copy needed
- `FTPConfigWindow` (`tk.Toplevel`) — dedicated panel for host, port, credentials, remote path, passive mode, timeout
- `_download_to_ftp()` — streaming HTTP → FTP pipeline using an internal `StreamToFTP` adapter; data flows directly from the CDN to the PS4
- `ftp_config.json` + `ftp_config.json.example` — persistent FTP configuration file
- `GUIA_FTP_COMPLETA.txt` / `RESUMEN_FTP.txt` — Spanish FTP setup guides
- "Send PKG via FTP" button in toolbar and Downloads menu
- `_send_local_pkg()` — send an already-downloaded local PKG to the PS4

### Changed
- `download_pkg()` detects FTP mode and routes to `_download_to_ftp()` instead of local save

---

## [v5.11] — AI translation + formal credits

### Added
- **Real-time patch note translation** via Anthropic Claude API
  - `translate_patch_notes(text_en, target_lang)` — async, non-blocking, cached per session
  - "Translate" button in `UpdatesWindow` per patch entry
  - Falls back silently when `ANTHROPIC_API_KEY` is not set
- Formal author credits in module docstring: Bucanero → ItsJokerZz → RastaFairy
- MIT licence header in source file
- Module attributes: `__title__`, `__version__`, `__author__`, `__licence__`, `__repository__`

---

## [v5.10] — Session persistence

### Added
- `_SETTINGS` dict with `load_settings()` / `save_settings()` backed by `settings.json`
- Persistent across sessions: window geometry, last opened JSON path, paned sash position, selected UI language
- Auto-reload of last JSON on startup (delayed 300 ms for smooth UI init)
- Sash position restored via `after(200, ...)` after window render

---

## [v5.9] — Scraper robustness

### Changed
- OrbisPatches HTML parser hardened against layout changes
- `_is_cf_blocked()` improved Cloudflare challenge detection
- `fetch_orbis_full()` two-tier strategy: Playwright first, `requests` fallback
- Better error messaging in `UpdatesWindow` for network failures and empty results

---

## [v5.8] — Floating windows

### Added
- **`UpdatesWindow`** (`tk.Toplevel`) — scrollable patch list per game: version, required firmware, file size, release date, patch notes, OrbisPatches attribution
- **`DownloadManager`** (`tk.Toplevel`) — singleton floating window tracking all active and queued PKG downloads with per-download cancel support
- `DownloadWindow` helper for per-download card widgets inside `DownloadManager`
- Right-click context menu on the game list: View Updates / Check Availability / Download / Open OrbisPatches
- Double-click on a game row opens `UpdatesWindow` directly

### Changed
- Download progress cards moved from main panel into `DownloadManager` window

---

## [v5.7] — Stability fixes

### Fixed
- OrbisPatches scraper updated for HTML structure changes in the OrbisPatches site
- Playwright wait selector tuned to `.patch-container`
- Improved timeout and error handling for slow network connections

---

## [v5.6] — Playwright / Cloudflare bypass

### Added
- **Playwright** (`playwright` + Chromium) dependency
- `_playwright_get_html()` — renders the full JavaScript SPA, bypasses Cloudflare 403 / JS challenge
- Navigator `webdriver` fingerprint removed to lower Cloudflare bot detection score
- `_is_cf_blocked()` — detects Cloudflare challenge pages and triggers fallback
- `requests` fallback path when Playwright is not installed (graceful degradation)

### Changed
- OrbisPatches fetching completely rewritten around headless Chromium rendering
- `requirements.txt` updated: `playwright>=1.40`

---

## [v5.4 / v5.5] — Thread-safe queue + external language files

### Added (v5.4)
- `queue.Queue` for thread-safe icon progress reporting (`_icon_queue`)
- `_poll_icon_queue()` — polls the queue from the main thread every 50 ms (safe for tkinter)
- **External language files**: `lang/{code}.json` loaded on demand; English built-in as silent fallback
- `MAX_WORKERS` capped at 8 (was uncapped at 100 in v5.2)

### Added (v5.5)
- Icon progress bar shown while prefetching covers during JSON load
- `_show_progress()` / `_hide_progress()` helpers

---

## [v5.2 / v5.3] — Multilingual UI + availability check

### Added
- **9-language UI**: ES, EN, IT, DE, FR, RU, ZH, KO, JA
- Full `TRANSLATIONS` dict embedded in source (later externalised to `lang/*.json`)
- `t(key, **kw)` localisation helper with keyword interpolation
- **PKG availability check** via HTTP HEAD — `check_url_available()`
- Status column in game list: AVAILABLE (green) / NOT AVAILABLE (red) / NOT CHECKED (grey)
- Per-session configurable download path (`_session_download_base`)
- OrbisPatches as primary patch source (replaces PSN XML)
- Parallel non-blocking downloads via `ThreadPoolExecutor`

### Changed (v5.3)
- Internal class refactor for cleaner state management
- Stability improvements for large JSON catalogues

---

## [v4.2] — Dual JSON format + OrbisPatches

### Added
- **Dual JSON format normaliser**: reads both FPKGi `DATA` dict and PS4PKGInstaller `packages` list into a unified internal model
- **OrbisPatches** (`orbispatches.com/{tid}`) as primary patch source — provides full patch history (vs. PSN XML which returns only the latest patch)
- `fetch_orbis_patches()` — HTML scraper for the complete patch table
- Downloads saved to `./descargas/{title_id}/` relative to the script directory
- Removed BeautifulSoup4 dependency

### Changed
- PSN Update XML API retained as metadata source (firmware requirement, file size) alongside OrbisPatches
- `fetch_full_info()` combines both sources

---

## [v3.3] — PSN Update XML API + SerialStation

### Added
- **PSN Update XML API** with HMAC-SHA256 request signing — returns exact firmware requirement, file size, and latest patch version from Sony's official servers
- **SerialStation** scraper (`/updates/CUSA/*`, `/titles/CUSA/*`) for changelog text and game metadata
- `beautifulsoup4` dependency for HTML parsing
- Built-in Spanish translation dictionary for common English patch note phrases
- `MAX_WORKERS = 8` parallel executor for icon prefetch
- Versioned app header (`APP_VERSION = "3.3"`)

---

## [v2.0] — Persistent cache + PKG download

### Added
- `icons_cache/` directory — PNG covers cached to disk by URL hash (survives app restart)
- `downloads/` directory — downloaded PKGs saved locally
- `download_pkg()` — threaded PKG download with progress indicator
- `is_downloading` flag to prevent concurrent downloads
- `open_downloads_folder()` / `open_cache_folder()` menu shortcuts
- `clear_icon_cache()` — wipes all cached icons
- `hashlib` for deterministic cache filenames

### Changed
- `cover_cache` is now a two-level cache: memory (fast) + disk (persistent)

---

## [v1.0] — First prototype

### Added
- `FPKGiManager` class — single-file tkinter application, 1400×800 window
- Dark theme palette: `#1a1a2e` / `#16213e` / `#0f3460` / `#e94560`
- Menu bar: File → Open JSON / Save as / Exit
- `ttk.Treeview` game list with columns: Name, Title ID, Region, Size
- Detail panel: cover art loaded from URL + game metadata labels
- `ScraperWindow` — basic web scraping helper window
- `load_json_file()` / `save_json_file()` — open and save `GAMES.json`
- In-memory cover image cache (`cover_cache` dict)
- Dependencies: `requests` + `Pillow`
- UI language: Spanish (hard-coded)
