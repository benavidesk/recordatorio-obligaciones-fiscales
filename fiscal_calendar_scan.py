#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fiscal_calendar_scan.py - Escanea si hay nuevas fechas o actualizaciones en
los calendarios de obligaciones fiscales.

Compara las bases locales (bases/*.json) y VERSION.json contra el repositorio
publico de GitHub (rama main). Solo LEE; no modifica ni publica nada.

USO:
    python fiscal_calendar_scan.py \
        --proyecto "C:/Users/benav/Documents/ObligacionesFiscales" \
        [--repo benavidesk/recordatorio-obligaciones-fiscales]

Sin argumentos usa rutas por defecto del proyecto de Benavidesk.

SALIDA (codigos):
    0 = todo al dia / sin_red (sin cambios)
    1 = hay cambios en calendarios y/o version
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import urllib.request
import urllib.error

DEFAULT_REPO = "benavidesk/recordatorio-obligaciones-fiscales"
RAW = "https://raw.githubusercontent.com/{repo}/main/bases/{archivo}"
RAW_VER = "https://raw.githubusercontent.com/{repo}/main/VERSION.json"
TIMEOUT = 40


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def descargar(url, destino):
    req = urllib.request.Request(url, headers={"User-Agent": "FiscalScan/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            with open(destino, "wb") as f:
                f.write(r.read())
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return False


def scan_bases(proyecto, repo, tmp):
    bases_dir = os.path.join(proyecto, "bases")
    locales = sorted(f for f in os.listdir(bases_dir) if f.endswith(".json"))
    cambios = []
    sin_red = False
    for b in locales:
        url = RAW.format(repo=repo, archivo=b)
        destino = os.path.join(tmp, b)
        if not descargar(url, destino):
            sin_red = True
            cambios.append((b, "ERROR_descarga (sin_red)"))
            continue
        h_local = md5(os.path.join(bases_dir, b))
        h_rem = md5(destino)
        if h_local == h_rem:
            cambios.append((b, "IGUAL"))
        else:
            try:
                with open(os.path.join(bases_dir, b), encoding="utf-8") as f:
                    loc = json.load(f)
                with open(destino, encoding="utf-8") as f:
                    rem = json.load(f)
                cambios.append((
                    b,
                    "DIFERENTE",
                    f"local_ult_act={loc.get('ultima_actualizacion')} "
                    f"remota_ult_act={rem.get('ultima_actualizacion')} "
                    f"local_oblig={len(loc.get('obligaciones', []))} "
                    f"remota_oblig={len(rem.get('obligaciones', []))}",
                ))
            except Exception as e:
                cambios.append((b, f"ERROR_parse {e}"))
    return cambios, sin_red


def scan_version(proyecto):
    """Compara el VERSION.json local con el remoto. Devuelve (hay, info)."""
    local_path = os.path.join(proyecto, "VERSION.json")
    try:
        with open(local_path, encoding="utf-8") as f:
            local = json.load(f)
    except Exception:
        return "ERROR_parse_local", None
    url = RAW_VER.format(repo=DEFAULT_REPO)
    req = urllib.request.Request(url, headers={"User-Agent": "FiscalScan/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            remoto = json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError):
        return "sin_red", None

    v_l = tuple(int(x) for x in str(local.get("version", "0")).strip("v").split(".") if x.isdigit())
    v_r = tuple(int(x) for x in str(remoto.get("version", "0")).strip("v").split(".") if x.isdigit())
    if v_r > v_l:
        return "hay", remoto
    return "ok", local


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proyecto", default="C:/Users/benav/Documents/ObligacionesFiscales")
    ap.add_argument("--repo", default=DEFAULT_REPO)
    args = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="fiscalscan_")
    cambios, sin_red = scan_bases(args.proyecto, args.repo, tmp)
    ver_estado, ver_info = scan_version(args.proyecto)

    base_diff = [c for c in cambios if c[1] not in ("IGUAL", "ERROR_descarga (sin_red)")]
    print("=== BASES DE CALENDARIO (local vs GitHub main) ===")
    for b, estado, *extra in cambios:
        suf = (" " + " ".join(extra)) if extra and extra[0] else ""
        print(f"  {b:35} {estado:15}{suf}")

    print("\n=== VERSION DEL SOFTWARE ===")
    if ver_estado == "hay":
        print(f"  Hay version nueva: {ver_info.get('version')} -> {ver_info.get('url_github')}")
    elif ver_estado == "ok":
        print(f"  Al dia (version {ver_info.get('version')})")
    elif ver_estado == "sin_red":
        print("  No se pudo consultar (sin_red)")
    else:
        print(f"  Error: {ver_estado}")

    hay_cambios = any(c[1] not in ("IGUAL",) and not c[1].startswith("ERROR") for c in cambios)
    hay_version = ver_estado == "hay"
    print("\nRESULTADO:", "HAY actualizaciones" if (hay_cambios or hay_version) else "todo al dia")
    sys.exit(0 if not (hay_cambios or hay_version) else 1)


if __name__ == "__main__":
    main()
