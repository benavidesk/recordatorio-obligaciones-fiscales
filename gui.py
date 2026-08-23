#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI de configuracion de los Avisos de Obligaciones Fiscales.
Permite elegir, de forma visual (sin tocar archivos):
  - el Pais de los recordatorios
  - la HORA del aviso diario
  - los DIAS de anticipo
Y aplica los cambios (actualiza config.json + la tarea programada de Windows).

USO:  py -3.14 gui.py   (o doble clic)
"""
import json, os, subprocess, glob, sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

RUTA = os.path.dirname(os.path.abspath(__file__))
BASES = os.path.join(RUTA, "bases")
CONFIG = os.path.join(RUTA, "config.json")
TAREA = "AvisosObligacionesFiscales"
BAT = os.path.join(RUTA, "ejecutar_avisos.bat")

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

def aplicar_tarea(hora):
    def run(cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=False)
            return (r.stdout or b"").decode("mbcs", errors="replace")
        except: return ""
    run(["schtasks", "/Delete", "/TN", TAREA, "/F"])
    run(["schtasks", "/Create", "/TN", TAREA, "/TR", BAT,
         "/SC", "DAILY", "/ST", hora, "/F"])

def main():
    cfg = cargar_config()
    paises = listar_paises()
    cods = [p[0] for p in paises]

    root = tk.Tk()
    root.title("Avisos de Obligaciones Fiscales - Configuración")
    root.geometry("640x480")
    root.minsize(600, 440)
    root.configure(bg="#f5f9ff")
    root.resizable(True, True)

    style = ttk.Style(root)
    try: style.theme_use("clam")
    except: pass
    style.configure("TFrame", background="#f5f9ff")
    style.configure("TLabel", background="#f5f9ff", font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI", 11, "bold"))

    pad = dict(pady=8)

    main = ttk.Frame(root, padding=22)
    main.pack(fill="both", expand=True)

    ttk.Label(main, text="Avisos de Obligaciones Fiscales",
              font=("Segoe UI", 15, "bold")).pack(**pad)

    # --- Pais ---
    ttk.Label(main, text="País para los recordatorios:").pack(anchor="w")
    pais_var = tk.StringVar(value=cfg.get("pais_por_defecto","SV"))
    combo = ttk.Combobox(main, textvariable=pais_var, values=cods, state="readonly", width=18)
    combo.set(cfg.get("pais_por_defecto","SV"))
    combo.pack(anchor="w", **pad)
    # nombre del pais seleccionado
    def mostrar_nombre(*a):
        cod = pais_var.get()
        for c, n in paises:
            if c == cod: lbl_nombre.config(text=n)
    lbl_nombre = ttk.Label(main, text="", font=("Segoe UI", 9))
    lbl_nombre.pack(anchor="w")
    pais_var.trace_add("write", mostrar_nombre)
    mostrar_nombre()

    # --- Hora del aviso ---
    ttk.Label(main, text="Hora del aviso diario:").pack(anchor="w", pady=(15,0))
    hora_actual = cfg.get("hora_aviso","08:00")
    try:
        h, m = map(int, hora_actual.split(":"))
    except:
        h, m = 8, 0
    frm_hora = ttk.Frame(main)
    frm_hora.pack(anchor="w", pady=4)
    ttk.Label(frm_hora, text="Horas:").pack(side="left")
    sph = tk.Spinbox(frm_hora, from_=0, to=23, width=4, font=("Segoe UI", 11))
    sph.delete(0,"end"); sph.insert(0, str(h)); sph.pack(side="left", padx=4)
    ttk.Label(frm_hora, text="Min:").pack(side="left")
    spm = tk.Spinbox(frm_hora, from_=0, to=59, width=4, font=("Segoe UI", 11))
    spm.delete(0,"end"); spm.insert(0, f"{m:02d}"); spm.pack(side="left", padx=4)
    ttk.Label(frm_hora, text="(HH:MM, 24h)", font=("Segoe UI", 9)).pack(side="left", padx=8)

    # --- Dias de aviso ---
    ttk.Label(main, text="Anticipar aviso (días antes):").pack(anchor="w", pady=(15,0))
    dias_var = tk.IntVar(value=int(cfg.get("dias_aviso",7)))
    spd = tk.Spinbox(main, from_=1, to=30, textvariable=dias_var, width=6, font=("Segoe UI", 11))
    spd.pack(anchor="w", pady=4)

    # --- boton aplicar ---
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
                f"✅ País: {cod}\nHora del aviso: {hora}\nAnticipación: {dias} días\n\n"
                f"La tarea 'AvisosObligacionesFiscales' se actualizó.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la tarea:\n{e}")

    btn = tk.Button(main, text="Guardar y aplicar", command=on_aplicar,
                    bg="#2f9bff", fg="white", font=("Segoe UI", 12, "bold"),
                    padx=28, pady=12, relief="flat", cursor="hand2")
    btn.pack(pady=20)

    ttk.Label(main, text="La tarea 'AvisosObligacionesFiscales' corre a diario. "
                         "Si hay vencimientos en el periodo, salta una notificación.",
              font=("Segoe UI", 9), justify="left", wraplength=560).pack(anchor="w")

    root.mainloop()

if __name__ == "__main__":
    main()
