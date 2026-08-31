#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scheduler_fiscal.py - Logica UNICA para programar el aviso diario de obligaciones
fiscales en Windows.

Centraliza (evitando la duplicacion entre gui.py y aplicar_hora.py):
  - Elegir el launcher correcto (vbs silencioso > exe d eavisos > .bat).
  - Validar que la ruta no tenga caracteres peligrosos para cmd/schtasks.
  - Crear la tarea programada diaria (HABILITADA).
  - Crear/eliminar el acceso directo en la carpeta 'Inicio' (aviso al iniciar
    sesion, sin necesitar admin como schtasks /SC ONLOGON).
"""
import os
import sys
import subprocess

# Nombres de las tareas programadas
TAREA = "AvisosObligacionesFiscales"
LNK_INICIO = "Avisos Obligaciones Fiscales.lnk"
WSCRIPT = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "wscript.exe")

# Caracteres que rompen/inyectan en la linea de comandos de cmd/schtasks
CARACTERES_PELIGROSOS = set('&|<>^%"()')

class RutaInsegura(Exception):
    """La ruta de instalacion contiene caracteres que podrian romper cmd/schtasks."""


def _ruta_base():
    """Directorio donde viven bases/, config.json y los ejecutables."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def validar_ruta(ruta):
    """Lanza RutaInsegura si 'ruta' contiene caracteres que rompan cmd/schtasks.

    Devuelve la ruta tal cual si es segura. Evita que un path con &, |, ", etc.
    pueda inyectar comandos al pasar /TR a schtasks o al lanzar el .vbs.
    """
    if any(c in ruta for c in CARACTERES_PELIGROSOS):
        raise RutaInsegura(
            f"La ruta '{ruta}' contiene caracteres no seguros "
            f"({''.join(sorted(CARACTERES_PELIGROSOS))}). Reinstala la app en "
            "una carpeta sin &, comillas ni parentesis."
        )
    return ruta


def _launcher():
    """Devuelve el comando (string) que ejecuta el aviso con notificacion.

    Preferencia:
      1. .vbs silencioso (no muestra ventana de consola, solo la notificacion)
      2. exe de avisos (AvisosAutomaticos.exe --notificar)
      3. .bat (modo desarrollo con Python)
    """
    ruta = _ruta_base()
    vbs = os.path.join(ruta, "ejecutar_aviso_silencioso.vbs")
    exe = os.path.join(ruta, "AvisosAutomaticos.exe")
    bat = os.path.join(ruta, "ejecutar_avisos.bat")

    if os.path.exists(vbs):
        return validar_ruta(vbs)          # tarea diaria -> vbs (ya trae --notificar interno)
    if os.path.exists(exe):
        return '\"{}\" --notificar'.format(validar_ruta(exe))
    if os.path.exists(bat):
        return '\"{}\" --notificar'.format(validar_ruta(bat))
    raise FileNotFoundError("No se encontro el launcher del aviso (vbs/exe/bat).")


def _run(cmd):
    """Ejecuta un comando y devuelve su salida decodificada, sin lanzar."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=False)
        return (r.stdout or b"").decode("mbcs", errors="replace")
    except Exception:
        return ""


def programar_tarea(hora):
    """Borra y recrea la tarea programada diaria 'AvisosObligacionesFiscales',
    habilitada, ejecutando el launcher elegido. Lanza RutaInsegura si la ruta
    de instalacion no es segura."""
    validar_ruta(_ruta_base())          # falla temprano si la ruta es peligrosa
    _run(["schtasks", "/Delete", "/TN", TAREA, "/F"])
    _run(["schtasks", "/Create", "/TN", TAREA, "/TR", _launcher(),
          "/SC", "DAILY", "/ST", hora, "/F"])
    _run(["schtasks", "/Change", "/TN", TAREA, "/ENABLE"])


def eliminar_tarea():
    """Elimina la tarea programada si existe."""
    _run(["schtasks", "/Delete", "/TN", TAREA, "/F"])


def carpeta_inicio():
    """Ruta de la carpeta Inicio del usuario, por API COM de Windows (sin
    depender de win32com)."""
    import ctypes
    from ctypes import wintypes
    CSIDL_STARTUP = 7
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_STARTUP, 0, 0, buf)
    return buf.value


def crear_acceso_inicio():
    """Crea un acceso directo en la carpeta Inicio que lanza el aviso (vbs via
    wscript) al iniciar la sesion. Devuelve True si quedo creado."""
    lnk = os.path.join(carpeta_inicio(), LNK_INICIO)
    try:
        # Construye el .lnk vía COM de Windows (WScript.Shell desde PowerShell).
        rc = subprocess.run(
            [
                "powershell", "-NoProfile", "-Command",
                "$ws=New-Object -ComObject WScript.Shell; "
                "$sc=$ws.CreateShortcut('{lnk}'); "
                "$sc.TargetPath='{wscript}'; "
                "$sc.Arguments='\"{vbs}\"'; "
                "$sc.Description='Aviso diario de obligaciones fiscales'; "
                "$sc.Save()".format(
                    lnk=lnk.replace("'", "''"),
                    wscript=validar_ruta(WSCRIPT).replace("'", "''"),
                    vbs=os.path.join(_ruta_base(), "ejecutar_aviso_silencioso.vbs").replace("'", "''"),
                )
            ],
            capture_output=True, timeout=30,
        )
        return os.path.exists(lnk)
    except Exception:
        return False


def eliminar_acceso_inicio():
    """Borra el acceso directo de Inicio si existe."""
    lnk = os.path.join(carpeta_inicio(), LNK_INICIO)
    try:
        if os.path.exists(lnk):
            os.remove(lnk)
    except Exception:
        pass


def aplicar(hora):
    """Punto de entrada unico: programa la tarea diaria y el inicio de sesion.
    Usado por gui.py y aplicar_hora.py."""
    validar_ruta(_ruta_base())
    programar_tarea(hora)
    eliminar_acceso_inicio()
    crear_acceso_inicio()
