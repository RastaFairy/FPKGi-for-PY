<div align="center">

# 🎮 FPKGi Manager

**PS4 FPKG game manager with OrbisPatches integration**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-5.11-orange)
![Status](https://img.shields.io/badge/Status-Maintained-brightgreen)

</div>

---

## 📋 Table of contents

- [✨ Key features](#key-features)
- [🚀 Quick start](#quick-start)
- [📦 Requirements and installation](#requirements-and-installation)
- [📁 Project structure](#project-structure)
- [🎯 User guide](#user-guide)
- [🔧 Configuration](#configuration)
- [🌍 Supported languages](#supported-languages)
- [🔎 OrbisPatches patch system](#orbispatches-patch-system)
- [⬇️ Downloads and manager](#downloads-and-manager)
- [🌐 Cloudflare handling](#cloudflare-handling)
- [📝 Changelog](#changelog)
- [⚠️ Disclaimer](#disclaimer)

---

## ✨ Key features

### 🎛️ Game management
- **Dual JSON support** — Compatible with two formats:
  - `FPKGi` format (DATA dictionary)
  - `PS4PKGInstaller` format (packages list)
- **Visual catalog** — Interactive table with covers, title, version, and status
- **Real-time search** — Filter by name, TITLE_ID, or region
- **Sorting** — Click any column header to sort

### 🔄 OrbisPatches integration
- **Advanced scraper** — Extracts metadata directly from orbispatches.com:
  - Patch version
  - Firmware requirement
  - File size
  - Creation date
  - Patch notes
- **Chromium rendering** — Executes JavaScript to bypass Cloudflare
- **Automatic fallback** — Uses requests if Playwright unavailable
- **Compatibility indicator** — Shows 🟢 (compatible) or 🔴 (incompatible) by FW

### ✅ Availability verification
- **HTTP checking** — Verifies download URLs are alive
- **Session caching** — Stores results to avoid re-queries
- **Visual indicators** — Real-time status (AVAILABLE/UNAVAILABLE/NOT CHECKED)

### ⬇️ Download manager
- **Parallel downloads** — Download multiple files simultaneously
- **Progress bars** — Real-time visualization per file
- **Configurable path** — Change download folder without config files
- **Floating manager** — Independent window to monitor downloads
- **Auto-organization** — Files saved to `./download/{TITLE_ID}/`

### 🎨 Multilingual interface
- **8 additional languages** — Dynamically loaded from `lang/*.json`
  - 🇬🇧 English · 🇪🇸 Español · 🇮🇹 Italiano · 🇩🇪 Deutsch · 🇫🇷 Français
  - 🇷🇺 Русский · 🇨🇳 中文 · 🇰🇷 한국어 · 🇯🇵 日本語
- **Automatic fallback** — Missing keys fall back to English
- **Real-time switching** — Entire UI updates without restart

### 🖼️ Icon caching
- **Parallel prefetch** — Downloads all covers automatically
- **Progress bar** — Visualize prefetch progress
- **Persistent cache** — Icons saved locally in `icons_cache/`
- **Manual cleanup** — Clear cache from menu

### 🌐 Patch notes translation
- **Automatic translation** — Converts patch notes to selected language
- **Claude API** — Uses Anthropic's API for quality translation
- **Translation cache** — Stores translations for quick access
- **Graceful fallback** — Shows original if translation fails

---

## 🚀 Quick start

### Minimal installation (without Playwright)
```bash
# Clone or download repository
git clone https://github.com/RastaFairy/FPKGi-for-PY.git
cd FPKGi-for-PY

# Install basic dependencies
pip install Pillow requests

# Run application
python fpkgi_manager.py
```

### Full installation (with Playwright for JS rendering)
```bash
# Install all dependencies
pip install Pillow requests playwright

# Download Chromium browser
python -m playwright install chromium

# Run application
python fpkgi_manager.py
```

---

## 📦 Requirements and installation

### System requirements
```
Python 3.8 or higher
Operating system: Windows, Linux, or macOS
Internet connection (to access OrbisPatches)
```

### Optional dependencies

#### 🖼️ Pillow (Recommended)
```bash
pip install Pillow>=9.0.0
```
**Usage:** Display game covers in the interface.
**Fallback:** Without Pillow, shows 🎮 emoji instead of image.

#### 🌐 Requests (Recommended)
```bash
pip install requests>=2.28.0
```
**Usage:** Faster HTTP requests and session cookie management.
**Fallback:** Without requests, uses standard `urllib` (slower).

#### 🎬 Playwright (Optional but recommended)
```bash
pip install playwright>=1.40.0
python -m playwright install chromium
```
**Usage:** Execute JavaScript and render dynamic OrbisPatches content.
**Fallback:** Without Playwright, tries basic requests (may fail on Cloudflare).

---

## 📁 Project structure

```
fpkgi_manager.py          ← Main application (single file)
├── Tkinter GUI
├── Language system
├── OrbisPatches scraper
├── Download manager
└── Persistent Playwright pool

lang/                     ← Translation files
├── es.json            (Spanish)
├── it.json            (Italian)
├── de.json            (German)
├── fr.json            (French)
├── ru.json            (Russian)
├── zh.json            (Chinese)
├── ko.json            (Korean)
└── ja.json            (Japanese)

download/               ← Downloads folder (auto-created)
└── {TITLE_ID}/       (Games organized by ID)

icons_cache/            ← Cover cache (auto-created)
└── *.png             (Downloaded images)

config.json            ← Configuration (optional)
```

---

## 🎯 User guide

### 1️⃣ Load a JSON catalog

#### Method 1: Menu
```
File → Open JSON...  (or Ctrl+O)
```

#### Method 2: Toolbar button
```
Click "  Open JSON"
```

**Supported formats:**

**FPKGi format:**
```json
{
  "DATA": {
    "https://example.com/game.pkg": {
      "title_id": "CUSA12345",
      "name": "My Game",
      "version": "1.05",
      "region": "EU",
      "size": 45000000000,
      "min_fw": "9.00",
      "cover_url": "https://..."
    }
  }
}
```

**PS4PKGInstaller format:**
```json
{
  "packages": [
    {
      "title_id": "CUSA12345",
      "name": "My Game",
      "version": "1.05",
      "region": "EU",
      "size": "45GB",
      "system_version": "9.00",
      "pkg_url": "https://example.com/game.pkg",
      "icon_url": "https://..."
    }
  ]
}
```

### 2️⃣ Explore the catalog

**Quick search:**
- Type in the 🔍 field to filter by:
  - Game name
  - TITLE_ID (e.g., CUSA12345)
  - Region (e.g., EU, US, JP)

**Sort columns:**
- Click any column header to sort

**View details:**
- Select a game in the table
- Right panel shows:
  - Game cover
  - Name, TITLE_ID, version
  - Required firmware, region, size
  - Availability status

### 3️⃣ Check download availability

#### Check one game
```
1. Select game in table
2. Click "  Check availability" or right-click menu
3. Wait for verification
4. Status changes to AVAILABLE ✅ or UNAVAILABLE ❌
```

#### Check all
```
Downloads → Check all (TODO: not in v5.11 yet)
```

### 4️⃣ Download a game

#### Method 1: Details panel
```
1. Select game
2. Click "  Download PKG"
3. Confirm download
```

#### Method 2: Right-click menu
```
1. Right-click game
2. Select "  Download PKG"
3. Confirm download
```

#### Method 3: Double-click
```
Double-click game to open download manager
```

**Download progress:**
- Download Manager shows:
  - Game name and version
  - Destination folder
  - Real-time progress bar
  - Bytes downloaded / total
  - Completion percentage
- When done, option to open folder

### 5️⃣ View available updates

#### Open updates window
```
1. Select game
2. Click "  View Updates"
3. Or double-click game
4. Or right-click → "  View updates"
```

**Information shown:**
- ✅ Versions available on OrbisPatches
- 📊 Required firmware (🟢 compatible / 🔴 incompatible)
- 📦 File size
- 📅 Creation date
- 📝 Patch notes (auto-translated)
- ⭐ Latest version indicator
- ← Your current version indicator

---

## 🔧 Configuration

### Change downloads folder

#### Method 1: Menu
```
Downloads → Change download path...
```

#### Method 2: Toolbar button
```
Click "  DL Path"
```

**Note:** Change only affects current session. On restart, reverts to `./download/`

### Reset to default folder
```
Downloads → Reset to default path
```

### Clear cache

**Icon cache:**
```
Cache → Clear icon cache
```
Deletes all downloaded covers. Will re-download when opening a JSON.

**Verification cache:**
```
Cache → Clear status cache
```
Deletes availability verification results. Games show "NOT CHECKED" again.

### Change language

```
Language → [Select desired language]
```

Interface updates immediately. Change not saved (restarts in English).

---

## 🌍 Supported languages

| Code | Language | File | Status |
|------|----------|------|--------|
| en | English | Built-in | ✅ |
| es | Spanish | lang/es.json | ✅ |
| it | Italian | lang/it.json | ✅ |
| de | German | lang/de.json | ✅ |
| fr | French | lang/fr.json | ✅ |
| ru | Russian | lang/ru.json | ✅ |
| zh | Chinese | lang/zh.json | ✅ |
| ko | Korean | lang/ko.json | ✅ |
| ja | Japanese | lang/ja.json | ✅ |

### Add a new language

1. Copy existing file:
   ```bash
   cp lang/es.json lang/pl.json
   ```

2. Edit `lang/pl.json` and translate all values:
   ```json
   {
     "lang_name": "Polski",
     "menu_file": "Plik",
     "menu_exit": "Wyjść",
     ...
   }
   ```

3. Add code to `AVAILABLE_LANGS` in `fpkgi_manager.py`:
   ```python
   AVAILABLE_LANGS = ["en", "es", "it", "de", "fr", "ru", "zh", "ko", "ja", "pl"]
   ```

4. Restart application — language appears in menu

**Note:** Missing keys automatically use English version.

---

## 🔎 OrbisPatches patch system

### How it works

1. **Input:** Select game and click "  View Updates"

2. **Navigation:** App accesses `https://orbispatches.com/{TITLE_ID}`

3. **Rendering:**
   - If Playwright available: Execute JavaScript with headless Chromium
   - If not: Try HTML download with requests
   - If Cloudflare blocks: Show warning

4. **Parsing:** Extract patches using regex patterns from actual HTML structure

5. **Extracted data:**
   - Patch version
   - Required firmware
   - File size
   - Creation date
   - HTML patch notes

6. **Presentation:**
   - Display patches sorted by version (newest first)
   - Mark newest version with ⭐
   - Mark your current version with ←
   - Show firmware compatibility (🟢/🔴)

### Verified HTML structure

```html
<div class="mb-4 patch-wrapper">
  <div class="patch-container [latest]">
    <a class="patch-link" data-contentver="01.04">
      <!-- Size -->
      <div class="col-auto text-end">7.2GB</div>
      <!-- Firmware -->
      <div class="col-auto text-end">8.50</div>
      <!-- Date -->
      <div class="col-auto text-end">2021-06-09</div>
    </a>
    <!-- Notes (if present) -->
    <a class="changeinfo-preview" 
       data-patchnotes-charcount="54">Patch notes</a>
  </div>
</div>
```

### Limitations and solutions

**Issue:** OrbisPatches uses Cloudflare
**Solution 1:** Install Playwright to bypass bot-protection
**Solution 2:** Open manually in your browser

**Issue:** Title has no patches on OrbisPatches
**Solution:** Window shows "No data"

**Issue:** HTML structure changed
**Solution:** Run `python diagnostico_orbis.py CUSA12345` to see current HTML

---

## ⬇️ Downloads and manager

### Download manager

**Features:**
- Parallel downloads (up to 8 simultaneous)
- Individual progress bar per file
- Pause/cancel
- Independent floating window
- Session download history

**Interface:**
```
[Download Manager]
├── My Game v1.05
│   ├── Destination: ./download/CUSA12345/
│   ├── [=================] 45.2GB / 50GB (90%)
│   └── Button: Open folder
├── Other Game v2.00
│   ├── [==] 5GB / 15GB (33%)
│   └── Button: Cancel
```

### Folder structure

```
./download/
├── CUSA00001/
│   ├── game_v1.05.pkg
│   └── game_v2.00.pkg
├── CUSA00002/
│   └── other_game.pkg
```

### Change downloads folder

**Per session:**
```
Downloads → Change download path...
```

**Permanent:**
Edit `DOWNLOADS_BASE` variable in code or create launcher script.

---

## 🌐 Cloudflare handling

### Automatic detection

App detects if Cloudflare blocks request using patterns:
- `"challenge-form"`
- `"just a moment"`
- `"cf-browser-verification"`
- `"ddos protection by"`

### Solutions

**Option 1: Install Playwright (Recommended)**
```bash
pip install playwright
python -m playwright install chromium
```

**Option 2: Open manually**
- App provides link to orbispatches.com
- Click "🌐 OrbisPatches" button
- Opens in your browser (Cloudflare lets you through)

**Option 3: Use proxy/VPN**
- Configure SOCKS5 proxy (requires code modification)

### Persistent Playwright pool

App maintains open Chromium browser during entire session:

**Advantages:**
- Consistent Cloudflare evasion
- Cookie reuse
- Fast query startup

**Disadvantages:**
- Uses ~100-200 MB RAM
- Requires ~500 MB disk for Chromium

**Auto-management:**
- Starts when app opens
- Closes when app closes
- Automatic fallback if issues

---

## 🔧 Advanced options

### Environment variables

```bash
# Change number of download workers
export FPKGI_WORKERS=16

# Change icon cache path
export FPKGI_ICONS_CACHE="./my_icons/"

# Enable debug mode
export FPKGI_DEBUG=1
```

### Translate patch notes

**Requirement:** `ANTHROPIC_API_KEY` environment variable

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python fpkgi_manager.py
```

App will automatically translate patch notes to selected language.

### Diagnose OrbisPatches issues

Diagnostic script (create `diagnostico_orbis.py`):

```python
#!/usr/bin/env python3
import sys
from fpkgi_manager import fetch_orbis_full

if len(sys.argv) < 2:
    print("Usage: python diagnostico_orbis.py CUSA12345")
    sys.exit(1)

tid = sys.argv[1]
result = fetch_orbis_full(tid, lambda m: print(m))

print("\n=== RESULT ===")
print(f"Total patches: {result['total']}")
print(f"Blocked by Cloudflare: {result['blocked']}")
print(f"Playwright used: {result['playwright_used']}")
if result.get('error'):
    print(f"Error: {result['error']}")
for p in result['patches']:
    print(f"  - v{p['version']}: FW {p['firmware']}, {p['size']}")
```

---

## 📝 Changelog

### v5.11 (Current)
- **Fixed Chromium headless** — HTML + JS match live OrbisPatches
- **Improved download manager** — Better cancellation handling
- **Refined UI** — Better visual feedback

### v5.4
- **Fixed scraper** — Updated HTML selectors for current OrbisPatches:
  - Version from `data-contentver` attribute
  - Size/FW/Date from `<div class="col-auto text-end">` in order
  - Notes from `<a class="changeinfo-preview">` when present
- **Refactored language system** — English base, others in `lang/*.json`
- **Instant update** — Detail panel updates on language change
- **Persistent cookies** — Shared `requests` session for Cloudflare

### v5.3
- **OrbisPatches as sole source** — PSN XML API removed
- **Cloudflare detection** — User warning
- **Improved interface** — Better visuals

### v5.2
- **Dual JSON parser** — Support DATA dict + packages list
- **Parallel download manager** — ThreadPoolExecutor

### v5.1
- **Icon prefetch** — With progress bar
- **Per-session download path** — Configurable without config files

### v5.0
- **Public release**

---

## ❓ Frequently asked questions

**Q: Where do games download to?**
A: To `./download/{TITLE_ID}/` by default. Change folder with Downloads → Change path.

**Q: Can I download multiple games at once?**
A: Yes, app downloads up to 8 files simultaneously.

**Q: What if download interrupts?**
A: Cancels. Try again without losing progress (if server supports resumption).

**Q: Do I need Playwright?**
A: No, optional. Without it, uses basic requests (less secure vs Cloudflare).

**Q: Can I translate to my language?**
A: Yes, copy `lang/es.json` to `lang/xx.json`, translate, and restart.

**Q: Does config save?**
A: Partially — only current language remembers (needs code for persistence).

---

## ⚠️ Disclaimer

> **This tool is only a metadata manager. It does not download, host, or distribute game files.**
>
> - Reads publicly accessible data (OrbisPatches)
> - Generates download URLs you verify
> - Connects directly to origin servers
>
> **Use only with content you have legal right to use.**
>
> Author is NOT responsible for:
> - Damage to your PS4 or system
> - Copyright infringement
> - Data loss
> - Any other issue

---

## 📞 Support and contributions

- **Issues:** GitHub Issues in repository
- **Contributions:** Pull Requests welcome
- **License:** MIT

---

## 🙏 Credits & Project History

### Origins
This project is part of a multi-generational evolution of game management tools for PlayStation devices:

- **Original concept (2010s):** Bucanero - Created the original PKGi homebrew for PSP, establishing the core philosophy of unified game catalog management.
- **PS4/PS5 port (2020s):** ItsJokerZz - Adapted the concept to modern PlayStation consoles, bringing FPKGi to PS4 and PS5.
- **Python multiplatform edition (2026):** RastaFairy - Ported the philosophy to Python, creating a cross-platform desktop application with modern features like Playwright integration, multilingual support, and OrbisPatches scraping.

### Philosophy
The core idea remains consistent across all versions: *a unified, intuitive interface to manage game packages PS4, making it easy for users to organize, verify, and download their game collections.*

### Acknowledgments
- Thanks to the PSP, PS4, and PS5 modding communities
- OrbisPatches.com for providing freely accessible patch information
- All contributors and users who report issues and suggest improvements

---

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/release/RastaFairy/FPKGi-for-PY.svg)](https://github.com/RastaFairy/FPKGi-for-PY/releases)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/downloads/)
[![GitHub Issues](https://img.shields.io/github/issues/RastaFairy/FPKGi-for-PY)](https://github.com/RastaFairy/FPKGi-for-PY/issues)
[![GitHub Stars](https://img.shields.io/github/stars/RastaFairy/FPKGi-for-PY)](https://github.com/RastaFairy/FPKGi-for-PY/stargazers)

**Made with ❤️ for the PS4 community**
