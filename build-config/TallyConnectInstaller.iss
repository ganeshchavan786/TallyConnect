; Inno Setup Script for TallyConnect
; Modern Tally Sync Platform - Professional Installer
; Version 5.6

[Setup]
AppName=TallyConnect
AppVersion=1.5.2
AppPublisher=Vrushali Infotech Pvt Ltd
AppPublisherURL=
AppSupportURL=
AppUpdatesURL=
DefaultDirName={localappdata}\Programs\TallyConnect
DefaultGroupName=TallyConnect
UninstallDisplayIcon={app}\TallyConnect.exe
OutputDir=..\dist
OutputBaseFilename=TallyConnectSetup_v1.5.2
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
SetupIconFile=TallyConnect.ico
UninstallDisplayName=TallyConnect - Modern Tally Sync Platform
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\TallyConnect.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\TallyConnectPortal.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "TallyConnect.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build_info.json"; DestDir: "{app}"; Flags: ignoreversion
; Database will be created automatically by the application on first run
; Source: "TallyConnectDb.db"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\TallyConnect"; Filename: "{app}\TallyConnect.exe"
Name: "{group}\TallyConnect Portal"; Filename: "{app}\TallyConnectPortal.exe"
Name: "{group}\Uninstall TallyConnect"; Filename: "{uninstallexe}"
Name: "{autodesktop}\TallyConnect"; Filename: "{app}\TallyConnect.exe"; Tasks: desktopicon
Name: "{autodesktop}\TallyConnect Portal"; Filename: "{app}\TallyConnectPortal.exe"; Tasks: desktopicon
; Portal auto-starts with Windows (always enabled)
Name: "{userstartup}\TallyConnect Portal"; Filename: "{app}\TallyConnectPortal.exe"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\TallyConnect.exe"; Description: "Launch TallyConnect now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\notes"
Type: files; Name: "{app}\TallyConnectDb.db"
Type: files; Name: "{app}\TallyConnectDb.db-journal"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('Welcome to TallyConnect Setup!' #13#13 
         'This will install TallyConnect - Modern Tally Sync Platform on your computer.', 
         mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('TallyConnect has been successfully installed!' #13#13 
           'Click Finish to launch the application.', 
           mbInformation, MB_OK);
  end;
end;

