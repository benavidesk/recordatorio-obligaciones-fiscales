#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APLICAR HORA DE AVISO PERSONALIZADA
Lee 'hora_aviso' (HH:MM) de config.json y recrea la tarea programada de Windows
'AvisosObligacionesFiscales' con esa hora (tarea diaria + inicio de sesion),
usando el modulo compartido scheduler_fiscal.

USO:  py -3.14 aplicar_hora.py
1. Edita config.json -> 'hora_aviso' (ej. "07:30", "12:00", "21:15").
2. Ejecuta este script (o 'aplicar_hora_avisos.bat').
3. La tarea se actualiza con la nueva hora.
"""
import json, os

import scheduler_fiscal

RUTA = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(RUTA, "config.json")


def _normalizar_hora(hora):
    """Devuelve 'HH:MM' valida desde 'hora', o None si es invalida."""
    hora = str(hora or "08:00").strip()
    if ":" in hora:
        hh, mm = hora.split(":")
    elif len(hora) == 4 and hora.isdigit():  # ej 0730
        hh, mm = hora[:2], hora[2:]
    else:
        hh, mm = "08", "00"
    try:
        hh = int(hh); mm = int(mm)
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise ValueError
    except ValueError:
        return None
    return f"{hh:02d}:{mm:02d}"


def main():
    try:
        with open(CONFIG, encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"❌ No pude leer config.json: {e}")
        return

    hora_final = _normalizar_hora(cfg.get("hora_aviso", "08:00"))
    if hora_final is None:
        print(f"❌ Hora inválida. Usa formato HH:MM (ej. 07:30, 12:00).")
        return

    try:
        scheduler_fiscal.aplicar(hora_final)
        print(f"✅ Hora de aviso configurada a las {hora_final} (diaria + inicio de sesión).")
        print(f"Tarea diaria: '{scheduler_fiscal.TAREA}'")
        print(f"Acceso directo de inicio de sesión: '{scheduler_fiscal.LNK_INICIO}'")
    except scheduler_fiscal.RutaInsegura as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ No se pudo programar el aviso: {e}")


if __name__ == "__main__":
    main()
