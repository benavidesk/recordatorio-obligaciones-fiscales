#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APLICAR HORA DE AVISO PERSONALIZADA
Lee 'hora_aviso' (HH:MM) de config.json y recrea la tarea programada de Windows
'AppisosObligacionesFiscales' con esa hora, para que el aviso diario corra a la
hora que el usuario prefiera.

USO:  py -3.14 aplicar_hora.py
1. Edita config.json -> 'hora_aviso' (ej. "07:30", "12:00", "21:15").
2. Ejecuta este script (o 'aplicar_hora_avisos.bat').
3. La tarea se actualiza con la nueva hora.
"""
import json, os, subprocess

RUTA = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(RUTA, "config.json")
TAREA = "AvisosObligacionesFiscales"
TAREA_INICIO = "AvisosObligacionesFiscalesInicio"
BAT = os.path.join(RUTA, "ejecutar_avisos.bat")
EXE_AVISOS = os.path.join(RUTA, "AvisosAutomaticos.exe")

def comando_tarea():
    """Comando con --notificar para la tarea diaria/ inicio de sesion.
    Preferimos el exe de avisos (no depende de Python); si no, el .bat."""
    base = EXE_AVISOS if os.path.exists(EXE_AVISOS) else BAT
    return "\"{}\" --notificar".format(base)

def main():
    try:
        with open(CONFIG, encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"❌ No pude leer config.json: {e}")
        return

    hora = str(cfg.get("hora_aviso", "08:00")).strip()
    # normalizar a HH:MM
    if ":" in hora:
        hh, mm = hora.split(":")
    elif len(hora) == 4:  # ej 0730
        hh, mm = hora[:2], hora[2:]
    else:
        hh, mm = "08", "00"
    try:
        hh = int(hh); mm = int(mm)
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise ValueError
    except:
        print(f"❌ Hora '{hora}' invalida. Usa formato HH:MM (ej. 07:30, 12:00).")
        return

    hora_final = f"{hh:02d}:{mm:02d}"
    # schtasks usa la codificacion del sistema (cp1252/cp850), no utf-8 -> errors replace
    def run_silencioso(cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=False)
            out = r.stdout.decode("mbcs", errors="replace") if r.stdout else ""
            err = r.stderr.decode("mbcs", errors="replace") if r.stderr else ""
            return out, err
        except Exception:
            return "", ""

    # recrear las tareas (diaria + inicio de sesion) con la nueva hora
    run_silencioso(["schtasks", "/Delete", "/TN", TAREA, "/F"])
    run_silencioso(["schtasks", "/Delete", "/TN", TAREA_INICIO, "/F"])
    out, err = run_silencioso([
        "schtasks", "/Create", "/TN", TAREA,
        "/TR", comando_tarea(),
        "/SC", "DAILY", "/ST", hora_final, "/F",
    ])
    # tarea al iniciar sesion (por si la PC estaba apagada)
    run_silencioso(["schtasks", "/Create", "/TN", TAREA_INICIO,
                    "/TR", comando_tarea(), "/SC", "ONLOGON", "/F"])
    # asegurar que queden habilitadas
    run_silencioso(["schtasks", "/Change", "/TN", TAREA, "/ENABLE"])
    run_silencioso(["schtasks", "/Change", "/TN", TAREA_INICIO, "/ENABLE"])

    # verificar
    q, _ = run_silencioso(["schtasks", "/Query", "/TN", TAREA, "/FO", "LIST"])
    print(f"✅ Hora de aviso configurada a las {hora_final} (diaria).")
    for linea in q.splitlines():
        s = linea.strip()
        if s[:2] in ("Ho", "No", "Es", "Ca") or "Hora" in s or "Nombre" in s or "Estado" in s or "Carpeta" in s:
            print("   ", s)
    print(f"\nLa tarea '{TAREA}' ahora ejecuta el aviso diario a las {hora_final}.")

if __name__ == "__main__":
    main()
