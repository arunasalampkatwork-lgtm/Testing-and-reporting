$ErrorActionPreference = "Stop"

$InstallerDir = $PSScriptRoot
$Root = Split-Path -Parent $InstallerDir

Set-Location $Root

Write-Host ""
Write-Host "============================================"
Write-Host " Protection Testing Suite - Build"
Write-Host "============================================"
Write-Host ""

# ---------------------------------------------------------
# Prefer the project's virtual environment.
# ---------------------------------------------------------

$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (!(Test-Path $Python)) {
    $Python = "python"
}

Write-Host "Project root : $Root"
Write-Host "Using Python : $Python"

& $Python --version

if ($LASTEXITCODE -ne 0) {
    throw "Python could not be started."
}

# ---------------------------------------------------------
# Install / update build tools.
# ---------------------------------------------------------

Write-Host ""
Write-Host "Checking PyInstaller..."

& $Python -m pip install pyinstaller

if ($LASTEXITCODE -ne 0) {
    throw "Unable to install PyInstaller."
}

# ---------------------------------------------------------
# Clean previous build.
# ---------------------------------------------------------

Write-Host ""
Write-Host "Cleaning previous build..."

Remove-Item `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue `
    (Join-Path $Root "build")

Remove-Item `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue `
    (Join-Path $Root "dist")

# ---------------------------------------------------------
# Verify the important files before building.
# ---------------------------------------------------------

$MainPy = Join-Path $Root "main.py"
$Spec = Join-Path $InstallerDir "ProtectionTestingSuite.spec"

if (!(Test-Path $MainPy)) {
    throw "main.py was not found at $MainPy"
}

if (!(Test-Path $Spec)) {
    throw "ProtectionTestingSuite.spec was not found at $Spec"
}

Write-Host ""
Write-Host "main.py      : $MainPy"
Write-Host "spec         : $Spec"

# ---------------------------------------------------------
# Build.
#
# IMPORTANT:
# The spec file is inside installer\, but its paths point
# back to the project root.
# ---------------------------------------------------------

Write-Host ""
Write-Host "Running PyInstaller..."

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    $Spec

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
}

# ---------------------------------------------------------
# Verify executable.
# ---------------------------------------------------------

$Exe = Join-Path $Root "dist\ProtectionTestingSuite.exe"

if (!(Test-Path $Exe)) {
    throw "PyInstaller finished without creating $Exe"
}

Write-Host ""
Write-Host "Executable created:"
Write-Host $Exe

# ---------------------------------------------------------
# Find Inno Setup.
# ---------------------------------------------------------

$ISCCCandidates = @(
    "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)

$ISCC = $null

foreach ($Candidate in $ISCCCandidates) {

    if (Test-Path $Candidate) {

        $ISCC = $Candidate

        break
    }
}

if ($null -eq $ISCC) {

    Write-Warning ""
    Write-Warning "Inno Setup 6 was not found."
    Write-Warning "The standalone EXE was built successfully."
    Write-Warning ""
    Write-Warning "Install Inno Setup 6 and run this script again"
    Write-Warning "to create ProtectionTestingSuite_Setup.exe."
    Write-Warning ""

    exit 0
}

# ---------------------------------------------------------
# Build installer.
# ---------------------------------------------------------

Write-Host ""
Write-Host "Building Windows installer..."
Write-Host "Inno Setup : $ISCC"

$Iss = Join-Path $InstallerDir "ProtectionTestingSuite.iss"

& $ISCC $Iss

if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup build failed."
}

$Installer = Join-Path `
    $Root `
    "installer_output\ProtectionTestingSuite_Setup.exe"

if (!(Test-Path $Installer)) {
    throw "Inno Setup finished without creating $Installer"
}

Write-Host ""
Write-Host "============================================"
Write-Host " BUILD COMPLETE"
Write-Host "============================================"
Write-Host ""
Write-Host "Executable:"
Write-Host $Exe
Write-Host ""
Write-Host "Installer:"
Write-Host $Installer
Write-Host ""
