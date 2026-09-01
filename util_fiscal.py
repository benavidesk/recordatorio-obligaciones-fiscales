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
    - Regla 'trimestral' (meses=[...], dia=N) -> fecha en los meses de cierre de trimestre.
    - Regla 'anual_fijo' (MM-DD) -> fecha anual (o proximo anio si ya paso).
    - Si no aplica -> None (va por calendario oficial).
    """
    dia = regla.get("dias")
    if dia and dia > 0:
        # dia fijo mensual (periodo mes siguiente); con manejo correcto del cruce de ano
        hoy_ref = hoy
        for i in [0, 1]:
            m = hoy_ref.month + i
            anio_mes = hoy_ref.year + (m - 1) // 12
            mes_ = (m - 1) % 12 + 1
            try:
                f = date(anio_mes, mes_, dia)
            except ValueError:
                continue
            if hoy <= f:
                return f
        return None

    # Regla trimestral: meses de vencimiento fijos (ej. ES: [1,4,7,10]).
    # Soporta dia unico (meses=[...], dia=N) o dias por mes (dias_por_mes={mes:dia}).
    trim = regla.get("trimestral")
    if trim:
        meses = trim.get("meses") or []
        dia_t = trim.get("dia") or 0
        dias_por_mes = trim.get("dias_por_mes") or {}
        if meses:
            for i in range(0, 9):
                m = hoy.month + i
                anio_m = hoy.year + (m - 1) // 12
                mes_m = (m - 1) % 12 + 1
                if mes_m in meses:
                    # dias_por_mes puede tener claves int o str (JSON); buscar ambos
                    d = dias_por_mes.get(mes_m)
                    if d is None:
                        d = dias_por_mes.get(str(mes_m))
                    if d is None:
                        d = dia_t
                    if not d:
                        continue
                    try:
                        f = date(anio_m, mes_m, d)
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

    # Regla bimensual: vence cada 2 meses (meses pares 2,4,6,8,10,12 por defecto,
    # o lista 'meses' explicita). Uso: {"bimensual": {"dia": N}} o {"bimensual":{"meses":[...],"dia":N}}.
    bimens = regla.get("bimensual")
    if bimens:
        dia_b = bimens.get("dia") or 0
        meses_b = bimens.get("meses") or [2, 4, 6, 8, 10, 12]
        if dia_b:
            for i in range(0, 14):
                m = hoy.month + i
                anio_m = hoy.year + (m - 1) // 12
                mes_m = (m - 1) % 12 + 1
                if mes_m in meses_b:
                    try:
                        f = date(anio_m, mes_m, dia_b)
                    except ValueError:
                        continue
                    if hoy <= f:
                        return f
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
            "trimestral": (regla.get("trimestral") or {}).get(did),
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
