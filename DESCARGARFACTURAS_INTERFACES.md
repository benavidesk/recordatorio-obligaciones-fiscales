# 🧾 DescargarFacturas — Interfaces y Funcionalidad (guía de referencia)

**Complementa:** skill `descargar-facturas-estructura` (que mapea dónde están los archivos).
**Este doc explica QUÉ hace cada variante/interfaz** y su modelo de uso.
**Fecha de revisión:** 2026-08-23

## Variantes (interfaces) y su propósito

| Variante | Archivo principal | Qué hace | Modelo |
|---|---|---|---|
| **Sesiones** | `src/descargar_facturas.py` (GUI `_gui.pyw`) | Descarga DTEs por **sesión de Thunderbird** (una cuenta de correo por sesión), organiza por mes. | Cuenta por cliente (sesión) |
| **Clientes** | `src/descargar_facturas_clientes_gui.pyw` | Un correo con **facturas de varios clientes**, organiza en **carpeta por cliente** (`base_out/<cliente>`). | Un correo → varios clientes |
| **Unificado** | `src/descargar_facturas_unificado.py` (+ GUI `_unificado.pyw`) | Versión que combina/enlaza la funcionalidad de sesiones y clientes en una sola app. | Unificado |
| **CTK ClientGUIDs** | `src/gui_clientes_ctk.py`, `src/gui_unificado_ctk.py` | Versiones con **interfaz CustomTkinter (CTK)** — interfaz moderna en vez de tkinter estándar. | Variantes CTK |

## Funcionalidad clave en **Sesiones** (la principal)

- **Descarga de DTEs (facturas) de Hacienda** — desde el correo/sesión que el contador usa.
- **Verificación con Hacienda** — comprueba la autenticidad del DTE en el portal público de Hacienda (MSJ: "verificación con Hacienda", NO "API").
- **Organización por mes / por cliente** — los archivos se clasifican.
- **Segregación de no relacionados** — los que no son del cliente van a `no_relacionado/00-Desconocido` (receptor/emisor define el cliente).
- **Confrontación con Hacienda** — solo si el país = El Salvador.
- **Licenciamiento** — software con licencia por hardware; `Activador.spec` genera el activador; clave privada/pública PEM, registro en `backup_registry.db`.

## Interfaces de apoyo

| Módulo | Función |
|---|---|
| `src/calendario_fiscal_sv.py` + `calendario_tributario_2026.ics/.json` | Calendario fiscal SV → exporta a `.ics` (importable en Google Calendar/Outlook) |
| `src/license_*.py` (crypto/validator) + `license_generator.py` | Emisión y validación de licencias |
| `src/activador.py` | Código del activador (para obtener licencia) |
| `src/hardware_fingerprint.py` | Huella de hardware para el licenciamiento |
| `src/registro_db.py` + `registro.db` | Registro de activaciones |
| `launcher.py` | Lanzador multi-variante (elige cuál cargar) |

## Configuraciones por país
- `configs/config_local.json` + `config_<pais>.json` (SV, GT, ...) — define parámetros por país.
- **Pais El Salvador** → activa la confrontación/verificación con Hacienda.

## Notas (decisiones de producto)
- **No declarar en la interfaz que el software está hecho con Python** (solo si piden descargar archivos). Texto público: "verificación con Hacienda".
- En la GUI CTK (modo clientes), **las sesiones SIEMPRE se toman de Thunderbird**, pero se organizan en carpeta por cliente.
- El software es **de pago** ($150, contadores salvadoreños), con licencia por hardware y registro.

## Pendiente / plan (ver también MAPA_COMPROBACION_DTE.md)
- Ampliar la **comprobación de DTEs multi-país** (El Salvador ya; México confirmado; Guatemala/CR/RD probables) — ver documento de mapa.
