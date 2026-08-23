# 📅 Recordatorio de Obligaciones Fiscales (multi-país)

Software de código abierto que lee una base de obligaciones fiscales por país y
te recuerda en automático los **vencimientos** (IVA, renta, ISSS/AFP, retenciones,
impuestos municipales, etc.). **¡No te vuelvas a perder una fecha y evita multas!**

## ✨ Características
- 🔔 **Recordatorios automáticos** de obligaciones que vencen (hoy, próximas, vencidas).
- 🌎 **Multi-país** desde el diseño: El Salvador primero, listo para agregar
  Guatemala, Honduras, etc. (solo se agrega un JSON, no se toca el código).
- 📂 **Base de documentos editable** (JSON por país): fácil de actualizar y de
  aportar/corregir por cualquier contador o profesional.
- 🆓 **Gratis** para quien lo necesite.

## 🚀 Cómo usar
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
│   └── obligaciones_sv.json    ← base de El Salvador (editable/contribuible)
├── recordatorios.py            ← el motor (lee la base y calcula vencimientos)
└── README.md
```

### Agregar un país nuevo
1. Crea `bases/obligaciones_<codigo>.json` (copia `_sv.json` como plantilla).
2. Llena las obligaciones y sus reglas de vencimiento del país.
3. Corre `python recordatorios.py --pais <CODIGO>`.
No se toca el código del motor.

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
- **19 países** con base lista para leer:
  - **América Hispana (16):** El Salvador · MH | Guatemala · SAT | Honduras · SAR | Nicaragua · DGI
    Panamá · DGI-MEF | Costa Rica · DGT | Rep. Dominicana · DGII | México · SAT
    Colombia · DIAN | Perú · SUNAT | Chile · SII | Argentina · ARCA
    Ecuador · SRI | Uruguay · DGI | Paraguay · SET | Bolivia · SIN
  - **América (no hispana, por su comunidad hispanohablante):** Estados Unidos · IRS (Form 1040)
  - **Europa (1):** España · AEAT
  - **África (1):** Guinea Ecuatorial · Ministerio de Hacienda
- **Notas:** Argentina: AFIP ahora se llama **ARCA** (2026). Venezuela y Cuba no incluidos
  por condiciones especiales. Guinea Ecuatorial: datos de referencia (fuentes locales limitadas).
- Datos validados con fuentes oficiales y calendarios 2026.
- Actualizado: 2026-08-23
