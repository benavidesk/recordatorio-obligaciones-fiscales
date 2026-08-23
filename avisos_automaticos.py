#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AVISOS AUTOMATICOS DE OBLIGACIONES FISCALES
Revisa los vencimientos del PAIS configurado (config.json) y avisa los proximos dias.

Por defecto revisa SOLO el pais de config.json (pais_por_defecto). Para ver todos:
  py -3.14 avisos_automaticos.py --pais all
Para ver uno especifico sin cambiar config:
  py -3.14 avisos_automaticos.py --pais MX

Este script lo ejecuta una TAREA PROGRAMADA diaria.
"""
import os, json, argparse
from datetime import date

from util_fiscal import cargar_archivo, listar_paises, cargar_pais, calcular_vencimientos_ventana

RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(RUTA_BASE, "config.json")

def leer_config():
    """Devuelve el config como dict, con valores por defecto si faltan."""
    cfg = cargar_archivo(CONFIG_FILE) or {}
    return {
        "pais_por_defecto": str(cfg.get("pais_por_defecto", "SV")).upper(),
        "dias_aviso": int(cfg.get("dias_aviso", 7)),
        "hora_aviso": str(cfg.get("hora_aviso", "08:00")),
    }

def revisar(paises_seleccion, hoy, dias):
    """Recorre los paises seleccionados y devuelve (alertas, revisados)."""
    alertas = []
    revisados = []
    for cod, nombre_pais in paises_seleccion:
        data = cargar_pais(cod)
        if not data:
            continue
        revisados.append(cod)
        for v in calcular_vencimientos_ventana(data, hoy, dias):
            alertas.append({"codigo": cod, "pais": nombre_pais, **v})
    alertas.sort(key=lambda a: a["fecha"])
    return alertas, revisados

def generar_mensaje(alerta_list, revisados, dias, hoy):
    """Construye el texto del aviso."""
    if len(revisados) == 1:
        cabecera = f"País revisado: {revisados[0]}"
    else:
        cabecera = f"Países revisados: {len(revisados)} ({', '.join(revisados)})"

    if alerta_list:
        lineas = [f"⏰ {cabecera} · {len(alerta_list)} vencen en {dias}d ({hoy.isoformat()})", ""]
        for a in alerta_list:
            urg = "🔴" if a["dias_rest"] <= 2 else ("🟠" if a["dias_rest"] <= 5 else "🟡")
            lineas.append(f"  {urg} {a['fecha']} ({a['dias_rest']}d) · [{a['codigo']}] {a['nombre']}")
        return "\n".join(lineas)
    return f"✅ {cabecera} · Sin obligaciones en los proximos {dias} dias ({hoy.isoformat()})."

def guardar_log(msg, hoy):
    """Escribe el aviso en avisos/ (fecha + ultimo_aviso)."""
    log_dir = os.path.join(RUTA_BASE, "avisos")
    os.makedirs(log_dir, exist_ok=True)
    for nombre in (f"aviso_{hoy.isoformat()}.txt", "ultimo_aviso.txt"):
        with open(os.path.join(log_dir, nombre), "w", encoding="utf-8") as f:
            f.write(msg + "\n")

def notificar_si_hay(msg):
    """Muestra notificacion visual si el mensaje contiene alertas."""
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, msg, "Aviso Obligaciones Fiscales", 0x30)
    except Exception:
        pass

def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("--pais", default=None, help="codigo de pais o 'all' (default: config.json)")
    argp.add_argument("--dias", type=int, default=None, help="dias a la vista (default: config o 7)")
    argp.add_argument("--notificar", action="store_true", help="mostrar notificacion visual")
    args = argp.parse_args()
    hoy = date.today()
    cfg = leer_config()

    # Determinar paises a revisar
    todos = listar_paises()
    sel = (args.pais or "").upper().strip()
    if sel == "ALL":
        paises = todos
    elif sel:
        paises = [t for t in todos if t[0] == sel]
        if not paises:
            disp = ", ".join(t[0] for t in todos)
            print(f"❌ Pais '{sel}' no existe. Disponibles: {disp} (o 'all').")
            return
    else:
        paises = [t for t in todos if t[0] == cfg["pais_por_defecto"]] or (todos[:1] if todos else [])

    dias = args.dias or cfg["dias_aviso"]
    alertas, revisados = revisar(paises, hoy, dias)
    msg = generar_mensaje(alertas, revisados, dias, hoy)

    guardar_log(msg, hoy)
    print(msg)

    if args.notificar and alertas:
        notificar_si_hay(msg)

if __name__ == "__main__":
    main()
