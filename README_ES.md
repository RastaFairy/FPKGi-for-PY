<div align="center">

# 🎮 FPKGi Manager

**Gestor de juegos PS4 FPKG con integración de OrbisPatches**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green)
![Versión](https://img.shields.io/badge/Versión-5.11-orange)
![Estado](https://img.shields.io/badge/Estado-Mantenido-brightgreen)

</div>

---

## 📋 Tabla de contenidos

- [✨ Características principales](#características-principales)
- [🚀 Inicio rápido](#inicio-rápido)
- [📦 Requisitos e instalación](#requisitos-e-instalación)
- [📁 Estructura del proyecto](#estructura-del-proyecto)
- [🎯 Guía de uso](#guía-de-uso)
- [🔧 Configuración](#configuración)
- [🌍 Idiomas soportados](#idiomas-soportados)
- [🔎 Sistema de parches OrbisPatches](#sistema-de-parches-orbispatches)
- [⬇️ Descargas y gestor](#descargas-y-gestor)
- [🌐 Manejo de Cloudflare](#manejo-de-cloudflare)
- [📝 Registro de cambios](#registro-de-cambios)
- [⚠️ Descargo de responsabilidad](#descargo-de-responsabilidad)

---

## ✨ Características principales

### 🎛️ Gestión de juegos
- **Soporte dual en JSON** — Compatible con dos formatos:
  - Formato `FPKGi` (diccionario `DATA`)
  - Formato `PS4PKGInstaller` (lista `packages`)
- **Catálogo visual** — Tabla interactiva con portadas, título, versión y estado
- **Búsqueda en tiempo real** — Filtra por nombre, TITLE_ID o región
- **Ordenamiento** — Haz clic en cualquier columna para ordenar

### 🔄 Integración OrbisPatches
- **Scraper avanzado** — Extrae metadatos directamente desde orbispatches.com:
  - Versión del parche
  - Requisito de firmware
  - Tamaño del archivo
  - Fecha de creación
  - Notas de parches
- **Renderizado con Chromium** — Ejecuta JavaScript para eludir Cloudflare
- **Fallback automático** — Si Playwright no está disponible, usa requests estándar
- **Indicador de compatibilidad** — Muestra 🟢 (compatible) o 🔴 (incompatible) según tu FW

### ✅ Verificación de disponibilidad
- **Comprobación HTTP** — Verifica que las URLs de descarga estén activas
- **Caché por sesión** — Almacena resultados para evitar re-búsquedas
- **Indicadores visuales** — Estado en tiempo real (DISPONIBLE/NO DISPONIBLE/NO VERIFICADO)

### ⬇️ Gestor de descargas
- **Descargas paralelas** — Descarga múltiples archivos simultáneamente
- **Barras de progreso** — Visualización en tiempo real del progreso de cada archivo
- **Ruta configurable** — Cambia la carpeta de descargas sin afectar la configuración
- **Gestor flotante** — Ventana independiente para monitorear descargas
- **Recuperación** — Los archivos se descargan al directorio `./download/{TITLE_ID}/`

### 🎨 Interfaz multilingüe
- **8 idiomas adicionales** — Cargados dinámicamente desde `lang/*.json`
  - 🇬🇧 English · 🇪🇸 Español · 🇮🇹 Italiano · 🇩🇪 Deutsch · 🇫🇷 Français
  - 🇷🇺 Русский · 🇨🇳 中文 · 🇰🇷 한국어 · 🇯🇵 日本語
- **Fallback automático** — Las claves faltantes retroceden a inglés
- **Cambio en tiempo real** — Toda la interfaz se actualiza sin reiniciar

### 🖼️ Caché de iconos
- **Precarga paralela** — Descarga todas las portadas automáticamente
- **Barra de progreso** — Visualiza el progreso de la precarga
- **Caché persistente** — Los iconos se guardan localmente en `icons_cache/`
- **Limpieza manual** — Borra la caché desde el menú

### 🌐 Traducción de notas
- **Traducción automática** — Convierte notas de parches al idioma seleccionado
- **API Claude** — Usa la API de Anthropic para traducción de calidad
- **Caché de traducciones** — Almacena traducciones para acceso rápido
- **Fallback elegante** — Si la traducción falla, muestra el original

---

## 🚀 Inicio rápido

### Instalación minimal (sin Playwright)
```bash
# Clonar o descargar el repositorio
git clone https://github.com/RastaFairy/FPKGi-for-PY.git
cd FPKGi-for-PY

# Instalar dependencias básicas
pip install Pillow requests

# Ejecutar la aplicación
python fpkgi_manager.py
```

### Instalación completa (con Playwright para JS rendering)
```bash
# Instalar todas las dependencias
pip install Pillow requests playwright

# Descargar el navegador Chromium
python -m playwright install chromium

# Ejecutar la aplicación
python fpkgi_manager.py
```

---

## 📦 Requisitos e instalación

### Requisitos del sistema
```
Python 3.8 o superior
Sistema operativo: Windows, Linux o macOS
Conexión a Internet (para acceder a OrbisPatches)
```

### Dependencias opcionales

#### 🖼️ Pillow (Recomendado)
```bash
pip install Pillow>=9.0.0
```
**Uso:** Para mostrar las portadas de los juegos en la interfaz.
**Fallback:** Sin Pillow, se muestra un emoji 🎮 en lugar de la imagen.

#### 🌐 Requests (Recomendado)
```bash
pip install requests>=2.28.0
```
**Uso:** Para realizar peticiones HTTP más rápidas y mantener cookies de sesión.
**Fallback:** Sin requests, usa `urllib` de la librería estándar (más lento).

#### 🎬 Playwright (Opcional pero recomendado)
```bash
pip install playwright>=1.40.0
python -m playwright install chromium
```
**Uso:** Para ejecutar JavaScript y renderizar contenido dinámico de OrbisPatches.
**Fallback:** Sin Playwright, intenta con requests básico (puede fallar si Cloudflare bloquea).

---

## 📁 Estructura del proyecto

```
fpkgi_manager.py          ← Aplicación principal (archivo único)
├── GUI Tkinter
├── Sistema de idiomas
├── Scraper OrbisPatches
├── Gestor de descargas
└── Pool Playwright persistente

lang/                     ← Archivos de traducción
├── es.json            (Español)
├── it.json            (Italiano)
├── de.json            (Alemán)
├── fr.json            (Francés)
├── ru.json            (Ruso)
├── zh.json            (Chino)
├── ko.json            (Coreano)
└── ja.json            (Japonés)

download/               ← Carpeta de descargas (auto-creada)
└── {TITLE_ID}/       (Juegos organizados por ID)

icons_cache/            ← Caché de portadas (auto-creada)
└── *.png             (Imágenes descargadas)

config.json            ← Configuración (opcional)
```

---

## 🎯 Guía de uso

### 1️⃣ Cargar un catálogo JSON

#### Método 1: Menú
```
Archivo → Abrir JSON...  (o Ctrl+O)
```

#### Método 2: Botón en barra de herramientas
```
Haz clic en "  Open JSON"
```

**Formatos soportados:**

**Formato FPKGi:**
```json
{
  "DATA": {
    "https://ejemplo.com/juego.pkg": {
      "title_id": "CUSA12345",
      "name": "Mi Juego",
      "version": "1.05",
      "region": "EU",
      "size": 45000000000,
      "min_fw": "9.00",
      "cover_url": "https://..."
    }
  }
}
```

**Formato PS4PKGInstaller:**
```json
{
  "packages": [
    {
      "title_id": "CUSA12345",
      "name": "Mi Juego",
      "version": "1.05",
      "region": "EU",
      "size": "45GB",
      "system_version": "9.00",
      "pkg_url": "https://ejemplo.com/juego.pkg",
      "icon_url": "https://..."
    }
  ]
}
```

### 2️⃣ Explorar el catálogo

**Búsqueda rápida:**
- Escribe en el campo 🔍 para filtrar por:
  - Nombre del juego
  - TITLE_ID (ej: CUSA12345)
  - Región (ej: EU, US, JP)

**Ordenar columnas:**
- Haz clic en cualquier encabezado de columna para ordenar

**Ver detalles:**
- Selecciona un juego en la tabla
- El panel derecho muestra:
  - Portada del juego
  - Nombre, TITLE_ID, versión
  - Firmware requerido, región, tamaño
  - Estado de disponibilidad

### 3️⃣ Verificar disponibilidad de descargas

#### Verificar un juego
```
1. Selecciona el juego en la tabla
2. Botón "  Check availability" o menú contextual
3. Espera a que se complete la verificación
4. El estado cambiará a DISPONIBLE ✅ o NO DISPONIBLE ❌
```

#### Verificar todos
```
Menú Descargas → Verificar disponibilidad (TODO: no está en v5.11)
```

### 4️⃣ Descargar un juego

#### Método 1: Panel de detalles
```
1. Selecciona el juego
2. Haz clic en "  Download PKG"
3. Confirma la descarga
```

#### Método 2: Menú contextual
```
1. Haz clic derecho en el juego
2. Selecciona "  Download PKG"
3. Confirma la descarga
```

#### Método 3: Doble clic
```
Doble clic en el juego abre el gestor de descargas
```

**Progreso de descarga:**
- El Gestor de Descargas muestra:
  - Nombre del juego y versión
  - Carpeta de destino
  - Barra de progreso en tiempo real
  - Bytes descargados / total
  - Porcentaje completado
- Al terminar, opción para abrir la carpeta

### 5️⃣ Ver actualizaciones disponibles

#### Abrir ventana de actualizaciones
```
1. Selecciona un juego
2. Haz clic en "  View Updates"
3. O doble clic en el juego
4. O menú contextual → "  View updates"
```

**Información mostrada:**
- ✅ Versiones disponibles en OrbisPatches
- 📊 Firmware requerido (🟢 compatible / 🔴 incompatible)
- 📦 Tamaño del archivo
- 📅 Fecha de creación
- 📝 Notas del parche (traducidas automáticamente)
- ⭐ Indicador de versión más reciente
- ← Indicador de tu versión actual

---

## 🔧 Configuración

### Cambiar carpeta de descargas

#### Método 1: Menú
```
Descargas → Cambiar ruta de descarga...
```

#### Método 2: Botón en barra
```
Haz clic en "  DL Path"
```

**Nota:** El cambio solo afecta a la sesión actual. Al cerrar y reiniciar, vuelve a `./download/`

### Resetear a carpeta por defecto
```
Descargas → Resetear a ruta por defecto
```

### Limpiar caché

**Caché de iconos:**
```
Caché → Limpiar caché de iconos
```
Borra todas las portadas descargadas. Se descargarán nuevamente al abrir un JSON.

**Caché de verificación:**
```
Caché → Limpiar caché de estado
```
Borra los resultados de verificación de disponibilidad. Los juegos volverán a mostrar "NO VERIFICADO".

### Cambiar idioma

```
Idioma → [Selecciona el idioma deseado]
```

La interfaz se actualiza inmediatamente. El cambio no se guarda (se reinicia en inglés).

---

## 🌍 Idiomas soportados

| Código | Idioma | Archivo | Estado |
|--------|--------|---------|--------|
| en | English | Integrado | ✅ |
| es | Español | lang/es.json | ✅ |
| it | Italiano | lang/it.json | ✅ |
| de | Alemán | lang/de.json | ✅ |
| fr | Francés | lang/fr.json | ✅ |
| ru | Ruso | lang/ru.json | ✅ |
| zh | Chino | lang/zh.json | ✅ |
| ko | Coreano | lang/ko.json | ✅ |
| ja | Japonés | lang/ja.json | ✅ |

### Añadir un idioma nuevo

1. Copiar un archivo existente:
   ```bash
   cp lang/es.json lang/pl.json
   ```

2. Editar `lang/pl.json` y traducir todos los valores:
   ```json
   {
     "lang_name": "Polski",
     "menu_file": "Plik",
     "menu_exit": "Wyjść",
     ...
   }
   ```

3. Agregar el código a `AVAILABLE_LANGS` en `fpkgi_manager.py`:
   ```python
   AVAILABLE_LANGS = ["en", "es", "it", "de", "fr", "ru", "zh", "ko", "ja", "pl"]
   ```

4. Reiniciar la aplicación — el idioma aparecerá en el menú

**Nota:** Las claves faltantes usan automáticamente la versión en inglés.

---

## 🔎 Sistema de parches OrbisPatches

### Cómo funciona

1. **Entrada:** Selecciona un juego e haz clic en "  View Updates"

2. **Navegación:** La aplicación accede a `https://orbispatches.com/{TITLE_ID}`

3. **Renderizado:** 
   - Si Playwright está disponible: ejecuta JavaScript con Chromium headless
   - Si no: intenta descargar HTML con requests
   - Si hay Cloudflare: muestra un aviso

4. **Parsing:** Extrae parches usando patrones regex de la estructura HTML real

5. **Datos extraídos:**
   - Versión del parche
   - Firmware requerido
   - Tamaño del archivo
   - Fecha de creación
   - Notas en HTML

6. **Presentación:**
   - Muestra parches ordenados por versión (más reciente arriba)
   - Marca la versión más nueva con ⭐
   - Marca tu versión actual con ←
   - Muestra compatibilidad de firmware (🟢/🔴)

### Estructura HTML verificada

```html
<div class="mb-4 patch-wrapper">
  <div class="patch-container [latest]">
    <a class="patch-link" data-contentver="01.04">
      <!-- Tamaño -->
      <div class="col-auto text-end">7.2GB</div>
      <!-- Firmware -->
      <div class="col-auto text-end">8.50</div>
      <!-- Fecha -->
      <div class="col-auto text-end">2021-06-09</div>
    </a>
    <!-- Notas (si existen) -->
    <a class="changeinfo-preview" 
       data-patchnotes-charcount="54">Notas del parche</a>
  </div>
</div>
```

### Limitaciones y soluciones

**Problema:** OrbisPatches usa Cloudflare
**Solución 1:** Instala Playwright para eludir bot-protection
**Solución 2:** Abre manualmente en tu navegador

**Problema:** El título no tiene parches en OrbisPatches
**Solución:** La ventana muestra "Sin datos"

**Problema:** Cambios en estructura HTML
**Solución:** Ejecuta `python diagnostico_orbis.py CUSA12345` para ver HTML actual

---

## ⬇️ Descargas y gestor

### Gestor de descargas

**Características:**
- Descargas paralelas (hasta 8 simultáneas)
- Barra de progreso individual por archivo
- Pausa/cancelación
- Ventana flotante independiente
- Historial de descargas en la sesión

**Interfaz:**
```
[Gestor de Descargas]
├── Mi Juego v1.05
│   ├── Destino: ./download/CUSA12345/
│   ├── [=================] 45.2GB / 50GB (90%)
│   └── Botón: Abrir carpeta
├── Otro Juego v2.00
│   ├── [==] 5GB / 15GB (33%)
│   └── Botón: Cancelar
```

### Estructura de carpetas

```
./download/
├── CUSA00001/
│   ├── juego_v1.05.pkg
│   └── juego_v2.00.pkg
├── CUSA00002/
│   └── otro_juego.pkg
```

### Cambiar carpeta de descargas

**Por sesión:**
```
Descargas → Cambiar ruta de descarga...
```

**Permanente:**
Edita la variable `DOWNLOADS_BASE` en el código o crea un script de lanzamiento.

---

## 🌐 Manejo de Cloudflare

### Detección automática

La aplicación detecta si Cloudflare bloquea la solicitud mediante patrones:
- `"challenge-form"`
- `"just a moment"`
- `"cf-browser-verification"`
- `"ddos protection by"`

### Soluciones

**Opción 1: Instalar Playwright (Recomendado)**
```bash
pip install playwright
python -m playwright install chromium
```

**Opción 2: Abrir manualmente**
- La app te proporciona el enlace a orbispatches.com
- Haz clic en el botón "🌐 OrbisPatches"
- Se abre en tu navegador (Cloudflare te dejará pasar)

**Opción 3: Usar un proxy/VPN**
- Configura un proxy SOCKS5 (requiere modificación del código)

### Pool Playwright persistente

La aplicación mantiene un browser Chromium abierto durante toda la sesión:

**Ventajas:**
- Evasión de Cloudflare consistente
- Reutilización de cookies
- Inicio rápido de consultas posteriores

**Desventajas:**
- Consume ~100-200 MB de RAM
- Requiere ~500 MB de espacio en disco para Chromium

**Gestión automática:**
- Se inicia al abrir la aplicación
- Se cierra al cerrar la aplicación
- Fallback automático si hay problemas

---

## 🔧 Opciones avanzadas

### Variables de entorno

```bash
# Cambiar número de workers de descarga
export FPKGI_WORKERS=16

# Cambiar ruta de caché de iconos
export FPKGI_ICONS_CACHE="./mis_iconos/"

# Habilitar modo debug
export FPKGI_DEBUG=1
```

### Traducción de notas de parches

**Requisito:** Variable de entorno `ANTHROPIC_API_KEY`

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python fpkgi_manager.py
```

La aplicación traducirá automáticamente las notas de parches al idioma seleccionado.

### Diagnosticar problemas con OrbisPatches

Script de diagnóstico (crear archivo `diagnostico_orbis.py`):

```python
#!/usr/bin/env python3
import sys
from fpkgi_manager import fetch_orbis_full

if len(sys.argv) < 2:
    print("Uso: python diagnostico_orbis.py CUSA12345")
    sys.exit(1)

tid = sys.argv[1]
result = fetch_orbis_full(tid, lambda m: print(m))

print("\n=== RESULTADO ===")
print(f"Total parches: {result['total']}")
print(f"Bloqueado por Cloudflare: {result['blocked']}")
print(f"Playwright utilizado: {result['playwright_used']}")
if result.get('error'):
    print(f"Error: {result['error']}")
for p in result['patches']:
    print(f"  - v{p['version']}: FW {p['firmware']}, {p['size']}")
```

---

## 📝 Registro de cambios

### v5.11 (Actual)
- **Chromium Headless corregido** — HTML + JS coinciden con OrbisPatches en vivo
- **Gestor de descargas mejorado** — Mejor manejo de cancelaciones
- **UI refinada** — Mejor feedback visual

### v5.4
- **Scraper corregido** — Selectores HTML actualizados para OrbisPatches actual:
  - Versión desde atributo `data-contentver`
  - Size/FW/Date desde `<div class="col-auto text-end">` en orden
  - Notas desde `<a class="changeinfo-preview">` cuando existe
- **Sistema de idiomas refactorizado** — Base en inglés, otros en `lang/*.json`
- **Actualización instantánea** — Panel de detalle se actualiza al cambiar idioma
- **Cookies persistentes** — Sesión `requests` compartida para Cloudflare

### v5.3
- **OrbisPatches como única fuente** — API XML de PSN eliminada
- **Detección de Cloudflare** — Aviso al usuario
- **Interfaz mejorada** — Mejor visual

### v5.2
- **Parser JSON dual** — Soporte DATA dict + packages list
- **Gestor de descargas paralelas** — ThreadPoolExecutor

### v5.1
- **Precarga de iconos** — Con barra de progreso
- **Ruta de descarga por sesión** — Configurable sin tocar configuración

### v5.0
- **Lanzamiento público**

---

## ❓ Preguntas frecuentes

**P: ¿Dónde se descargan los juegos?**
R: En `./download/{TITLE_ID}/` por defecto. Puedes cambiar la carpeta con Descargas → Cambiar ruta.

**P: ¿Puedo descargar múltiples juegos a la vez?**
R: Sí, la aplicación descarga hasta 8 archivos simultáneamente.

**P: ¿Qué pasa si se interrumpe una descarga?**
R: Se cancela. Puedes intentar de nuevo sin perder el progreso (si el servidor soporta reanudación).

**P: ¿Necesito Playwright obligatoriamente?**
R: No, es opcional. Sin él, usa requests básico (menos seguro contra Cloudflare).

**P: ¿Puedo traducir a mi idioma?**
R: Sí, copia `lang/es.json` a `lang/xx.json`, traduce y reinicia.

**P: ¿Se guarda la configuración?**
R: Parcialmente — solo el idioma actual se recuerda (requiere código adicional para persistencia).

---

## ⚠️ Descargo de responsabilidad

> **Esta herramienta es solo un gestor de metadatos. No descarga, aloja ni distribuye archivos de juegos.**
>
> - Lee datos de acceso público (OrbisPatches)
> - Genera URLs de descarga que tú verificas
> - Conecta directamente a servidores de origen
>
> **Úsala solo con contenido que tengas derecho legal a usar.**
>
> El autor NO es responsable de:
> - Daños a tu PS4 o sistema
> - Infracciones de copyright
> - Pérdida de datos
> - Cualquier otro problema

---

## 📞 Soporte y contribuciones

- **Issues:** GitHub Issues del repositorio
- **Contribuciones:** Pull Requests bienvenidas
- **Licencia:** MIT

---

## 🙏 Créditos e historia del proyecto

### Orígenes
Este proyecto es parte de una evolución multigeneracional de herramientas para gestionar juegos en dispositivos PlayStation:

- **Concepto original (2010s):** Bucanero - Creó el homebrew original PKGi para PSP, estableciendo la filosofía central de gestión unificada de catálogos de juegos.
- **Port a PS4/PS5 (2020s):** ItsJokerZz - Adaptó el concepto a consolas PlayStation modernas, llevando FPKGi a PS4 y PS5.
- **Edición multiplatforma en Python (2026):** -Porté la filosofía a Python, creando una aplicación de escritorio multiplataforma con características modernas como integración de Playwright, soporte multilingüe, y scraping de OrbisPatches.

### Filosofía
La idea central se mantiene consistente en todas las versiones: *una interfaz unificada e intuitiva para gestionar paquetes de juegos en PS4, facilitando a los usuarios organizar, verificar y descargar sus colecciones de juegos.*

### Agradecimientos
- Gracias a las comunidades de modding de PSP, PS4 y PS5
- OrbisPatches.com por proporcionar libremente información accesible sobre parches
- Todos los contribuidores y usuarios que reportan issues y sugieren mejoras

---

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/release/RastaFairy/FPKGi-for-PY.svg)](https://github.com/RastaFairy/FPKGi-for-PY/releases)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/downloads/)
[![GitHub Issues](https://img.shields.io/github/issues/RastaFairy/FPKGi-for-PY)](https://github.com/RastaFairy/FPKGi-for-PY/issues)
[![GitHub Stars](https://img.shields.io/github/stars/RastaFairy/FPKGi-for-PY)](https://github.com/RastaFairy/FPKGi-for-PY/stargazers)

**Creado con ❤️ para la comunidad PS4**
