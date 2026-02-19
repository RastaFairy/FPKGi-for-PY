<div align="center">

# 🎮 FPKGi Manager

**PS4 FPKG game manager with OrbisPatches integration**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-5.4-orange)

</div>

---

## ✨ Features

- **Dual JSON format** support — reads both `DATA` dict and `packages` list formats
- **OrbisPatches integration** — scrapes patch metadata directly from orbispatches.com
  - Version, firmware requirement, file size, creation date
  - Patch notes with optional auto-translation
  - FW compatibility indicator (🟢/🔴 vs your FPKG's target FW)
- **PKG availability check** — HTTP HEAD request to verify download URL is alive
- **Parallel downloads** — non-blocking, with live progress bars per file
- **Per-session download path** — change where PKGs are saved without touching config
- **Multilingual UI** — English built-in; 8 extra languages loaded from `lang/*.json`
  - 🇬🇧 English · 🇪🇸 Español · 🇮🇹 Italiano · 🇩🇪 Deutsch · 🇫🇷 Français
  - 🇷🇺 Русский · 🇨🇳 中文 · 🇰🇷 한국어 · 🇯🇵 日本語
- **Icon cache** — parallel prefetch with progress bar, persistent across sessions

---

## 📦 Installation

### Requirements

```
Python 3.8+
Pillow    (cover images)
requests  (faster HTTP, Cloudflare session cookies)
```

```bash
pip install Pillow requests
```

> Both packages are **optional** — the app runs without them, but covers won't show and HTTP will use the slower urllib fallback.

### Run

```bash
python fpkgi_manager.py
```

No build step needed. Everything is a single `.py` file + a `lang/` folder.

---

## 📁 Project structure

```
fpkgi_manager.py   ← main application (single file)
lang/
  es.json          ← Spanish
  it.json          ← Italian
  de.json          ← German
  fr.json          ← French
  ru.json          ← Russian
  zh.json          ← Chinese
  ko.json          ← Korean
  ja.json          ← Japanese
descargas/         ← default download output (auto-created)
icons_cache/       ← game cover thumbnails (auto-created)
```

---

## 🌍 Adding a new language

1. Copy an existing file, e.g. `lang/es.json`, and rename it to `lang/xx.json`  
   where `xx` is the [ISO 639-1 code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).
2. Translate all values. **Do not change the keys.**
3. Set `"lang_name"` to the language's native name (e.g. `"Polski"`).
4. Add the code to `AVAILABLE_LANGS` in `fpkgi_manager.py`.
5. Restart the app — the new language appears in **Language** menu.

Keys missing from your file fall back to English automatically.

---

## 🔎 OrbisPatches scraper

The scraper fetches `https://orbispatches.com/{TITLE_ID}` and parses the HTML.

**Verified structure** (from live page, February 2026):

```html
<div class="patch-container [latest]">
  <a class="patch-link" data-contentver="01.04" ...>
    <div class="row"><div class="col-auto text-end">7.2GB</div></div>   <!-- size  -->
    <div class="row"><div class="col-auto text-end">8.50</div></div>    <!-- fw    -->
    <div class="row"><div class="col-auto text-end">2021-06-09</div></div> <!-- date -->
  </a>
  <!-- notes only present when data-patchnotes-charcount > 0 -->
  <a class="changeinfo-preview" data-patchnotes-charcount="54">...</a>
</div>
```

If Cloudflare bot-protection is active, the app shows a hint to open the page manually in a browser.

---

## ⬇️ Downloads

PKGs are saved to `./descargas/{TITLE_ID}/` by default.  
You can change the path for the current session via **Downloads → Change download path** or the toolbar button.

---

## ⚠️ Disclaimer

> This tool reads publicly accessible data. It does **not** host, mirror, or distribute any game files.  
> Clicking a download link connects directly to the original server.  
> Use at your own risk and only with content you are legally entitled to.

---

## 📝 Changelog

### v5.4
- **Scraper fixed** — corrected HTML selectors to match live OrbisPatches structure:
  - Version from `data-contentver` attribute (not `<h4>`)
  - Size/FW/Date from `<div class="col-auto text-end">` in order
  - Notes from `<a class="changeinfo-preview">` when `data-patchnotes-charcount > 0`
- **Language system refactored** — English built-in as base, all other languages in `lang/*.json`
- **Detail panel** now updates immediately on language change
- **Session cookie** management for Cloudflare (shared `requests.Session`)
- Gzip fallback in urllib path

### v5.3
- OrbisPatches as sole update source (PSN XML API removed)
- Cloudflare detection + user hint

### v5.2
- Dual JSON parser (DATA dict + packages list)
- Parallel download manager (ThreadPoolExecutor)

### v5.1
- Icon prefetch with progress bar
- Per-session configurable download path

### v5.0
- Initial public release
