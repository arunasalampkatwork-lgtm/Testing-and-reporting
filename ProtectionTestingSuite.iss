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

OutputDir=.
OutputBaseFilename=ProtectionTestingSuite_Setup

Compression=lzma2
SolidCompression=yes
WizardStyle=modern

ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
DisableProgramGroupPage=yes

SetupIconFile=resources\ProtectionTestingSuite.ico
Uninstallable=yes
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}


[Files]

; ---------------------------------------------------------
; Main application
; ---------------------------------------------------------

Source: "ProtectionTestingSuite.exe"; \
    DestDir: "{app}"; \
    Flags: ignoreversion


; ---------------------------------------------------------
; Application resources / main icon
; ---------------------------------------------------------

Source: "resources\*"; \
    DestDir: "{app}\resources"; \
    Flags: ignoreversion recursesubdirs createallsubdirs


; ---------------------------------------------------------
; CLEAN initial application data
; ---------------------------------------------------------

Source: "release_data\*"; \
    DestDir: "{app}\release_data"; \
    Flags: ignoreversion recursesubdirs createallsubdirs


[Dirs]

; Installed application directories
Name: "{app}\resources"

; These are retained by the uninstaller because they are
; user/application data directories.
Name: "{localappdata}\ProtectionTestingSuite"
Name: "{localappdata}\ProtectionTestingSuite\data"
Name: "{localappdata}\ProtectionTestingSuite\projects"


[Icons]

Name: "{autoprograms}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\resources\ProtectionTestingSuite.ico"

Name: "{autodesktop}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\resources\ProtectionTestingSuite.ico"


[Run]

Filename: "{app}\{#MyAppExeName}"; \
    Description: "Launch {#MyAppName}"; \
    Flags: nowait postinstall skipifsilent
