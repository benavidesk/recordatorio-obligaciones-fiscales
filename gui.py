#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI de configuracion de los Avisos de Obligaciones Fiscales.
Permite elegir, de forma visual (sin tocar archivos):
  - el Pais de los recordatorios
  - la HORA del aviso diario
  - los DIAS de anticipo
Y aplica los cambios (actualiza config.json + la tarea programada de Windows).

Cada campo va en un recuadro (LabelFrame) para que label + control queden
agrupados y no haya confusion. Todo centrado.

USO:  py -3.14 gui.py   (o doble clic)
"""
import json, os, subprocess, glob, sys
import tkinter as tk
from tkinter import ttk, messagebox

from check_actualizaciones import buscar as buscar_actualizacion

def ruta_base():
    """Director donde viven bases/, config.json y el .exe.
    - Empaquetado (exe): la carpeta donde está el ejecutable.
    - Script: la carpeta del proyecto.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# Diseño distribución: el paquete lleva el .exe + la carpeta bases/ + config.json
# juntos en el mismo directorio (persistente y editable por el usuario).
RUTA = ruta_base()
BASES = os.path.join(RUTA, "bases")
CONFIG = os.path.join(RUTA, "config.json")
TAREA = "AvisosObligacionesFiscales"
BAT = os.path.join(RUTA, "ejecutar_avisos.bat")
# Ejecutable de avisos (empaguetado, sin depender de que haya Python instalado)
EXE_AVISOS = os.path.join(RUTA, "AvisosAutomaticos.exe")
# Launcher VBS que ejecuta el aviso SIN ventana de consola (solo la notificacion)
VBS = os.path.join(RUTA, "ejecutar_aviso_silencioso.vbs")

# Paleta de color (tema claro/celeste)
BG = "#f5f9ff"
ACCENT = "#2f9bff"
ACCENT2 = "#0a6edb"
BORDER = "#c9d9f0"
FR_CASILLA = "#ffffff"

def cargar_config():
    try:
        with open(CONFIG, encoding="utf-8") as f: return json.load(f)
    except: return {}

def guardar_config(cfg):
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def listar_paises():
    paises = []
    for archivo in sorted(glob.glob(os.path.join(BASES, "obligaciones_*.json"))):
        try:
            with open(archivo, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("codigo"):
                paises.append((d["codigo"], d.get("pais","")))
        except: pass
    return paises

def _carpeta_inicio():
    """Ruta de la carpeta 'Inicio' del usuario (para lanzar el aviso al iniciar
    sesion sin necesitar privilegios de administrador, que exige schtasks ONLOGON)."""
    try:
        import win32com.client  # no disponible; se usa ctypes/registro
    except Exception:
        pass
    # Ruta estandar de la carpeta de inicio del usuario
    import ctypes
    from ctypes import wintypes
    CSIDL_STARTUP = 7
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_STARTUP, 0, 0, buf)
    return buf.value

def _crear_acceso_inicio():
    """Crea un acceso directo en la carpeta de Inicio que ejecuta el aviso
    silenciosamente (vbs via wscript) al iniciar la sesion."""
    try:
        import subprocess
        carpeta = _carpeta_inicio()
        lnk = os.path.join(carpeta, "Avisos Obligaciones Fiscales.lnk")
        # PS = \Windows\System32\wscript.exe + comillas del vbs
        cmd = (
            'powershell -Command "$ws=New-Object -ComObject WScript.Shell; '
            '$sc=$ws.CreateShortcut(\'{lnk}\'); '
            '$sc.TargetPath=\'C:\\Windows\\System32\\wscript.exe\'; '
            '$sc.Arguments=\'"{vbs}"\'; $sc.Description=\'Aviso diario\'; $sc.Save()"'
        ).format(lnk=lnk.replace("\\", "\\\\"), vbs=VBS.replace("\\", "\\\\"))
        subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
        return os.path.exists(lnk)
    except Exception:
        return False

def _eliminar_acceso_inicio():
    """Borra el acceso directo de Inicio si existe."""
    try:
        lnk = os.path.join(_carpeta_inicio(), "Avisos Obligaciones Fiscales.lnk")
        if os.path.exists(lnk):
            os.remove(lnk)
    except Exception:
        pass

def aplicar_tarea(hora):
    def run(cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=False)
            return (r.stdout or b"").decode("mbcs", errors="replace")
        except: return ""
    # Launcher silencioso: el VBS ejecuta el aviso sin ventana de consola, solo
    # la notificacion. Si no existe (modo script sin el VBS), usamos exe/bat.
    if os.path.exists(VBS):
        launcher = VBS
    elif os.path.exists(EXE_AVISOS):
        launcher = "\"{}\" --notificar".format(EXE_AVISOS)
    else:
        launcher = "\"{}\" --notificar".format(BAT)

    # 1) Tarea diaria a la hora elegida (silenciosa, solo notificacion)
    run(["schtasks", "/Delete", "/TN", TAREA, "/F"])
    run(["schtasks", "/Create", "/TN", TAREA, "/TR", launcher,
         "/SC", "DAILY", "/ST", hora, "/F"])
    run(["schtasks", "/Change", "/TN", TAREA, "/ENABLE"])

    # 2) Inicio de sesion: acceso directo en la carpeta Inicio (no requiere
    #    administrador, a diferencia de schtasks /SC ONLOGON).
    _eliminar_acceso_inicio()
    _crear_acceso_inicio()

def crear_casilla(parent, titulo):
    """Crea un recuadro (LabelFrame) con borde visible y fondo blanco."""
    caja = ttk.LabelFrame(parent, text=titulo, padding=14, style="Casilla.TLabelframe")
    return caja

def main():
    cfg = cargar_config()

    # Verificar actualizaciones (en segundo plano no bloquea la ventana)
    def _revisar_actualizaciones():
        ruta_version = os.path.join(RUTA, "VERSION.json")
        try:
            hay, info = buscar_actualizacion(ruta_version)
            if hay and info.get("version"):
                root.after(0, lambda: _mostrar_aviso_nueva(info))
        except Exception:
            pass  # si falla la red, no molestar

    def _mostrar_aviso_nueva(info):
        try:
            messagebox.showinfo(
                "Actualización disponible",
                f"Hay una actualización nueva del software (v{info['version']}, {info.get('fecha','')}).\n\n"
                f"La versión que tienes es la v{info.get('local','?')}.\n\n"
                f"Descarga la nueva versión desde:\n{info.get('url','')}",
            )
        except Exception:
            pass

    paises = listar_paises()
    cods = [p[0] for p in paises]

    root = tk.Tk()
    root.title("Avisos de Obligaciones Fiscales - Configuración")
    root.geometry("560x560")
    root.minsize(520, 520)
    root.configure(bg=BG)

    # Estilo del recuadro: borde visible y titulo en accent
    style = ttk.Style(root)
    try: style.theme_use("clam")
    except: pass
    style.configure("Casilla.TLabelframe", background=FR_CASILLA, bordercolor=BORDER,
                    relief="solid", borderwidth=1)
    style.configure("Casilla.TLabelframe.Label", background=FR_CASILLA,
                    foreground=ACCENT2, font=("Segoe UI", 10, "bold"))
    style.configure("TLabel", background=FR_CASILLA, font=("Segoe UI", 11))
    style.configure("App.TFrame", background=BG)
    style.configure("Casilla.TFrame", background=FR_CASILLA)
    style.configure("TCombobox", font=("Segoe UI", 11))

    main = ttk.Frame(root, padding=24, style="App.TFrame")
    main.pack(fill="both", expand=True)

    ttk.Label(main, text="Avisos de Obligaciones Fiscales",
              font=("Segoe UI", 16, "bold"), background=BG,
              foreground=ACCENT2).pack(pady=(0, 18))

    # ---- Casilla: PAÍS ----
    caja_pais = crear_casilla(main, "País de los recordatorios")
    caja_pais.pack(fill="x", pady=8)
    inner_pais = ttk.Frame(caja_pais, style="Casilla.TFrame")
    inner_pais.pack(fill="x")
    pais_var = tk.StringVar(value=cfg.get("pais_por_defecto","SV"))
    combo = ttk.Combobox(inner_pais, textvariable=pais_var, values=cods,
                         state="readonly", width=20, font=("Segoe UI", 11))
    combo.set(cfg.get("pais_por_defecto","SV"))
    combo.pack(side="left", pady=4)
    def mostrar_nombre(*a):
        cod = pais_var.get()
        for c, n in paises:
            if c == cod: lbl_nombre.config(text=f"  {n}")
    lbl_nombre = ttk.Label(inner_pais, text="", font=("Segoe UI", 10))
    lbl_nombre.pack(side="left", padx=8)
    pais_var.trace_add("write", mostrar_nombre)
    mostrar_nombre()

    # ---- Casilla: HORA ----
    caja_hora = crear_casilla(main, "Hora del aviso diario")
    caja_hora.pack(fill="x", pady=8)
    inner_hora = ttk.Frame(caja_hora, style="Casilla.TFrame")
    inner_hora.pack(fill="x")
    hora_actual = cfg.get("hora_aviso","08:00")
    try:
        h, m = map(int, hora_actual.split(":"))
    except:
        h, m = 8, 0
    ttk.Label(inner_hora, text="Horas:").pack(side="left")
    sph = tk.Spinbox(inner_hora, from_=0, to=23, width=4, font=("Segoe UI", 11), bg="white")
    sph.delete(0,"end"); sph.insert(0, str(h)); sph.pack(side="left", padx=4)
    ttk.Label(inner_hora, text="Min:").pack(side="left")
    spm = tk.Spinbox(inner_hora, from_=0, to=59, width=4, font=("Segoe UI", 11), bg="white")
    spm.delete(0,"end"); spm.insert(0, f"{m:02d}"); spm.pack(side="left", padx=4)
    ttk.Label(inner_hora, text="(HH:MM, 24h)", font=("Segoe UI", 9)).pack(side="left", padx=10)

    # ---- Casilla: DÍAS ----
    caja_dias = crear_casilla(main, "Anticipar aviso (días antes)")
    caja_dias.pack(fill="x", pady=8)
    inner_dias = ttk.Frame(caja_dias, style="Casilla.TFrame")
    inner_dias.pack(fill="x")
    dias_var = tk.IntVar(value=int(cfg.get("dias_aviso",7)))
    spd = tk.Spinbox(inner_dias, from_=1, to=30, textvariable=dias_var,
                     width=6, font=("Segoe UI", 11), bg="white")
    spd.pack(side="left", pady=4)
    ttk.Label(inner_dias, text="días", font=("Segoe UI", 11)).pack(side="left", padx=8)

    # ---- Botón ----
    def on_aplicar():
        cod = pais_var.get()
        try: hh = int(sph.get())
        except: hh = 8
        try: mm = int(spm.get())
        except: mm = 0
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            messagebox.showerror("Error", "Hora inválida. Usa hora 0-23 y minutos 0-59.")
            return
        hora = f"{hh:02d}:{mm:02d}"
        dias = int(dias_var.get())
        cfg_new = {"pais_por_defecto": cod, "dias_aviso": dias, "hora_aviso": hora,
                   "nota": cfg.get("nota","")}
        guardar_config(cfg_new)
        try:
            aplicar_tarea(hora)
            messagebox.showinfo(
                "Configuración aplicada",
                f"País: {cod}\nHora del aviso: {hora}\nAnticipación: {dias} días\n\n"
                f"La tarea 'AvisosObligacionesFiscales' se actualizó.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la tarea:\n{e}")

    btn = tk.Button(main, text="Guardar y aplicar", command=on_aplicar,
                    bg=ACCENT, fg="white", font=("Segoe UI", 12, "bold"),
                    padx=32, pady=12, relief="flat", cursor="hand2", activebackground=ACCENT2)
    btn.pack(pady=22)

    ttk.Label(main,
              text="La tarea 'AvisosObligacionesFiscales' corre a diario. "
                   "Si hay vencimientos en el periodo, salta una notificación.",
              font=("Segoe UI", 9), background=BG, foreground="#444",
              justify="center", wraplength=480).pack()

    # Revisar actualizaciones al abrir (sin bloquear la interfaz)
    root.after(600, _revisar_actualizaciones)

    root.mainloop()

if __name__ == "__main__":
    main()
