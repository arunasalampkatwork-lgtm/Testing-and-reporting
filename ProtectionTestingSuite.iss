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

; =========================================================
; APPLICATION
; =========================================================

Source: "ProtectionTestingSuite.exe"; \
    DestDir: "{app}"; \
    Flags: ignoreversion


; =========================================================
; APPLICATION RESOURCES
; =========================================================

Source: "resources\*"; \
    DestDir: "{app}\resources"; \
    Flags: ignoreversion recursesubdirs createallsubdirs


[Dirs]

; =========================================================
; PERSISTENT USER DATA
;
; These directories are created empty.
;
; NO development projects or test data are installed.
; =========================================================

Name: "{localappdata}\ProtectionTestingSuite"

Name: "{localappdata}\ProtectionTestingSuite\data"

Name: "{localappdata}\ProtectionTestingSuite\projects"


[Icons]

; =========================================================
; START MENU SHORTCUT
; =========================================================

Name: "{autoprograms}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\resources\ProtectionTestingSuite.ico"


; =========================================================
; DESKTOP SHORTCUT
; =========================================================

Name: "{autodesktop}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\resources\ProtectionTestingSuite.ico"


[UninstallDelete]

; =========================================================
; DO NOT DELETE USER DATA
;
; Projects, test history, assets and thermal templates
; are deliberately preserved during uninstall.
; =========================================================

; Nothing is specified here intentionally.


[Run]

; =========================================================
; LAUNCH APPLICATION AFTER INSTALLATION
; =========================================================

Filename: "{app}\{#MyAppExeName}"; \
    Description: "Launch {#MyAppName}"; \
    Flags: nowait postinstall skipifsilent