# Protection Testing Suite Installer

## Fixed build-path issue

The PyInstaller spec file is located in:

    installer\ProtectionTestingSuite.spec

The project root is one directory above it.

The corrected spec therefore resolves:

    PROJECT_ROOT = Path(SPECPATH).resolve().parent

This prevents PyInstaller from looking for:

    installer\data

instead of:

    data

## Project layout

The expected layout is:

    ProtectionTestingSuite\
    |
    +-- main.py
    +-- app\
    +-- data\
    +-- projects\
    +-- installer\
        +-- ProtectionTestingSuite.spec
        +-- ProtectionTestingSuite.iss
        +-- ProtectionTestingSuite_2.ico
        +-- version_info.txt
        +-- build_installer.ps1
        +-- build_installer.bat

## Build

From the project root:

    .\installer\build_installer.ps1

If PowerShell blocks the script:

    Set-ExecutionPolicy -Scope Process Bypass
    .\installer\build_installer.ps1

Or simply double-click:

    installer\build_installer.bat

## Output

PyInstaller creates:

    dist\ProtectionTestingSuite.exe

If Inno Setup 6 is installed, the full installer is created at:

    installer_output\ProtectionTestingSuite_Setup.exe

## Desktop shortcut

The Inno Setup installer creates:

    Desktop\Protection Testing Suite

and a Start Menu shortcut.

## Runtime data

Installed applications use:

    %LOCALAPPDATA%\ProtectionTestingSuite\data
    %LOCALAPPDATA%\ProtectionTestingSuite\projects

The application executable itself is installed under Program Files.

This prevents permission problems when the application writes:

- AssetDatabase.xlsx
- TestHistory.xlsx
- assets.json
- components.json
- tests.json
- asset_links.json
- other project files

Existing user data is not overwritten when an application update is installed.

## If you already ran the previous installer

The old version may have placed files in the wrong location or failed to
write data because of Program Files permissions.

After installing the corrected version, the application should use:

    %LOCALAPPDATA%\ProtectionTestingSuite

for its writable data.
