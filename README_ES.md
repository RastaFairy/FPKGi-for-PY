<div align="center">

# 🎮 FPKGi Manager — Edición Python

**Gestor completo de catálogos de juegos FPKG para PS4, desarrollado en Python**

[![Version](https://img.shields.io/badge/versión-5.11--FTP-blue?style=flat-square)](https://github.com/RastaFairy/FPKGi-for-PY)
[![Python](https://img.shields.io/badge/python-3.8%2B-yellow?style=flat-square)](https://python.org)
[![Licencia](https://img.shields.io/badge/licencia-MIT-green?style=flat-square)](LICENSE)
[![Plataforma](https://img.shields.io/badge/plataforma-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)]()

*Concepto original por [Bucanero](https://github.com/bucanero) (PSP Homebrew) · Port PS4/PS5 por [ItsJokerZz](https://github.com/ItsJokerZz) · Adaptación Python por [RastaFairy](https://github.com/RastaFairy)*

</div>

---

## 📖 ¿Qué es esto?

**FPKGi Manager** es una aplicación de escritorio que te permite explorar, buscar, organizar y descargar archivos **FPKG (Fake PKG)** de juegos para PlayStation 4 desde tu PC.

### 🤔 ¿Qué es un FPKG?

Un FPKG (Fake Package) es un formato utilizado en consolas PS4 modificadas que permite instalar copias de seguridad de juegos. Estos archivos siguen el mismo formato `.pkg` de Sony, pero se distribuyen a través de listas y archivos de terceros. Esta herramienta **no genera ni crea FPKGs** — solo te ayuda a **gestionar catálogos existentes** que ya posees o cargas a través de un archivo JSON.

### 📋 ¿Qué es un GAMES.json / archivo de catálogo?

FPKGi (la aplicación homebrew para PS4 de ItsJokerZz) utiliza un formato JSON especial para almacenar listas de juegos. Esta herramienta Python lee esos mismos archivos JSON, permitiéndote gestionar tu biblioteca de juegos en el PC con una interfaz gráfica moderna.

---

## ✨ Características (v5.11-FTP — Última versión)

- 📂 **Doble formato JSON** — lee tanto el formato `FPKGi DATA dict` como el formato `PS4PKGInstaller packages list`
- 🌐 **Integración OrbisPatches** — obtiene el historial real de parches (versión, tamaño, notas) mediante Playwright con bypass de Cloudflare
- 🔍 **Verificación de disponibilidad** — comprueba si una URL de descarga sigue activa (HTTP HEAD)
- ⬇️ **Descargas en paralelo** — hasta 8 descargas simultáneas sin bloquear la interfaz
- 📡 **Transferencia FTP** — envía PKGs directamente a tu PS4 por red local (nuevo en 5.11-FTP)
- 🌍 **Interfaz multiidioma** — inglés integrado + 8 idiomas adicionales mediante archivos `lang/*.json`
- 🖼️ **Carátulas** — precarga en paralelo con caché persistente en disco
- 🤖 **Traducción de notas de parche** — traduce las notas de actualización a cualquier idioma vía la API de Claude (opcional)
- 🖥️ **Multiplataforma** — funciona en Windows, Linux y macOS
- 🔎 **Búsqueda y filtrado avanzados** — por nombre, Title ID, región, versión, tamaño
- ↕️ **Ordenación por columna** — haz clic en cualquier encabezado de columna para ordenar la lista

---

## 🚀 Instalación y Requisitos

### Requisitos previos

- **Python 3.8 o superior** → [Descargar Python](https://python.org/downloads/)
- **pip** (incluido con Python)

### Paso 1 — Instalar dependencias Python

```bash
pip install Pillow requests playwright
```

### Paso 2 — Instalar Chromium (para OrbisPatches / bypass de Cloudflare)

```bash
python -m playwright install chromium
```

### Paso 3 — (Opcional) Configurar la clave de API de Claude para traducción de parches

```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

# Linux / macOS
export ANTHROPIC_API_KEY=sk-ant-...
```

### Paso 4 — Ejecutar la aplicación

```bash
python fpkgi_manager_with_ftp.py
```

---

## 📡 Configuración FTP (v5.11-FTP)

La función FTP te permite transferir archivos PKG directamente a tu PS4 sin necesidad de copiarlos a un USB.

1. En tu PS4, asegúrate de tener un servidor FTP activo (por ejemplo, mediante GoldHEN u otro)
2. En FPKGi Manager, ve a **Archivo → Configuración FTP**
3. Introduce la IP local de tu PS4 (p. ej. `192.168.1.210`), el puerto (`2121` por defecto) y la ruta remota (`/data/pkg`)
4. Haz clic en **Probar conexión** para verificar
5. Activa el modo FTP y las descargas se enviarán directamente a tu PS4

La configuración FTP se guarda automáticamente en `ftp_config.json` en la carpeta de la aplicación.

---

## 📂 Estructura del Proyecto

```
FPKGi-for-PY/
├── fpkgi_manager_with_ftp.py   ← Script principal (v5.11-FTP, actual)
├── ftp_config.json              ← Configuración FTP (se genera automáticamente)
├── lang/                        ← Archivos de idioma (JSON)
│   ├── es.json                  ← Español
│   ├── fr.json                  ← Francés
│   └── ...
├── icons_cache/                 ← Caché de carátulas (se genera automáticamente)
└── descargas/                   ← Carpeta de descargas (se genera automáticamente)
    └── CUSAXXXXX/
        └── juego.pkg
```

---

## 🗂️ Formatos JSON Compatibles

### Formato 1 — FPKGi DATA dict

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

### Formato 2 — PS4PKGInstaller packages list

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

## 🕹️ Cómo Usar

1. **Inicia** la aplicación con `python fpkgi_manager_with_ftp.py`
2. **Abre un JSON** — usa Archivo → Abrir JSON o el botón de la barra de herramientas para cargar tu catálogo
3. **Navega por la lista** — busca por nombre o Title ID, filtra por región, ordena por cualquier columna
4. **Selecciona un juego** — haz clic en una fila para ver la carátula y los detalles en el panel derecho
5. **Verifica disponibilidad** — clic derecho → "Verificar disponibilidad" para comprobar si la URL de descarga funciona
6. **Ver actualizaciones** — clic derecho → "Ver actualizaciones" para consultar el historial de parches en OrbisPatches
7. **Descargar** — clic derecho → "Descargar PKG" o usa el botón; elige carpeta local o FTP a la PS4
8. **Gestionar descargas** — Archivo → Gestionar descargas para ver el progreso, cancelar o abrir los archivos descargados

---

## 🌍 Soporte de Idiomas

El idioma de la interfaz se puede cambiar desde el menú **Idioma** en tiempo de ejecución (sin necesidad de reiniciar). El inglés está integrado por defecto. Los idiomas adicionales se cargan desde `lang/<código>.json`.

Para añadir un nuevo idioma, copia `lang/es.json`, traduce todos los valores y guárdalo como `lang/<tu_código>.json`. El nuevo idioma aparecerá automáticamente en el menú.

---

## 📜 Historial de Versiones

### v1.0 — Los Cimientos
- Interfaz gráfica tkinter con tema oscuro (azul marino + acento rojo)
- Carga y visualización de `GAMES.json` (formato DATA dict)
- Búsqueda por nombre o Title ID, filtro por región, opciones de ordenación
- Visualización de carátulas (descarga en tiempo real, sin caché)
- Panel de detalles del juego con metadatos
- Abrir URL del PKG en el navegador
- Agregar / editar / eliminar juegos
- Interfaz de scraper de Archive.org (stub — no funcional aún)
- Panel de estadísticas (total de juegos, tamaño, desglose por región)

### v2.0 — Descargas y Caché
- **Descargas reales de PKG** a una carpeta local `downloads/`
- **Caché de iconos en disco** (`icons_cache/`) — las carátulas se guardan localmente y se reutilizan
- Herramientas de gestión de caché (limpiar caché de iconos desde el menú)
- Gestión de carpeta de descargas (abrir desde el menú)
- Indicador de progreso de descarga

### v3.3 — Integración PSN y SerialStation
- **Integración con PSN Update XML API** — obtiene versión oficial, tamaño y firmware mínimo mediante solicitudes firmadas con HMAC
- **Integración con SerialStation** — obtiene changelogs de parches e información de títulos
- Traducciones integradas de notas de parche (inglés → español) para frases comunes
- ThreadPoolExecutor para llamadas API en paralelo (hasta 8 workers)
- Fallback elegante si `requests` o `Pillow` no están instalados
- Constantes configurables `ICONS_CACHE_DIR` y `MAX_WORKERS`

### v4.2 — OrbisPatches y Doble Formato
- **Soporte de doble formato JSON**: tanto `DATA dict` (FPKGi) como `packages list` (PS4PKGInstaller)
- Eliminada la dependencia de SerialStation — reemplazada por **OrbisPatches** para historial completo de parches
- **Descargas de PKG** organizadas por Title ID: `./descargas/CUSAXXXXX/*.pkg`
- API HMAC de PSN mantenida para verificación de datos oficiales
- API de fallback de OrbisPatches (`/api/patch.php`) cuando la página principal no está disponible
- Cabeceras de descarga simuladas como navegador (UA de Chromium)
- Rutas relativas a `APP_DIR` — funciona independientemente del directorio de trabajo

### v5.4 — Interfaz Multiidioma
- **Interfaz en 9 idiomas** — inglés integrado, idiomas adicionales cargados desde `lang/*.json`
- El idioma puede cambiarse en tiempo de ejecución desde el menú de Idioma
- Todas las cadenas de UI pasan por una función de traducción `t(key)`
- Las claves faltantes caen silenciosamente al inglés
- Ruta de descarga configurable por sesión
- Barra de progreso para la precarga de iconos

### v5.6 — Playwright y Bypass de Cloudflare
- **Integración de Playwright** — Chromium headless para hacer bypass a Cloudflare en OrbisPatches
- Estrategia de dos niveles: Playwright (preferido) → fallback con requests
- Endpoint de OrbisPatches actualizado a `api/patch.php` (basado en JSON)
- Ahora requiere `python -m playwright install chromium`
- Inyección de JS anti-detección (oculta `navigator.webdriver`)

### v5.8 — Parser HTML Verificado
- Estructura HTML de OrbisPatches re-verificada contra dump en vivo
- Parser actualizado para el nuevo layout del DOM: `patch-wrapper > patch-container > patch-link`
- Extracción más fiable de versión, tamaño y notas de parche
- Heurísticas mejoradas de detección de Cloudflare

### v5.9 — Pool de Playwright Asíncrono
- **Pool de navegador Playwright persistente** — el navegador permanece activo durante toda la sesión
- Sin arranque en frío por consulta — búsquedas de parches dramáticamente más rápidas
- El bucle asyncio corre en un hilo daemon dedicado
- Fetch thread-safe mediante sincronización basada en queue

### v5.10 — Arquitectura Asíncrona Estable
- Pool asíncrono reescrito con gestión correcta del event loop de asyncio
- API limpiada: `_pw_pool.start()` / `_pw_pool.fetch(url)` / `_pw_pool.stop()`
- El ciclo de vida ahora es gestionado automáticamente por la clase principal de la app
- Manejo de errores mejorado y recuperación de timeouts

### v5.11 — Traducción via API de Claude
- **Integración con la API de Claude** — las notas de parche pueden traducirse a cualquier idioma en tiempo real
- Bloque de créditos formal añadido al encabezado (Bucanero / ItsJokerZz / RastaFairy)
- Licencia MIT declarada en el encabezado del archivo
- Campos de metadatos `__version__`, `__author__`, `__license__`, `__repository__`
- Soporte para la variable de entorno `ANTHROPIC_API_KEY`

### v5.11-FTP — Transferencia FTP a PS4 *(Actual)*
- **Cliente FTP integrado** — transfiere PKGs directamente a tu PS4 por red local
- Diálogo de configuración FTP: host, puerto, usuario, contraseña, ruta remota, modo pasivo, timeout
- Botón de **Probar conexión** — verifica el FTP antes de descargar
- `ftp_config.json` — configuración FTP persistente guardada en disco
- Enrutamiento de descargas: carpeta local o FTP según el estado de FTP habilitado
- Subida en streaming con callback de progreso — progreso de transferencia en tiempo real mostrado en el gestor de descargas
- Creación automática del directorio remoto si no existe
- Toggle de FTP en el menú principal

---

## 🙏 Créditos

| Rol | Persona |
|---|---|
| Concepto original FPKGi (PSP) | [Bucanero](https://github.com/bucanero) |
| Port PS4/PS5 de FPKGi | [ItsJokerZz](https://github.com/ItsJokerZz) |
| Adaptación Python y todas las versiones | [RastaFairy](https://github.com/RastaFairy) |

---

## ⚠️ Aviso Legal

Esta herramienta está destinada **únicamente para uso educativo y personal**. No aloja, distribuye ni genera ningún archivo de juego. Los usuarios son los únicos responsables de lo que hagan con el software y deben cumplir las leyes de su país. Los autores no aprueban la piratería.

---

## 📄 Licencia

Licencia MIT — consulta [LICENSE](LICENSE) para más detalles.
