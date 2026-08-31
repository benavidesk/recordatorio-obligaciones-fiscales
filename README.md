# 📅 Recordatorio de Obligaciones Fiscales (multi-país)

Software de código abierto que lee una base de obligaciones fiscales por país y
te recuerda en automático los **vencimientos** (IVA, renta, ISSS/AFP, retenciones,
impuestos municipales, etc.). **¡No te vuelvas a perder una fecha y evita multas!**

## ✨ Características
- 🔔 **Recordatorios automáticos** de obligaciones que vencen (hoy, próximas, vencidas).
- 🌎 **19 países** listos: El Salvador, Guatemala, México, Colombia, España, EE. UU. y más.
- 🖥️ **Sin instalación de Python**: para el usuario final hay un **instalador (.exe)** que
  funciona en cualquier Windows, sin tener que instalar nada más.
- 🕐 **Aviso diario + aviso al iniciar sesión**: si la computadora estaba apagada a la
  hora programada, el aviso se muestra al encender la PC.
- 🔕 **Notificación siempre**: el programa avisa cada día (haya o no vencimientos próximos),
  para que sepas que revisó.
- 💾 **100% local**: tus datos no salen de tu computadora.
- 📂 **Base editable** (JSON por país): fácil de actualizar o aportar.
- 🆓 **Gratis** para quien lo necesite.

## 🚀 Instalación (usuario final, sin Python)

La forma más fácil es descargar el **instalador** desde la página o la última versión:

1. **Descarga** el instalador (`AvisosObligacionesFiscales-Setup-0.3.0.exe`) o el
   archivo `.zip` de la versión.
2. **Ejecútalo**: si usas el instalador, sigue los pasos; si usas el `.zip`, descomprímelo
   y haz doble clic en `AvisosObligacionesFiscales.exe`.
3. **Configura** tu país, la hora del aviso y los días de anticipo en la ventana que se abre.
4. **Listo**: el programa crea automáticamente el aviso diario y el aviso al iniciar la PC.

> El aviso diario lo hace `AvisosAutomaticos.exe` (incluido), que no necesita Python.

## 🚀 Uso para desarrolladores (con Python)

```bash
# Ver obligaciones y vencimientos de El Salvador (mes de agosto)
cd ObligacionesFiscales
python recordatorios.py --pais SV --mes 8 --anio 2026

# Ver del mes actual
python recordatorios.py --pais SV

# Ajustar el aviso a 10 días antes
python recordatorios.py --pais SV --aviso 10
```

## 🗂️ Estructura
```
ObligacionesFiscales/
├── bases/
│   ├── obligaciones_ar.json ... obligaciones_uy.json   ← 19 países (editable)
│   └── obligaciones_sv.json    ← base de El Salvador (editable/contribuible)
├── recordatorios.py            ← el motor (lee la base y calcula vencimientos)
├── avisos_automaticos.py       ← el aviso diario
├── util_fiscal.py              ← lógica compartida
├── AvisosAutomaticos.exe       ← exe del aviso (sin Python)
├── ejecutar_aviso_silencioso.vbs← lanzador silencioso (solo notificación)
└── README.md
```

### Agregar un país nuevo
1. Crea `bases/obligaciones_<codigo>.json` (copia `_sv.json` como plantilla).
2. Llena las obligaciones y sus reglas de vencimiento del país.
3. Corre `python recordatorios.py --pais <CODIGO>`.
No se toca el código del motor.

### Recordatorios automáticos (tarea programada diaria)
```bat
ejecutar_avisos.bat   → corre los avisos (tarea 'AvisosObligacionesFiscales', diaria)
py avisos_automaticos.py                    → revisa el país de config.json (por defecto)
py avisos_automaticos.py --pais all         → selector: todos los países
py avisos_automaticos.py --pais MX          → selector: un país específico
```
- Editá `config.json` (pais_por_defecto, dias_aviso) para cambiar el país que se avisa.
- El aviso automático **revisa el país configurado** (no todos), y `--pais all`/`--pais XX` es el **selector** para ampliar.
- **Notifica SIEMPRE** (haya o no vencimientos próximos) para que el usuario sepa que revisó.

## 🤝 Contribuye / Dona
- **¿Eres contador o profesional?** Puedes **corregir/ampliar** la base de tu país
  (agrega obligaciones que falten, ajusta fechas) y compartirla. El código es abierto.
- **¿El software te es útil?** Considera una **donación voluntaria** para apoyar su
  desarrollo y el de los demás países. No es obligatorio, pero cada aporte ayuda a
  que siga creciendo gratis para todos.

    **Donación:** (aquí iría tu enlace de donación / pago — PayPal, Pagost, o un
    QR; indícalo cuando lo tengas listo y lo colocamos)

## ⚠️ Nota importante
Las fechas pueden moverse si caen en fin de semana o asueto, y cambian cada año.
**Siempre verifica el calendario oficial anual** del Ministerio de Hacienda de tu
país. Este software es una guía de apoyo, no sustituye el asesoramiento contable.

## ✔️ Estado
- **19 países** con base lista (verificado: `listar_paises()` → 19):
  Argentina · ARCA | Bolivia · SIN | Chile · SII | Colombia · DIAN | Costa Rica · DGT
  República Dominicana · DGII | Ecuador · SRI | España · AEAT | Guinea Ecuatorial · MH
  Guatemala · SAT | Honduras · SAR | México · SAT | Nicaragua · DGI | Panamá · DGI-MEF
  Perú · SUNAT | Paraguay · SET | El Salvador · MH | Estados Unidos · IRS | Uruguay · DGI
- **Notas:** Argentina: AFIP ahora se llama **ARCA** (2026). Venezuela y Cuba no incluidos
  por condiciones especiales. Guinea Ecuatorial: datos de referencia (fuentes locales limitadas).
- Datos validados con fuentes oficiales y calendarios 2026.
- Actualizado: 2026-08-31
