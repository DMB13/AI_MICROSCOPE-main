#define MyAppName "DMB AI Microscope"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Devis Byaru"
#define MyAppExeName "DMB AI Microscope.exe"

[Setup]
AppId={{DMB-AI-MICROSCOPE-MBEYA-2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installers
OutputBaseFilename=DMB_AI_Microscope_v1
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
; This grabs the entire bundled application from the Briefcase build folder
Source: "build\dmbaimicroscope\windows\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Filename: "{app}\{#MyAppExeName}"; Flags: nowait postinstall skipifsilent
