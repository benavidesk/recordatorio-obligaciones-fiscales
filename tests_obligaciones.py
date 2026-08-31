#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitarios para la logica critica de Recordatorio de Obligaciones Fiscales.

Cubre:
  - util_fiscal: proximo_vencimiento, esta_en_ventana, calcular_vencimientos_ventana
  - avisos_automaticos: generar_mensaje (nombre completo del pais, con/sin alertas)
  - scheduler_fiscal: validar_ruta (proteccion contra caracteres peligrosos de cmd)

Ejecutar (sin dependencias externas):
  py -3.14 -m unittest tests_obligaciones -v
"""
import os
import sys
import unittest
from datetime import date

# Asegurar que el modulo se encuentra (si se corre desde otra carpeta)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import util_fiscal
import avisos_automaticos
import scheduler_fiscal


class TestProximoVencimiento(unittest.TestCase):
    """Calculo de la proxima fecha de vencimiento por regla."""

    def test_dia_fijo_mensual(self):
        # regla dias=10: vence el dia 10 del mes actual y siguiente
        regla = {"dias": 10, "anual_fijo": None}
        oblig = {"id": "SV-F07"}
        # hoy 3-sep -> vence 10-sep
        f = util_fiscal.proximo_vencimiento(oblig, regla, date(2026, 9, 3))
        self.assertEqual(f, date(2026, 9, 10))
        # hoy 11-sep -> ya paso el 10, vence 10-oct
        f = util_fiscal.proximo_vencimiento(oblig, regla, date(2026, 9, 11))
        self.assertEqual(f, date(2026, 10, 10))

    def test_dia_fijo_salto_mes_sin_dia(self):
        # dia 31: hoy 30-ene hay 31-ene (valido), y si hoy es 31-ene ya paso,
        # busca en el mes siguiente con un 31 (marzo, no febrero).
        regla = {"dias": 31, "anual_fijo": None}
        oblig = {"id": "X"}
        # hoy 30-ene -> vence el propio 31-ene (es el siguiente dia 31 >= hoy)
        f = util_fiscal.proximo_vencimiento(oblig, regla, date(2026, 1, 30))
        self.assertEqual(f, date(2026, 1, 31))
        # hoy 1-feb (ya paso el 31-ene): feb no tiene 31 -> salta a 31-mar
        f = util_fiscal.proximo_vencimiento(oblig, regla, date(2026, 2, 1))
        self.assertEqual(f, date(2026, 3, 31))

    def test_anual_fijo(self):
        regla = {"dias": None, "anual_fijo": "04-30"}
        oblig = {"id": "Y"}
        # hoy 3-sep: vence el 30-abr del proximo anio
        f = util_fiscal.proximo_vencimiento(oblig, regla, date(2026, 9, 3))
        self.assertEqual(f, date(2027, 4, 30))

    def test_sin_regla(self):
        # sin dia fijo ni anual -> None (va por calendario oficial)
        regla = {"dias": None, "anual_fijo": None}
        self.assertIsNone(util_fiscal.proximo_vencimiento({"id": "Z"}, regla, date(2026, 9, 3)))


class TestVentana(unittest.TestCase):
    def test_esta_en_ventana_inclusive(self):
        hoy = date(2026, 9, 3)
        self.assertTrue(util_fiscal.esta_en_ventana(date(2026, 9, 3), hoy, 7))   # hoy
        self.assertTrue(util_fiscal.esta_en_ventana(date(2026, 9, 10), hoy, 7))  # borde
        self.assertFalse(util_fiscal.esta_en_ventana(date(2026, 9, 11), hoy, 7)) # fuera
        self.assertFalse(util_fiscal.esta_en_ventana(date(2026, 9, 2), hoy, 7))  # pasado
        self.assertFalse(util_fiscal.esta_en_ventana(None, hoy, 7))

    def test_calcular_sobre_base_real_sv(self):
        # Carga la base real de El Salvador y verifica que en ventana amplia
        # aparece al menos una obligacion con los campos esperados.
        data = util_fiscal.cargar_pais("SV")
        self.assertIsNotNone(data, "la base de SV debe existir")
        resultados = util_fiscal.calcular_vencimientos_ventana(data, date(2026, 9, 1), 120)
        self.assertTrue(resultados, "con 120 dias debe haber vencimientos en SV")
        r = resultados[0]
        for campo in ("id", "nombre", "formulario", "fecha", "dias_rest"):
            self.assertIn(campo, r, f"el resultado debe tener el campo {campo}")


class TestGenerarMensaje(unittest.TestCase):
    def test_sin_alertas_usa_nombre_completo(self):
        msg = avisos_automaticos.generar_mensaje([], ["SV"], 7, date(2026, 9, 3))
        self.assertIn("El Salvador", msg)
        self.assertNotIn("País revisado: SV", msg)  # debe usar nombre, no sigla

    def test_sin_alertas_plural(self):
        msg = avisos_automaticos.generar_mensaje([], ["SV", "MX"], 7, date(2026, 9, 3))
        self.assertIn("El Salvador", msg)
        self.assertIn("México", msg)

    def test_con_alertas(self):
        alerta = {"codigo": "SV", "pais": "El Salvador", "nombre": "IVA mensual",
                  "fecha": "2026-09-10", "dias_rest": 4}
        msg = avisos_automaticos.generar_mensaje([alerta], ["SV"], 7, date(2026, 9, 3))
        self.assertIn("El Salvador", msg)
        self.assertIn("vencen", msg, "debe citar el vencimiento")
        self.assertIn("4", msg)


class TestValidarRuta(unittest.TestCase):
    def test_ruta_segura(self):
        self.assertEqual(scheduler_fiscal.validar_ruta(r"C:\Archivos\Programa"), r"C:\Archivos\Programa")

    def test_ruta_con_ampersand_deniega(self):
        with self.assertRaises(scheduler_fiscal.RutaInsegura):
            scheduler_fiscal.validar_ruta(r"C:\Users\benav&malo")

    def test_ruta_con_comilla_deniega(self):
        with self.assertRaises(scheduler_fiscal.RutaInsegura):
            scheduler_fiscal.validar_ruta(r'C:\Programa"o')

    def test_ruta_con_pipe_deniega(self):
        with self.assertRaises(scheduler_fiscal.RutaInsegura):
            scheduler_fiscal.validar_ruta(r"C:\a|b")


if __name__ == "__main__":
    unittest.main(verbosity=2)
