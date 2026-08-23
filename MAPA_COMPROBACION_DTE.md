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

## Notas (no declarar en la interfaz pública)
- Para el usuario final de DescargarFacturas, se describe como "**verificación con Hacienda**" (no "API").
- La comprobación multi-país se integra por país, como se hizo con El Salvador; cada país puede requerir ajustes del endpoint/parámetros de su consulta pública.
