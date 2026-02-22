# 🎮 FPKGi Manager — Edición Python

<p align="center">
  <img src="https://img.shields.io/badge/versión-5.12--FTP-00D4FF" />
  <img src="https://img.shields.io/badge/python-3.9%2B-yellow" />
  <img src="https://img.shields.io/badge/plataforma-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" />
  <img src="https://img.shields.io/badge/licencia-MIT-green" />
</p>

<p align="center">
  Gestor multiplataforma de escritorio para bibliotecas de juegos PS4 en formato Fake-PKG.<br>
  Navega tu catálogo, consulta notas de parche en OrbisPatches, verifica enlaces de descarga<br>
  y envía PKGs directamente a tu PS4 vía FTP — todo en una sola interfaz de tema oscuro.
</p>

> 🤖 ¿Buscas la **app Android**? → [FPKGi-A-](https://github.com/RastaFairy/FPKGi-A-)

---

## ✨ Características

| Función | Descripción |
|---------|-------------|
| 📂 **Doble formato JSON** | Compatible con el formato dict de FPKGi y el formato list de PS4PKGInstaller |
| 🔍 **OrbisPatches** | Historial completo de parches con Playwright (Chromium headless, bypass de Cloudflare) |
| 📡 **Transferencia FTP** | Envía PKGs directamente a tu PS4/PS5 por red local — sin USB, sin copia intermedia |
| ⬇️ **Descargas paralelas** | Hasta 8 descargas simultáneas de PKGs con progreso en tiempo real |
| ✅ **Verificación de disponibilidad** | Comprobación HTTP HEAD por entrada — estado verde/rojo por juego |
| 🌍 **9 idiomas** | DE · ES · FR · IT · JA · KO · RU · ZH · EN (cargados desde `lang/*.json`) |
| 🤖 **Traducción IA** | Notas de parche traducidas en tiempo real vía API de Anthropic Claude (opcional) |
| 🖼️ **Caché de iconos** | Precarga paralela con caché persistente en disco — las portadas sobreviven al reinicio |
| 🎨 **Fondo animado** | Gradiente animado estilo PS4 con símbolos △○×□ flotantes |
| 💾 **Persistencia de sesión** | Geometría de ventana, último JSON, posición de panel e idioma guardados automáticamente |

---

## 📦 Requisitos

| Paquete | Versión | Uso |
|---------|---------|-----|
| Python | ≥ 3.9 | Intérprete |
| Pillow | ≥ 9.0 | Imágenes de icono / portadas |
| requests | ≥ 2.28 | Descargas HTTP y verificación de disponibilidad |
| playwright | ≥ 1.40 | Renderizado JavaScript de OrbisPatches |

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### Opcional — Traducción IA de notas de parche

```bash
# Linux / macOS
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-...
```

---

## 🚀 Inicio rápido

```bash
git clone https://github.com/RastaFairy/FPKGi-for-PY.git
cd FPKGi-for-PY

pip install -r requirements.txt
python -m playwright install chromium

python fpkgi_manager_with_ftp.py
```

En Windows también puedes hacer doble clic en **`START.bat`**.

---

## 📡 Configuración FTP

1. Copia `ftp_config.json.example` → `ftp_config.json`
2. Edita los valores según tu red:

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

3. O configúralo desde **Configuración → Configuración FTP** en la app.

Servidores FTP compatibles con PS4:
- **GoldHEN FTP Server** *(recomendado)*
- PS4FTP Homebrew
- Cualquier servidor FTP en el puerto 2121

> Guía completa: [`GUIA_FTP_COMPLETA.txt`](GUIA_FTP_COMPLETA.txt)

---

## 📁 Estructura del proyecto

```
.
├── fpkgi_manager_with_ftp.py   # App principal — edición FTP (un solo fichero, 2800+ líneas)
├── fpkgi_manager.py            # Edición estándar (sin FTP)
├── ftp_config.json             # Tu configuración FTP (ignorado por git)
├── ftp_config.json.example     # Plantilla — segura para el repositorio
├── requirements.txt
├── START.bat                   # Lanzador rápido para Windows
├── lang/                       # Ficheros de traducción de la UI
│   ├── de.json   es.json   fr.json   it.json
│   └── ja.json   ko.json   ru.json   zh.json
├── icons_cache/                # Caché persistente de iconos (auto-generada)
├── descargas/                  # Carpeta de descarga de PKGs por defecto
└── .github/
    ├── workflows/
    │   ├── ci.yml              # Lint + compilación EXE para Windows (Python 3.9 / 3.11 / 3.13)
    │   └── release.yml         # Compilación y publicación al crear un tag
    └── ISSUE_TEMPLATE/
        ├── bug_report.md
        └── feature_request.md
```

---

## 🏗️ Compilar EXE para Windows

```powershell
pip install pyinstaller
pyinstaller --onedir --windowed --name FPKGiManager `
  --add-data "lang;lang" `
  --add-data "ftp_config.json.example;." `
  fpkgi_manager_with_ftp.py
```

Resultado: `dist/FPKGiManager/`

---

## 🤝 Contribuir

1. Haz un fork y crea una rama para tu función.
2. Ejecuta `flake8 fpkgi_manager_with_ftp.py --max-line-length=120` y corrige todos los errores E9/F.
3. Abre un Pull Request hacia `main`.

---

## 📜 Créditos

| Rol | Nombre |
|-----|--------|
| Concepto original (PSP Homebrew) | [Bucanero](https://github.com/bucanero) |
| Puerto PS4 / PS5 | ItsJokerZz |
| Adaptación y evolución en Python | RastaFairy |

---

## 📄 Licencia

[MIT](LICENSE) © RastaFairy
