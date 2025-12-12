Param(
    [string]$ProjectRoot = $PSScriptRoot,
    [string]$VenvPath = ".\.venv",
    [switch]$SkipInstall,
    [switch]$AutoCreateRequirements
)

Set-Location $ProjectRoot

# Resolve venv path: if VenvPath is relative, join with ProjectRoot; else assume absolute
if ([System.IO.Path]::IsPathRooted($VenvPath)) {
    $venvRoot = $VenvPath
} else {
    $venvRoot = Join-Path $ProjectRoot $VenvPath
}
$python = Join-Path $venvRoot "Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Python in venv not found at $python. Activate or create the venv first."
    exit 1
}

if (-not $SkipInstall) {
    $req = Join-Path $ProjectRoot 'requirements.txt'
    if (Test-Path $req) {
        Write-Host "Installing from requirements: $req"
        & $python -m pip install -r $req
    }
    else {
        if ($AutoCreateRequirements) {
            Write-Host "requirements.txt not found; auto-creating default requirements at $req"
            @("mido","python-rtmidi","pyinstaller") | Out-File -FilePath $req -Encoding UTF8
            Write-Host "Created requirements.txt with default packages"
            & $python -m pip install -r $req
        } else {
            Write-Host "requirements.txt not found in repo root; installing default packages"
            & $python -m pip install --upgrade pip setuptools wheel pyinstaller mido python-rtmidi
        }
    }
}

# determine the script path (relative to project root)
$scriptFile = Join-Path $ProjectRoot 'tools\convert_fil_to_mid.py'
if (-not (Test-Path $scriptFile)) {
    Write-Error "Script file '$scriptFile' does not exist. Verify the project root or move tools/convert_fil_to_mid.py into the project."
    exit 1
}
Write-Host "Building fil2mid.exe using venv python: $python"
& $python -m PyInstaller --onefile --name fil2mid --console $scriptFile

if (Test-Path "dist\fil2mid.exe") {
    Write-Host "Built:" (Resolve-Path "dist\fil2mid.exe")
} else {
    Write-Error "Build failed. Check PyInstaller output for missing modules or errors."
    exit 1
}
