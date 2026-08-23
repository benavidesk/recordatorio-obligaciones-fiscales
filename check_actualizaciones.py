#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_actualizaciones.py - Verifica si hay una version mas reciente del software.

Compara la version local (VERSION.json) con la del repositorio publico de GitHub.
Si hay una version mas nueva, devuelve la info para que la GUI muestre un aviso.

Funciona via urllib (sin dependencias externas). Si no hay internet o el repo
aun no esta publicado, no falla: devuelve que esta al dia (o error silencioso).

USO (desde gui.py):
    hay, info = check_actualizaciones.buscar("0.3.0")
    if hay:
        # mostrar "hay version nueva", info["version"], info["url"]
"""
import json, urllib.request, urllib.error

# URL del archivo VERSION.json en el repo publico (rama main).
# Cambiar el repo/usuario cuando se suba a GitHub.
REPO_URL = "https://raw.githubusercontent.com/benavidesk/recordatorio-obligaciones-fiscales/main/VERSION.json"
TIMEOUT = 6  # segundos

def _leer_local(ruta_local):
    """Lee la version local; devuelve dict o None."""
    try:
        with open(ruta_local, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _version_a_tuple(v):
    """Convierte '1.2.3' a (1,2,3) para comparar. Tolera prefijos v/espacios."""
    v = str(v).strip().lstrip("vV")
    partes = []
    for p in v.split("."):
        try:
            partes.append(int(p))
        except ValueError:
            partes.append(0)
    return tuple(partes)

def _remota():
    """Obtiene la VERSION.json del repo publico. Devuelve dict o None si falla."""
    try:
        req = urllib.request.Request(REPO_URL, headers={"User-Agent": "ObligacionesFiscales/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError):
        return None

def buscar(ruta_local, url_repo=None):
    """Compara version local con la remota.
    Devuelve (hay_actualizacion: bool, info: dict).
    info = {version, fecha, url} si hay nueva; si no, {"ok": True}.
    Si no se puede consultar remota, devuelve (False, {"error": "sin_red"}).
    """
    global REPO_URL
    if url_repo:
        REPO_URL = url_repo

    local = _leer_local(ruta_local)
    if not local:
        return False, {"error": "sin_version_local"}

    remota = _remota()
    if not remota:
        return False, {"error": "sin_red"}

    v_local = _version_a_tuple(local.get("version", "0"))
    v_remota = _version_a_tuple(remota.get("version", "0"))

    if v_remota > v_local:
        info = {
            "version": remota.get("version", "?"),
            "fecha": remota.get("fecha", ""),
            "url": remota.get("url_github", REPO_URL),
            "nombre": remota.get("nombre", "Actualización"),
            "local": local.get("version", "?"),
        }
        return True, info
    return False, {"ok": True, "version": local.get("version", "?")}

if __name__ == "__main__":
    import os, sys
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION.json")
    hay, info = buscar(ruta)
    if hay:
        print(f"Hay version nueva ({info['version']}) -> {info['url']}")
    else:
        print("Sin actualizaciones:", info)
