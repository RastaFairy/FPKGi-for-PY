<div align="center">

# 🎮 FPKGi Manager — Python Edition

**A full-featured PS4 FPKG game catalog manager built in Python**

[![Version](https://img.shields.io/badge/version-5.11--FTP-blue?style=flat-square)](https://github.com/RastaFairy/FPKGi-for-PY)
[![Python](https://img.shields.io/badge/python-3.8%2B-yellow?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)]()

*Original concept by [Bucanero](https://github.com/bucanero) (PSP Homebrew) · PS4/PS5 port by [ItsJokerZz](https://github.com/ItsJokerZz) · Python adaptation by [RastaFairy](https://github.com/RastaFairy)*

</div>

---

## 📖 What is this?

**FPKGi Manager** is a desktop application that lets you browse, search, organize, and download **FPKG (Fake PKG)** game files for the PlayStation 4 from your PC.

### 🤔 What is FPKG?

An FPKG (Fake Package) is a format used on modified PS4 consoles that allows users to install game backups. These files follow the same `.pkg` format used by Sony, but they are distributed through third-party lists and archives. This tool does **not** generate or create FPKGs — it only helps you **manage existing catalogs** that you already have or load via a JSON list.

### 📋 What is a GAMES.json / catalog file?

FPKGi (the PS4 homebrew app by ItsJokerZz) uses a special JSON format to store game lists. This Python tool reads those same JSON files, so you can manage your game library on your PC with a modern graphical interface.

---

## ✨ Features (v5.11-FTP — Latest)

- 📂 **Dual JSON format** — reads both `FPKGi DATA dict` and `PS4PKGInstaller packages list` formats
- 🌐 **OrbisPatches integration** — fetches real patch history (version, size, notes) for each game via Playwright JS rendering with Cloudflare bypass
- 🔍 **PKG availability check** — verifies if a download URL is still live (HTTP HEAD)
- ⬇️ **Parallel downloads** — up to 8 simultaneous downloads, non-blocking UI
- 📡 **FTP transfer** — send PKGs directly to your PS4 over your local network (new in 5.11-FTP)
- 🌍 **Multilingual UI** — English built-in + 8 additional languages via `lang/*.json` files
- 🖼️ **Cover art** — parallel prefetch with persistent disk cache
- 🤖 **Patch note translation** — translate patch notes to any language via Claude API (optional)
- 🖥️ **Cross-platform** — works on Windows, Linux, and macOS
- 🔎 **Advanced search & filtering** — by name, Title ID, region, version, size
- ↕️ **Column sorting** — click any column header to sort the game list

---

## 🚀 Installation & Requirements

### Prerequisites

- **Python 3.8 or newer** → [Download Python](https://python.org/downloads/)
- **pip** (comes with Python)

### Step 1 — Install Python dependencies

```bash
pip install Pillow requests playwright
```

### Step 2 — Install Chromium (for OrbisPatches / Cloudflare bypass)

```bash
python -m playwright install chromium
```

### Step 3 — (Optional) Set Claude API key for patch note translation

```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

# Linux / macOS
export ANTHROPIC_API_KEY=sk-ant-...
```

### Step 4 — Run the application

```bash
python fpkgi_manager_with_ftp.py
```

---

## 📡 FTP Setup (v5.11-FTP)

The FTP feature lets you transfer PKG files directly to your PS4 without copying to a USB drive.

1. On your PS4, make sure an FTP server is running (e.g. via GoldHEN or similar)
2. In FPKGi Manager, go to **File → FTP Settings**
3. Enter your PS4's local IP address (e.g. `192.168.1.210`), port (`2121` by default), and remote path (`/data/pkg`)
4. Click **Test Connection** to verify
5. Enable FTP mode and downloads will be sent directly to your PS4

The FTP configuration is saved automatically to `ftp_config.json` in the app folder.

---

## 📂 Project Structure

```
FPKGi-for-PY/
├── fpkgi_manager_with_ftp.py   ← Main script (v5.11-FTP, latest)
├── ftp_config.json              ← Auto-generated FTP settings
├── lang/                        ← Language files (JSON)
│   ├── es.json                  ← Spanish
│   ├── fr.json                  ← French
│   └── ...
├── icons_cache/                 ← Cover art cache (auto-generated)
└── descargas/                   ← Downloads folder (auto-generated)
    └── CUSAXXXXX/
        └── game.pkg
```

---

## 🗂️ Supported JSON Formats

### Format 1 — FPKGi DATA dict

```json
{
  "DATA": {
    "https://example.com/game.pkg": {
      "title_id": "CUSA09267",
      "name": "A Hat in Time",
      "region": "USA",
      "version": "01.04",
      "size": 7747563520,
      "min_fw": "9.00",
      "cover_url": "https://..."
    }
  }
}
```

### Format 2 — PS4PKGInstaller packages list

```json
{
  "packages": [
    {
      "title_id": "CUSA09267",
      "name": "A Hat in Time",
      "region": "USA",
      "version": "01.04",
      "pkg_url": "https://example.com/game.pkg",
      "icon_url": "https://...",
      "size": "7.21 GB",
      "system_version": "9.00"
    }
  ]
}
```

---

## 🕹️ How to Use

1. **Launch** the application with `python fpkgi_manager_with_ftp.py`
2. **Open a JSON** — use File → Open JSON or the toolbar button to load your game catalog
3. **Browse the list** — search by name or Title ID, filter by region, sort by any column
4. **Select a game** — click a row to see cover art and details in the right panel
5. **Check availability** — right-click → "Check availability" to test if the download URL works
6. **View updates** — right-click → "View Updates" to fetch patch history from OrbisPatches
7. **Download** — right-click → "Download PKG" or use the button; choose local folder or FTP to PS4
8. **Manage downloads** — File → Manage Downloads to monitor progress, cancel, or open downloaded files

---

## 🌍 Language Support

The UI language can be changed from the **Language** menu at runtime (no restart needed). English is built-in. Additional languages are loaded from `lang/<code>.json`.

To add a new language, copy `lang/es.json`, translate all values, and save as `lang/<your_code>.json`. The new language will appear automatically in the menu.

---

## 📜 Version History

### v1.0 — The Foundation
- Basic tkinter GUI with dark theme (navy blue + red accent)
- Load and display `GAMES.json` (DATA dict format)
- Search by name or Title ID, filter by region, sort options
- Cover art display (downloaded live, no cache)
- Game detail panel with metadata
- Open PKG URL in browser
- Add / edit / delete games
- Archive.org scraper UI (stub — not yet functional)
- Statistics panel (total games, size, region breakdown)

### v2.0 — Downloads & Cache
- **Real PKG downloads** to a local `downloads/` folder
- **Icon disk cache** (`icons_cache/`) — covers are now saved locally and reused
- Cache management tools (clear icon cache from menu)
- Download folder management (open from menu)
- Download progress indicator

### v3.3 — PSN & SerialStation Integration
- **PSN Update XML API** integration — fetches official version, size, and minimum firmware using HMAC-signed requests
- **SerialStation** integration — fetches patch changelogs and title info
- Built-in patch note translations (English → Spanish) for common phrases
- ThreadPoolExecutor for parallel API calls (up to 8 workers)
- Graceful fallback if `requests` or `Pillow` is not installed
- Configurable ICONS_CACHE_DIR and MAX_WORKERS constants

### v4.2 — OrbisPatches & Dual Format
- **Dual JSON format** support: both `DATA dict` (FPKGi) and `packages list` (PS4PKGInstaller)
- Removed SerialStation dependency — replaced by **OrbisPatches** for full patch history
- **PKG downloads** organized by Title ID: `./descargas/CUSAXXXXX/*.pkg`
- PSN HMAC API retained for official data verification
- OrbisPatches fallback API (`/api/patch.php`) when main page is unavailable
- Download headers simulated as browser (Chromium UA)
- `APP_DIR`-relative paths — works regardless of working directory

### v5.4 — Multilingual UI
- **9-language UI** — English built-in, additional languages loaded from `lang/*.json`
- Language can be switched at runtime from the Language menu
- All UI strings now go through a translation function `t(key)`
- Missing keys fall back to English silently
- Per-session configurable download path
- Progress bar for icon prefetch

### v5.6 — Playwright & Cloudflare Bypass
- **Playwright integration** — headless Chromium to bypass Cloudflare on OrbisPatches
- Two-tier strategy: Playwright (preferred) → requests fallback
- OrbisPatches endpoint updated to `api/patch.php` (JSON-based)
- `python -m playwright install chromium` now required
- Anti-detection JS injection (`navigator.webdriver` hidden)

### v5.8 — Verified HTML Parser
- OrbisPatches HTML structure re-verified against live dump
- Parser updated for new DOM layout: `patch-wrapper > patch-container > patch-link`
- More reliable extraction of version, size, and patch notes
- Improved Cloudflare detection heuristics

### v5.9 — Async Playwright Pool
- **Persistent Playwright browser pool** — browser stays alive for the full session
- No more cold-start per query — dramatically faster patch lookups
- asyncio loop runs in a dedicated daemon thread
- Thread-safe fetch via queue-based synchronization

### v5.10 — Stable Async Architecture
- Rewritten async pool with proper asyncio event loop management
- API cleaned up: `_pw_pool.start()` / `_pw_pool.fetch(url)` / `_pw_pool.stop()`
- Lifecycle now managed automatically by the main app class
- Improved error handling and timeout recovery

### v5.11 — Claude API Translation
- **Claude API integration** — patch notes can be translated to any language in real time
- Formal credit block added to header (Bucanero / ItsJokerZz / RastaFairy)
- MIT license declared in file header
- `__version__`, `__author__`, `__license__`, `__repository__` metadata fields
- `ANTHROPIC_API_KEY` environment variable support

### v5.11-FTP — FTP Transfer to PS4 *(Current)*
- **FTP client built in** — transfer PKGs directly to your PS4 over local network
- FTP settings dialog: host, port, user, password, remote path, passive mode, timeout
- **Test connection** button — verify FTP before downloading
- `ftp_config.json` — persistent FTP configuration saved to disk
- Download routing: local folder or FTP depending on FTP enabled state
- Streaming upload with progress callback — real-time transfer progress shown in download manager
- Auto-create remote directory if it doesn't exist
- FTP toggle in main menu

---

## 🙏 Credits

| Role | Person |
|---|---|
| Original FPKGi concept (PSP) | [Bucanero](https://github.com/bucanero) |
| PS4/PS5 port of FPKGi | [ItsJokerZz](https://github.com/ItsJokerZz) |
| Python adaptation & all versions | [RastaFairy](https://github.com/RastaFairy) |

---

## ⚠️ Disclaimer

This tool is intended for **educational and personal use only**. It does not host, distribute, or generate any game files. Users are solely responsible for what they do with the software and must comply with the laws of their country. The authors do not condone piracy.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
