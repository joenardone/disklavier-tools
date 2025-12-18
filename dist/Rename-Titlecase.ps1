# Rename files with track numbers and apply title case
param(
    [string]$Path = "."
)

$textInfo = (Get-Culture).TextInfo

Write-Host "=== PREVIEW MODE ===" -ForegroundColor Cyan
Write-Host "Working directory: $Path" -ForegroundColor Gray
Write-Host ""

# Count all .mid files to determine padding
$allFiles = Get-ChildItem -Path $Path -Filter "*.mid" -File
$padding = if ($allFiles.Count -gt 99) { 3 } else { 2 }
$paddingFormat = "D$padding"

Write-Host "Found $($allFiles.Count) file(s), using $padding-digit numbering." -ForegroundColor Gray
Write-Host ""

$filesToRename = @()

$allFiles | ForEach-Object {
    $name = $_.Name
    $extension = $_.Extension
    $baseName = $_.BaseName
    $newBaseName = $baseName
    $needsChange = $false
    
    # Pattern 1: NNN-NNNN-Rest (e.g., 001-2004-Albeniz)
    if ($baseName -match '^(\d{3})-(\d{4})-(.+)$') {
        $trackNum = [int]$matches[1]
        $rest = $matches[3]
        $newBaseName = "{0:$paddingFormat} - {1}" -f $trackNum, $rest
        $needsChange = $true
    }
    # Pattern 2: NNN-NNNN Rest (e.g., 003-2006 Barber)
    elseif ($baseName -match '^(\d{3})-(\d{4})\s+(.+)$') {
        $trackNum = [int]$matches[1]
        $rest = $matches[3]
        $newBaseName = "{0:$paddingFormat} - {1}" -f $trackNum, $rest
        $needsChange = $true
    }
    # Pattern 3: NN-WNNNN Rest (e.g., 44-W2009 Ludwig)
    elseif ($baseName -match '^(\d{1,3})-[A-Z]\d{4}\s+(.+)$') {
        $trackNum = [int]$matches[1]
        $rest = $matches[2]
        $newBaseName = "{0:$paddingFormat} - {1}" -f $trackNum, $rest
        $needsChange = $true
    }
    # Pattern 4: NNN-Rest (e.g., 054-PROKOFIEV) - exactly 3 digits
    elseif ($baseName -match '^(\d{3})-(.+)$') {
        $trackNum = [int]$matches[1]
        $rest = $matches[2]
        $newBaseName = "{0:$paddingFormat} - {1}" -f $trackNum, $rest
        $needsChange = $true
    }
    # Pattern 5: NN-Text (e.g., 29-3rd-Prize, 52-4th-b Prize) - 1 or 2 digits
    elseif ($baseName -match '^(\d{1,2})-(.+)$') {
        $trackNum = [int]$matches[1]
        $rest = $matches[2]
        $newBaseName = "{0:$paddingFormat} - {1}" -f $trackNum, $rest
        $needsChange = $true
    }
    # Pattern 6: NNN Text (e.g., 310 Jazz Trio) - 3 digits followed by space and text
    elseif ($baseName -match '^(\d{3})\s+(.+)$') {
        $trackNum = [int]$matches[1]
        $rest = $matches[2]
        $newBaseName = "{0:$paddingFormat} - {1}" -f $trackNum, $rest
        $needsChange = $true
    }
    # Pattern 7: Already has NN - format but needs case fix
    elseif ($baseName -match '^\d{1,3}\s+-\s+.+$') {
        $newBaseName = $baseName
        $needsChange = $true
    }
    
    # Apply transformations
    if ($needsChange) {
        # Replace underscores with spaces
        $newBaseName = $newBaseName -replace '_', ' '
        
        # Apply title case
        $newBaseName = $textInfo.ToTitleCase($newBaseName.ToLower())
        
        # Make extension lowercase
        $extension = $extension.ToLower()
        
        $newName = $newBaseName + $extension
        
        # Use case-sensitive comparison
        if ($newName -cne $name) {
            Write-Host "Old: $name" -ForegroundColor Yellow
            Write-Host "New: $newName" -ForegroundColor Green
            Write-Host ""
            
            $filesToRename += @{
                OldPath = $_.FullName
                NewName = $newName
            }
        }
    }
}

if ($filesToRename.Count -eq 0) {
    Write-Host "No files need renaming." -ForegroundColor Green
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

if ($filesToRename.Count -eq 0) {
    Write-Host "No files need renaming." -ForegroundColor Green
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

Write-Host ""
Write-Host "Found $($filesToRename.Count) file(s) to rename." -ForegroundColor Cyan
Write-Host ""
Write-Host "Do you want to rename these files? (Y/N): " -NoNewline -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Renaming files..." -ForegroundColor Cyan
    
    $successCount = 0
    $errorCount = 0
    
    foreach ($file in $filesToRename) {
        try {
            Rename-Item -LiteralPath $file.OldPath -NewName $file.NewName -ErrorAction Stop
            $successCount++
        } catch {
            Write-Host "ERROR: Failed to rename $(Split-Path $file.OldPath -Leaf)" -ForegroundColor Red
            Write-Host "  Reason: $($_.Exception.Message)" -ForegroundColor Red
            $errorCount++
        }
    }
    
    Write-Host ""
    Write-Host "Complete! Renamed $successCount file(s)." -ForegroundColor Green
    if ($errorCount -gt 0) {
        Write-Host "Failed: $errorCount file(s)." -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "Cancelled. No files were renamed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
