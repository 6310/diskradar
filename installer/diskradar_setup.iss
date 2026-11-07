; ============================================================================
; Script Inno Setup 6 Oficial — Geio DiskRadar (Instalação Canônica & Upgrade)
; Garante instância única instalada via AppId imutável, comparação SemVer e
; limpeza transacional [InstallDelete] sem race condition de unins000.exe.
; ============================================================================

#define MyAppId "{{8B49E7C2-1C2A-4D4F-9E62-F9F71B39D4E2}"
#define MyAppName "Geio DiskRadar"
#define MyAppVersion "2.3.0"
#define MyAppPublisher "Geio Forensics & Security"
#define MyAppURL "https://github.com/6310/diskradar"
#define MyAppExeName "DiskRadar.exe"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\GeioDiskRadar
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist_installer
OutputBaseFilename=Geio_DiskRadar_Setup_v{#MyAppVersion}
SetupIconFile=..\ui\assets\diskradar.ico
UninstallDisplayIcon={app}\ui\assets\diskradar.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
CloseApplicationsFilter=DiskRadar.exe,python.exe,pythonw.exe
UsePreviousAppDir=yes
DirExistsWarning=no
DisableDirPage=auto

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

; Limpeza transacional segura de código antigo antes de extrair a nova versão (sem race condition!)
[InstallDelete]
Type: filesandordirs; Name: "{app}\core"
Type: filesandordirs; Name: "{app}\ui"
Type: files; Name: "{app}\DiskRadar-*.exe"
Type: files; Name: "{userdesktop}\DiskRadar*.lnk"
Type: files; Name: "{userdesktop}\Geio DiskRadar v*.lnk"

[Files]
Source: "..\main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\version.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LEIAME.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Executar_DiskRadar.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Instalar_DiskRadar.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Desinstalar_DiskRadar.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\ui\*"; DestDir: "{app}\ui"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\Executar_DiskRadar.bat"; WorkingDir: "{app}"; IconFilename: "{app}\ui\assets\diskradar.ico"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\Executar_DiskRadar.bat"; WorkingDir: "{app}"; IconFilename: "{app}\ui\assets\diskradar.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\Executar_DiskRadar.bat"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent shellexec

[Code]
function ParseSemVer(VStr: String): Int64;
var
  P: Integer;
  Major, Minor, PatchNum: Int64;
begin
  Major := 0; Minor := 0; PatchNum := 0;
  if (Length(VStr) > 0) and ((VStr[1] = 'v') or (VStr[1] = 'V')) then
    Delete(VStr, 1, 1);
  P := Pos('.', VStr);
  if P > 0 then begin
    Major := StrToIntDef(Copy(VStr, 1, P - 1), 0);
    Delete(VStr, 1, P);
    P := Pos('.', VStr);
    if P > 0 then begin
      Minor := StrToIntDef(Copy(VStr, 1, P - 1), 0);
      Delete(VStr, 1, P);
      PatchNum := StrToIntDef(VStr, 0);
    end else
      Minor := StrToIntDef(VStr, 0);
  end else
    Major := StrToIntDef(VStr, 0);
  Result := (Major * 1000000) + (Minor * 1000) + PatchNum;
end;

function InitializeSetup(): Boolean;
var
  OldVersion: String;
  NewVerNum, OldVerNum: Int64;
  RegKey: String;
begin
  Result := True;
  NewVerNum := ParseSemVer('{#MyAppVersion}');
  RegKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1';

  if RegQueryStringValue(HKCU, RegKey, 'DisplayVersion', OldVersion) or
     RegQueryStringValue(HKLM, RegKey, 'DisplayVersion', OldVersion) then
  begin
    OldVerNum := ParseSemVer(OldVersion);
    if OldVerNum > NewVerNum then
    begin
      MsgBox('Bloqueio de Segurança: Uma versão mais recente (v' + OldVersion + ') do Geio DiskRadar já está instalada neste sistema.' + #13#10 +
             'Não é permitido sobrescrever com uma versão anterior (v{#MyAppVersion}).', mbError, MB_OK);
      Result := False;
      Exit;
    end;
  end;
end;
