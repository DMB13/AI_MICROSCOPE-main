[Setup]
AppName=DMB AI Microscope
AppVersion=1.0
Publisher=Devis / MRRH
DefaultDirName={autopf}\DMB AI Microscope
DefaultGroupName=DMB AI Microscope
OutputBaseFilename=DMB_AI_Microscope_Setup
OutputDir=Output
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\logo.ico

[Files]
; Grabs the entire compiled application and its dependencies
Source: "main_app.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Creates Start Menu and Desktop shortcuts automatically
Name: "{autoprograms}\DMB AI Microscope"; Filename: "{app}\DMB-AI-MICROSCOPE.exe"; IconFilename: "{app}\logo.ico"
Name: "{autodesktop}\DMB AI Microscope"; Filename: "{app}\DMB-AI-MICROSCOPE.exe"; IconFilename: "{app}\logo.ico"

[Run]
; Gives the hospital staff the option to launch immediately after installing
Filename: "{app}\DMB-AI-MICROSCOPE.exe"; Description: "{cm:LaunchProgram,DMB AI Microscope}"; Flags: nowait postinstall skipifsilent
