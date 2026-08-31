=== REVISIÓN DE CÓDIGO — Recordatorio de Obligaciones Fiscales ===
Método: five-axis review (code-review-and-quality) + security (security-and-hardening)
Fecha: 2026-08-31

NOTA DE CONTEXTO: el software es Python de escritorio/task-scheduler (Windows),
no web. Se adaptan los ejes (seguridad enfocada a comando de sistema, rutas,
datos locales) y varios patrones web (XSS, cookies, HTTPS) NO aplican.

=== EJE 1: CORRECTNESS ===
[OK] Los cambios de hoy (modo consola, rutas sys.frozen, notificar siempre,
  nombre país, _escribir_reemplazando) verificados por pruebas reales: el log
  se actualiza desde tarea y desde acceso directo.

[CORRECTNESS - MEDIO] _escribir_reemplazando hace os.remove() antes de abrir en "w".
  Si el archivo NO existe, os.path.exists es False (no lo borra) -> bien.
  PERO: si os.remove falla (PermissionError) silenciosamente y el open "w" tambien
  falla, el log se pierde en silencio. Aceptable (mejor que crashear) pero
  no hay registro de que el guardado fallo.

[CORRECTNESS - MEDIO] En util_fiscal.proximo_vencimiento, para la regla 'dias'
  se itera sobre [mes actual, mes siguiente]. Si hoy == 31 y el mes siguiente
  no tiene ese dia (ej 31 de fila), date() lanza ValueError -> continue.
  OK, pero no cubre salto de ANIO (ej 31-dic -> 31-ene esta bien, pero si un
  vencimiento fijo de diciembre 31 y hoy es 31-ene... cubre). Edge case raro.

=== EJE 2: READABILITY & SIMPLICITY ===
[OK] Nombres claros (ruta_base, aplicar_tarea, generar_mensaje, _escribir_reemplazando).

[READABILITY - BAJO] comentario redundante "import win32com.client  # no disponible"
  en _carpeta_inicio de gui.py: inoracion innecesaria, confunde.

[READABILITY - MEDIO] gui.py ha crecido bastante. _crear_acceso_inicio construye
  un comando powershell con string de escape anidado (.format con \\\\ duplicado).
  Fragil y dificil de leer. Considerar crear el .lnk de otra forma o extraer.

=== EJE 3: ARCHITECTURE ===
[ARQUITECTURA - ALTO] FRAGMENTACION: el set de "como programar el aviso" esta en:
  - gui.py (aplicar_tarea + _carpeta_inicio + _crear_acceso_inicio + _eliminar)
  - aplicar_hora.py (comando_tarea + su propia creacion de tareas)
  Duplicacion: aplicar_hora.py replica la logica de aplicar_tarea. Deberia
  compartir un modulo comun (ej scheduler_fiscal.py) que ambas llamen.
  Esto es exactamente el "bespoke near-duplicate" que senala la skill.

[ARQUITECTURA - ALTO] MECANISMOS REDUNDANTES de ejecucion del aviso:
  - ejecutar_avisos.bat (via py.exe)
  - AvisosAutomaticos.exe (via tarea/startup, con --notificar)
  - ejecutar_aviso_silencioso.vbs (launcher)
  3 caminos para lo mismo. OK por momentos (bat para dev, exe para prod) pero
  complica; el .bat ya no es necesario para el usuario final.

=== EJE 4: SECURITY ===
[SIN VULNERABILIDAD CRITICA] El software procesa datos locales (bases JSON) y
  crea tareas de Windows. Buen resultado: no hay input de usuario remoto, no hay
  SQL, no hay secreto en codigo, no hay red saliente en la logica de avisos.

[SECURITY - MEDIO] Inyeccion de comando via schtasks: aplicar_tarea() y
  aplicar_hora.py pasan rutas a schtasks /TR. Las rutas provienen de RUTA (carpeta
  del exe) y hora (validada 0-23/0-59). El riesgo: si la ruta de instalacion
  contuviera caracteres especiales (comillas, &, |) podria romper/inyectar en la
  linea de comando. Mitigacion actual: rutas predecibles. ACCION RECOMENDADA:
  validar que la ruta no contenga caracteres de peligro para cmd, o usar la API
  COM de Task Scheduler en vez de schtasks string.

[SECURITY - BAJO] El .vbs usa sh.Run con ruta + argumento. Misma consideracion
  de caracteres especiales en ruta de instalacion.

[SECURITY - BAJO/MEDIO] El aviso se lanza al INICIO de sesion codigo --notificar
  que ejecuta AvisosAutomaticos.exe. Si un atacante con acceso a la carpeta de
  instalacion reemplaza AvisosAutomaticos.exe por un binario malicioso, ese corre
  al iniciar sesion. NO es un riesgo nuevo (es un software local no firmado),
  pero es un vector a tener en cuenta al distribuir.

=== EJE 5: PERFORMANCE ===
[OK] El aviso diario es un script Python que lee 1-19 JSON pequenos y calcula
  fechas. No es un cuello de botella. La notificacion es inmediata.
[OK] Sin N+1, sin loops unbounded, sin fetch masivo.

=== OTRAS OBSERVACIONES ===
[FYI] No hay TESTS automatizados. La skill test-driven-development recomienda
  al menos tests de las funciones de calculo (util_fiscal) y generacion de mensaje
  (generar_mensaje). Ahora mismo la verificacion es manual (ejecutar y ver log).
[FYI] git-workflow-and-versioning: los commits de hoy son descriptivos y correctos.

=== VERDICTO ===
El software CIERTO mejorar la salud del codigo. Las mejoras de hoy lo hicieron
mas robusto (sin Python, notifica siempre, nombre completo). Se aprueba.

MEJORAS RECOMENDADAS (ordenadas por leverage):
1. [ARQ, ALTA] Extraer la logica de "programar el aviso" (schtasks + startup) a un
   modulo compartido unico, y que gui.py y aplicar_hora.py lo usen. Elimina la
   duplicacion.
2. [SEC, MEDIA] Validar la ruta de instalacion contra caracteres peligrosos de cmd
   antes de pasarla a schtasks /TR (o usar API COM de Task Scheduler).
3. [TEST, MEDIA] Agregar tests unitarios para util_fiscal.calcular_vencimientos_ventana,
   proximo_vencimiento, y generar_mensaje (cobertura de la logica critica).
4. [READ, BAJA] Refactorizar _crear_acceso_inicio para construir el .lnk sin el
   string powershell anidado (mas legible y robusto).
5. [READ, BAJA] Quitar el import/comment win32com muerto en _carpeta_inicio.
6. [SEC, BAJA] Considerar una nota/README de que el aviso al inicio executa exe
   local reemplazable: educar sobre integridad de la instalacion.

=== ESTADO DE IMPLEMENTACION (2026-08-31) ===
[1] HECHO - Creado scheduler_fiscal.py (modulo unico). gui.py y aplicar_hora.py
    ya no duplican schtasks/startup; delegan en scheduler_fiscal.aplicar().
[2] HECHO - validar_ruta() en scheduler_fiscal lanza RutaInsegura si la ruta
    contiene & | < > ^ % " ( )  antes de pasarla a schtasks /TR.
[3] HECHO - tests_obligaciones.py: 13 tests unitarios (util_fiscal vencimientos,
    generar_mensaje, validar_ruta). Todos pasan.
    Ejecutar: py -3.14 -m unittest tests_obligaciones -v
[4] HECHO - crear_acceso_inicio() reescrito en scheduler_fiscal con sintetizacion
    PowerShell clara (sin string .lnk anidado fragil de gui.py).
[5] HECHO - Eliminado import win32com/comentario muerto y las constantes sin uso
    (TAREA/BAT/EXE_AVISOS/VBS) de gui.py.

