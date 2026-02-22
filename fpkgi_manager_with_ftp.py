#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════╗
║           FPKGi Manager - Python Edition v5.11                ║
║                                                                ║
║  Original concept by Bucanero (PSP Homebrew)                  ║
║  PS4/PS5 port by ItsJokerZz                                   ║
║  Python adaptation and evolution by RastaFairy                ║
║                                                                ║
║  Licensed under MIT License                                   ║
║  Repository: github.com/RastaFairy/FPKGi-for-PY               ║
╚════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━��━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 PS4 FPKG game manager with OrbisPatches integration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FEATURES:
  • Dual JSON format support (FPKGi dict & PS4PKGInstaller list)
  • OrbisPatches integration with Playwright JS rendering
  • Cloudflare bypass via Chromium headless
  • PKG availability verification (HTTP HEAD)
  • Parallel non-blocking downloads (up to 8 simultaneous)
  • Per-session configurable download paths
  • Multilingual UI (9 languages from lang/*.json)
  • Parallel icon prefetch with persistent cache
  • Real-time patch notes translation (Claude API)
  • Cross-platform: Windows, Linux, macOS

REQUIREMENTS:
  pip install Pillow requests playwright
  python -m playwright install chromium

OPTIONAL:
  export ANTHROPIC_API_KEY="sk-ant-..." (for patch note translation)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

__title__       = "FPKGi Manager"
__version__     = "5.11"
__author__      = "RastaFairy (Python Edition)"
__original__    = "Bucanero (PSP), ItsJokerZz (PS4/PS5)"
__license__     = "MIT"
__repository__  = "https://github.com/RastaFairy/FPKGi-for-PY"

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, os, re, hashlib, queue
import threading, webbrowser, urllib.request, urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from ftplib import FTP, error_perm
from io import BytesIO

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# ══════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════
APP_TITLE       = "FPKGi Manager"
APP_VERSION     = "5.12-FTP"
ICONS_CACHE_DIR = "icons_cache"
MAX_WORKERS     = 8

APP_DIR        = Path(os.path.abspath(__file__)).parent
DOWNLOADS_BASE = APP_DIR / "descargas"
LANG_DIR       = APP_DIR / "lang"

_session_download_base = None

# FTP Configuration
FTP_CONFIG = {
    "enabled": False,
    "host": "192.168.1.210",
    "port": 2121,
    "user": "anonymous",
    "password": "",
    "remote_path": "/data/pkg",
    "passive_mode": True,
    "timeout": 30
}

def load_ftp_config():
    """Cargar configuración FTP desde archivo"""
    config_file = APP_DIR / "ftp_config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                FTP_CONFIG.update(saved)
        except:
            pass

def save_ftp_config():
    """Guardar configuración FTP en archivo"""
    config_file = APP_DIR / "ftp_config.json"
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(FTP_CONFIG, f, indent=2)
    except:
        pass

# Cargar configuración al inicio
load_ftp_config()

# ══════════════════════════════════════════════════════
#  PERSISTENT SETTINGS
# ══════════════════════════════════════════════════════
_SETTINGS_FILE = APP_DIR / "settings.json"
_SETTINGS = {
    "language":      "en",
    "download_path": None,
    "last_json":     None,
    "geometry":      "1440x800",
    "paned_sash":    None,
}

def load_settings():
    global _session_download_base, _current_lang
    if _SETTINGS_FILE.exists():
        try:
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            _SETTINGS.update(saved)
        except Exception:
            pass
    # Apply language
    if _SETTINGS["language"] in AVAILABLE_LANGS:
        set_lang(_SETTINGS["language"])
    # Apply download path
    if _SETTINGS["download_path"]:
        p = Path(_SETTINGS["download_path"])
        if p.exists():
            _session_download_base = p

def save_settings(extra=None):
    if extra:
        _SETTINGS.update(extra)
    try:
        with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(_SETTINGS, f, indent=2)
    except Exception:
        pass


ORBIS_URL         = "https://orbispatches.com/{tid}"
ORBIS_API_PATCH   = "https://orbispatches.com/api/patch.php"

WEB_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# ══════════════════════════════════════════════════════
#  LANGUAGE SYSTEM
#  English is the built-in base; all other languages
#  are loaded on-demand from lang/{code}.json.
#  Missing keys fall back to English silently.
# ══════════════════════════════════════════════════════
_LANG_EN = {
    "lang_name": "English",
    "menu_file": "File", "menu_open_json": "Open JSON...",
    "menu_exit": "Exit", "menu_cache": "Cache",
    "menu_clear_icons": "Clear icon cache",
    "menu_clear_verify": "Clear status cache",
    "menu_downloads": "Downloads", "menu_manage_dl": "Manage downloads",
    "menu_change_path": "Change download path...",
    "menu_reset_path": "Reset to default path",
    "menu_open_dl_folder": "Open downloads folder",
    "menu_language": "Language",
    "btn_open_json": "  Open JSON", "btn_downloads": "  Downloads",
    "btn_dl_path": "  DL Path", "btn_open_dl_folder": "  Open downloads",
    "lbl_details": "DETAILS",
    "btn_download_pkg": "  Download PKG",
    "btn_view_updates": "  View Updates",
    "btn_check_avail": "  Check availability",
    "detail_name": "Name", "detail_title_id": "Title ID",
    "detail_version": "Version", "detail_fw": "FW FPKG",
    "detail_region": "Region", "detail_size": "Size",
    "detail_status": "Status",
    "status_available": "AVAILABLE",
    "status_unavailable": "UNAVAILABLE",
    "status_checking": "Checking...",
    "status_not_checked": "NOT CHECKED",
    "col_icon": "", "col_name": "Name", "col_title_id": "Title ID",
    "col_version": "Version", "col_status": "Status",
    "col_fw": "FW FPKG", "col_region": "Region", "col_size": "Size",
    "status_ready": "Ready  |  Path: {path}",
    "status_loaded": "Loaded: {name}",
    "status_checking_avail": "Checking {tid}...",
    "status_avail_result": "{tid} \u2192 {result}",
    "status_path_changed": "Download path: {path}",
    "status_path_reset": "Path reset: {path}",
    "status_icons_loading": "Icons: {n} / {total}",
    "status_icons_loaded": "Icons loaded.",
    "n_games": "{n} games",
    "msg_select_game": "Select a game first.",
    "msg_no_url": "This game has no download URL.",
    "msg_no_folder": "Downloads folder does not exist yet:\n{path}",
    "msg_path_updated_title": "Path updated",
    "msg_path_updated_body": "Downloads will be saved to:\n{path}",
    "dlg_select_json": "Select JSON",
    "dlg_select_folder": "Select download folder",
    "dlg_error_load": "Error loading",
    "confirm_dl_title": "Download PKG",
    "confirm_dl_body": "Download:\n{name}  ({size})\n\nDestination:\n{dest}",
    "cache_avail": "Cache: {tid} \u2192 {result}",
    "ctx_view_updates": "  View updates",
    "ctx_check_avail": "  Check availability",
    "ctx_download": "  Download PKG",
    "ctx_orbis": "  View on OrbisPatches",
    "upd_win_title": "Updates \u2014 {name}",
    "upd_fetching": "  Querying OrbisPatches...",
    "upd_no_data": "  No data on OrbisPatches for this title",
    "upd_blocked": "  OrbisPatches blocked the request (bot protection)",
    "upd_blocked_hint": "Click \"\U0001f310 OrbisPatches\" to open it in your browser.",
    "upd_found": "  {n} update(s) found on OrbisPatches",
    "upd_your_fpkg": "\u2190 your FPKG",
    "upd_notes_title": "Patch notes (v{ver})",
    "upd_no_notes": "No notes available.",
    "upd_notes_source": "Source: OrbisPatches",
    "upd_notes_translating": "Translating notes...",
    "upd_latest_badge": "\u2605 LATEST",
    "upd_close": "  Close", "upd_open_orbis": "  \U0001f310 OrbisPatches",
    "upd_warning": (
        "  Applying official updates to backported FPKGs is not advised.\n"
        "    It may corrupt the game or system."),
    "upd_fw_label": "Required FW",
    "upd_size_label": "Size",
    "upd_date_label": "Date",
    "dl_title": "  Download Manager",
    "dl_clear_done": "  Clear completed",
    "dl_no_active": "No active downloads.",
    "dl_count": "{active} active / {total} total",
    "dl_all_done": "All downloads completed.",
    "dl_cancel": "  Cancel", "dl_cancelled": "Cancelled",
    "dl_pause":   "  ⏸ Pause",
    "dl_resume":  "  ▶ Resume",
    "dl_restart": "  ↺ Restart",
    "dl_paused":  "  ⏸ Paused",

    "dl_cancelled_msg": "  Cancelled.",
    "dl_open_folder": "  Open folder",
    "dl_starting": "Starting...", "dl_close": "Close",
    "dl_update_label": "{name}  [Update v{ver}]",
    "dl_game_label": "{name}  v{ver}",
    # FTP Config Dialog
    "ftp_win_title": "🌐  FTP Configuration",
    "ftp_enable": "✓  Enable direct FTP download",
    "ftp_host_label": "🖥️  IP / Host:",
    "ftp_port_label": "🔌  Port:",
    "ftp_user_label": "👤  User:",
    "ftp_pass_label": "🔐  Password:",
    "ftp_dir_label": "📁  Remote directory:",
    "ftp_passive": "Passive mode (recommended)",
    "ftp_test_btn": "🔍  Test FTP connection",
    "ftp_save_btn": "💾  Save and close",
    "ftp_cancel_btn": "❌  Cancel",
    "ftp_testing": "🔄 Testing...",
    "ftp_conn_ok": "✅ Connection OK",
    "ftp_conn_warn": "⚠️ Connected (dir not found)",
    "ftp_err_port": "❌ Port must be a number between 1 and 65535.",
    "ftp_err_title": "Error",
    "ftp_save_ok_title": "Success",
    "ftp_save_ok_body": "✅ FTP configuration saved.\n\nStatus: {status}\nDestination: {dest}",
    "ftp_status_enabled": "✅ ENABLED",
    "ftp_status_disabled": "○ DISABLED",
    "ftp_err_save_body": "❌ Error saving configuration:\n\n{error}",
    # Settings / persistent prefs
    "menu_ftp_on":  "✓ FTP Enabled",
    "menu_ftp_off": "○ FTP Disabled",
    "menu_send_pkg": "  Send local PKG via FTP…",
    "btn_send_pkg_ftp": "  Send PKG via FTP",
    # FTP upload
    "ftp_send_title": "FTP Upload",
    "ftp_not_enabled": (
        "FTP is not enabled.\n"
        "Please configure it in Downloads → FTP Configuration."),
    "ftp_browse_pkg": "Select PKG file to send",
    "ftp_pkg_filetype": "PKG files",
    "ftp_all_files": "All files",
    "ftp_upload_label": "Upload: {name}",
    "ftp_uploading": "  Connecting and uploading…",
    "ftp_uploading_pct": "  {pct}%  —  {sent} / {total}",
    "ftp_upload_done": "  ✅ Upload complete",
    "ftp_upload_error": "  ❌ Error: {error}",

    "ftp_dialog_title": "⚙️  FTP Configuration - Direct transfer to PS4",
    "ftp_desc": ("Sends PKGs directly to your PS4 via FTP.\n"
                 "Make sure ftpd is running on your console.\n"
                 "Example: homebrew ftpd, PS4FTP, etc."),
    # Playwright / Updates status
    "pw_starting": "  ⏳ Starting Chromium headless…",
    "pw_waiting": "  ⏳ Waiting for Chromium to be ready…",
    "pw_ready": "  🟢 Chromium ready  |  {status}",
    "pw_unavail": "  ⚠ Chromium unavailable — using requests  |  {status}",
    "upd_err_unexpected": "  Unexpected error: {error}",
    "upd_no_data_engine": "  No data ({engine})",
    "upd_no_patches": "  This title has no patches on OrbisPatches.",
}

AVAILABLE_LANGS = ["en", "es", "it", "de", "fr", "ru", "zh", "ko", "ja"]
_lang_cache   = {"en": _LANG_EN}
_current_lang = "en"


def _load_lang(code):
    if code in _lang_cache:
        return _lang_cache[code]
    path = LANG_DIR / f"{code}.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = {**_LANG_EN, **data}
            _lang_cache[code] = merged
            return merged
        except Exception:
            pass
    _lang_cache[code] = _LANG_EN
    return _LANG_EN


def t(key, **kw):
    text = _load_lang(_current_lang).get(key, _LANG_EN.get(key, f"[{key}]"))
    return text.format(**kw) if kw else text


def get_lang_name(code):
    return _load_lang(code).get("lang_name", code.upper())


def set_lang(code):
    global _current_lang
    if code in AVAILABLE_LANGS:
        _current_lang = code


# ══════════════════════════════════════════════════════
#  HTTP — shared session keeps cookies (Cloudflare)
# ══════════════════════════════════════════════════════
_http_session = None


def _get_session():
    global _http_session
    if _http_session is None and REQUESTS_AVAILABLE:
        _http_session = requests.Session()
        _http_session.headers.update(WEB_HEADERS)
    return _http_session


def _http_get(url, headers=None, timeout=15):
    try:
        if REQUESTS_AVAILABLE:
            s = _get_session()
            r = (s.get(url, headers=headers, timeout=timeout)
                 if headers else s.get(url, timeout=timeout))
            return r.content if r.status_code == 200 else None
        else:
            import gzip as _gz
            req = urllib.request.Request(url, headers=headers or WEB_HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                if r.info().get("Content-Encoding") == "gzip":
                    raw = _gz.decompress(raw)
                return raw
    except Exception:
        return None


def _http_get_text(url, headers=None, timeout=15):
    raw = _http_get(url, headers, timeout)
    return raw.decode("utf-8", errors="ignore") if raw else None


def _http_head(url, timeout=8):
    try:
        if REQUESTS_AVAILABLE:
            r = _get_session().head(url, timeout=timeout, allow_redirects=True)
            return r.status_code in (200, 206, 301, 302, 303, 307, 308)
        else:
            req = urllib.request.Request(url, headers=WEB_HEADERS, method="HEAD")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status in (200, 206)
    except Exception:
        return False


# ══════════════════════════════════════════════════════
#  UTILITIES
# ══════════════════════════════════════════════════════
def _bytes_to_human(val):
    try:
        b = int(float(str(val).replace(",", "")))
        if b >= 1_073_741_824: return f"{b/1_073_741_824:.2f} GB"
        if b >= 1_048_576:     return f"{b/1_048_576:.0f} MB"
        return f"{b} B"
    except Exception:
        return str(val)


def _parse_version(ver):
    if not ver: return "?"
    s = str(ver).strip().lstrip("v")
    p = s.split(".")
    try:
        return f"{int(p[0]):02d}.{int(p[1]) if len(p)>1 else 0:02d}"
    except Exception:
        return s


def _norm_ver(v):
    parts = re.split(r"[.\-]", str(v).strip().lstrip("v"))
    try: return tuple(int(x) for x in parts if x.isdigit())
    except Exception: return (0,)


def _strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


# ══════════════════════════════════════════════════════
#  JSON LOADER — two catalog formats
# ══════════════════════════════════════════════════════
def load_json(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        raw = json.load(f)
    games = []

    if isinstance(raw, dict) and "DATA" in raw:
        for pkg_url, m in raw["DATA"].items():
            sz = m.get("size", 0)
            games.append({
                "title_id":  m.get("title_id", "?"),
                "name":      m.get("name", "?"),
                "version":   _parse_version(m.get("version", "?")),
                "region":    m.get("region", "?"),
                "size":      sz if isinstance(sz, str) else _bytes_to_human(sz),
                "min_fw":    str(m.get("min_fw", m.get("required_fw", m.get("fw", "?")))),
                "cover_url": m.get("cover_url", m.get("icon_url", "")),
                "pkg_url":   pkg_url.strip().strip("_"),
            })
        return games

    items = raw.get("packages", raw) if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise ValueError("Unrecognised JSON format.")
    for m in items:
        sz = m.get("size", 0)
        size_s = (sz if isinstance(sz, str) and
                  not str(sz).replace(".", "").replace(" ","")
                    .replace("GB","").replace("MB","").isdigit()
                  else _bytes_to_human(sz))
        fw = str(m.get("system_version",
             m.get("min_fw", m.get("required_fw", m.get("fw", "?")))))
        games.append({
            "title_id":  m.get("title_id", "?"),
            "name":      m.get("name", "?"),
            "version":   _parse_version(m.get("version", "?")),
            "region":    m.get("region", "?"),
            "size":      size_s,
            "min_fw":    fw,
            "cover_url": m.get("icon_url", m.get("cover_url", "")),
            "pkg_url":   m.get("pkg_url", "").strip().strip("_"),
        })
    return games


# ══════════════════════════════════════════════════════
#  AVAILABILITY
# ══════════════════════════════════════════════════════
def check_url_available(url):
    return bool(url and url not in ("?","")) and _http_head(url)


# ══════════════════════════════════════════════════════
#  NOTE TRANSLATION  (via Claude API)
# ══════════════════════════════════════════════════════
_translation_cache = {}
_LANG_NAMES = {
    "es":"Spanish","it":"Italian","de":"German","fr":"French",
    "ru":"Russian","zh":"Chinese","ko":"Korean","ja":"Japanese",
}

def translate_patch_notes(text_en, target_lang):
    if not text_en or target_lang == "en": return text_en
    ck = (text_en[:200], target_lang)
    if ck in _translation_cache: return _translation_cache[ck]
    lang_name = _LANG_NAMES.get(target_lang, "Spanish")
    try:
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514", "max_tokens": 1000,
            "messages": [{"role": "user", "content": (
                f"Translate the following PS4 game patch notes to {lang_name}. "
                "Keep formatting and line breaks. Return ONLY the translated text:\n\n"
                + text_en)}],
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=payload,
            headers={"Content-Type":"application/json",
                     "anthropic-version":"2023-06-01"}, method="POST")
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        result = "".join(b.get("text","") for b in data.get("content",[])
                        if b.get("type")=="text").strip()
        if result:
            _translation_cache[ck] = result
            return result
    except Exception:
        pass
    return text_en


# ══════════════════════════════════════════════════════
#  ORBISPATCHES SCRAPER  —  v5.8  (estructura verificada)
#
#  Estructura HTML real post-JS (verificada con dump vivo):
#
#  <div class="mb-4 patch-wrapper">
#    <div class="patch-container [latest]">
#      <a href="#" class="patch-link d-block p-4"
#         data-titleid="CUSA09267"
#         data-contentver="01.04"
#         data-key="fe321acc…"
#         data-title="Patch 01.04">
#        <h4>Patch 01.04</h4>
#        <div class="row mt-4">
#          <div class="col-auto flex-fill text-start fw-normal">PKG Size</div>
#          <div class="col-auto text-end">7.2GB</div>         ← SIZE
#        </div>
#        <div class="row mt-1">
#          <div class="col-auto flex-fill ...">Required Firmware</div>
#          <div class="col-auto text-end">8.50</div>          ← FW
#        </div>
#        <div class="row mt-1">
#          <div class="col-auto flex-fill ...">Creation Date</div>
#          <div class="col-auto text-end">2021-06-09</div>    ← DATE
#        </div>
#      </a>
#      <div class="text-end border-top">
#        <nav class="nav patch-options …">
#          <!-- Share -->
#          <!-- Details -->
#          <a class="nav-link … notes-icon [disabled]"
#             data-patchnotes-charcount="54"
#             data-key="ba5a61…">NOTAS DE TEXTO EMBEBIDAS AQUÍ</a>
#        </nav>
#      </div>
#    </div>
#  </div>
#
#  Las notas vienen incrustadas en el HTML ya renderizado, dentro
#  del <a class="notes-icon">, cuando charcount > 0.
# ══════════════════════════════════════════════════════

# ── Configuración Playwright ───────────────────────────────────────
_PW_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_PW_EXTRA_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-setuid-sandbox",
]
_PW_STEALTH_JS = (
    "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
    "Object.defineProperty(navigator,'languages',{get:()=>['es-ES','es','en']});"
    "Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3,4,5]});"
    "window.chrome={runtime:{}};"
)


# ── Playwright: pool persistente ─────────────────────────────────
# ── Playwright: pool persistente ─────────────────────────────────
class _PlaywrightPool:
    """Browser Chromium headless persistente para toda la sesión.

    Playwright es asyncio internamente. Lo ejecutamos en un loop asyncio
    dedicado dentro de un hilo daemon, y exponemos una API síncrona
    (fetch) que los hilos worker pueden llamar sin preocuparse de asyncio.

    Ciclo de vida (gestionado automáticamente por la app):
        _pw_pool.start()   →  al arrancar FPKGiManager
        _pw_pool.fetch(url) →  desde cualquier hilo
        _pw_pool.stop()    →  al cerrar la app
    """

    def __init__(self):
        self._ready    = threading.Event()  # set cuando el browser está listo
        self._ok       = False              # True si el browser arrancó bien
        self._lock     = threading.Lock()   # serializa las consultas
        self._loop     = None              # asyncio loop del hilo daemon
        self._browser  = None
        self._ctx      = None
        self._page     = None
        self._thread   = None

    # ── Arranque ──────────────────────────────────────────────────
    def start(self):
        """Inicia el browser en un hilo daemon. No bloquea el hilo llamante."""
        if not PLAYWRIGHT_AVAILABLE:
            self._ready.set()
            return
        self._thread = threading.Thread(
            target=self._thread_main, daemon=True, name="PlaywrightPool")
        self._thread.start()

    def _thread_main(self):
        """Hilo daemon: crea un loop asyncio propio y lo mantiene vivo."""
        import asyncio
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._async_main())
        finally:
            self._loop.close()

    async def _async_main(self):
        """Cuerpo async: inicializa Playwright y espera en un Future."""
        from playwright.async_api import async_playwright, TimeoutError as _APWTimeout
        self._APWTimeout = _APWTimeout
        try:
            self._apw = await async_playwright().start()
            self._browser = await self._apw.chromium.launch(
                headless=True,
                args=_PW_EXTRA_ARGS,
            )
            self._ctx = await self._browser.new_context(
                user_agent=_PW_USER_AGENT,
                viewport={"width": 1280, "height": 900},
                locale="es-ES",
                timezone_id="Europe/Madrid",
            )
            self._page = await self._ctx.new_page()
            await self._page.add_init_script(_PW_STEALTH_JS)
            self._ok = True
        except Exception:
            self._ok = False
        finally:
            self._ready.set()

        if self._ok:
            # Mantener el loop vivo con un Future que se cancela en stop()
            self._stop_future = self._loop.create_future()
            try:
                await self._stop_future
            except Exception:
                pass

        # Limpieza
        try:
            await self._browser.close()
        except Exception:
            pass
        try:
            await self._apw.stop()
        except Exception:
            pass

    # ── Parada ────────────────────────────────────────────────────
    def stop(self):
        """Señaliza al loop async que debe terminar."""
        if self._loop and self._loop.is_running():
            try:
                fut = getattr(self, '_stop_future', None)
                if fut and not fut.done():
                    self._loop.call_soon_threadsafe(fut.set_result, None)
            except Exception:
                pass

    # ── Consulta (API síncrona para hilos worker) ─────────────────
    def fetch(self, url, timeout_ms=40000):
        """Navega a *url* y devuelve el HTML renderizado.

        Bloquea el hilo llamante hasta tener resultado.
        Las llamadas concurrentes se serializan con _lock.
        """
        import asyncio, time as _time

        if not self._ready.wait(timeout=60):
            return ""
        if not self._ok or not self._loop or not self._loop.is_running():
            return ""

        with self._lock:
            future = asyncio.run_coroutine_threadsafe(
                self._async_fetch(url, timeout_ms), self._loop)
            try:
                return future.result(timeout=timeout_ms / 1000 + 10)
            except Exception:
                return ""

    async def _async_fetch(self, url, timeout_ms):
        """Navega y captura el HTML dentro del loop asyncio del pool."""
        import asyncio
        try:
            try:
                await self._page.goto(url, wait_until="domcontentloaded",
                                      timeout=timeout_ms)
            except self._APWTimeout:
                pass
            try:
                await self._page.wait_for_load_state("networkidle",
                                                     timeout=timeout_ms)
            except self._APWTimeout:
                pass
            await asyncio.sleep(2)
            return await self._page.content() or ""
        except Exception:
            # Página crasheó → reabrir
            try:
                self._page = await self._ctx.new_page()
                await self._page.add_init_script(_PW_STEALTH_JS)
            except Exception:
                self._ok = False
            return ""


# Instancia global compartida por toda la app
_pw_pool = _PlaywrightPool()


def _pw_fetch(url, timeout_ms=40000):
    """Obtiene el HTML renderizado de *url* usando el pool persistente.
    Si el pool no está disponible, usa un browser desechable como fallback.
    """
    if not PLAYWRIGHT_AVAILABLE:
        return ""

    # Pool disponible (arrancado o arrancando) → usarlo
    if not _pw_pool._ready.is_set() or _pw_pool._ok:
        return _pw_pool.fetch(url, timeout_ms=timeout_ms)

    # Pool falló → fallback con browser desechable (sync_playwright en
    # el hilo actual, que SÍ es válido para sync_playwright)
    import time as _time
    html = ""
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=_PW_EXTRA_ARGS)
            ctx = browser.new_context(
                user_agent=_PW_USER_AGENT,
                viewport={"width": 1280, "height": 900},
                locale="es-ES", timezone_id="Europe/Madrid")
            page = ctx.new_page()
            page.add_init_script(_PW_STEALTH_JS)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            except PWTimeout:
                pass
            try:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            except PWTimeout:
                pass
            _time.sleep(2)
            html = page.content() or ""
            browser.close()
    except Exception:
        pass
    return html


# ── Cloudflare ────────────────────────────────────────────────────
_CF_MARKERS = [
    "challenge-form", "just a moment", "cf-browser-verification",
    'id="cf-wrapper"', "enable javascript and cookies",
    "ddos protection by", "_cf_chl_opt",
]

def _is_cf_blocked(html):
    return any(m in html[:10000].lower() for m in _CF_MARKERS)


# ── Parser principal ───────────────────────────────────────────────
def _parse_orbis_html(html):
    """Parsea el HTML renderizado de OrbisPatches.

    Usa la estructura real verificada con dump vivo:
      - Contenedor: div.patch-wrapper
      - Versión:    data-contentver en a.patch-link
      - Datos:      divs .col-auto.text-end (size, fw, date en orden)
      - Notas:      texto embebido en a.notes-icon (charcount > 0)

    Devuelve (game_name: str, patches: list[dict], blocked: bool).
    """
    if not html:
        return "", [], False
    if _is_cf_blocked(html):
        return "", [], True

    # Nombre del juego
    game_name = ""
    mt = re.search(r"<title>([^<]+)</title>", html, re.I)
    if mt:
        raw = re.sub(r"^CUSA\d+[:\s]*", "", mt.group(1))
        raw = re.sub(r"\s*\|\s*ORBISPatches.*$", "", raw, flags=re.I)
        game_name = raw.strip()

    # Separar en bloques por patch-wrapper (estructura real verificada)
    blocks = re.split(
        r"(?=<div[^>]*class=[\"'][^\"']*\bpatch-wrapper\b)", html)

    patches, seen = [], set()

    for block in blocks:
        if "patch-wrapper" not in block:
            continue

        # ── Versión (data-contentver en patch-link) ────────────────
        ver_m = re.search(
            r'class=["\'][^"\']*\bpatch-link\b[^"\']*["\'][^>]+'
            r'data-contentver=["\']([^"\']+)["\']', block)
        if not ver_m:
            # Fallback: cualquier data-contentver en el bloque
            ver_m = re.search(r'data-contentver=["\']([^"\']+)["\']', block)
        if not ver_m:
            continue

        ver = _parse_version(ver_m.group(1))
        if not ver or ver in seen:
            continue
        seen.add(ver)

        # ── ¿Es el más reciente? ─────────────────────────────────
        is_latest = "patch-container latest" in block

        # ── data-key del patch-link (descarga directa) ────────────
        key_m = re.search(
            r'class=["\'][^"\']*\bpatch-link\b[^"\']*["\'][^>]+'
            r'data-key=["\']([a-f0-9]{10,})["\']', block)
        patch_key = key_m.group(1) if key_m else ""

        # ── Size / FW / Date (divs col-auto text-end, en ese orden) ─
        vals = re.findall(
            r'<div[^>]+class=["\'][^"\']*\bcol-auto\b[^"\']*\btext-end\b'
            r'[^"\']*["\'][^>]*>\s*([^<\n]{1,40}?)\s*</div>',
            block)
        size          = vals[0].strip() if len(vals) > 0 else "?"
        firmware      = vals[1].strip() if len(vals) > 1 else "?"
        creation_date = vals[2].strip() if len(vals) > 2 else ""

        # ── Notas de parche ────────────────────────────────────────
        # Estructura real: <div class="changelog-wrapper">
        #   <table class="changelog-table"><tbody><tr><td>
        #     <a class="changeinfo-preview …"
        #        data-patchnotes-charcount="54">TEXTO DE NOTAS</a>
        #   </td></tr></tbody></table>
        # </div>
        notes = ""
        nm = re.search(
            r'class=["\'][^"\']*\bchangeinfo-preview\b[^"\']*["\']'
            r'[^>]+data-patchnotes-charcount=["\'](\d+)["\'][^>]*>'
            r'(.*?)</a>',
            block, re.S | re.I)
        if not nm:
            # Orden de atributos invertido
            nm = re.search(
                r'data-patchnotes-charcount=["\'](\d+)["\']'
                r'[^>]+class=["\'][^"\']*\bchangeinfo-preview\b[^"\']*["\'][^>]*>'
                r'(.*?)</a>',
                block, re.S | re.I)
        if nm and int(nm.group(1)) > 0:
            raw_notes = nm.group(2)
            # Eliminar spans internos (ej: el <span> del botón de notas)
            raw_notes = re.sub(r'<span[^>]*>.*?</span>', '', raw_notes, flags=re.S | re.I)
            notes = re.sub(r"\n{3,}", "\n\n",
                           _strip_html(raw_notes).strip())

        patches.append({
            "version":       ver,
            "firmware":      firmware,
            "size":          size,
            "creation_date": creation_date,
            "notes":         notes,
            "is_latest":     is_latest,
            "patch_key":     patch_key,
        })

    patches.sort(key=lambda p: _norm_ver(p["version"]), reverse=True)
    if patches:
        patches[0]["is_latest"] = True

    return game_name, patches, False


# ── Fallback sin Playwright ────────────────────────────────────────
def _fetch_orbis_requests(tid, page_url):
    """Intenta obtener HTML con requests (sin JS). Solo funciona si
    Cloudflare no bloquea la petición.
    """
    html = _http_get_text(page_url, timeout=20)
    if not html or _is_cf_blocked(html):
        return "", []
    game_name, patches, _ = _parse_orbis_html(html)
    return game_name, patches


# ── Función pública ────────────────────────────────────────────────
def fetch_orbis_full(title_id, _progress_cb=None):
    """Obtiene todos los parches de *title_id* desde OrbisPatches.

    Devuelve::

        {
          "patches":        list[dict],
          "total":          int,
          "game_name":      str,
          "blocked":        bool,
          "playwright_used":bool,
          "error":          str,
        }
    """
    tid      = title_id.strip().upper()
    page_url = ORBIS_URL.format(tid=tid)

    def _cb(msg):
        if _progress_cb:
            try:
                _progress_cb(msg)
            except Exception:
                pass

    # ── Nivel 1: Playwright ────────────────────────────────────────
    if PLAYWRIGHT_AVAILABLE:
        _cb(t("pw_starting"))
        html = _pw_fetch(page_url, timeout_ms=40000)
        _cb(t("upd_fetching"))

        if html and not _is_cf_blocked(html):
            game_name, patches, blocked = _parse_orbis_html(html)
            if blocked:
                return {"patches": [], "total": 0, "game_name": "",
                        "blocked": True, "playwright_used": True, "error": ""}
            if patches:
                return {"patches": patches, "total": len(patches),
                        "game_name": game_name, "blocked": False,
                        "playwright_used": True, "error": ""}
            if len(html) > 5000:
                err = t("upd_no_data")
                return {"patches": [], "total": 0, "game_name": game_name,
                        "blocked": False, "playwright_used": True, "error": err}

    # ── Nivel 2: requests ──────────────────────────────────────────
    _cb(t("upd_fetching"))
    game_name, patches = _fetch_orbis_requests(tid, page_url)
    err = "" if patches else t("upd_no_data")
    return {
        "patches":         patches,
        "total":           len(patches),
        "game_name":       game_name,
        "blocked":         False,
        "playwright_used": False,
        "error":           err,
    }


# ══════════════════════════════════════════════════════
#  ICON CACHE
# ══════════════════════════════════════════════════════
def _url_to_filename(url):
    parsed = urllib.parse.urlparse(url)
    base   = os.path.basename(parsed.path).split("?")[0]
    if base and "." in base:
        return re.sub(r'[<>:"/\\|?*]', "_", base)
    m = re.search(r"(CUSA\d+)", url, re.I)
    return f"{m.group(1).upper()}.png" if m else hashlib.md5(url.encode()).hexdigest()[:12]+".png"


def download_icon(url, cache_dir=ICONS_CACHE_DIR):
    if not url: return None
    os.makedirs(cache_dir, exist_ok=True)
    local = os.path.join(cache_dir, _url_to_filename(url))
    if os.path.exists(local): return local
    try:
        if REQUESTS_AVAILABLE:
            r = requests.get(url, headers=WEB_HEADERS, timeout=10)
            if r.status_code == 200:
                open(local,"wb").write(r.content)
                return local
        else:
            req = urllib.request.Request(url, headers=WEB_HEADERS)
            with urllib.request.urlopen(req, timeout=10) as r:
                open(local,"wb").write(r.read())
            return local
    except Exception:
        return None


# ══════════════════════════════════════════════════════
#  DOWNLOADS
# ══════════════════════════════════════════════════════
def get_active_base():
    return _session_download_base if _session_download_base else DOWNLOADS_BASE

def get_download_dir(title_id):
    d = get_active_base() / title_id
    d.mkdir(parents=True, exist_ok=True)
    return d

def download_pkg(pkg_url, title_id, name,
                 progress_cb=None, done_cb=None,
                 ctrl=None):
    """
    Download a PKG file.
    ctrl  – shared control dict:
      {
        "pause":     threading.Event   (set=running, clear=paused),
        "cancelled": bool,
        "done":      bool,
        "bytes_done": int,             # written so far
        "total":     int,              # content-length
        "dest":      str | None,       # local path (local mode only)
      }
    If ctrl is None a default one is created.
    """
    if ctrl is None:
        ctrl = {"pause": threading.Event(), "cancelled": False,
                "done": False, "bytes_done": 0, "total": 0, "dest": None}
    ctrl["pause"].set()   # start unpaused

    raw_name = os.path.basename(urllib.parse.urlparse(pkg_url).path).split("?")[0]
    try: raw_name = urllib.parse.unquote(raw_name)
    except Exception: pass
    if not raw_name or not raw_name.lower().endswith(".pkg"):
        raw_name = f"{title_id}_{re.sub(r'[^a-zA-Z0-9._-]','_',name)}.pkg"

    if FTP_CONFIG["enabled"]:
        _download_to_ftp(pkg_url, title_id, raw_name,
                         progress_cb, done_cb, ctrl)
        return ctrl

    # ── Local download ────────────────────────────────────────────
    dest_dir  = get_download_dir(title_id)
    dest_path = dest_dir / raw_name
    ctrl["dest"] = str(dest_path)

    def _worker():
        try:
            # Resume from partial file if it exists
            resume_from = dest_path.stat().st_size if dest_path.exists() else 0
            ctrl["bytes_done"] = resume_from

            headers = dict(WEB_HEADERS)
            if resume_from > 0:
                headers["Range"] = f"bytes={resume_from}-"

            if REQUESTS_AVAILABLE:
                r = requests.get(pkg_url, headers=headers,
                                 stream=True, timeout=30)
                if r.status_code == 416:          # Range not satisfiable → file complete
                    if done_cb: done_cb(True, str(dest_path))
                    ctrl["done"] = True; return
                r.raise_for_status()
                content_range = r.headers.get("Content-Range", "")
                if content_range:
                    total = int(content_range.split("/")[-1])
                else:
                    total = int(r.headers.get("content-length", 0)) + resume_from
                ctrl["total"] = total

                mode = "ab" if resume_from > 0 else "wb"
                with open(dest_path, mode) as f:
                    for chunk in r.iter_content(1 << 20):
                        if ctrl["cancelled"]:
                            return
                        ctrl["pause"].wait()           # ← blocks while paused
                        if ctrl["cancelled"]:
                            return
                        if chunk:
                            f.write(chunk)
                            ctrl["bytes_done"] += len(chunk)
                            if progress_cb:
                                progress_cb(ctrl["bytes_done"], total)
            else:
                req = urllib.request.Request(pkg_url, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as r:
                    cl  = r.headers.get("Content-Length") or r.headers.get("content-length")
                    total = (int(cl) + resume_from) if cl else 0
                    ctrl["total"] = total
                    mode = "ab" if resume_from > 0 else "wb"
                    with open(dest_path, mode) as f:
                        while True:
                            if ctrl["cancelled"]:
                                return
                            ctrl["pause"].wait()
                            if ctrl["cancelled"]:
                                return
                            chunk = r.read(1 << 20)
                            if not chunk:
                                break
                            f.write(chunk)
                            ctrl["bytes_done"] += len(chunk)
                            if progress_cb:
                                progress_cb(ctrl["bytes_done"], total)

            ctrl["done"] = True
            if done_cb: done_cb(True, str(dest_path))
        except Exception as e:
            if not ctrl["cancelled"]:
                if done_cb: done_cb(False, str(e))

    threading.Thread(target=_worker, daemon=True).start()
    return ctrl


def _download_to_ftp(pkg_url, title_id, filename,
                     progress_cb=None, done_cb=None, ctrl=None):
    """Stream PKG from HTTP directly to FTP (no local storage)."""
    if ctrl is None:
        ctrl = {"pause": threading.Event(), "cancelled": False,
                "done": False, "bytes_done": 0, "total": 0, "dest": None}
    ctrl["pause"].set()

    def _worker():
        ftp = None
        response = None
        try:
            resume_from = ctrl.get("bytes_done", 0)
            headers = dict(WEB_HEADERS)
            if resume_from > 0:
                headers["Range"] = f"bytes={resume_from}-"

            ftp = FTP()
            ftp.connect(FTP_CONFIG["host"], FTP_CONFIG["port"],
                        timeout=FTP_CONFIG["timeout"])
            ftp.login(FTP_CONFIG["user"], FTP_CONFIG["password"])
            if FTP_CONFIG["passive_mode"]:
                ftp.set_pasv(True)

            remote_path = FTP_CONFIG["remote_path"]
            _ensure_ftp_directory(ftp, remote_path)
            remote_file = remote_path.rstrip("/") + "/" + filename

            if REQUESTS_AVAILABLE:
                response = requests.get(pkg_url, headers=headers,
                                        stream=True, timeout=30)
                if response.status_code == 416:
                    ctrl["done"] = True
                    if done_cb:
                        full = f"{FTP_CONFIG['host']}:{FTP_CONFIG['port']}{remote_path}/{filename}"
                        done_cb(True, f"FTP: {full}")
                    return
                response.raise_for_status()
                content_range = response.headers.get("Content-Range", "")
                total = (int(content_range.split("/")[-1]) if content_range
                         else int(response.headers.get("content-length", 0)) + resume_from)
                ctrl["total"] = total

                # FTP REST for resume
                stor_cmd = f"STOR {remote_file}"
                if resume_from > 0:
                    try:
                        ftp.sendcmd(f"REST {resume_from}")
                        stor_cmd = f"APPE {remote_file}"
                    except Exception:
                        pass

                class _PausableStream:
                    def __init__(self, it):
                        self._it  = it
                        self._buf = b""
                    def read(self, size=65536):
                        while len(self._buf) < size:
                            if ctrl["cancelled"]:
                                return b""
                            ctrl["pause"].wait()
                            if ctrl["cancelled"]:
                                return b""
                            try:
                                self._buf += next(self._it)
                            except StopIteration:
                                break
                        out = self._buf[:size]
                        self._buf = self._buf[size:]
                        ctrl["bytes_done"] += len(out)
                        if progress_cb:
                            progress_cb(ctrl["bytes_done"], total)
                        return out

                stream = _PausableStream(response.iter_content(chunk_size=65536))
                ftp.storbinary(stor_cmd, stream, blocksize=65536)
            else:
                req = urllib.request.Request(pkg_url, headers=headers)
                response = urllib.request.urlopen(req, timeout=30)
                cl = response.headers.get("Content-Length") or response.headers.get("content-length")
                total = (int(cl) + resume_from) if cl else 0
                ctrl["total"] = total
                data = BytesIO()
                while True:
                    if ctrl["cancelled"]: return
                    ctrl["pause"].wait()
                    if ctrl["cancelled"]: return
                    chunk = response.read(1 << 20)
                    if not chunk: break
                    data.write(chunk)
                    ctrl["bytes_done"] += len(chunk)
                    if progress_cb:
                        progress_cb(ctrl["bytes_done"], total)
                data.seek(0)
                ftp.storbinary(f"STOR {remote_file}", data, blocksize=65536)

            ctrl["done"] = True
            full_path = f"{FTP_CONFIG['host']}:{FTP_CONFIG['port']}{remote_path}/{filename}"
            if done_cb: done_cb(True, f"FTP: {full_path}")

        except Exception as e:
            if not ctrl["cancelled"]:
                if done_cb: done_cb(False, f"Error FTP: {str(e)}")
        finally:
            if response and REQUESTS_AVAILABLE:
                try: response.close()
                except Exception: pass
            if ftp:
                try: ftp.quit()
                except Exception:
                    try: ftp.close()
                    except Exception: pass

    threading.Thread(target=_worker, daemon=True).start()
    return ctrl


def _ensure_ftp_directory(ftp, path):
    """Asegurar que el directorio FTP existe, crearlo si no"""
    try:
        ftp.cwd(path)
        return
    except error_perm:
        pass
    
    # Crear directorios recursivamente
    parts = path.strip('/').split('/')
    current = ""
    for part in parts:
        current += f"/{part}"
        try:
            ftp.cwd(current)
        except error_perm:
            try:
                ftp.mkd(current)
                ftp.cwd(current)
            except:
                pass


# ══════════════════════════════════════════════════════
#  UPDATES WINDOW
# ══════════════════════════════════════════════════════
class UpdatesWindow(tk.Toplevel):
    def __init__(self, parent, game):
        super().__init__(parent)
        self.game = game
        self.title(t("upd_win_title", name=game["name"]))
        self.geometry("780x640"); self.minsize(560, 420)
        self.configure(bg="#1a1a2e"); self.resizable(True, True)
        self.transient(parent)
        self._closed = False
        self._build(); self.after(80, self._fetch)

    def _build(self):
        g = self.game
        hdr = tk.Frame(self, bg="#16213e", pady=10, padx=15)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🎮  {g['name']}", font=("Consolas",12,"bold"),
                 bg="#16213e", fg="#00d4ff").pack(side="left")
        tk.Label(hdr, text=f"  {g['title_id']}  ·  v{g['version']}  ·  FW:{g['min_fw']}",
                 font=("Consolas",9), bg="#16213e", fg="#557").pack(side="left")

        self.st_frame = tk.Frame(self, bg="#0f3460", pady=8); self.st_frame.pack(fill="x")
        self.st_lbl = tk.Label(self.st_frame, text=t("upd_fetching"),
                               font=("Consolas",11,"bold"), bg="#0f3460", fg="#ffd700")
        self.st_lbl.pack()

        outer = tk.Frame(self, bg="#1a1a2e"); outer.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(outer, bg="#1a1a2e", highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y"); self.canvas.pack(side="left", fill="both", expand=True)
        self.content = tk.Frame(self.canvas, bg="#1a1a2e")
        self._wid = self.canvas.create_window((0,0), window=self.content, anchor="nw")
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self._wid, width=e.width))
        self.content.bind("<Configure>",
                          lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1*(e.delta//120),"units"))

        foot = tk.Frame(self, bg="#1a1a2e", pady=8); foot.pack(fill="x")
        bst = dict(relief="flat", font=("Consolas",9), padx=10, pady=4, cursor="hand2")
        tk.Button(foot, text=t("upd_open_orbis"), command=self._open_orbis,
                  bg="#1a3a5c", fg="#88ccff", **bst).pack(side="left", padx=6)
        tk.Button(foot, text=t("upd_close"), command=self.destroy,
                  bg="#2a2a40", fg="#ccc", **bst).pack(side="right", padx=10)

    def destroy(self):
        self._closed = True
        super().destroy()

    def _safe_after(self, fn):
        """Schedule fn() only if the window is still alive."""
        if self._closed:
            return
        try:
            if self.winfo_exists():
                self.after(0, fn)
        except Exception:
            pass

    def _fetch(self):
        def _progress(msg):
            self._safe_after(lambda m=msg: self.st_lbl.config(text=m))

        def worker():
            # Si el pool aún está arrancando, avisar al usuario
            if PLAYWRIGHT_AVAILABLE and not _pw_pool._ready.is_set():
                _progress(t("pw_waiting"))
            try:
                result = fetch_orbis_full(self.game["title_id"],
                                          _progress_cb=_progress)
                self._safe_after(lambda: self._show(result))
            except Exception as e:
                err = t("upd_err_unexpected", error=str(e)[:100])
                self._safe_after(lambda: self.st_lbl.config(text=err, fg="#ffaa00"))
        threading.Thread(target=worker, daemon=True).start()

    def _show(self, result):
        if self._closed or not self.winfo_exists():
            return
        for w in self.content.winfo_children(): w.destroy()
        patches  = result.get("patches", [])
        blocked  = result.get("blocked", False)
        pw_used  = result.get("playwright_used", False)
        err_msg  = result.get("error", "")

        if blocked:
            self.st_lbl.config(text=t("upd_blocked"), fg="#ffaa00")
            tk.Label(self.content,
                     text=t("upd_blocked_hint"),
                     font=("Consolas", 10), bg="#1a1a2e", fg="#888",
                     justify="center").pack(pady=20)
            hint = (
                "  Si el bloqueo persiste, ejecuta:\n"
                "      python diagnostico_orbis.py {tid}\n"
                "  para ver qué devuelve el sitio exactamente."
            ).format(tid=self.game.get("title_id","?"))
            tk.Label(self.content, text=hint,
                     font=("Consolas", 9), bg="#1a1a2e", fg="#666",
                     justify="left").pack(pady=(0,20), padx=20, anchor="w")

        elif not patches:
            engine = "Playwright" if pw_used else "requests"
            self.st_lbl.config(text=t("upd_no_data_engine", engine=engine), fg="#ff6666")

            # Hint de instalación si falta Playwright
            if not PLAYWRIGHT_AVAILABLE:
                hint = (
                    "  ⚠  Playwright no instalado — el JS del sitio no se ejecuta.\n\n"
                    "  Para activar el renderizado JS, ejecuta:\n"
                    "      pip install playwright\n"
                    "      python -m playwright install chromium\n\n"
                    "  Luego reinicia la aplicación."
                )
                tk.Label(self.content, text=hint,
                         font=("Consolas", 10), bg="#1a1a2e", fg="#aaa",
                         justify="left").pack(pady=20, padx=20, anchor="w")
            elif err_msg:
                # Error de parseo: mostrar detalle y cómo diagnosticar
                tk.Label(self.content,
                         text="  ℹ  " + err_msg,
                         font=("Consolas", 9), bg="#1a1a2e", fg="#888",
                         justify="left", wraplength=560).pack(
                             pady=12, padx=20, anchor="w")
                tip = (
                    "  Ejecuta el script de diagnóstico para ver la\n"
                    "  estructura HTML real que devuelve el sitio:\n\n"
                    "      python diagnostico_orbis.py "
                    + self.game.get("title_id","?")
                )
                tk.Label(self.content, text=tip,
                         font=("Consolas", 9), bg="#1a1a2e", fg="#666",
                         justify="left").pack(pady=(0,20), padx=20, anchor="w")
            else:
                tk.Label(self.content,
                         text=t("upd_no_patches"),
                         font=("Consolas", 10), bg="#1a1a2e", fg="#888").pack(
                             pady=30)

        else:
            engine = "Playwright ✓" if pw_used else "requests"
            self.st_lbl.config(
                text=t("upd_found", n=len(patches)) + f"  [{engine}]",
                fg="#00ff99")
            for p in patches:
                self._card(p)
            warn = tk.Frame(self.content, bg="#3b1800", padx=12, pady=8)
            warn.pack(fill="x", padx=8, pady=(10, 4))
            tk.Label(warn, text=t("upd_warning"), font=("Consolas", 9),
                     bg="#3b1800", fg="#ff9944", justify="left").pack(anchor="w")

        self.canvas.yview_moveto(0)

    def _card(self, p):
        ver     = p["version"]; is_latest = p.get("is_latest", False)
        is_mine = _norm_ver(ver) == _norm_ver(self.game.get("version",""))
        bg = "#1a2a3a" if is_latest else "#16213e"
        card = tk.Frame(self.content, bg=bg, padx=10, pady=8)
        card.pack(fill="x", padx=8, pady=3)

        r1 = tk.Frame(card, bg=bg); r1.pack(fill="x")
        tk.Label(r1, text=f"  Patch {ver}", font=("Consolas",11,"bold"),
                 bg=bg, fg="#ffd700" if is_latest else "#00d4ff").pack(side="left")
        if is_latest:
            tk.Label(r1, text=f"  {t('upd_latest_badge')}",
                     font=("Consolas",9,"bold"), bg=bg, fg="#ffd700").pack(side="left")
        if is_mine:
            tk.Label(r1, text=f"  {t('upd_your_fpkg')}",
                     font=("Consolas",9,"italic"), bg=bg, fg="#00cc66").pack(side="left")

        fw_str = p.get("firmware","?"); my_fw = self.game.get("min_fw","?")
        fw_icon, fw_col = "", "#aaa"
        if fw_str != "?" and my_fw != "?":
            try:
                fw_icon, fw_col = (("🟢 ","#00ff99") if float(fw_str) <= float(my_fw)
                                   else ("🔴 ","#ff5555"))
            except ValueError: pass

        r2 = tk.Frame(card, bg=bg); r2.pack(fill="x", pady=(4,0))
        for lbl, val, col in [
            (t("upd_fw_label"),   f"{fw_icon}{fw_str}", fw_col),
            (t("upd_size_label"), p.get("size","?"), "#aaa"),
            (t("upd_date_label"), p.get("creation_date",""), "#666"),
        ]:
            if val and val not in ("?",""):
                tk.Label(r2, text=f"{lbl}: ", font=("Consolas",8),
                         bg=bg, fg="#557").pack(side="left")
                tk.Label(r2, text=f"{val}   ", font=("Consolas",8,"bold"),
                         bg=bg, fg=col).pack(side="left")

        nf = tk.Frame(card, bg=bg); nf.pack(fill="x", pady=(4,0))
        notes = p.get("notes","")
        if notes: self._notes_widget(nf, ver, notes, bg)
        else:
            tk.Label(nf, text=f"  {t('upd_no_notes')}",
                     font=("Consolas",8,"italic"), bg=bg, fg="#444").pack(anchor="w")
        tk.Frame(card, bg="#1a2a3a", height=1).pack(fill="x", pady=(6,0))

    def _notes_widget(self, parent, ver, notes_en, bg):
        frame = tk.Frame(parent, bg=bg); frame.pack(fill="x")
        hrow  = tk.Frame(frame, bg=bg);  hrow.pack(fill="x")
        tk.Label(hrow, text=f"  📋 {t('upd_notes_title',ver=ver)}",
                 font=("Consolas",8,"bold"), bg=bg, fg="#88aacc").pack(side="left")
        tk.Label(hrow, text=f"  {t('upd_notes_source')}",
                 font=("Consolas",7), bg=bg, fg="#336688").pack(side="left")
        txt = tk.Text(frame, bg="#060e18", fg="#b8cee0", font=("Consolas",9),
                      relief="flat", state="disabled", wrap="word",
                      height=4, bd=0, padx=6, pady=4)
        txt.pack(fill="x", pady=(2,0))
        lang   = _current_lang
        cached = _translation_cache.get((notes_en[:200], lang))
        disp   = cached if cached else notes_en
        txt.config(state="normal"); txt.insert("end", disp); txt.config(state="disabled")
        if lang != "en" and not cached:
            st = tk.Label(hrow, text=f"  ⟳ {t('upd_notes_translating')}",
                          font=("Consolas",7), bg=bg, fg="#667788")
            st.pack(side="left")
            def do_translate():
                translated = translate_patch_notes(notes_en, lang)
                def upd():
                    try:
                        txt.config(state="normal"); txt.delete("1.0","end")
                        txt.insert("end", translated); txt.config(state="disabled")
                        st.destroy()
                    except Exception: pass
                self.after(0, upd)
            threading.Thread(target=do_translate, daemon=True).start()

    def _open_orbis(self):
        webbrowser.open(ORBIS_URL.format(tid=self.game["title_id"].upper()))


# ══════════════════════════════════════════════════════
#  DOWNLOAD MANAGER  (singleton Toplevel)
# ══════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════
#  FTP CONFIGURATION WINDOW
# ══════════════════════════════════════════════════════
class FTPConfigWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(t("ftp_dialog_title"))
        self.geometry("560x580")
        self.minsize(500, 550)
        self.configure(bg="#1a1a2e")
        self.resizable(True, True)
        self.transient(parent)
        self._build()
    
    def _build(self):
        # Header
        hdr = tk.Frame(self, bg="#16213e", pady=12, padx=15)
        hdr.pack(fill="x")
        tk.Label(hdr, text=t("ftp_win_title"), 
                font=("Consolas", 14, "bold"),
                bg="#16213e", fg="#00d4ff").pack(side="left")
        
        # Estado actual
        status_text = t("ftp_status_enabled") if FTP_CONFIG["enabled"] else t("ftp_status_disabled")
        status_color = "#00ff88" if FTP_CONFIG["enabled"] else "#666"
        tk.Label(hdr, text=status_text,
                font=("Consolas", 10, "bold"),
                bg="#16213e", fg=status_color).pack(side="right")
        
        # Descripción
        desc_frame = tk.Frame(self, bg="#0f3460", pady=10, padx=15)
        desc_frame.pack(fill="x")
        tk.Label(desc_frame, text=t("ftp_desc"), 
                font=("Consolas", 9),
                bg="#0f3460", fg="#aaa",
                justify="left").pack(anchor="w")
        
        # Contenedor del formulario con scroll
        outer = tk.Frame(self, bg="#1a1a2e")
        outer.pack(fill="both", expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(outer, bg="#1a1a2e", highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        form = tk.Frame(canvas, bg="#1a1a2e")
        canvas_window = canvas.create_window((0, 0), window=form, anchor="nw")
        
        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=e.width)
        
        canvas.bind("<Configure>", _on_configure)
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Habilitar FTP
        chk_frame = tk.Frame(form, bg="#16213e", padx=15, pady=12)
        chk_frame.pack(fill="x", pady=(0, 10))
        
        self.enabled_var = tk.BooleanVar(value=FTP_CONFIG["enabled"])
        chk = tk.Checkbutton(chk_frame, 
                            text=t("ftp_enable"),
                            variable=self.enabled_var,
                            font=("Consolas", 11, "bold"),
                            bg="#16213e", fg="#00ff88",
                            selectcolor="#0f3460",
                            activebackground="#16213e",
                            activeforeground="#00ffaa",
                            command=self._toggle_enabled)
        chk.pack(anchor="w")
        
        # Campos del formulario
        self.fields_frame = tk.Frame(form, bg="#16213e", padx=15, pady=15)
        self.fields_frame.pack(fill="both", expand=True)
        
        # IP / Host
        self._add_field(t("ftp_host_label"), "host", FTP_CONFIG["host"],
                       tooltip="IP / Host (e.g.: 192.168.1.210)")
        
        # Puerto
        self._add_field(t("ftp_port_label"), "port", str(FTP_CONFIG["port"]),
                       tooltip="FTP port (e.g.: 2121)")
        
        # Usuario
        self._add_field(t("ftp_user_label"), "user", FTP_CONFIG["user"],
                       tooltip="FTP user (usually: anonymous)")
        
        # Contraseña
        self._add_field(t("ftp_pass_label"), "password", FTP_CONFIG["password"],
                       show="*", tooltip="FTP password (leave empty if none)")
        
        # Ruta remota
        self._add_field(t("ftp_dir_label"), "remote_path", 
                       FTP_CONFIG["remote_path"],
                       tooltip="Path on PS4 to save files (e.g.: /data/pkg)")
        
        # Opciones adicionales
        opts_frame = tk.Frame(self.fields_frame, bg="#16213e")
        opts_frame.pack(fill="x", pady=(10, 0))
        
        self.passive_var = tk.BooleanVar(value=FTP_CONFIG.get("passive_mode", True))
        tk.Checkbutton(opts_frame, text=t("ftp_passive"),
                      variable=self.passive_var,
                      font=("Consolas", 9),
                      bg="#16213e", fg="#aaa",
                      selectcolor="#0f3460",
                      activebackground="#16213e").pack(anchor="w")
        
        # Separador
        tk.Frame(self.fields_frame, bg="#0f3460", height=1).pack(fill="x", pady=15)
        
        # Botón de prueba
        test_frame = tk.Frame(self.fields_frame, bg="#16213e")
        test_frame.pack(fill="x")
        
        tk.Button(test_frame, text=t("ftp_test_btn"),
                 command=self._test_connection,
                 bg="#1a3a5c", fg="#88ccff",
                 relief="flat",
                 font=("Consolas", 10),
                 padx=15, pady=8,
                 cursor="hand2").pack(side="left")
        
        self.test_result_lbl = tk.Label(test_frame, text="",
                                        font=("Consolas", 9),
                                        bg="#16213e")
        self.test_result_lbl.pack(side="left", padx=10)
        
        # Botones de acción
        btn_frame = tk.Frame(self, bg="#0f0f1a", pady=12)
        btn_frame.pack(fill="x", side="bottom")
        
        bst = dict(relief="flat", font=("Consolas", 10, "bold"), 
                  padx=20, pady=8, cursor="hand2")
        
        tk.Button(btn_frame, text=t("ftp_save_btn"),
                 command=self._save,
                 bg="#0f7a3c", fg="white", **bst).pack(side="right", padx=(5, 15))
        
        tk.Button(btn_frame, text=t("ftp_cancel_btn"),
                 command=self.destroy,
                 bg="#7a0f0f", fg="white", **bst).pack(side="right", padx=5)
        
        # Estado inicial
        self._toggle_enabled()
    
    def _add_field(self, label_text, var_name, default_value, show=None, tooltip=""):
        row = tk.Frame(self.fields_frame, bg="#16213e")
        row.pack(fill="x", pady=6)
        
        lbl_frame = tk.Frame(row, bg="#16213e", width=180)
        lbl_frame.pack(side="left", fill="y")
        lbl_frame.pack_propagate(False)
        
        tk.Label(lbl_frame, text=label_text,
                font=("Consolas", 10),
                bg="#16213e", fg="#00d4ff",
                anchor="w").pack(side="left", padx=(0, 5))
        
        var = tk.StringVar(value=default_value)
        setattr(self, f"{var_name}_var", var)
        
        entry = tk.Entry(row, textvariable=var,
                        font=("Consolas", 10),
                        bg="#0f3460", fg="white",
                        insertbackground="white",
                        relief="flat",
                        show=show)
        entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 5))
        
        if tooltip:
            # Tooltip simple
            def show_tooltip(e):
                entry.config(bg="#1a5080")
            def hide_tooltip(e):
                entry.config(bg="#0f3460")
            entry.bind("<Enter>", show_tooltip)
            entry.bind("<Leave>", hide_tooltip)
    
    def _toggle_enabled(self):
        state = "normal" if self.enabled_var.get() else "disabled"
        for widget in self.fields_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, (tk.Entry, tk.Checkbutton, tk.Button)):
                        try:
                            child.configure(state=state)
                        except:
                            pass
    
    def _test_connection(self):
        """Probar conexión FTP"""
        self.test_result_lbl.config(text=t("ftp_testing"), fg="#ffd700")
        self.update()
        
        def test_thread():
            try:
                ftp = FTP()
                ftp.connect(self.host_var.get().strip(), 
                           int(self.port_var.get().strip()), 
                           timeout=10)
                ftp.login(self.user_var.get().strip(), 
                         self.password_var.get())
                
                if self.passive_var.get():
                    ftp.set_pasv(True)
                
                # Intentar cambiar al directorio
                remote_path = self.remote_path_var.get().strip()
                try:
                    ftp.cwd(remote_path)
                    msg = t("ftp_conn_ok")
                    color = "#00ff88"
                except error_perm:
                    msg = t("ftp_conn_warn")
                    color = "#ffaa00"
                
                ftp.quit()
                self.after(0, lambda: self.test_result_lbl.config(text=msg, fg=color))
                
            except Exception as e:
                error_msg = str(e)[:40]
                self.after(0, lambda: self.test_result_lbl.config(
                    text=f"❌ Error: {error_msg}", fg="#ff4444"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _save(self):
        """Guardar configuración"""
        try:
            # Validar puerto
            try:
                port = int(self.port_var.get().strip())
                if port < 1 or port > 65535:
                    raise ValueError()
            except ValueError:
                messagebox.showerror(t("ftp_err_title"),
                                   t("ftp_err_port"),
                                   parent=self)
                return
            
            # Actualizar configuración
            FTP_CONFIG["enabled"] = self.enabled_var.get()
            FTP_CONFIG["host"] = self.host_var.get().strip()
            FTP_CONFIG["port"] = port
            FTP_CONFIG["user"] = self.user_var.get().strip()
            FTP_CONFIG["password"] = self.password_var.get()
            FTP_CONFIG["remote_path"] = self.remote_path_var.get().strip()
            FTP_CONFIG["passive_mode"] = self.passive_var.get()
            
            # Guardar en archivo
            save_ftp_config()
            
            # Mensaje de éxito
            status = t("ftp_status_enabled") if FTP_CONFIG["enabled"] else t("ftp_status_disabled")
            dest = f"{FTP_CONFIG['host']}:{FTP_CONFIG['port']}{FTP_CONFIG['remote_path']}"
            
            messagebox.showinfo(t("ftp_save_ok_title"),
                              t("ftp_save_ok_body", status=status, dest=dest),
                              parent=self)
            self.destroy()
        
        except Exception as e:
            messagebox.showerror(t("ftp_err_title"),
                               t("ftp_err_save_body", error=str(e)),
                               parent=self)


# ══════════════════════════════════════════════════════
#  DOWNLOAD MANAGER
# ══════════════════════════════════════════════════════
class DownloadManager(tk.Toplevel):
    _instance = None

    @classmethod
    def get_or_create(cls, parent):
        if cls._instance is None or not cls._instance.winfo_exists():
            cls._instance = cls(parent)
        else: cls._instance.lift()
        return cls._instance

    def __init__(self, parent):
        super().__init__(parent)
        self.title(t("dl_title").strip())
        self.geometry("720x480"); self.minsize(520,300)
        self.configure(bg="#1a1a2e"); self.resizable(True,True)
        self.transient(parent); self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._downloads = {}; self._build()

    def _build(self):
        hdr = tk.Frame(self, bg="#16213e", pady=8, padx=12); hdr.pack(fill="x")
        tk.Label(hdr, text=t("dl_title"), font=("Consolas",13,"bold"),
                 bg="#16213e", fg="#00d4ff").pack(side="left")
        tk.Button(hdr, text=t("dl_clear_done"), command=self._clear_done,
                  bg="#1a3a5c", fg="#88ccff", relief="flat",
                  font=("Consolas",9), padx=8, pady=3, cursor="hand2").pack(side="right")
        outer = tk.Frame(self, bg="#1a1a2e"); outer.pack(fill="both", expand=True, padx=8, pady=8)
        self.canvas = tk.Canvas(outer, bg="#1a1a2e", highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y"); self.canvas.pack(side="left",fill="both",expand=True)
        self.content = tk.Frame(self.canvas, bg="#1a1a2e")
        self._wid = self.canvas.create_window((0,0), window=self.content, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._wid, width=e.width))
        self.content.bind("<Configure>",
                          lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1*(e.delta//120),"units"))
        sb = tk.Frame(self, bg="#0f0f1a", pady=3); sb.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value=t("dl_no_active"))
        self.count_var  = tk.StringVar(value="")
        ttk.Label(sb, textvariable=self.status_var, style="SB.TLabel").pack(side="left", padx=8)
        ttk.Label(sb, textvariable=self.count_var,  style="SB.TLabel").pack(side="right", padx=8)

    def add_download(self, game, pkg_url=None, update_info=None):
        url = pkg_url or game.get("pkg_url","")
        if not url: return
        key = f"{game['title_id']}_{url[-24:]}"
        if key in self._downloads:
            # Already present: just bring window to front
            return
        self._downloads[key] = self._make_card(key, game, url, update_info)
        self._update_count()
        self._start(key, game, url)

    def _make_card(self, key, game, url, update_info):
        """Build a download card with Pause / Resume / Restart / Cancel controls."""
        import threading as _th

        card = tk.Frame(self.content, bg="#16213e", padx=10, pady=8)
        card.pack(fill="x", padx=4, pady=3)
        tk.Frame(card, bg="#0f3460", height=1).pack(fill="x", pady=(0,6))

        lbl_text = (t("dl_update_label", name=game["name"],
                      ver=update_info.get("version","?")) if update_info
                    else t("dl_game_label", name=game["name"], ver=game.get("version","?")))
        tk.Label(card, text=f"  {lbl_text}", font=("Consolas",10,"bold"),
                 bg="#16213e", fg="#00d4ff").pack(anchor="w")

        if FTP_CONFIG["enabled"]:
            dest_text  = f"  🌐 FTP: {FTP_CONFIG['host']}:{FTP_CONFIG['port']}{FTP_CONFIG['remote_path']}"
            dest_color = "#00ff88"
        else:
            dest_text  = f"  📁 {get_download_dir(game['title_id'])}"
            dest_color = "#556"
        tk.Label(card, text=dest_text,
                 font=("Consolas",8), bg="#16213e", fg=dest_color).pack(anchor="w")

        prog = ttk.Progressbar(card, orient="horizontal", mode="determinate",
                               style="TProgressbar")
        prog.pack(fill="x", pady=(4,2))
        info_lbl = tk.Label(card, text=t("dl_starting"), font=("Consolas",9),
                            bg="#16213e", fg="#888")
        info_lbl.pack(anchor="w")

        bf = tk.Frame(card, bg="#16213e"); bf.pack(anchor="w", pady=(4,0))
        btn_pause   = tk.Button(bf, text=t("dl_pause"),   bg="#1a3a5c", fg="#88ccff",
                                relief="flat", font=("Consolas",9), padx=6, pady=2, cursor="hand2")
        btn_restart = tk.Button(bf, text=t("dl_restart"), bg="#2a1a00", fg="#ffaa44",
                                relief="flat", font=("Consolas",9), padx=6, pady=2, cursor="hand2")
        btn_cancel  = tk.Button(bf, text=t("dl_cancel"),  bg="#2a2a40", fg="#ccc",
                                relief="flat", font=("Consolas",9), padx=6, pady=2, cursor="hand2")
        btn_pause.pack(side="left", padx=(0,4))
        btn_restart.pack(side="left", padx=(0,4))
        btn_cancel.pack(side="left")

        ctrl = {"pause": _th.Event(), "cancelled": False,
                "done": False, "bytes_done": 0, "total": 0, "dest": None}
        ctrl["pause"].set()

        d = {"card": card, "prog": prog, "info_lbl": info_lbl,
             "btn_pause": btn_pause, "btn_restart": btn_restart, "btn_cancel": btn_cancel,
             "ctrl": ctrl, "cancelled": False, "done": False,
             "game": game, "url": url, "update_info": update_info}

        def _do_pause():
            if ctrl["cancelled"] or ctrl["done"]: return
            ctrl["pause"].clear()
            btn_pause.config(text=t("dl_resume"), bg="#003d5c", fg="#00ff99")
            info_lbl.config(text=t("dl_paused"), fg="#ffd700")

        def _do_resume():
            if ctrl["cancelled"] or ctrl["done"]: return
            ctrl["pause"].set()
            btn_pause.config(text=t("dl_pause"), bg="#1a3a5c", fg="#88ccff")

        def _toggle_pause():
            if ctrl["pause"].is_set():
                _do_pause()
            else:
                _do_resume()

        def _do_restart():
            # Cancel current download then restart from beginning
            ctrl["cancelled"] = True
            ctrl["pause"].set()            # unblock thread so it can exit
            d["done"] = False
            ctrl["cancelled"] = False
            ctrl["done"]      = False
            ctrl["bytes_done"] = 0
            ctrl["total"]     = 0
            ctrl["pause"].set()
            # Delete partial local file if present
            if ctrl.get("dest"):
                try:
                    p = Path(ctrl["dest"])
                    if p.exists(): p.unlink()
                except Exception: pass
            # Reset UI
            prog["value"] = 0
            info_lbl.config(text=t("dl_starting"), fg="#888")
            btn_pause.config(text=t("dl_pause"), bg="#1a3a5c", fg="#88ccff", state="normal")
            btn_restart.config(state="normal")
            btn_cancel.config(text=t("dl_cancel"), bg="#2a2a40", fg="#ccc", state="normal")
            d["cancelled"] = False
            self._start(key, game, url)

        def _do_cancel():
            ctrl["cancelled"] = True
            ctrl["pause"].set()            # unblock if paused
            d["cancelled"] = True
            btn_pause.config(state="disabled")
            btn_restart.config(state="normal")   # allow restart after cancel
            btn_cancel.config(text=t("dl_cancelled"), state="disabled")
            info_lbl.config(text=t("dl_cancelled_msg"), fg="#ff6666")
            d["done"] = True; self._update_count()

        btn_pause.config(command=_toggle_pause)
        btn_restart.config(command=_do_restart)
        btn_cancel.config(command=_do_cancel)
        return d

    def _start(self, key, game, url):
        d = self._downloads[key]
        ctrl = d["ctrl"]
        ctrl["cancelled"] = False
        ctrl["done"]      = False
        ctrl["pause"].set()

        def pcb(done, total):
            if ctrl["cancelled"]: return
            if total > 0:
                pct = done / total * 100
                self.after(0, lambda p=pct, dh=_bytes_to_human(done),
                                      th=_bytes_to_human(total): self._upd(key, p, dh, th))
        def dcb(ok, info):
            self.after(0, lambda: self._finish(key, ok, info))

        download_pkg(url, game["title_id"], game["name"],
                     progress_cb=pcb, done_cb=dcb, ctrl=ctrl)

    def _upd(self, key, pct, dh, th):
        d = self._downloads.get(key)
        if not d or d["cancelled"]: return
        d["prog"]["value"] = pct
        d["info_lbl"].config(text=f"  {dh} / {th}  ({pct:.1f}%)", fg="#aaa")

    def _finish(self, key, ok, info):
        d = self._downloads.get(key)
        if not d or d.get("ctrl", {}).get("cancelled", d.get("cancelled", False)): return
        d["done"] = True
        if d.get("ctrl"): d["ctrl"]["done"] = True
        bp = d.get("btn_pause"); br = d.get("btn_restart"); bc = d.get("btn_cancel")
        if ok:
            d["prog"]["value"] = 100
            d["info_lbl"].config(text=f"  ✅ {info}", fg="#00ff99")
            if bp: bp.config(state="disabled")
            if br: br.config(state="disabled")
            if bc: bc.config(text=t("dl_open_folder"),
                             command=lambda: self._open_folder(info),
                             bg="#0f3460", fg="#00d4ff", state="normal")
        else:
            d["info_lbl"].config(text=f"  ❌ {info[:90]}", fg="#ff4444")
            if bp: bp.config(state="disabled")
            if br: br.config(text=t("dl_restart"), bg="#2a1a00", fg="#ffaa44", state="normal")
            if bc: bc.config(text=t("dl_close"), state="normal",
                             command=lambda k=key: self._remove(k))
        self._update_count()

    def _update_count(self):
        active = sum(1 for d in self._downloads.values() if not d["done"])
        total  = len(self._downloads)
        self.count_var.set(t("dl_count", active=active, total=total))
        if active == 0 and total > 0: self.status_var.set(t("dl_all_done"))

    def _clear_done(self):
        for k in [k for k,d in self._downloads.items() if d["done"]]:
            try: self._downloads.pop(k)["card"].destroy()
            except Exception: pass
        self._update_count()

    def _remove(self, key):
        d = self._downloads.pop(key, None)
        if d:
            try: d["card"].destroy()
            except Exception: pass
        self._update_count()

    @staticmethod
    def _open_folder(fp):
        folder = str(Path(fp).parent)
        if os.name == "nt": os.startfile(folder)
        else: webbrowser.open(f"file://{folder}")


    def add_local_ftp_transfer(self, local_path):
        """Upload a locally selected .pkg file to PS4 via FTP."""
        filename = os.path.basename(local_path)
        try:
            file_size = os.path.getsize(local_path)
        except Exception:
            file_size = 0
        size_str = _bytes_to_human(file_size) if file_size else "?"
        key = f"local_ftp_{id(local_path) & 0xFFFFFF}"
        if key in self._downloads:
            return

        # Build a minimal card for the local→FTP upload
        card_frame = tk.Frame(self.content, bg="#16213e", padx=10, pady=8)
        card_frame.pack(fill="x", padx=4, pady=3)
        tk.Frame(card_frame, bg="#0f3460", height=1).pack(fill="x", pady=(0,6))
        tk.Label(card_frame, text=f"  📤 {t('ftp_upload_label', name=filename)}",
                 font=("Consolas",10,"bold"), bg="#16213e", fg="#aa88ff").pack(anchor="w")
        dest_text = f"  🌐 FTP → {FTP_CONFIG['host']}:{FTP_CONFIG['port']}{FTP_CONFIG['remote_path']}"
        tk.Label(card_frame, text=dest_text,
                 font=("Consolas",8), bg="#16213e", fg="#00ff88").pack(anchor="w")
        prog = ttk.Progressbar(card_frame, orient="horizontal", mode="determinate",
                               style="TProgressbar")
        prog.pack(fill="x", pady=(4,2))
        info_lbl = tk.Label(card_frame, text=t("dl_starting"), font=("Consolas",9),
                            bg="#16213e", fg="#888")
        info_lbl.pack(anchor="w")
        bf = tk.Frame(card_frame, bg="#16213e"); bf.pack(anchor="w", pady=(4,0))
        cancelled = [False]
        btn = tk.Button(bf, text=t("dl_cancel"), bg="#2a2a40", fg="#ccc",
                        relief="flat", font=("Consolas",9), padx=6, pady=2, cursor="hand2")
        btn.pack(side="left")

        d = {"card": card_frame, "prog": prog, "info_lbl": info_lbl, "btn": btn,
             "cancelled": False, "done": False}
        self._downloads[key] = d

        def _cancel():
            cancelled[0] = True
            d["cancelled"] = True
            btn.config(text=t("dl_cancelled"), state="disabled")
            info_lbl.config(text=t("dl_cancelled_msg"), fg="#ff6666")
            d["done"] = True; self._update_count()
        btn.config(command=_cancel)
        self._update_count()

        def worker():
            try:
                self.after(0, lambda: info_lbl.config(
                    text=t("ftp_uploading"), fg="#ffd700"))
                remote_dir  = FTP_CONFIG.get("remote_path", "/data/pkg")
                remote_full = remote_dir.rstrip("/") + "/" + filename

                ftp = FTP()
                ftp.connect(FTP_CONFIG["host"], int(FTP_CONFIG["port"]),
                            timeout=FTP_CONFIG.get("timeout", 30))
                ftp.login(FTP_CONFIG.get("user", "anonymous"),
                          FTP_CONFIG.get("password", ""))
                if FTP_CONFIG.get("passive_mode", True):
                    ftp.set_pasv(True)
                _ensure_ftp_directory(ftp, remote_dir)

                sent = [0]
                def progress_cb(block):
                    if cancelled[0]:
                        raise InterruptedError()
                    sent[0] += len(block)
                    if file_size > 0:
                        pct = sent[0] / file_size * 100
                        sh  = _bytes_to_human(sent[0])
                        self.after(0, lambda p=pct, s=sh: (
                            prog.configure(value=p),
                            info_lbl.config(
                                text=t("ftp_uploading_pct", pct=int(p), sent=s, total=size_str),
                                fg="#ffd700")
                        ))

                with open(local_path, "rb") as fh:
                    ftp.storbinary(f"STOR {remote_full}", fh,
                                   blocksize=65536, callback=progress_cb)
                ftp.quit()
                if not cancelled[0]:
                    self.after(0, lambda: (
                        prog.configure(value=100),
                        info_lbl.config(text=t("ftp_upload_done"), fg="#00ff99"),
                        btn.config(text=t("dl_close"), state="normal",
                                   command=lambda k=key: self._remove(k))
                    ))
                    d["done"] = True; self.after(0, self._update_count)
            except InterruptedError:
                pass
            except Exception as e:
                err = str(e)[:70]
                self.after(0, lambda: (
                    info_lbl.config(text=t("ftp_upload_error", error=err), fg="#ff4444"),
                    btn.config(text=t("dl_close"), state="normal",
                               command=lambda k=key: self._remove(k))
                ))
                d["done"] = True; self.after(0, self._update_count)

        threading.Thread(target=worker, daemon=True).start()

    def _on_close(self):
        active = sum(1 for d in self._downloads.values() if not d["done"])
        if active > 0: self.withdraw()
        else: DownloadManager._instance = None; self.destroy()


class DownloadWindow:
    def __init__(self, parent, game, pkg_url=None, update_info=None):
        mgr = DownloadManager.get_or_create(parent)
        mgr.deiconify(); mgr.lift()
        mgr.add_download(game, pkg_url=pkg_url, update_info=update_info)


# ══════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════
class FPKGiManager(tk.Tk):
    def __init__(self):
        super().__init__()
        # Load persistent settings (language, paths, geometry)
        load_settings()
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        geom = _SETTINGS.get("geometry", "1440x800")
        self.geometry(geom); self.minsize(960,600)
        self.configure(bg="#0a0a1e")
        self.games = []; self.icon_cache = {}; self.avail_cache = {}
        self._executor  = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self._icon_queue = queue.Queue()
        self._icon_done  = False
        self._last_game = None
        self._bg_running = False
        self._apply_styles()
        self._build_background()      # animated PS4 wallpaper
        self._build_menu()
        self._build_ui()
        # Bind gradient repaint on resize
        # <Configure> is bound inside _build_ui (also calls _place_panels)
        # Restore paned sash position
        sash = _SETTINGS.get("paned_sash")
        if sash:
            self.after(200, lambda: self._restore_sash(sash))
        # Auto-load last JSON
        last = _SETTINGS.get("last_json")
        if last and Path(last).exists():
            self.after(300, lambda: self._auto_load_json(last))
        # Arrancar el browser Chromium en segundo plano al inicio
        if PLAYWRIGHT_AVAILABLE:
            _pw_pool.start()
            self._update_pw_status()


    # ══════════════════════════════════════════════════════
    #  ANIMATED PS4-STYLE BACKGROUND
    # ══════════════════════════════════════════════════════
    def _build_background(self):
        """Create the animated canvas background (PS symbols + blue gradient)."""
        import math, random

        self._bg_canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self._bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # PS button symbol pool
        self._ps_symbols = list("△○×□") * 8 + list("△○×□") * 4
        self._ps_particles = []

        W, H = 1440, 800
        random.seed(42)
        for _ in range(36):
            sym   = random.choice(self._ps_symbols)
            x     = random.uniform(0, W)
            y     = random.uniform(0, H)
            size  = random.randint(16, 72)
            alpha = random.uniform(0.04, 0.22)
            speed = random.uniform(0.18, 0.55)
            dx    = random.uniform(-0.4, 0.4)
            dy    = random.uniform(-speed, -speed * 0.4)
            drift = random.uniform(-0.003, 0.003)   # slow horizontal drift
            # colour: icy blue-white palette matching the reference
            r = int(120 + alpha * 135)
            g = int(160 + alpha * 95)
            b = int(220 + alpha * 35)
            color = f"#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}"
            tid = self._bg_canvas.create_text(
                x, y, text=sym, font=("Arial", size, "bold"),
                fill=color, anchor="center"
            )
            self._ps_particles.append({
                "id": tid, "x": x, "y": y,
                "dx": dx, "dy": dy, "drift": drift,
                "size": size, "W": W, "H": H,
            })

        self._bg_running = True
        self._animate_bg()

    def _animate_bg(self):
        if not self._bg_running:
            return
        try:
            W = self._bg_canvas.winfo_width()  or 1440
            H = self._bg_canvas.winfo_height() or 800
        except Exception:
            self.after(40, self._animate_bg)
            return

        for p in self._ps_particles:
            p["x"] += p["dx"] + p["drift"] * H
            p["y"] += p["dy"]
            # Wrap vertically – rise up and re-enter from bottom
            if p["y"] < -p["size"]:
                p["y"] = H + p["size"]
                p["x"] = __import__("random").uniform(0, W)
            # Gentle horizontal wrap
            if p["x"] < -p["size"]:
                p["x"] = W + p["size"]
            elif p["x"] > W + p["size"]:
                p["x"] = -p["size"]
            try:
                self._bg_canvas.coords(p["id"], p["x"], p["y"])
            except Exception:
                pass

        self.after(40, self._animate_bg)    # ~25 fps

    def _on_resize(self, event=None):
        """Resize handler: repaint the background gradient."""
        self._draw_bg_gradient(event)

    def _draw_bg_gradient(self, event=None):
        """Repaint gradient bands when window resizes."""
        try:
            c = self._bg_canvas
            c.delete("gradient")
            W = c.winfo_width();  H = c.winfo_height()
            if W < 10 or H < 10:
                return
            steps = 32
            for i in range(steps):
                t_ = i / steps
                # top: very deep navy → richer PS4 royal blue at bottom
                r = int(10  + t_ * 18)
                g = int(10  + t_ * 22)
                b = int(30  + t_ * 50)
                color = f"#{r:02x}{g:02x}{b:02x}"
                y0 = int(H * i / steps)
                y1 = int(H * (i + 1) / steps) + 1
                c.create_rectangle(0, y0, W, y1, fill=color, outline="", tags="gradient")
            # Keep gradient below symbols
            c.tag_lower("gradient")
        except Exception:
            pass

    def _apply_styles(self):
        s = ttk.Style(self); s.theme_use("clam")
        s.configure(".", background="#1a1a2e", foreground="#e0e0e0", font=("Consolas",10))
        # Treeview colours match the gradient midpoint (#0d1230) → appears transparent
        s.configure("Treeview", background="#0d1230", foreground="#c8d8f0",
                    fieldbackground="#0d1230", rowheight=28)
        s.configure("Treeview.Heading", background="#090e24", foreground="#00ccff",
                    font=("Consolas",10,"bold"), relief="flat")
        s.map("Treeview", background=[("selected","#0d2a50")],
              foreground=[("selected","#ffffff")])
        s.configure("TScrollbar", background="#0b0f28", troughcolor="#080c1e", arrowcolor="#334")
        s.configure("TProgressbar", troughcolor="#0f0f1a", background="#00d4ff", thickness=5)
        s.configure("SB.TLabel", background="#0a0a1e", foreground="#557799", font=("Consolas",9))

    def _build_menu(self):
        ko = dict(bg="#16213e", fg="#e0e0e0",
                  activebackground="#0f3460", activeforeground="#00d4ff")
        try:
            old = self.cget("menu")
            if old: self.nametowidget(old).destroy()
        except Exception: pass
        mb = tk.Menu(self, relief="flat", **ko); self.configure(menu=mb)
        mf = tk.Menu(mb, tearoff=0, **ko)
        mf.add_command(label=t("menu_open_json"), command=self._open_json, accelerator="Ctrl+O")
        mf.add_separator(); mf.add_command(label=t("menu_exit"), command=self._on_close)
        mb.add_cascade(label=t("menu_file"), menu=mf)
        self.bind_all("<Control-o>", lambda e: self._open_json())
        mc = tk.Menu(mb, tearoff=0, **ko)
        mc.add_command(label=t("menu_clear_icons"), command=self._clear_icon_cache)
        mc.add_command(label=t("menu_clear_verify"), command=self._clear_avail_cache)
        mb.add_cascade(label=t("menu_cache"), menu=mc)
        md = tk.Menu(mb, tearoff=0, **ko)
        md.add_command(label=t("menu_manage_dl"),   command=self._open_download_mgr)
        md.add_command(label=t("menu_open_dl_folder"), command=self._open_dl_folder)
        md.add_separator()
        md.add_command(label=t("menu_change_path"), command=self._set_download_path)
        md.add_command(label=t("menu_reset_path"),  command=self._reset_download_path)
        md.add_separator()
        # Indicador de estado FTP
        ftp_lbl = t("menu_ftp_on") if FTP_CONFIG["enabled"] else t("menu_ftp_off")
        md.add_command(label=f"⚙️ {ftp_lbl}", command=self._open_ftp_config)
        md.add_command(label=t("menu_send_pkg"), command=self._send_local_pkg)
        mb.add_cascade(label=t("menu_downloads"), menu=md)
        ml = tk.Menu(mb, tearoff=0, **ko)
        for code in AVAILABLE_LANGS:
            ml.add_command(
                label=f"{'✓ ' if code==_current_lang else '   '}{get_lang_name(code)}",
                command=lambda c=code: self._change_lang(c))
        mb.add_cascade(label=t("menu_language"), menu=ml)

    def _build_ui(self):
        top = tk.Frame(self, bg="#111828", pady=8, padx=12); top.pack(fill="x")
        tk.Label(top, text=APP_TITLE, font=("Consolas",17,"bold"),
                 bg="#111828", fg="#00ccff").pack(side="left")
        tk.Label(top, text=f" v{APP_VERSION}", font=("Consolas",9),
                 bg="#111828", fg="#334466").pack(side="left", pady=6)
        bcfg = dict(relief="flat", padx=8, pady=5, cursor="hand2", font=("Consolas",10))
        self._btn_open_json = tk.Button(top, text=t("btn_open_json"), command=self._open_json,
            bg="#0f3460", fg="#00d4ff", font=("Consolas",10,"bold"),
            padx=12, pady=5, cursor="hand2", relief="flat")
        self._btn_open_json.pack(side="right")
        self._btn_downloads = tk.Button(top, text=t("btn_downloads"),
            command=self._open_download_mgr, bg="#1a2a4c", fg="#88aadd", **bcfg)
        self._btn_downloads.pack(side="right", padx=6)
        self._btn_dl_path = tk.Button(top, text=t("btn_dl_path"),
            command=self._set_download_path, bg="#1a3a1a", fg="#88dd88", **bcfg)
        self._btn_dl_path.pack(side="right", padx=6)
        self._btn_open_dl = tk.Button(top, text=t("btn_open_dl_folder"),
            command=self._open_dl_folder, bg="#1a2a3a", fg="#6699bb", **bcfg)
        self._btn_open_dl.pack(side="right", padx=6)
        self._btn_send_ftp = tk.Button(top, text=t("btn_send_pkg_ftp"),
            command=self._send_local_pkg, bg="#1a1a3a", fg="#aa88ff", **bcfg)
        self._btn_send_ftp.pack(side="right", padx=6)

        sf = tk.Frame(self, bg="#0e0e28", pady=4, padx=10); sf.pack(fill="x")
        tk.Label(sf, text="🔍", bg="#0e0e28", fg="#555", font=("Consolas",11)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter())
        tk.Entry(sf, textvariable=self.search_var, bg="#16213e", fg="#e0e0e0",
                 insertbackground="#00d4ff", relief="flat", font=("Consolas",11),
                 bd=6).pack(side="left", fill="x", expand=True, padx=6)

        self.prog_outer = tk.Frame(self, bg="#1a1a2e")
        self.prog_lbl = tk.Label(self.prog_outer, text="", bg="#1a1a2e",
                                 fg="#888", font=("Consolas",9))
        self.prog_lbl.pack(side="left", padx=8)
        self.prog_bar = ttk.Progressbar(self.prog_outer, orient="horizontal",
                                        mode="determinate", style="TProgressbar")
        self.prog_bar.pack(side="left", fill="x", expand=True, padx=(0,8))

        # ═══════════════════════════════════════════════════════════════
        # TRANSPARENT PANELS
        # Panels are placed() over _bg_canvas (which stays lower()'d).
        # Widget backgrounds match the gradient-blended colour so they
        # appear as semi-transparent glass. PS symbols animate freely in
        # the window margins. Panel borders are drawn on _bg_canvas itself.
        # ═══════════════════════════════════════════════════════════════

        # Gradient at panel midpoint: rgb(19,21,55)=#131537
        # Blended 75% gradient + 25% panel tint → #101638
        _G  = "#0d1230"   # matches gradient – base for Treeview rows
        _GA = "#0b0f28"   # alternate row (slightly darker)
        _GH = "#090e24"   # heading background
        _GB = "#1a3468"   # accent border / glow colour

        # Left panel frame — no border, bg matches gradient
        tree_wrap = tk.Frame(self, bg=_G, bd=0, highlightthickness=0)

        # Right detail panel frame
        det = tk.Frame(self, bg=_G, bd=0, highlightthickness=0)

        # Helper: place both panels proportionally and draw their borders on bg_canvas
        def _place_panels(e=None):
            try:
                W = self.winfo_width()
                H = self.winfo_height()
                if W < 100 or H < 100:
                    return
                # Vertical span: below search-bar (≈y_top) to above status-bar (≈y_bot)
                try:
                    y_top = sf.winfo_y() + sf.winfo_height() + 4
                    y_bot = H - (sb.winfo_height() + 3)
                except Exception:
                    y_top = 80; y_bot = H - 28
                ph = max(y_bot - y_top, 20)
                split = int(W * 0.455)    # list panel takes 45 % of width
                pad   = 8

                # Position panels
                tree_wrap.place(x=pad,         y=y_top,
                                width=split-pad-3, height=ph)
                det.place      (x=split+3,     y=y_top,
                                width=W-split-3-pad, height=ph)

                # Draw glowing borders on bg_canvas so symbols show around panels
                if hasattr(self, "_bg_canvas"):
                    c = self._bg_canvas
                    c.delete("panel_border")
                    # List panel outline
                    lx1,ly1 = pad-1,           y_top-1
                    lx2,ly2 = split-pad-3+pad, y_top+ph
                    # Detail panel outline
                    dx1,dy1 = split+2,     y_top-1
                    dx2,dy2 = W-pad+1,     y_top+ph
                    for rect, col in [((lx1,ly1,lx2,ly2), _GB),
                                      ((dx1,dy1,dx2,dy2), _GB)]:
                        x1,y1_,x2,y2_ = rect
                        # Glow: two concentric outlines
                        c.create_rectangle(x1-1,y1_-1,x2+1,y2_+1,
                            outline="#0f2050", fill="", width=2, tags="panel_border")
                        c.create_rectangle(x1,y1_,x2,y2_,
                            outline=col, fill="", width=1, tags="panel_border")
                    c.tag_lower("panel_border")   # keep borders behind widgets
            except Exception:
                pass

        self._place_panels = _place_panels
        self.bind("<Configure>", lambda e: (self._on_resize(e), _place_panels(e)))
        self.after(150, _place_panels)

        # ── TREEVIEW inside left panel ─────────────────────────────────
        cols = ("icon","name","title_id","version","estado","min_fw","region","size")
        self.tree = ttk.Treeview(tree_wrap, columns=cols, show="headings",
                                 selectmode="browse")
        col_cfg = {
            "icon":("col_icon",44),"name":("col_name",270),"title_id":("col_title_id",100),
            "version":("col_version",75),"estado":("col_status",120),"min_fw":("col_fw",75),
            "region":("col_region",65),"size":("col_size",80),
        }
        for col,(lk,w) in col_cfg.items():
            self.tree.heading(col, text=t(lk), command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, minwidth=36)
        vsb = ttk.Scrollbar(tree_wrap, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y"); hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("AVAIL",   foreground="#00ff99")
        self.tree.tag_configure("UNAVAIL", foreground="#ff6666")
        self.tree.tag_configure("pend",    foreground="#555577")
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)
        self.tree.bind("<Button-3>",          self._show_ctx)
        self.tree.bind("<Double-1>",          lambda e: self._show_updates())

        # ── DETAIL panel contents ──────────────────────────────────────
        _DET_BG = _G
        self._lbl_details = tk.Label(det, text=t("lbl_details"),
                                     font=("Consolas",10,"bold"),
                                     bg=_DET_BG, fg="#00ccff", pady=8)
        self._lbl_details.pack()
        self.det_img = tk.Label(det, bg=_DET_BG, text="🎮",
                                font=("Consolas",64), fg="#1e2e4a")
        self.det_img.pack(pady=6)
        self.det_txt = tk.Text(det, bg=_DET_BG, fg="#c0d4e8",
                               font=("Consolas",10), relief="flat",
                               state="disabled", wrap="word", height=10, width=40,
                               bd=0, insertbackground="#00ccff")
        self.det_txt.pack(fill="both", expand=True, padx=10)
        bst2 = dict(relief="flat", font=("Consolas",10,"bold"), pady=6,
                    cursor="hand2", activeforeground="#ffffff", bd=0)
        self._btn_dl_pkg = tk.Button(det, text=t("btn_download_pkg"),
            command=self._download,
            bg="#061828", fg="#00d4ff", activebackground="#0a2a4a", **bst2)
        self._btn_dl_pkg.pack(fill="x", padx=10, pady=(6,2))
        self._btn_updates = tk.Button(det, text=t("btn_view_updates"),
            command=self._show_updates,
            bg="#150a00", fg="#ff9944", activebackground="#2a1500", **bst2)
        self._btn_updates.pack(fill="x", padx=10, pady=(0,2))
        self._btn_check = tk.Button(det, text=t("btn_check_avail"),
            command=self._check_avail_sel,
            bg="#030e03", fg="#00cc66", activebackground="#082008", **bst2)
        self._btn_check.pack(fill="x", padx=10, pady=(0,8))

        ko = dict(bg="#16213e", fg="#e0e0e0",
                  activebackground="#0f3460", activeforeground="#00d4ff")
        self.ctx_menu = tk.Menu(self, tearoff=0, **ko)
        self.ctx_menu.add_command(label=t("ctx_view_updates"), command=self._show_updates)
        self.ctx_menu.add_command(label=t("ctx_check_avail"),  command=self._check_avail_sel)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label=t("ctx_download"), command=self._download)
        self.ctx_menu.add_command(label=t("ctx_orbis"),    command=self._open_orbis)

        sb = tk.Frame(self, bg="#0a0a1e", pady=3); sb.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value=t("status_ready", path=get_active_base()))
        self.count_var  = tk.StringVar(value=t("n_games", n=0))
        ttk.Label(sb, textvariable=self.status_var, style="SB.TLabel").pack(side="left",  padx=8)
        ttk.Label(sb, textvariable=self.count_var,  style="SB.TLabel").pack(side="right", padx=8)
        # Push bg canvas behind all packed+placed widgets
        if hasattr(self, "_bg_canvas"):
            tk.Misc.lower(self._bg_canvas)
            self._draw_bg_gradient()
            self.after(100, self._draw_bg_gradient)
            # Panel borders drawn on canvas need real sizes → delay
            self.after(250, self._place_panels)

    def _change_lang(self, code):
        set_lang(code)
        save_settings({"language": code})
        self._build_menu()
        self._lbl_details.config(text=t("lbl_details"))
        self._btn_open_json.config(text=t("btn_open_json"))
        self._btn_downloads.config(text=t("btn_downloads"))
        self._btn_dl_path.config(text=t("btn_dl_path"))
        self._btn_open_dl.config(text=t("btn_open_dl_folder"))
        self._btn_dl_pkg.config(text=t("btn_download_pkg"))
        self._btn_updates.config(text=t("btn_view_updates"))
        self._btn_check.config(text=t("btn_check_avail"))
        if hasattr(self, "_btn_send_ftp"):
            self._btn_send_ftp.config(text=t("btn_send_pkg_ftp"))
        for col, lk in [("icon","col_icon"),("name","col_name"),("title_id","col_title_id"),
                         ("version","col_version"),("estado","col_status"),("min_fw","col_fw"),
                         ("region","col_region"),("size","col_size")]:
            self.tree.heading(col, text=t(lk))
        for idx, key in enumerate(["ctx_view_updates","ctx_check_avail",None,
                                   "ctx_download","ctx_orbis"]):
            if key:
                try: self.ctx_menu.entryconfig(idx, label=t(key))
                except Exception: pass
        self.status_var.set(t("status_ready", path=get_active_base()))
        self.count_var.set(t("n_games", n=len(self.games)))
        self._populate(self.games)
        if self._last_game: self._show_detail(self._last_game)

    def _show_progress(self, total):
        self.prog_bar["maximum"] = total; self.prog_bar["value"] = 0
        self.prog_lbl.config(text=t("status_icons_loading", n=0, total=total))
        self.prog_outer.pack(fill="x", padx=10, pady=(0,2))

    def _hide_progress(self): self.prog_outer.pack_forget()

    def _prog_tick(self, n, total):
        self.prog_bar["value"] = n
        self.prog_lbl.config(text=t("status_icons_loading", n=n, total=total))
        if n >= total:
            self._icon_done = True
            self.status_var.set(t("status_icons_loaded"))
            self.after(2000, self._hide_progress)

    def _open_json(self):
        path = filedialog.askopenfilename(title=t("dlg_select_json"),
            filetypes=[("JSON","*.json"),("All files","*.*")])
        if not path: return
        try: self.games = load_json(path)
        except Exception as e:
            messagebox.showerror(t("dlg_error_load"), str(e)); return
        self.avail_cache.clear(); self._last_game = None; self._icon_done = False
        save_settings({"last_json": path})
        self._populate(self.games)
        self.status_var.set(t("status_loaded", name=os.path.basename(path)))
        self.count_var.set(t("n_games", n=len(self.games)))
        self._preload_icons()

    def _game_iid(self, g):
        return f"{g['title_id']}_{hashlib.md5(g['pkg_url'].encode()).hexdigest()[:8]}"

    def _row_values(self, g):
        c = self.avail_cache.get(g["title_id"])
        estado = (t("status_available") if c is True else
                  t("status_unavailable") if c is False else t("status_not_checked"))
        return ("🖼",g["name"],g["title_id"],g["version"],estado,g["min_fw"],g["region"],g["size"])

    def _row_tag(self, g):
        c = self.avail_cache.get(g["title_id"])
        return ("AVAIL",) if c is True else ("UNAVAIL",) if c is False else ()

    def _populate(self, games):
        for r in self.tree.get_children(): self.tree.delete(r)
        for g in games:
            self.tree.insert("","end", values=self._row_values(g),
                             iid=self._game_iid(g), tags=self._row_tag(g))

    def _filter(self):
        q = self.search_var.get().lower()
        filtered = [g for g in self.games if not q or
                    q in g["name"].lower() or q in g["title_id"].lower()
                    or q in g["region"].lower()]
        self._populate(filtered)
        self.count_var.set(t("n_games", n=len(filtered)))

    def _sort(self, col):
        rows = [(self.tree.set(iid,col),iid) for iid in self.tree.get_children()]
        rows.sort(key=lambda x: x[0].lower())
        for i,(_,iid) in enumerate(rows): self.tree.move(iid,"",i)

    def _preload_icons(self):
        urls = [g["cover_url"] for g in self.games if g["cover_url"]]
        if not urls: return
        total = len(urls); self._show_progress(total)
        lock  = threading.Lock(); done = [0]
        def cb(fut):
            with lock: done[0] += 1; n = done[0]
            # add_done_callback fires from the worker thread, not the main
            # thread, so we must use a thread-safe queue instead of after().
            self._icon_queue.put(n)
        for url in urls: self._executor.submit(download_icon, url).add_done_callback(cb)
        self._poll_icon_queue(total)

    def _poll_icon_queue(self, total):
        """Drain the icon-progress queue from the main thread (safe for Tkinter)."""
        try:
            while True:
                n = self._icon_queue.get_nowait()
                self._prog_tick(n, total)
        except Exception:
            pass
        if not getattr(self, "_icon_done", False):
            self.after(50, lambda: self._poll_icon_queue(total))

    def _sel_game(self):
        sel = self.tree.selection()
        if not sel: return None
        iid = sel[0]
        for g in self.games:
            if self._game_iid(g) == iid: return g
        return None

    def _on_sel(self, _=None):
        g = self._sel_game()
        if g: self._last_game = g; self._show_detail(g)

    def _show_detail(self, g):
        cover = g["cover_url"]
        if PIL_AVAILABLE and cover:
            def load():
                photo = self._load_photo(cover, (280,280))
                self.after(0, lambda: self._set_img(photo))
            threading.Thread(target=load, daemon=True).start()
        else:
            self.det_img.config(image="", text="🎮", font=("Consolas",42),
                                fg="#333", compound="center")
            self.det_img.image = None

        c = self.avail_cache.get(g["title_id"])
        estado = (t("status_available") if c is True else
                  t("status_unavailable") if c is False else t("status_not_checked"))
        lines = [
            (t("detail_name"),     g["name"]),
            (t("detail_title_id"), g["title_id"]),
            (t("detail_version"),  g["version"]),
            (t("detail_fw"),       g["min_fw"]),
            (t("detail_region"),   g["region"]),
            (t("detail_size"),     g["size"]),
            (t("detail_status"),   estado),
        ]
        max_k = max(len(k) for k,_ in lines)
        txt   = "\n".join(f"{k:<{max_k}}   {v}" for k,v in lines)
        self.det_txt.config(state="normal")
        self.det_txt.delete("1.0","end")
        self.det_txt.insert("end", txt)
        self.det_txt.config(state="disabled")

    def _load_photo(self, url, size):
        if url in self.icon_cache: return self.icon_cache[url]
        path = os.path.join(ICONS_CACHE_DIR, _url_to_filename(url))
        if not os.path.exists(path): path = download_icon(url)
        if not path or not os.path.exists(path): return None
        try:
            img   = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.icon_cache[url] = photo; return photo
        except Exception: return None

    def _set_img(self, photo):
        if photo:
            self.det_img.config(image=photo, text="", compound="center")
            self.det_img.image = photo
        else:
            self.det_img.config(image="", text="🎮", font=("Consolas",42), fg="#333")
            self.det_img.image = None

    def _show_ctx(self, event):
        row = self.tree.identify_row(event.y)
        if row: self.tree.selection_set(row); self.ctx_menu.post(event.x_root, event.y_root)

    def _show_updates(self):
        g = self._sel_game()
        if not g: messagebox.showinfo("", t("msg_select_game")); return
        UpdatesWindow(self, g)

    def _check_avail_sel(self):
        g = self._sel_game()
        if not g: return
        tid = g["title_id"]
        if tid in self.avail_cache:
            r = (t("status_available") if self.avail_cache[tid]
                 else t("status_unavailable"))
            messagebox.showinfo("", t("cache_avail", tid=tid, result=r)); return
        self._do_check_avail(g)

    def _do_check_avail(self, g):
        tid = g["title_id"]; iid = self._game_iid(g)
        self.status_var.set(t("status_checking_avail", tid=tid))
        try:
            v = list(self.tree.item(iid,"values")); v[4] = t("status_checking")
            self.tree.item(iid, values=v, tags=("pend",))
        except tk.TclError: pass
        def worker():
            ok = check_url_available(g["pkg_url"])
            self.avail_cache[tid] = ok
            self.after(0, lambda: self._set_avail(g, iid, ok))
        self._executor.submit(worker)

    def _set_avail(self, g, iid, ok):
        lbl = t("status_available") if ok else t("status_unavailable")
        tag = ("AVAIL",) if ok else ("UNAVAIL",)
        try:
            v = list(self.tree.item(iid,"values")); v[4] = lbl
            self.tree.item(iid, values=v, tags=tag)
        except tk.TclError: pass
        self.status_var.set(t("status_avail_result", tid=g["title_id"], result=lbl))
        if self._last_game and self._last_game["title_id"] == g["title_id"]:
            self._show_detail(g)

    def _download(self):
        g = self._sel_game()
        if not g: messagebox.showinfo("", t("msg_select_game")); return
        if not g["pkg_url"]: messagebox.showwarning("", t("msg_no_url")); return
        dest = get_download_dir(g["title_id"])
        if messagebox.askyesno(t("confirm_dl_title"),
                               t("confirm_dl_body",name=g["name"],size=g["size"],dest=dest)):
            DownloadWindow(self, g)

    def _open_download_mgr(self):
        mgr = DownloadManager.get_or_create(self)
        mgr.deiconify(); mgr.lift()

    def _open_dl_folder(self):
        base = get_active_base()
        if not base.exists():
            messagebox.showinfo("", t("msg_no_folder", path=base)); return
        if os.name=="nt": os.startfile(str(base))
        else: webbrowser.open(f"file://{base}")

    def _open_orbis(self):
        g = self._sel_game()
        if g: webbrowser.open(ORBIS_URL.format(tid=g["title_id"].upper()))

    def _set_download_path(self):
        global _session_download_base
        nueva = filedialog.askdirectory(title=t("dlg_select_folder"),
                                        initialdir=str(get_active_base()))
        if nueva:
            _session_download_base = Path(nueva)
            save_settings({"download_path": str(_session_download_base)})
            self.status_var.set(t("status_path_changed", path=_session_download_base))
            messagebox.showinfo(t("msg_path_updated_title"),
                                t("msg_path_updated_body", path=_session_download_base))

    def _reset_download_path(self):
        global _session_download_base
        _session_download_base = None
        save_settings({"download_path": None})
        self.status_var.set(t("status_path_reset", path=DOWNLOADS_BASE))
    
    def _open_ftp_config(self):
        """Abrir ventana de configuración FTP"""
        FTPConfigWindow(self)
        # Actualizar menú después de cerrar ventana
        self.after(100, self._build_menu)

    def _clear_icon_cache(self):
        self.icon_cache.clear(); removed = 0
        if os.path.isdir(ICONS_CACHE_DIR):
            for f in os.listdir(ICONS_CACHE_DIR):
                try: os.remove(os.path.join(ICONS_CACHE_DIR,f)); removed += 1
                except Exception: pass
        self.status_var.set(f"Icon cache cleared ({removed} files).")

    def _clear_avail_cache(self):
        self.avail_cache.clear()
        for iid in self.tree.get_children():
            v = list(self.tree.item(iid,"values"))
            if len(v)>=5: v[4]=t("status_not_checked"); self.tree.item(iid,values=v,tags=())
        self.status_var.set("Status cache cleared.")

    def _update_pw_status(self):
        """Actualiza la barra de estado mientras el browser arranca."""
        if _pw_pool._ready.is_set():
            ready_path = t("status_ready", path=str(_session_download_base or DOWNLOADS_BASE))
            if _pw_pool._ok:
                self._set_status(t("pw_ready", status=ready_path))
            else:
                self._set_status(t("pw_unavail", status=ready_path))
        else:
            self._set_status(t("pw_starting"))
            self.after(400, self._update_pw_status)

    def _set_status(self, msg):
        """Actualiza la barra de estado inferior."""
        try:
            self.status_var.set(msg)
        except Exception:
            pass


    def _restore_sash(self, pos):
        pass  # paned replaced by place() layout; sash no longer used

    def _auto_load_json(self, path):
        try:
            self.games = load_json(path)
            self.avail_cache.clear(); self._last_game = None; self._icon_done = False
            self._populate(self.games)
            self.status_var.set(t("status_loaded", name=os.path.basename(path)))
            self.count_var.set(t("n_games", n=len(self.games)))
            self._preload_icons()
        except Exception:
            pass

    def _send_local_pkg(self):
        """Browse for a local .pkg file and upload it via FTP."""
        if not FTP_CONFIG.get("enabled"):
            messagebox.showwarning(t("ftp_send_title"), t("ftp_not_enabled"))
            return
        path = filedialog.askopenfilename(
            title=t("ftp_browse_pkg"),
            filetypes=[(t("ftp_pkg_filetype"), "*.pkg"), (t("ftp_all_files"), "*.*")]
        )
        if not path:
            return
        # Show the download manager and add the local→FTP transfer
        mgr = DownloadManager.get_or_create(self)
        mgr.deiconify(); mgr.lift()
        mgr.add_local_ftp_transfer(path)

    def _on_close(self):
        self._bg_running = False
        # Save window state
        try:
            geo = self.geometry()
            save_settings({"geometry": geo})
        except Exception:
            pass
        self._executor.shutdown(wait=False, cancel_futures=True)
        if PLAYWRIGHT_AVAILABLE:
            _pw_pool.stop()
        self.destroy()


if __name__ == "__main__":
    if not PIL_AVAILABLE:
        print("[WARNING] Pillow not installed - covers disabled.  pip install Pillow")
    if not REQUESTS_AVAILABLE:
        print("[WARNING] requests not installed - using urllib.   pip install requests")
    app = FPKGiManager()
    app.protocol("WM_DELETE_WINDOW", app._on_close)
    app.mainloop()
