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
import sys, os, json, glob, argparse
from datetime import date, timedelta

RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
BASES_DIR = os.path.join(RUTA_BASE, "bases")
CONFIG_FILE = os.path.join(RUTA_BASE, "config.json")

def cargar_archivo(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def pais_por_defecto():
    cfg = cargar_archivo(CONFIG_FILE)
    if cfg and cfg.get("pais_por_defecto"):
        return str(cfg["pais_por_defecto"]).upper()
    return "SV"

def dias_por_defecto():
    cfg = cargar_archivo(CONFIG_FILE)
    if cfg and cfg.get("dias_aviso"):
        return int(cfg["dias_aviso"])
    return 7

def vencimiento_cercano(oblig, data, hoy, dias_ventana):
    regla = data.get("reglas_vencimiento", {})
    did = oblig["id"]
    tipo = oblig.get("tipo")
    dia = (regla.get("dias") or {}).get(did)
    if dia and dia > 0:
        for m in [hoy.month, (hoy.month % 12) + 1]:
            try:
                f = date(hoy.year, m, dia)
            except:
                continue
            if hoy <= f <= hoy + timedelta(days=dias_ventana):
                return f
    fijo = (regla.get("anual_fijo") or {}).get(did)
    if fijo:
        try:
            mm, dd = map(int, fijo.split("-"))
            f = date(hoy.year, mm, dd)
            if hoy <= f <= hoy + timedelta(days=dias_ventana):
                return f
            f2 = date(hoy.year + 1, mm, dd)
            if hoy <= f2 <= hoy + timedelta(days=dias_ventana):
                return f2
        except:
            pass
    return None

def listar_paises():
    paises = []
    for archivo in sorted(glob.glob(os.path.join(BASES_DIR, "obligaciones_*.json"))):
        data = cargar_archivo(archivo)
        if data and data.get("codigo"):
            paises.append((data["codigo"], data.get("pais","")))
    return paises

def revisar(paises_seleccion, hoy, dias):
    alertas = []
    paises_revisados = []
    for cod, pais in paises_seleccion:
        archivo = os.path.join(BASES_DIR, f"obligaciones_{cod.lower()}.json")
        data = cargar_archivo(archivo)
        if not data:
            continue
        paises_revisados.append(cod)
        for oblig in data.get("obligaciones", []):
            f = vencimiento_cercano(oblig, data, hoy, dias)
            if f:
                alertas.append({
                    "pais": pais, "codigo": cod, "nombre": oblig.get("nombre",""),
                    "formulario": oblig.get("formulario",""), "fecha": f.isoformat(),
                    "dias_rest": (f - hoy).days,
                })
    alertas.sort(key=lambda a: a["fecha"])
    return alertas, paises_revisados

def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("--pais", default=None, help="codigo de pais o 'all' (default: config.json)")
    argp.add_argument("--dias", type=int, default=None, help="dias a la vista (default: config o 7)")
    argp.add_argument("--notificar", action="store_true", help="mostrar notificacion visual")
    args = argp.parse_args()
    hoy = date.today()

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
        cod_default = pais_por_defecto()
        paises = [t for t in todos if t[0] == cod_default]
        # si el config no matchea, usar el primero
        if not paises and todos:
            paises = [todos[0]]

    dias = args.dias or dias_por_defecto()
    alertas, revisados = revisar(paises, hoy, dias)

    # Cabecera / mensaje
    if len(revisados) == 1:
        cabecera = f"País revisado: {revisados[0]}"
    else:
        cabecera = f"Países revisados: {len(revisados)} ({', '.join(revisados)})"

    if alertas:
        lineas = [f"⏰ {cabecera} · {len(alertas)} vencen en {dias}d ({hoy.isoformat()})", ""]
        for a in alertas:
            urg = "🔴" if a["dias_rest"] <= 2 else ("🟠" if a["dias_rest"] <= 5 else "🟡")
            lineas.append(f"  {urg} {a['fecha']} ({a['dias_rest']}d) · [{a['codigo']}] {a['nombre']}")
        msg = "\n".join(lineas)
    else:
        msg = f"✅ {cabecera} · Sin obligaciones en los proximos {dias} dias ({hoy.isoformat()})."

    # Log
    log_dir = os.path.join(RUTA_BASE, "avisos")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, f"aviso_{hoy.isoformat()}.txt"), "w", encoding="utf-8") as f:
        f.write(msg + "\n")
    with open(os.path.join(log_dir, "ultimo_aviso.txt"), "w", encoding="utf-8") as f:
        f.write(msg + "\n")

    print(msg)

    # Notificacion visual si hay alertas
    if args.notificar and alertas:
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, msg, "Aviso Obligaciones Fiscales", 0x30)
        except Exception:
            pass

if __name__ == "__main__":
    main()
