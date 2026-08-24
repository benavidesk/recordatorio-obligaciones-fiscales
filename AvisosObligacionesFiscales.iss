; Inno Setup script para el REGALO (Avisos Obligaciones Fiscales)
; Genera un instalador .exe para la version instalable del regalo.
; La version portable (ZIP) es independiente; esta script crea el Setup.

#define MyAppName "Avisos Obligaciones Fiscales"
#define MyAppVersion "0.3.0"
#define MyAppExeName "AvisosObligacionesFiscales.exe"

[Setup]
AppId={{8C2F1A5B-6D4E-4A91-B7C3-AvisosObligacion}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Benavides Software
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=AvisosObligacionesFiscales-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; El ejecutable principal + DLLs de Nuitka standalone + bases + config + docs
; (todo lo de la carpeta de distribucion va junto al exe, como standalone)
Source: "distribucion_nuitka\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
