#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RECORDATORIO DE OBLIGACIONES FISCALES - Motor universal multi-pais
Lee una base JSON por pais y genera el calendario de vencimientos + recordatorios.

Como USAR:
  1. Las bases viven en bases/obligaciones_<pais>.json (ej. obligaciones_sv.json).
  2. Corre:  python recordatorios.py --pais SV [--mes 8] [--aviso 5]
  3. Quien quiera DONAR/CORREGIR datos: edita o agrega un JSON en bases/ y lo
     compartes. El codigo no cambia al agregar un pais nuevo.

Estructura de la base (cada obligacion):
  id, nombre, formulario, tipo (mensual/anual), descripcion, y en reglas_vencimiento:
  dias (dia del mes) o anual_fijo (MM-DD) o marcada como "por calendario oficial".
"""
import json, sys, os, argparse
from datetime import date, timedelta
from collections import defaultdict

BASES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bases")

def cargar_obligaciones(pais):
    path = os.path.join(BASES_DIR, f"obligaciones_{pais.lower()}.json")
    if not os.path.exists(path):
        sys.exit(f"❌ No existe base para '{pais}'. Archivos disponibles: "
                 + ", ".join(f.split('_')[1].split('.')[0].upper() for f in os.listdir(BASES_DIR)
                             if f.startswith('obligaciones_')))
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def proximo_vencimiento(oblig, regla, hoy, mes, anio):
    """Calcula la proxima fecha de vencimiento de una obligacion."""
    tipo = oblig["tipo"]
    if tipo == "mensual":
        dia = regla.get("dias")
        if dia and dia > 0:
            # vence el dia X del mes siguiente al periodo (periodo = mes index)
            return date(anio, mes, dia)
        return None  # por calendario oficial (dia variable)
    if tipo == "anual":
        fijo = regla.get("anual_fijo")
        if fijo:
            mm, dd = map(int, fijo.split("-"))
            try: return date(anio, mm, dd)
            except ValueError: return None
    return None

def main():
    ap = argparse.ArgumentParser(description="Recordatorio de obligaciones fiscales multi-pais")
    ap.add_argument("--pais", required=True, help="Codigo de pais (SV, GT, HN...)")
    ap.add_argument("--mes", type=int, default=None, help="Mes (1-12) para periodo/vencimientos. Default=mes actual")
    ap.add_argument("--anio", type=int, default=None, help="Anio. Default=actual")
    ap.add_argument("--aviso", type=int, default=5, help="Dias previos para marcar 'PROXIMO' (default 5)")
    args = ap.parse_args()

    hoy = date.today()
    mes = args.mes or hoy.month
    anio = args.anio or hoy.year

    data = cargar_obligaciones(args.pais)
    print(f"\n═══ 📅 {data['pais']} ({data['codigo']}) · {data['ultima_actualizacion']} ═══")
    print(f"Moneda: {data['moneda']} | ID contribuyente: {data['id_contribuyente']}\n")

    if data["codigo"] == "SV":
        entidad = "Ministerio de Hacienda (MH)"
    elif data["codigo"] == "GT":
        entidad = "Superintendencia de Administración Tributaria (SAT)"
    elif data["codigo"] == "HN":
        entidad = "Servicio de Administración de Rentas (SAR)"
    elif data["codigo"] == "NI":
        entidad = "Dirección General de Ingresos (DGI)"
    elif data["codigo"] == "PA":
        entidad = "Dirección General de Ingresos (DGI-MEF)"
    elif data["codigo"] == "CR":
        entidad = "Ministerio de Hacienda (DGT)"
    elif data["codigo"] == "DO":
        entidad = "Dirección General de Impuestos Internos (DGII)"
    elif data["codigo"] == "MX":
        entidad = "Servicio de Administración Tributaria (SAT)"
    elif data["codigo"] == "CO":
        entidad = "Dirección de Impuestos y Aduanas Nacionales (DIAN)"
    elif data["codigo"] == "PE":
        entidad = "Superintendencia Nacional de Aduanas y Administración Tributaria (SUNAT)"
    elif data["codigo"] == "CL":
        entidad = "Servicio de Impuestos Internos (SII)"
    elif data["codigo"] == "AR":
        entidad = "Agencia de Recaudación y Control Aduanero (ARCA)"
    elif data["codigo"] == "EC":
        entidad = "Servicio de Rentas Internas (SRI)"
    elif data["codigo"] == "UY":
        entidad = "Dirección General Impositiva (DGI)"
    elif data["codigo"] == "PY":
        entidad = "Subsecretaría de Estado de Tributación (SET)"
    elif data["codigo"] == "BO":
        entidad = "Servicio de Impuestos Nacionales (SIN)"
    elif data["codigo"] == "ES":
        entidad = "Agencia Estatal de Administración Tributaria (AEAT)"
    elif data["codigo"] == "GQ":
        entidad = "Ministerio de Hacienda de Guinea Ecuatorial"
    else:
        entidad = "la autoridad fiscal oficial"

    vencen = []
    por_calendario = []
    for oblig in data["obligaciones"]:
        regla = data["reglas_vencimiento"]
        did = oblig["id"]
        # regla por obligacion
        regla_obl = {
            "dias": (regla["dias"] or {}).get(did),
            "anual_fijo": (regla.get("anual_fijo") or {}).get(did),
        }
        fecha = proximo_vencimiento(oblig, regla_obl, hoy, mes, anio)
        if fecha:
            dias_rest = (fecha - hoy).days
            estado = ""
            if fecha < hoy:
                estado = "⚠️ VENCIDA"
            elif fecha == hoy:
                estado = "🚨 VENCE HOY"
            elif dias_rest <= args.aviso:
                estado = f"🔔 PROXIMO ({dias_rest}d)"
            else:
                estado = "✔ en tiempo"
            vencen.append((fecha, oblig, estado, dias_rest))
        else:
            # Sin fecha fija (por calendario oficial del país)
            por_calendario.append(oblig)

    vencen = [v for v in vencen if v[0] is not None]
    vencen.sort(key=lambda v: v[0])

    print("── PROXIMOS VENCIMIENTOS ──")
    if not vencen and not por_calendario:
        print("(sin obligaciones para este mes)")
    for fecha, oblig, estado, dias in vencen:
        print(f"  {fecha.strftime('%Y-%m-%d')} [{estado}] {oblig['formulario']} · {oblig['nombre']}")

    if por_calendario:
        print(f"\n── SEGUN CALENDARIO OFICIAL (dias variables) · {entidad} ──")
        for oblig in por_calendario:
            print(f"  • {oblig['formulario']} · {oblig['nombre']} (consultar {entidad})")

    print(f"\n{data['pais']}: {len(data['obligaciones'])} obligaciones | "
          f"{len([v for v in vencen if v[2].startswith('🔔') or v[2].startswith('🚨') or v[2].startswith('⚠')])} requieren atencion")

if __name__ == "__main__":
    main()
