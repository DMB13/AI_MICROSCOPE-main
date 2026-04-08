[Setup]
AppName=DMB AI Microscope
AppVersion=1.0
AppPublisher=Devis / MRRH
DefaultDirName={autopf}\DMB AI Microscope
DefaultGroupName=DMB AI Microscope
; The setup file's icon during installation
SetupIconFile=logo.ico
; The icon shown in Windows Settings / Add-Remove Programs
UninstallDisplayIcon={app}\DMB-AI-MICROSCOPE.exe
OutputBaseFilename=DMB_AI_Microscope_Setup
OutputDir=Output
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
; Source: Points to the folder Nuitka creates in the root directory
Source: "main_app.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Safer: Pointing to the .exe extracts the embedded icon automatically
Name: "{autoprograms}\DMB AI Microscope"; Filename: "{app}\DMB-AI-MICROSCOPE.exe"; IconFilename: "{app}\DMB-AI-MICROSCOPE.exe"
Name: "{autodesktop}\DMB AI Microscope"; Filename: "{app}\DMB-AI-MICROSCOPE.exe"; IconFilename: "{app}\DMB-AI-MICROSCOPE.exe"

[Run]
; Matches your manual edit to allow immediate launch
Filename: "{app}\DMB-AI-MICROSCOPE.exe"; Description: "{cm:LaunchProgram,DMB AI Microscope}"; Flags: nowait postinstall skipifsilent
