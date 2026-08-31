' ejecutar_aviso_silencioso.vbs
' Lanza AvisosAutomaticos.exe --notificar SIN ventana de consola,
' para que solo se muestre la notificacion (MessageBox) al usuario.
' Usa la ruta de LA MISMA carpeta donde esta este .vbs (funciona sin importar
' donde se instale la aplicacion).
'
' El 0 en el segundo parametro = ventana oculta (no muestra cmd/consola).

Set fso = CreateObject("Scripting.FileSystemObject")
carpeta = fso.GetParentFolderName(WScript.ScriptFullName)
exe = carpeta & "\AvisosAutomaticos.exe"

Set sh = CreateObject("WScript.Shell")
sh.Run """" & exe & """ --notificar", 0, False
