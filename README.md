<div align="center">

# 🎮 FPKGi Manager

**PS4 FPKG Game Manager with OrbisPatches integration**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-5.11-orange)
![Status](https://img.shields.io/badge/Status-Actively%20Maintained-brightgreen)

</div>

---

## 📋 Table of Contents

- [✨ Key Features](#key-features)
- [🚀 Quick Start](#quick-start)
- [📦 Requirements & Installation](#requirements--installation)
- [📁 Project Structure](#project-structure)
- [🎯 Usage Guide](#usage-guide)
- [🔧 Configuration](#configuration)
- [🌍 Supported Languages](#supported-languages)
- [🔎 OrbisPatches Patch System](#orbispatches-patch-system)
- [⬇️ Downloads & Manager](#downloads--manager)
- [🌐 Cloudflare Handling](#cloudflare-handling)
- [📝 Changelog](#changelog)
- [⚠️ Disclaimer](#disclaimer)

---

## ✨ Key Features

### 🎛️ Game Management
- **Dual JSON support** — Compatible with two formats:
  - `FPKGi` format (`DATA` dictionary)
  - `PS4PKGInstaller` format (`packages` list)
- **Visual catalog** — Interactive table with covers, title, version & status
- **Real-time search** — Filter by name, TITLE_ID or region
- **Sorting** — Click any column header to sort

### 🔄 OrbisPatches Integration
- **Advanced scraper** — Pulls metadata directly from orbispatches.com:
  - Patch version
  - Required firmware
  - File size
  - Creation date
  - Patch notes
- **Chromium rendering** — Executes JavaScript to bypass Cloudflare
- **Automatic fallback** — Uses plain `requests` if Playwright is unavailable
- **Compatibility indicator** — Shows 🟢 (compatible) or 🔴 (incompatible) based on your FW

### ✅ Availability Checking
- **HTTP verification** — Confirms download URLs are live
- **Session cache** — Stores results to avoid repeated checks
- **Visual indicators** — Real-time status (AVAILABLE / UNAVAILABLE / NOT CHECKED)

### ⬇️ Download Manager
- **Parallel downloads** — Multiple files at once
- **Progress bars** — Real-time per-file progress
- **Custom path** — Change download folder per session
- **Floating manager** — Independent window to monitor downloads
- **Organized storage** — Files saved to `./download/{TITLE_ID}/`

### 🎨 Multilingual Interface
- **8+ languages** — Loaded dynamically from `lang/*.json`
  - 🇬🇧 English · 🇪🇸 Español · 🇮🇹 Italiano · 🇩🇪 Deutsch · 🇫🇷 Français
  - 🇷🇺 Русский · 🇨🇳 中文 · 🇰🇷 한국어 · 🇯🇵 日本語
- **Automatic fallback** — Missing keys fall back to English
- **Live language switching** — UI updates without restart

### 🖼️ Icon Caching
- **Parallel preloading** — Downloads all covers automatically
- **Progress bar** — Shows caching progress
- **Persistent cache** — Icons saved locally in `icons_cache/`
- **Manual cleanup** — Clear cache from menu

### 🌐 Patch Notes Translation
- **Automatic translation** — Converts patch notes to selected language
- **Claude API** — Uses Anthropic for high-quality translation
- **Translation cache** — Stores results for fast access
- **Graceful fallback** — Shows original text if translation fails

---

## 🚀 Quick Start

### Minimal install (no Playwright)
```bash
git clone https://github.com/RastaFairy/FPKGi-for-PY.git
cd FPKGi-for-PY

pip install Pillow requests
python fpkgi_manager.py
