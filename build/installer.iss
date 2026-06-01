; Inno Setup Script for DMB AI Microscope
; Production-grade Windows Installer

[Setup]
AppId={{A1B2C3D4-E5F6-4A5B-8C7D-9E0F1A2B3C4D}
AppName=DMB AI Microscope
AppVersion=1.0.0
AppPublisher=DMB
DefaultDirName={pf}\DMB\AI_Microscope
DefaultGroupName=DMB AI Microscope
AllowNoIcons=yes
OutputDir=..\Setup
OutputBaseFilename=DMB_AI_Microscope_Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\DMB_AI_Microscope.exe
ChangesAssociations=yes
DisableDirPage=no
DisableProgramGroupPage=yes
DisableFinishedPage=no
DisableReadyPage=no
DisableStartupPrompt=yes
DisableWelcomePage=no
AlwaysShowDirOnReadyPage=yes
AlwaysShowGroupOnReadyPage=yes
AppCopyright=Copyright © 2026 DMB. All rights reserved.
VersionInfoVersion=1.0.0.0
VersionInfoCompany=DMB
VersionInfoDescription=AI-powered bacterial identification microscope application
VersionInfoProductName=DMB AI Microscope
VersionInfoProductVersion=1.0.0
MinVersion=6.1sp1
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
; Enable disk spanning for large installations (>4GB)
DiskSpanning=yes
DiskSliceSize=2100000000

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"
Name: "quicklaunchicon"; Description: "Create a &Quick Launch icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Main executable and _internal folder from PyInstaller build (onedir mode)
Source: "..\dist\DMB_AI_Microscope\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
; README file
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
; Logo/icon file
Source: "..\logo.ico"; DestDir: "{app}"; Flags: ignoreversion
; Model files - critical for the application
Source: "..\model\best_clinical_rugged_1777619657.keras"; DestDir: "{app}\model"; Flags: ignoreversion
Source: "..\model\class_indices.json"; DestDir: "{app}\model"; Flags: ignoreversion
Source: "..\model\species_33_mapping.json"; DestDir: "{app}\model"; Flags: ignoreversion
Source: "..\model\clinical_records_schema.sql"; DestDir: "{app}\model"; Flags: ignoreversion
; Config files
Source: "..\config\*.py"; DestDir: "{app}\config"; Flags: ignoreversion
; Documentation
Source: "..\docs\*.md"; DestDir: "{app}\docs"; Flags: ignoreversion
; Initial storage files
Source: "..\storage\users.json"; DestDir: "{app}\storage"; Flags: ignoreversion
Source: "..\storage\session_state.json"; DestDir: "{app}\storage"; Flags: ignoreversion
Source: "..\storage\doc_viewer_config.json"; DestDir: "{app}\storage"; Flags: ignoreversion
; Database (if exists, will be created fresh if not)
Source: "..\clinical_records.db"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\DMB AI Microscope"; Filename: "{app}\DMB_AI_Microscope.exe"
Name: "{group}\Uninstall DMB AI Microscope"; Filename: "{uninstallexe}"
Name: "{autodesktop}\DMB AI Microscope"; Filename: "{app}\DMB_AI_Microscope.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\DMB AI Microscope"; Filename: "{app}\DMB_AI_Microscope.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\DMB_AI_Microscope.exe"; Description: "Launch DMB AI Microscope"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Registry]
; Register the application for file associations if needed in the future
Root: HKCU; Subkey: "Software\DMB\AI_Microscope"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\DMB\AI_Microscope"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"; Flags: uninsdeletevalue

[Code]
// Custom installation logic
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

// Pre-installation checks
function NextButtonClick(CurPageID: Integer): Boolean;
var
  FreeSpace, TotalSpace: Int64;
begin
  Result := True;
  
  // Check available disk space (need at least 2GB)
  if CurPageID = wpSelectDir then
  begin
    if GetSpaceOnDisk64(WizardDirValue, FreeSpace, TotalSpace) then
    begin
      if FreeSpace < 2147483648 then
      begin
        MsgBox('Insufficient disk space. At least 2 GB of free space is required.', mbError, MB_OK);
        Result := False;
      end;
    end;
  end;
end;

// Post-installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create necessary directories if they don't exist
    ForceDirectories(ExpandConstant('{app}\storage\backups'));
    ForceDirectories(ExpandConstant('{app}\storage\exports'));
    ForceDirectories(ExpandConstant('{app}\storage\images'));
    ForceDirectories(ExpandConstant('{app}\exports'));
    ForceDirectories(ExpandConstant('{app}\logs'));
  end;
end;