#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Find and replace text in filenames in a directory.

.DESCRIPTION
    Renames files by replacing a specified pattern with a new pattern.
    Handles spaces, special characters, and provides preview before renaming.

.PARAMETER Path
    Directory containing files to rename. Defaults to current directory.

.PARAMETER Find
    Text pattern to find in filenames (case-insensitive).

.PARAMETER Replace
    Text to replace the found pattern with.

.PARAMETER Filter
    File filter pattern (default: *.mid).

.PARAMETER Recurse
    Process subdirectories recursively.

.EXAMPLE
    .\Rename-FindReplace.ps1 -Find "Frederic Francois" -Replace ""
    Remove "Frederic Francois" from all .mid files in current directory

.EXAMPLE
    .\Rename-FindReplace.ps1 -Path "C:\Music" -Find "Op.25" -Replace "Op-25" -Filter "*.mid"
    Replace "Op.25" with "Op-25" in all .mid files

.EXAMPLE
    .\Rename-FindReplace.ps1 -Find " - " -Replace " " -Recurse
    Replace " - " with single space in all .mid files recursively

.EXAMPLE
    .\Rename-FindReplace.ps1 -Find ", " -Replace " " -Filter "*.*"
    Replace ", " with space in all files (not just .mid)
#>

param(
    [string]$Path = ".",
    [Parameter(Mandatory=$true)]
    [string]$Find,
    [Parameter(Mandatory=$true)]
    [AllowEmptyString()]
    [string]$Replace,
    [string]$Filter = "*.mid",
    [switch]$Recurse
)

# Get all matching files
$searchParams = @{
    Path = $Path
    Filter = $Filter
    File = $true
}

if ($Recurse) {
    $searchParams['Recurse'] = $true
}

$files = Get-ChildItem @searchParams | Where-Object {
    $_.Name -like "*$Find*"
}

if ($files.Count -eq 0) {
    Write-Host "No files found matching filter '$Filter' containing '$Find'" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($files.Count) file(s) to rename" -ForegroundColor Cyan
Write-Host ""
Write-Host "Find:    '$Find'" -ForegroundColor Yellow
Write-Host "Replace: '$Replace'" -ForegroundColor Green
Write-Host ""
Write-Host "Preview of changes:" -ForegroundColor Cyan
Write-Host ("=" * 80)

# Preview changes
$changes = @()
foreach ($file in $files) {
    $newName = $file.Name -replace [regex]::Escape($Find), $Replace
    
    # Skip if no change
    if ($newName -eq $file.Name) {
        continue
    }
    
    $changes += [PSCustomObject]@{
        Directory = $file.Directory.FullName
        OldName = $file.Name
        NewName = $newName
        FullPath = $file.FullName
    }
}

if ($changes.Count -eq 0) {
    Write-Host "No changes needed (pattern not found in any filenames)" -ForegroundColor Yellow
    exit 0
}

# Show preview
foreach ($change in $changes) {
    Write-Host "Old: $($change.OldName)" -ForegroundColor Red
    Write-Host "New: $($change.NewName)" -ForegroundColor Green
    if ($changes.Count -le 20 -and $Recurse) {
        Write-Host "     ($($change.Directory))" -ForegroundColor DarkGray
    }
    Write-Host ""
}

if ($changes.Count -gt 20) {
    Write-Host "... showing first 20 of $($changes.Count) changes" -ForegroundColor DarkGray
    Write-Host ""
}

Write-Host ("=" * 80)
Write-Host ""
Write-Host "Ready to rename $($changes.Count) file(s)" -ForegroundColor Cyan

# Confirm
$response = Read-Host "Proceed with rename? (y/n)"
if ($response -ne 'y') {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 0
}

# Perform renames
Write-Host ""
Write-Host "Renaming files..." -ForegroundColor Cyan
$successCount = 0
$errorCount = 0

foreach ($change in $changes) {
    try {
        $newPath = Join-Path $change.Directory $change.NewName
        
        # Check if target already exists
        if (Test-Path -LiteralPath $newPath) {
            Write-Host "ERROR: Target already exists: $($change.NewName)" -ForegroundColor Red
            $errorCount++
            continue
        }
        
        # Rename using -LiteralPath to handle special characters
        Rename-Item -LiteralPath $change.FullPath -NewName $change.NewName -ErrorAction Stop
        $successCount++
        
        if ($successCount % 10 -eq 0) {
            Write-Host "  Renamed $successCount files..." -ForegroundColor DarkGray
        }
    }
    catch {
        Write-Host "ERROR renaming $($change.OldName): $_" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host ("=" * 80)
Write-Host "Complete!" -ForegroundColor Green
Write-Host "  Success: $successCount files" -ForegroundColor Green
if ($errorCount -gt 0) {
    Write-Host "  Errors:  $errorCount files" -ForegroundColor Red
}
Write-Host ""
