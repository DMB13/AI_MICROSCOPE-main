; --- DMB AI Microscope Cloud-Ready Setup Script ---
#define MyAppName "DMB AI Microscope"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "DMB AI Research"
#define MySourceDir "." 

[Setup]
AppId={{DMB-AI-MICROSCOPE-MBEYA-2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; GitHub Actions will look for the installer in this folder
OutputDir=installers
OutputBaseFilename=DMB_AI_Microscope_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
; The path is now relative to where the .iss file sits in your repo
Source: "src\dmbaimicroscope\app.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\dmbaimicroscope\services.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\dmbaimicroscope\settings_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\dmbaimicroscope\settings_dialog.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\dmbaimicroscope\__init__.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\dmbaimicroscope\__main__.py"; DestDir: "{app}"; Flags: ignoreversion

; Copying the Brain and logic folders
Source: "src\dmbaimicroscope\model\*"; DestDir: "{app}\model"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\dmbaimicroscope\inference\*"; DestDir: "{app}\inference"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\dmbaimicroscope\resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\app.py"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\app.py"; Tasks: desktopicon
