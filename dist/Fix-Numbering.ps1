#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Renumber MIDI files to use consistent 3-digit padding in folders with 100+ files.

.DESCRIPTION
    Scans directories for MIDI files. If a directory has 100+ files, renumbers ALL files
    to use 3-digit padding (001, 002, ..., 100, 101, etc.) to ensure correct sorting.

.PARAMETER Path
    Directory to process. Defaults to current directory.

.PARAMETER Recurse
    Process subdirectories recursively.

.EXAMPLE
    .\Fix-Numbering.ps1 -Path "\\RackStation\Music\Piano\MIDI" -Recurse
    Fix numbering in all subdirectories
#>

param(
    [string]$Path = ".",
    [switch]$Recurse
)

function Fix-FolderNumbering {
    param([string]$FolderPath)
    
    # Get all .mid files in this folder
    $files = Get-ChildItem -Path $FolderPath -Filter "*.mid" -File | Sort-Object Name
    
    if ($files.Count -lt 100) {
        return $null  # No need to fix - less than 100 files
    }
    
    Write-Host ""
    Write-Host "="*80 -ForegroundColor Cyan
    Write-Host "Folder: $FolderPath" -ForegroundColor Cyan
    Write-Host "Files: $($files.Count) (need 3-digit padding)" -ForegroundColor Yellow
    Write-Host "="*80 -ForegroundColor Cyan
    Write-Host ""
    
    $changes = @()
    
    foreach ($file in $files) {
        $baseName = $file.BaseName
        
        # Match various patterns to extract track number
        # Pattern: NN - Title or NNN - Title
        if ($baseName -match '^(\d{2,3})\s+-\s+(.+)$') {
            $trackNum = [int]$matches[1]
            $title = $matches[2]
            
            # Build new name with 3-digit padding
            $newBaseName = "{0:D3} - {1}" -f $trackNum, $title
            $newName = $newBaseName + $file.Extension.ToLower()
            
            if ($newName -cne $file.Name) {
                $changes += [PSCustomObject]@{
                    OldName = $file.Name
                    NewName = $newName
                    FullPath = $file.FullName
                    Folder = $FolderPath
                }
            }
        }
    }
    
    return $changes
}

Write-Host "Scanning for folders with 100+ files..." -ForegroundColor Cyan
Write-Host ""

$allChanges = @()

if ($Recurse) {
    # Get all subdirectories
    $folders = Get-ChildItem -Path $Path -Directory -Recurse | Select-Object -ExpandProperty FullName
    $folders += $Path  # Include root folder
} else {
    $folders = @($Path)
}

foreach ($folder in $folders) {
    $changes = Fix-FolderNumbering -FolderPath $folder
    if ($changes) {
        $allChanges += $changes
        
        # Show preview
        foreach ($change in $changes) {
            Write-Host "  $($change.OldName)" -ForegroundColor Yellow
            Write-Host "  → $($change.NewName)" -ForegroundColor Green
            Write-Host ""
        }
    }
}

if ($allChanges.Count -eq 0) {
    Write-Host "No files need renumbering." -ForegroundColor Green
    Write-Host ""
    exit 0
}

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "Summary: $($allChanges.Count) file(s) need renumbering" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

$response = Read-Host "Proceed with renaming? (y/n)"
if ($response -ne 'y') {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Renaming files..." -ForegroundColor Cyan

$successCount = 0
$errorCount = 0

foreach ($change in $allChanges) {
    try {
        $newPath = Join-Path $change.Folder $change.NewName
        
        # Check if target exists
        if (Test-Path -LiteralPath $newPath) {
            Write-Host "ERROR: Target already exists: $($change.NewName)" -ForegroundColor Red
            $errorCount++
            continue
        }
        
        # Rename
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
Write-Host "="*80 -ForegroundColor Green
Write-Host "Complete!" -ForegroundColor Green
Write-Host "  Success: $successCount files" -ForegroundColor Green
if ($errorCount -gt 0) {
    Write-Host "  Errors:  $errorCount files" -ForegroundColor Red
}
Write-Host "="*80 -ForegroundColor Green
Write-Host ""
