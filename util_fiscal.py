#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
util_fiscal.py - Modulo compartido de obligaciones fiscales.
Centraliza la logica comun usada por recordatorios.py y avisos_automaticos.py
para evitar duplicacion: cargar bases JSON, listar paises y calcular vencimientos.
"""
import os, sys, json, glob
from datetime import date, timedelta

def ruta_base():
    """Directorio donde viven bases/ y archivos de datos.
    - Empaquetado (exe): la carpeta donde está el ejecutable.
    - Script: la carpeta del módulo.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASES_DIR = os.path.join(ruta_base(), "bases")

def cargar_archivo(path):
    """Carga un JSON; devuelve dict o None si falla."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def listar_paises():
    """Devuelve lista de (codigo, nombre) de todos los paises en bases/."""
    paises = []
    for archivo in sorted(glob.glob(os.path.join(BASES_DIR, "obligaciones_*.json"))):
        data = cargar_archivo(archivo)
        if data and data.get("codigo"):
            paises.append((data["codigo"], data.get("pais", "")))
    return paises

def cargar_pais(codigo):
    """Carga la base JSON de un pais (por codigo). Devuelve dict o None."""
    return cargar_archivo(os.path.join(BASES_DIR, f"obligaciones_{codigo.lower()}.json"))

def proximo_vencimiento(oblig, regla, hoy, mes=None, anio=None):
    """Calcula la proxima fecha de vencimiento de una obligacion dada su regla.

    - Regla 'dias' (dia fijo del mes) >0 -> fecha estandar del mes.
    - Regla 'anual_fijo' (MM-DD) -> fecha anual (o proximo anio si ya paso).
    - Si no aplica dia fijo ni fecha fija -> None (va por calendario oficial).
    """
    dia = regla.get("dias")
    if dia and dia > 0:
        # dia fijo mensual (periodo mes siguiente); considerar mes actual y siguiente
        hoy_ref = hoy
        for m in [hoy_ref.month, (hoy_ref.month % 12) + 1]:
            try:
                f = date(hoy_ref.year, m, dia)
            except ValueError:
                continue
            if hoy <= f:
                return f
        return None
    fijo = regla.get("anual_fijo")
    if fijo:
        try:
            mm, dd = map(int, fijo.split("-"))
            f = date(hoy.year, mm, dd)
            if hoy <= f:
                return f
            return date(hoy.year + 1, mm, dd)
        except ValueError:
            return None
    return None

def esta_en_ventana(fecha, hoy, dias):
    """True si 'fecha' cae entre hoy y hoy+dias (inclusive)."""
    return fecha is not None and hoy <= fecha <= hoy + timedelta(days=dias)

def calcular_vencimientos_ventana(data, hoy, dias):
    """Devuelve lista de obligaciones del pais 'data' que vencen en la ventana.

    Dado que cada pais define reglas (dias fijos y/o anuales), se itera por
    obligacion. Solo se incluyen las que tienen vencimiento en [hoy, hoy+dias].
    """
    regla = data.get("reglas_vencimiento", {})
    resultado = []
    for oblig in data.get("obligaciones", []):
        did = oblig["id"]
        regla_obl = {
            "dias": (regla.get("dias") or {}).get(did),
            "anual_fijo": (regla.get("anual_fijo") or {}).get(did),
        }
        f = proximo_vencimiento(oblig, regla_obl, hoy)
        if esta_en_ventana(f, hoy, dias):
            resultado.append({
                "id": did,
                "nombre": oblig.get("nombre", ""),
                "formulario": oblig.get("formulario", ""),
                "fecha": f.isoformat(),
                "dias_rest": (f - hoy).days,
            })
    return resultado
