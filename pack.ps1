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
            @("mido","pillow","python-rtmidi","pyinstaller") | Out-File -FilePath $req -Encoding UTF8
            Write-Host "Created requirements.txt with default packages"
            & $python -m pip install -r $req
        } else {
            Write-Host "requirements.txt not found in repo root; installing default packages"
            & $python -m pip install --upgrade pip setuptools wheel pyinstaller mido pillow python-rtmidi
        }
    }
}

# determine the script path (relative to project root)
$scriptFile = Join-Path $ProjectRoot 'tools\convert_fil_to_mid.py'
if (-not (Test-Path $scriptFile)) {
    Write-Error "Script file '$scriptFile' does not exist. Verify the project root or move tools/convert_fil_to_mid.py into the project."
    exit 1
}
Write-Host "`nBuilding executables..."

$specs = @(
    "fil2mid.spec",
    "mid_title_from_filename.spec",
    "clean_filenames.spec",
    "patch_dkvsong_coverart.spec",
    "normalize_coverart.spec",
    "add_xf_solo_metadata.spec",
    "embed_tags_metadata.spec",
    "wav_to_mp3.spec",
    "convert_midi_type.spec"
)

foreach ($spec in $specs) {
    $specPath = Join-Path $ProjectRoot $spec
    if (Test-Path $specPath) {
        Write-Host "`nBuilding $spec..."
        & $python -m PyInstaller --clean $specPath
    } else {
        Write-Warning "Spec file not found: $spec"
    }
}

Write-Host "`n=== Build Complete ==="
Write-Host "Executables in dist/:"
Get-ChildItem "dist\*.exe" | ForEach-Object { Write-Host "  - $($_.Name)" }
