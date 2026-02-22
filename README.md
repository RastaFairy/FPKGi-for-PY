# 🎮 FPKGi Manager — Python Edition

<p align="center">
  <img src="https://img.shields.io/badge/version-5.12--FTP-00D4FF" />
  <img src="https://img.shields.io/badge/python-3.9%2B-yellow" />
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
</p>

<p align="center">
  A cross-platform desktop manager for PS4 Fake-PKG game libraries.<br>
  Browse your catalogue, fetch patch notes from OrbisPatches, verify download links<br>
  and send PKGs directly to your PS4 via FTP — all in one dark-themed GUI.
</p>

> 🤖 Looking for the **Android app**? → [FPKGi-A-](https://github.com/RastaFairy/FPKGi-A-)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📂 **Dual JSON format** | Supports both FPKGi dict format and PS4PKGInstaller list format |
| 🔍 **OrbisPatches** | Full patch history with Playwright (Chromium headless, Cloudflare bypass) |
| 📡 **FTP transfer** | Send PKGs directly to your PS4/PS5 over LAN — no USB, no intermediate copy |
| ⬇️ **Parallel downloads** | Up to 8 simultaneous PKG downloads with real-time progress tracking |
| ✅ **Availability check** | HTTP HEAD verification per entry — green/red status per game |
| 🌍 **9 languages** | DE · ES · FR · IT · JA · KO · RU · ZH · EN (loaded from `lang/*.json`) |
| 🤖 **AI translation** | Patch notes translated in real-time via Anthropic Claude API (optional) |
| 🖼️ **Icon cache** | Parallel prefetch with persistent disk cache — covers survive restart |
| 🎨 **Animated background** | PS4-style animated gradient with floating △○×□ symbols |
| 💾 **Session persistence** | Window geometry, last JSON, sash position and language saved automatically |

---

## 📦 Requirements

| Package | Version | Purpose |
|---------|---------|---------|
| Python | ≥ 3.9 | Runtime |
| Pillow | ≥ 9.0 | Icon images / cover art |
| requests | ≥ 2.28 | HTTP downloads & availability check |
| playwright | ≥ 1.40 | OrbisPatches JavaScript rendering |

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### Optional — AI patch note translation

```bash
# Linux / macOS
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-...
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/RastaFairy/FPKGi-for-PY.git
cd FPKGi-for-PY

pip install -r requirements.txt
python -m playwright install chromium

python fpkgi_manager_with_ftp.py
```

On Windows you can also double-click **`START.bat`**.

---

## 📡 FTP Setup

1. Copy `ftp_config.json.example` → `ftp_config.json`
2. Edit to match your network:

```json
{
  "enabled": true,
  "host": "192.168.1.XXX",
  "port": 2121,
  "user": "anonymous",
  "password": "",
  "remote_path": "/data/pkg",
  "passive_mode": true,
  "timeout": 30
}
```

3. Or configure via **Settings → FTP Configuration** inside the app.

Compatible PS4 FTP servers:
- **GoldHEN FTP Server** *(recommended)*
- PS4FTP Homebrew
- Any FTP server on port 2121

> Full walkthrough (Spanish): [`GUIA_FTP_COMPLETA.txt`](GUIA_FTP_COMPLETA.txt)

---

## 📁 Project Structure

```
.
├── fpkgi_manager_with_ftp.py   # Main app — FTP edition (single file, 2800+ lines)
├── fpkgi_manager.py            # Standard edition (no FTP)
├── ftp_config.json             # Your FTP settings (git-ignored)
├── ftp_config.json.example     # Template — safe to commit
├── requirements.txt
├── START.bat                   # Windows one-click launcher
├── lang/                       # UI translation files
│   ├── de.json   es.json   fr.json   it.json
│   └── ja.json   ko.json   ru.json   zh.json
├── icons_cache/                # Persistent icon cache (auto-generated)
├── descargas/                  # Default PKG download folder
└── .github/
    ├── workflows/
    │   ├── ci.yml              # Lint + Windows EXE build (Python 3.9 / 3.11 / 3.13)
    │   └── release.yml         # Tag-triggered release + GitHub Release upload
    └── ISSUE_TEMPLATE/
        ├── bug_report.md
        └── feature_request.md
```

---

## 🏗️ Building a Windows EXE

```powershell
pip install pyinstaller
pyinstaller --onedir --windowed --name FPKGiManager `
  --add-data "lang;lang" `
  --add-data "ftp_config.json.example;." `
  fpkgi_manager_with_ftp.py
```

Output: `dist/FPKGiManager/`

---

## 🤝 Contributing

1. Fork and create a feature branch.
2. Run `flake8 fpkgi_manager_with_ftp.py --max-line-length=120` — fix all E9/F errors.
3. Open a Pull Request against `main`.

---

## 📜 Credits

| Role | Name |
|------|------|
| Original concept (PSP Homebrew) | [Bucanero](https://github.com/bucanero) |
| PS4 / PS5 port | ItsJokerZz | [ItsJokerZz](https://github.com/ItsJokerZz) |
| Python adaptation & evolution | RastaFairy |

---

## 📄 License

[MIT](LICENSE) © RastaFairy
