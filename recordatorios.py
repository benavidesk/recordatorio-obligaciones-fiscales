#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RECORDATORIO DE OBLIGACIONES FISCALES - consulta manual
Lee la base JSON de un pais y muestra los vencimientos del periodo + estado.

Uso:
  python recordatorios.py --pais SV                # mes actual
  python recordatorios.py --pais SV --mes 8 --anio 2026
  python recordatorios.py --pais GT --aviso 10

La logica comun (cargar bases, listar paises, calcular vencimientos) vive en
util_fiscal.py. Este script se enfoca en la PRESENTACION de la consulta.
"""
import os, sys, argparse
from datetime import date

from util_fiscal import cargar_pais, listar_paises, proximo_vencimiento

BASES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bases")

def entidad_de(codigo):
    """Devuelve el nombre legible de la autoridad fiscal del pais."""
    tabla = {
        "SV": "Ministerio de Hacienda (MH)",
        "GT": "Superintendencia de Administración Tributaria (SAT)",
        "HN": "Servicio de Administración de Rentas (SAR)",
        "NI": "Dirección General de Ingresos (DGI)",
        "PA": "Dirección General de Ingresos (DGI-MEF)",
        "CR": "Ministerio de Hacienda (DGT)",
        "DO": "Dirección General de Impuestos Internos (DGII)",
        "MX": "Servicio de Administración Tributaria (SAT)",
        "CO": "Dirección de Impuestos y Aduanas Nacionales (DIAN)",
        "PE": "Superintendencia Nacional de Aduanas y Administración Tributaria (SUNAT)",
        "CL": "Servicio de Impuestos Internos (SII)",
        "AR": "Agencia de Recaudación y Control Aduanero (ARCA)",
        "EC": "Servicio de Rentas Internas (SRI)",
        "UY": "Dirección General Impositiva (DGI)",
        "PY": "Subsecretaría de Estado de Tributación (SET)",
        "BO": "Servicio de Impuestos Nacionales (SIN)",
        "ES": "Agencia Estatal de Administración Tributaria (AEAT)",
        "GQ": "Ministerio de Hacienda de Guinea Ecuatorial",
        "US": "Internal Revenue Service (IRS)",
    }
    return tabla.get(codigo, "la autoridad fiscal oficial")

def main():
    ap = argparse.ArgumentParser(description="Recordatorio de obligaciones fiscales multi-pais")
    ap.add_argument("--pais", required=True, help="Codigo de pais (SV, GT, HN...)")
    ap.add_argument("--mes", type=int, default=None, help="Mes (1-12) para vencimientos. Default=mes actual")
    ap.add_argument("--anio", type=int, default=None, help="Anio. Default=actual")
    ap.add_argument("--aviso", type=int, default=5, help="Dias previos para marcar 'PROXIMO' (default 5)")
    args = ap.parse_args()

    hoy = date.today()
    mes = args.mes or hoy.month
    anio = args.anio or hoy.year

    data = cargar_pais(args.pais)
    if not data:
        disponibles = ", ".join(c for c, _ in listar_paises())
        sys.exit(f"❌ No existe base para '{args.pais}'. Disponibles: {disponibles}")

    entidad = entidad_de(data["codigo"])
    print(f"\n═══ 📅 {data['pais']} ({data['codigo']}) · {data['ultima_actualizacion']} ═══")
    print(f"Moneda: {data['moneda']} | ID contribuyente: {data['id_contribuyente']}\n")

    regla = data["reglas_vencimiento"]
    vencen = []
    por_calendario = []
    for oblig in data["obligaciones"]:
        did = oblig["id"]
        regla_obl = {
            "dias": (regla.get("dias") or {}).get(did),
            "anual_fijo": (regla.get("anual_fijo") or {}).get(did),
            "trimestral": (regla.get("trimestral") or {}).get(did),
        }
        fecha = proximo_vencimiento(oblig, regla_obl, hoy, mes, anio)
        if fecha and fecha.year == anio:
            dias_rest = (fecha - hoy).days
            if dias_rest < 0:
                estado = "⚠️ VENCIDA"
            elif dias_rest == 0:
                estado = "🚨 VENCE HOY"
            elif dias_rest <= args.aviso:
                estado = f"🔔 PROXIMO ({dias_rest}d)"
            else:
                estado = "✔ en tiempo"
            vencen.append((fecha, oblig, estado, dias_rest))
        else:
            por_calendario.append(oblig)

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

    atencion = sum(1 for v in vencen if v[2].startswith(("🔔", "🚨", "⚠")))
    print(f"\n{data['pais']}: {len(data['obligaciones'])} obligaciones | {atencion} requieren atencion")

if __name__ == "__main__":
    main()
