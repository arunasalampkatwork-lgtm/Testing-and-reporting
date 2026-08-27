#define MyAppName "Protection Testing Suite"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "CPCL"
#define MyAppExeName "ProtectionTestingSuite.exe"

[Setup]
AppId={{C3E5C8E1-7F11-4A36-9F9A-CPCLPTS1001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Protection Testing Suite
DefaultGroupName={#MyAppName}
OutputDir=..\installer_output
OutputBaseFilename=ProtectionTestingSuite_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=ProtectionTestingSuite_1.ico

[Files]
Source: "..\dist\ProtectionTestingSuite.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\projects\*"; DestDir: "{app}\projects"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
