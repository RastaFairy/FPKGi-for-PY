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
APP_VERSION     = "5.11"
ICONS_CACHE_DIR = "icons_cache"
MAX_WORKERS     = 8

APP_DIR        = Path(os.path.abspath(__file__)).parent
DOWNLOADS_BASE = APP_DIR / "descargas"
LANG_DIR       = APP_DIR / "lang"

_session_download_base = None

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
    "dl_cancelled_msg": "  Cancelled.",
    "dl_open_folder": "  Open folder",
    "dl_starting": "Starting...", "dl_close": "Close",
    "dl_update_label": "{name}  [Update v{ver}]",
    "dl_game_label": "{name}  v{ver}",
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
        _cb("  Iniciando Chromium headless…")
        html = _pw_fetch(page_url, timeout_ms=40000)
        _cb("  Procesando respuesta…")

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
                err = (f"HTML recibido ({len(html):,} bytes) pero sin parches. "
                       "El título probablemente no tiene actualizaciones en OrbisPatches.")
                return {"patches": [], "total": 0, "game_name": game_name,
                        "blocked": False, "playwright_used": True, "error": err}

    # ── Nivel 2: requests ──────────────────────────────────────────
    _cb("  Probando requests (sin JS)…")
    game_name, patches = _fetch_orbis_requests(tid, page_url)
    err = "" if patches else (
        "Sin resultados. " +
        ("" if PLAYWRIGHT_AVAILABLE else
         "Instala Playwright para habilitar JS rendering:\n"
         "  pip install playwright\n"
         "  python -m playwright install chromium")
    )
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

def download_pkg(pkg_url, title_id, name, progress_cb=None, done_cb=None):
    dest_dir = get_download_dir(title_id)
    raw_name = os.path.basename(urllib.parse.urlparse(pkg_url).path).split("?")[0]
    try: raw_name = urllib.parse.unquote(raw_name)
    except Exception: pass
    if not raw_name or not raw_name.lower().endswith(".pkg"):
        raw_name = f"{title_id}_{re.sub(r'[^a-zA-Z0-9._-]','_',name)}.pkg"
    dest_path = dest_dir / raw_name

    def _worker():
        try:
            if REQUESTS_AVAILABLE:
                with requests.get(pkg_url, headers=WEB_HEADERS,
                                  stream=True, timeout=30) as r:
                    r.raise_for_status()
                    total = int(r.headers.get("content-length", 0))
                    done  = 0
                    with open(dest_path, "wb") as f:
                        for chunk in r.iter_content(1<<20):
                            if chunk:
                                f.write(chunk); done += len(chunk)
                                if progress_cb: progress_cb(done, total)
            else:
                req = urllib.request.Request(pkg_url, headers=WEB_HEADERS)
                with urllib.request.urlopen(req, timeout=30) as r:
                    total = int(r.headers.get("Content-Length", 0))
                    done  = 0
                    with open(dest_path, "wb") as f:
                        while True:
                            chunk = r.read(1<<20)
                            if not chunk: break
                            f.write(chunk); done += len(chunk)
                            if progress_cb: progress_cb(done, total)
            if done_cb: done_cb(True, str(dest_path))
        except Exception as e:
            if done_cb: done_cb(False, str(e))
    threading.Thread(target=_worker, daemon=True).start()


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

    def _fetch(self):
        def _progress(msg):
            try:
                self.after(0, lambda m=msg: self.st_lbl.config(text=m))
            except Exception:
                pass

        def worker():
            # Si el pool aún está arrancando, avisar al usuario
            if PLAYWRIGHT_AVAILABLE and not _pw_pool._ready.is_set():
                _progress("  ⏳ Esperando que Chromium esté listo…")
            try:
                result = fetch_orbis_full(self.game["title_id"],
                                          _progress_cb=_progress)
                self.after(0, lambda: self._show(result))
            except Exception as e:
                self.after(0, lambda: self.st_lbl.config(
                    text=f"  Error inesperado: {str(e)[:100]}", fg="#ffaa00"))
        threading.Thread(target=worker, daemon=True).start()

    def _show(self, result):
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
            status = f"  Sin datos ({engine})"
            self.st_lbl.config(text=status, fg="#ff6666")

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
                         text="  Este título no tiene parches en OrbisPatches.",
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
        if key in self._downloads: return
        self._downloads[key] = self._make_card(key, game, url, update_info)
        self._update_count(); self._start(key, game, url)

    def _make_card(self, key, game, url, update_info):
        card = tk.Frame(self.content, bg="#16213e", padx=10, pady=8)
        card.pack(fill="x", padx=4, pady=3)
        tk.Frame(card, bg="#0f3460", height=1).pack(fill="x", pady=(0,6))
        lbl_text = (t("dl_update_label", name=game["name"],
                      ver=update_info.get("version","?")) if update_info
                    else t("dl_game_label", name=game["name"], ver=game.get("version","?")))
        tk.Label(card, text=f"  {lbl_text}", font=("Consolas",10,"bold"),
                 bg="#16213e", fg="#00d4ff").pack(anchor="w")
        tk.Label(card, text=f"  {get_download_dir(game['title_id'])}",
                 font=("Consolas",8), bg="#16213e", fg="#556").pack(anchor="w")
        prog = ttk.Progressbar(card, orient="horizontal", mode="determinate",
                               style="TProgressbar")
        prog.pack(fill="x", pady=(4,2))
        info_lbl = tk.Label(card, text=t("dl_starting"), font=("Consolas",9),
                            bg="#16213e", fg="#888")
        info_lbl.pack(anchor="w")
        bf  = tk.Frame(card, bg="#16213e"); bf.pack(anchor="w", pady=(4,0))
        btn = tk.Button(bf, text=t("dl_cancel"), bg="#2a2a40", fg="#ccc",
                        relief="flat", font=("Consolas",9), padx=6, pady=2, cursor="hand2")
        btn.pack(side="left")
        d = {"card":card,"prog":prog,"info_lbl":info_lbl,"btn":btn,
             "cancelled":False,"done":False}
        def _cancel():
            d["cancelled"] = True
            btn.config(text=t("dl_cancelled"), state="disabled")
            info_lbl.config(text=t("dl_cancelled_msg"), fg="#ff6666")
            d["done"] = True; self._update_count()
        btn.config(command=_cancel)
        return d

    def _start(self, key, game, url):
        d = self._downloads[key]
        def pcb(done, total):
            if d["cancelled"]: raise InterruptedError()
            if total > 0:
                pct = done/total*100
                self.after(0, lambda p=pct, dh=_bytes_to_human(done),
                                      th=_bytes_to_human(total): self._upd(key,p,dh,th))
        def dcb(ok, info):
            self.after(0, lambda: self._finish(key,ok,info))
        download_pkg(url, game["title_id"], game["name"], progress_cb=pcb, done_cb=dcb)

    def _upd(self, key, pct, dh, th):
        d = self._downloads.get(key)
        if not d or d["cancelled"]: return
        d["prog"]["value"] = pct
        d["info_lbl"].config(text=f"  {dh} / {th}  ({pct:.1f}%)", fg="#aaa")

    def _finish(self, key, ok, info):
        d = self._downloads.get(key)
        if not d or d["cancelled"]: return
        d["done"] = True
        if ok:
            d["prog"]["value"] = 100
            d["info_lbl"].config(text=f"  {info}", fg="#00ff99")
            d["btn"].config(text=t("dl_open_folder"),
                            command=lambda: self._open_folder(info),
                            bg="#0f3460", fg="#00d4ff", state="normal")
        else:
            d["info_lbl"].config(text=f"  {info[:90]}", fg="#ff4444")
            d["btn"].config(text=t("dl_close"), state="normal",
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
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.geometry("1440x800"); self.minsize(960,600)
        self.configure(bg="#1a1a2e")
        self.games = []; self.icon_cache = {}; self.avail_cache = {}
        self._executor  = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self._icon_queue = queue.Queue()
        self._icon_done  = False
        self._last_game = None
        self._apply_styles(); self._build_menu(); self._build_ui()
        # Arrancar el browser Chromium en segundo plano al inicio
        if PLAYWRIGHT_AVAILABLE:
            _pw_pool.start()
            self._update_pw_status()

    def _apply_styles(self):
        s = ttk.Style(self); s.theme_use("clam")
        s.configure(".", background="#1a1a2e", foreground="#e0e0e0", font=("Consolas",10))
        s.configure("Treeview", background="#16213e", foreground="#e0e0e0",
                    fieldbackground="#16213e", rowheight=28)
        s.configure("Treeview.Heading", background="#0f3460", foreground="#00d4ff",
                    font=("Consolas",10,"bold"), relief="flat")
        s.map("Treeview", background=[("selected","#0f3460")],
              foreground=[("selected","#ffffff")])
        s.configure("TScrollbar", background="#16213e", troughcolor="#0f0f1a", arrowcolor="#555")
        s.configure("TProgressbar", troughcolor="#0f0f1a", background="#00d4ff", thickness=5)
        s.configure("SB.TLabel", background="#0f0f1a", foreground="#666", font=("Consolas",9))

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
        mb.add_cascade(label=t("menu_downloads"), menu=md)
        ml = tk.Menu(mb, tearoff=0, **ko)
        for code in AVAILABLE_LANGS:
            ml.add_command(
                label=f"{'✓ ' if code==_current_lang else '   '}{get_lang_name(code)}",
                command=lambda c=code: self._change_lang(c))
        mb.add_cascade(label=t("menu_language"), menu=ml)

    def _build_ui(self):
        top = tk.Frame(self, bg="#16213e", pady=8, padx=12); top.pack(fill="x")
        tk.Label(top, text=APP_TITLE, font=("Consolas",17,"bold"),
                 bg="#16213e", fg="#00d4ff").pack(side="left")
        tk.Label(top, text=f" v{APP_VERSION}", font=("Consolas",9),
                 bg="#16213e", fg="#444").pack(side="left", pady=6)
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

        sf = tk.Frame(self, bg="#1a1a2e", pady=4, padx=10); sf.pack(fill="x")
        tk.Label(sf, text="🔍", bg="#1a1a2e", fg="#555", font=("Consolas",11)).pack(side="left")
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

        self.paned = tk.PanedWindow(self, orient="horizontal",
                                    bg="#111122", sashwidth=4, sashrelief="flat")
        self.paned.pack(fill="both", expand=True, padx=10, pady=(4,0))

        tree_wrap = tk.Frame(self.paned, bg="#1a1a2e")
        self.paned.add(tree_wrap, minsize=520)
        cols = ("icon","name","title_id","version","estado","min_fw","region","size")
        self.tree = ttk.Treeview(tree_wrap, columns=cols, show="headings", selectmode="browse")
        col_cfg = {
            "icon":("col_icon",44),"name":("col_name",270),"title_id":("col_title_id",100),
            "version":("col_version",75),"estado":("col_status",120),"min_fw":("col_fw",75),
            "region":("col_region",65),"size":("col_size",80),
        }
        for col,(lk,w) in col_cfg.items():
            self.tree.heading(col, text=t(lk), command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, minwidth=36)
        vsb = ttk.Scrollbar(tree_wrap, orient="vertical",  command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",fill="y"); hsb.pack(side="bottom",fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("AVAIL",   foreground="#00ff99")
        self.tree.tag_configure("UNAVAIL", foreground="#ff6666")
        self.tree.tag_configure("pend",    foreground="#555555")
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)
        self.tree.bind("<Button-3>",         self._show_ctx)
        self.tree.bind("<Double-1>",         lambda e: self._show_updates())

        det = tk.Frame(self.paned, bg="#16213e")
        self.paned.add(det, minsize=360)
        self._lbl_details = tk.Label(det, text=t("lbl_details"),
                                     font=("Consolas",10,"bold"),
                                     bg="#16213e", fg="#00d4ff", pady=8)
        self._lbl_details.pack()
        self.det_img = tk.Label(det, bg="#16213e", text="🎮",
                                font=("Consolas",64), fg="#333")
        self.det_img.pack(pady=6)
        self.det_txt = tk.Text(det, bg="#16213e", fg="#ccc",
                               font=("Consolas",10), relief="flat",
                               state="disabled", wrap="word", height=10, width=40, bd=0)
        self.det_txt.pack(fill="both", expand=True, padx=10)
        bst2 = dict(relief="flat", font=("Consolas",10,"bold"), pady=5, cursor="hand2")
        self._btn_dl_pkg = tk.Button(det, text=t("btn_download_pkg"),
            command=self._download, bg="#003d5c", fg="#00d4ff", **bst2)
        self._btn_dl_pkg.pack(fill="x", padx=10, pady=(6,2))
        self._btn_updates = tk.Button(det, text=t("btn_view_updates"),
            command=self._show_updates, bg="#2d1b00", fg="#ff9944", **bst2)
        self._btn_updates.pack(fill="x", padx=10, pady=(0,2))
        self._btn_check = tk.Button(det, text=t("btn_check_avail"),
            command=self._check_avail_sel, bg="#0a2a0a", fg="#00cc66", **bst2)
        self._btn_check.pack(fill="x", padx=10, pady=(0,8))

        ko = dict(bg="#16213e", fg="#e0e0e0",
                  activebackground="#0f3460", activeforeground="#00d4ff")
        self.ctx_menu = tk.Menu(self, tearoff=0, **ko)
        self.ctx_menu.add_command(label=t("ctx_view_updates"), command=self._show_updates)
        self.ctx_menu.add_command(label=t("ctx_check_avail"),  command=self._check_avail_sel)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label=t("ctx_download"), command=self._download)
        self.ctx_menu.add_command(label=t("ctx_orbis"),    command=self._open_orbis)

        sb = tk.Frame(self, bg="#0f0f1a", pady=3); sb.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value=t("status_ready", path=get_active_base()))
        self.count_var  = tk.StringVar(value=t("n_games", n=0))
        ttk.Label(sb, textvariable=self.status_var, style="SB.TLabel").pack(side="left",  padx=8)
        ttk.Label(sb, textvariable=self.count_var,  style="SB.TLabel").pack(side="right", padx=8)

    def _change_lang(self, code):
        set_lang(code); self._build_menu()
        self._lbl_details.config(text=t("lbl_details"))
        self._btn_open_json.config(text=t("btn_open_json"))
        self._btn_downloads.config(text=t("btn_downloads"))
        self._btn_dl_path.config(text=t("btn_dl_path"))
        self._btn_open_dl.config(text=t("btn_open_dl_folder"))
        self._btn_dl_pkg.config(text=t("btn_download_pkg"))
        self._btn_updates.config(text=t("btn_view_updates"))
        self._btn_check.config(text=t("btn_check_avail"))
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
        self.prog_outer.pack(fill="x", padx=10, pady=(0,2), before=self.paned)

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
            self.status_var.set(t("status_path_changed", path=_session_download_base))
            messagebox.showinfo(t("msg_path_updated_title"),
                                t("msg_path_updated_body", path=_session_download_base))

    def _reset_download_path(self):
        global _session_download_base
        _session_download_base = None
        self.status_var.set(t("status_path_reset", path=DOWNLOADS_BASE))

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
            if _pw_pool._ok:
                self._set_status("  🟢 Chromium listo  |  " +
                                 t("status_ready", path=str(_session_download_base or DOWNLOADS_BASE)))
            else:
                self._set_status("  ⚠ Chromium no disponible — usando requests  |  " +
                                 t("status_ready", path=str(_session_download_base or DOWNLOADS_BASE)))
        else:
            self._set_status("  ⏳ Iniciando Chromium headless…")
            self.after(400, self._update_pw_status)

    def _set_status(self, msg):
        """Actualiza la barra de estado inferior."""
        try:
            self.status_var.set(msg)
        except Exception:
            pass

    def _on_close(self):
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
