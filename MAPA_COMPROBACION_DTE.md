# 🗺️ Mapa de COMPROBACIÓN de DTE multi-país (guía para DescargarFacturas)

**Fecha:** 2026-08-23 · **Objetivo:** ampliar la "verificación con Hacienda"
(comprobación de autenticidad de un DTE) de El Salvador a otros países hispanos.

## Alcance (definido por el usuario)
- **NO** la descarga automática de DTEs (requiere credenciales por país, más complejo).
- **SÍ** la **COMPROBACIÓN / verificación** de que una factura es válida, vía **consulta pública** (como la de El Salvador), sin credenciales del contribuyente.

## Hallazgos confirmados (con Chrome, 2026-08-23)
| País | Herramienta de comprobación | URL / acceso | Estado |
|---|---|---|---|
| **El Salvador** | Consulta pública DTE | `admin.factura.gob.sv/prod/consultas/publica/simple/1` | ✅ **YA integrado** |
| **México** | **Verificación CFDI (SAT)** "Consulta por Folio Fiscal / archivo XML" | `verificacfdi.facturaelectronica.sat.gob.mx` | ✅ **CONFIRMADO** — consulta pública, misma lógica que SV |

## Probablemente integrables (sistema de facturación con consulta pública — requiere verificar URL exacta)
- **Guatemala** — Régimen FEL (portal SAT), apps `gob.sat.fel`. Tiene descarga/verificación de DTE; falta localizar la consulta pública exacta.
- **Costa Rica** — Hacienda (factura electrónica), tiene consulta de comprobantes.
- **Rep. Dominicana** — DGII (e-CF), tiene verificación.
- **Colombia / Perú / Chile** — algunos tienen consulta pública de comprobantes.

## Lo que es más difícil / incierto
- **Honduras, Nicaragua, Panamá, Ecuador, Uruguay, Paraguay, Bolivia, España, GQ, US** — madurez de facturación + consulta pública variable; revisar caso a caso.

## Conclusión practica
La **comprobación multi-país es viable y mucho más simple que la descarga**, porque (como se vio con México) es una **consulta pública sin credenciales**: solo se necesita el **folio / XML / datos mínimos del DTE**.
**Camino sugerido:** El Salvador (ya) → **México** (confirmado, mismo patrón) → Guatemala / Costa Rica / RD (verificar URL de consulta pública) → resto según demanda.

## Referencias de investigación
- México SAT Verificación CFDI: `https://verificacfdi.facturaelectronica.sat.gob.mx/`
- Guatemala SAT FEL: `https://portal.sat.gob.gt/portal/efactura/` (y apps `gob.sat.fel`)
- El Salvador DTE: `https://factura.gob.sv/`

## 🔑 Recurso CLAVE: esquema oficial FEL de Guatemala (XSD/catálogos)
- **Repo GitHub:** `https://github.com/notificacioneselectfel/Catalogo-FEL`
  - Descripción: "Esquema y catálogos - FEL" (16★, 3 forks, actualizado).
  - **Carpeta `XSD/`:** contiene los **esquemas XML oficiales** de los DTEs de Guatemala
    (facturas, anulaciones, complementos: Cambiaria, Exportaciones, Medios de Pago,
    Retenciones, Turismo Pasaje, Traslado Mercancías, etc.).
  - **Carpeta `Catalogos/`:** catálogos de códigos oficiales del FEL.
  - **Uso:** base para **validar/parsear** los XML de DTEs guatemaltecos al integrar la
    comprobación (como parte del desarrollo de Guatemala).
  - **Nota honesta:** es la especificación (XSD/catálogos), NO el endpoint de consulta
    pública de la SAT. La comprobación en sí requiere conectar el portal/consulta de la SAT
    (análogo a El Salvador).

## 📄 Documento Técnico Informático SAT FEL (v1.2) — especificación del API
- **Archivo local:** `C:\Users\benav\Downloads\Documento-Tecnico-Servicios-SAT.pdf`
- **Qué es:** "Documento Técnico Informático para **Certificadores** del Régimen FEL" (Acuerdo 13-2018, v1.2).
- **Endpoints de desarrollo (ambiente `desa`):**
  - Recepción DTE: `https://api.desa.sat.gob.gt/postFactura`
  - Anulación: `https://api.desa.sat.gob.gt/postAnulacionDTE`
  - Autenticación (token 60 min): `https://api.desa.sat.gob.gt/getToken`
  - Chequeo: `https://api.desa.sat.gob.gt/test`
  - XSD oficiales: `https://cat.desa.sat.gob.gt/xsd/alfa/GT_Documento-0.1.0.xsd` (+ complementos)
  - Catálogos JSON: `https://cat.desa.sat.gob.gt/catalogos/alfa` (frases, unidades, mensajes/errores)
- **Firma:** Xades-Bes, RSA + SHA-256; DTE = XML con firma de emisión + firma de certificación (UUID v4).
- **⚠️ NOTA HONESTA (importante):** este documento es para **CERTIFICADORES** (emisores autorizados),
  describe cómo **ENVIAR/emitir/anular DTEs a la SAT** (con credenciales de certificador que otorga la SAT).
  **NO** es la **comprobación/consulta** de validez de un DTE por un contador normal.
  **No contiene un endpoint público de "consulta de DTE"** para verificar autenticidad (lo que DescargarFacturas
  necesita para el modelo como El Salvador). Si se quisiera desarrollar un sistema de facturación/certificador
  en Guatemala, este doc es la referencia técnica; pero la **comprobación multi-país** requiere el endpoint de
  consulta pública (a localizar en el portal SAT).
- **Archivo clave para referencia futura** si se desarrolla emisión/certificación FEL.

## Notas (no declarar en la interfaz pública)
- Para el usuario final de DescargarFacturas, se describe como "**verificación con Hacienda**" (no "API").
- La comprobación multi-país se integra por país, como se hizo con El Salvador; cada país puede requerir ajustes del endpoint/parámetros de su consulta pública.
