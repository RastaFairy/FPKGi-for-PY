# Changelog — FPKGi Manager (Python Edition)

All notable changes to this project are documented here.
Versions are listed from newest to oldest.

---

## [5.11-FTP] — Current Release

### Added
- Built-in FTP client — transfer PKG files directly to PS4 over local network
- FTP Settings dialog: host, port, user, password, remote path, passive mode, timeout
- "Test Connection" button in FTP dialog
- `ftp_config.json` — FTP configuration persisted to disk between sessions
- Streaming upload to FTP with real-time progress callback
- Auto-creation of remote FTP directory if it doesn't exist
- FTP toggle in File menu

### Changed
- Download routing: automatically uses FTP when enabled, local folder otherwise
- Progress display in Download Manager updated to show FTP transfer progress

---

## [5.11]

### Added
- Claude API integration for real-time patch note translation to any language
- `ANTHROPIC_API_KEY` environment variable support
- Formal credit block in file header (Bucanero / ItsJokerZz / RastaFairy)
- `__version__`, `__author__`, `__license__`, `__repository__` metadata fields

### Changed
- MIT License explicitly declared in file header

---

## [5.10]

### Changed
- Async Playwright pool fully rewritten with proper asyncio event loop management
- API simplified: `_pw_pool.start()` / `_pw_pool.fetch(url)` / `_pw_pool.stop()`
- Browser lifecycle now managed automatically by main app class

### Fixed
- asyncio event loop conflicts on Windows
- Timeout recovery now resets browser context instead of crashing

---

## [5.9]

### Added
- Persistent Playwright browser pool (`_PlaywrightPool`) — browser stays alive for the full session
- asyncio loop runs in dedicated daemon thread
- Thread-safe fetch via queue-based synchronization

### Changed
- Patch lookups dramatically faster — no cold-start per query

---

## [5.8]

### Fixed
- OrbisPatches HTML parser updated for new DOM layout (post-Cloudflare JS render)
- Patch-wrapper → patch-container → patch-link hierarchy now correctly parsed
- Size and version extraction made more robust

### Changed
- Cloudflare detection heuristics improved

---

## [5.7]

### Changed
- OrbisPatches scraper: switched from `networkidle` strategy to explicit element wait
- Playwright anti-detection: inject JS to hide `navigator.webdriver`

---

## [5.6]

### Added
- Playwright integration — headless Chromium to bypass Cloudflare on OrbisPatches
- Two-tier fetch strategy: Playwright (preferred) → requests + API fallback
- OrbisPatches API endpoint updated to `api/patch.php`

### Changed
- New requirement: `python -m playwright install chromium`

---

## [5.4 / 5.5]

### Added
- 9-language UI system — English built-in, others loaded from `lang/*.json`
- Language menu for runtime switching (no restart needed)
- `t(key)` translation function — all UI strings localized
- Per-session configurable download path
- Progress bar for parallel icon prefetch

---

## [4.2]

### Added
- Dual JSON format support: `DATA dict` (FPKGi) and `packages list` (PS4PKGInstaller)
- OrbisPatches integration for full patch history (replaced SerialStation)
- `APP_DIR`-relative paths — portable regardless of working directory

### Changed
- Downloads now organized by Title ID: `./descargas/CUSAXXXXX/*.pkg`
- PSN HMAC API retained for data verification

### Removed
- SerialStation dependency

---

## [3.3]

### Added
- PSN Update XML API (HMAC-signed) — official version, size, firmware data
- SerialStation integration — patch changelogs and title info
- Built-in EN→ES patch note translations for common phrases
- ThreadPoolExecutor (up to 8 workers) for parallel API calls
- Graceful fallback when `requests` or `Pillow` not installed

---

## [2.0]

### Added
- Real PKG downloads to local `downloads/` folder
- Icon disk cache (`icons_cache/`) — covers saved locally and reused
- Cache management (clear icon cache from menu)
- Download folder management (open from menu)
- Download progress indicator

---

## [1.0] — Initial Release

### Added
- Tkinter GUI with dark navy/red theme
- Load and display `GAMES.json` (DATA dict format)
- Search by name or Title ID, region filter, sort options
- Live cover art download (no cache)
- Game detail panel with metadata
- Open PKG URL in browser
- Add / edit / delete games
- Statistics panel (total, size, region breakdown)
- Archive.org scraper window (stub)
