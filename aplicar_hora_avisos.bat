@echo off
REM Aplica la HORA DE AVISO personalizada de config.json a la tarea programada de Windows.
REM Uso: 1) edita config.json y cambia "hora_aviso": "08:00" por la hora que quieras.
REM       2) ejecuta este archivo (doble clic).  La tarea se actualiza con la nueva hora.
cd /d "C:\Users\benav\Documents\ObligacionesFiscales"
"C:\Users\benav\AppData\Local\Programs\Python\Launcher\py.exe" -3.14 aplicar_hora.py
echo.
pause
