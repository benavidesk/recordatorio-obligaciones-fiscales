@echo off
REM Ejecuta los avisos automaticos de obligaciones fiscales (diario, via tarea programada)
REM Revisa el PAIS configurado en config.json por defecto (modifica config.json para cambiar el pais)
cd /d "C:\Users\benav\Documents\ObligacionesFiscales"
"C:\Users\benav\AppData\Local\Programs\Python\Launcher\py.exe" -3.14 avisos_automaticos.py --notificar
