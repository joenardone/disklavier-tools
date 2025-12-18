================================================================================
Rename-Titlecase.ps1 - MIDI Filename Normalization
================================================================================

DESCRIPTION:
    Normalizes MIDI filenames to consistent format with proper title case,
    standardized track numbering, and cleaned punctuation.

FEATURES:
    - Handles 7 different track numbering patterns
    - Replaces underscores with spaces
    - Applies title case (first letter capitalized)
    - Lowercases file extensions
    - Case-sensitive change detection
    - Dynamic padding (2-digit for ≤99 files, 3-digit for 100+ files)
    - Interactive preview and confirmation

USAGE:
    # Process current directory
    .\Rename-Titlecase.ps1

    # Process specific directory
    .\Rename-Titlecase.ps1 -Path "C:\Music\MIDI"

    # Process network share
    .\Rename-Titlecase.ps1 -Path "\\RackStation\Music\Piano\MIDI"

PARAMETERS:
    -Path <string>
        Directory to process. Defaults to current directory.

PATTERN TRANSFORMATIONS:
    Pattern 1: NNN-NNNN-Rest    (001-2004-Albeniz)           → NN - Rest
    Pattern 2: NNN-NNNN Rest    (003-2006 Barber)            → NN - Rest
    Pattern 3: NN-WNNNN Rest    (44-W2009 Ludwig)            → NN - Rest
    Pattern 4: NNN-Rest         (054-PROKOFIEV)              → NN - Rest
    Pattern 5: NN-Text          (29-3rd-Prize)               → NN - Text
    Pattern 6: NNN Text         (310 Jazz Trio)              → NN - Text
    Pattern 7: NN - Text        (Already formatted)          → case fix only

EXAMPLES:
    Before: 01 - ANGEL_EYES.MID
    After:  01 - Angel Eyes.mid

    Before: 054-PROKOFIEV SONATA.MID
    After:  54 - Prokofiev Sonata.mid

    Before: 310 Jazz Trio.mid
    After:  310 - Jazz Trio.mid

    Before: 12 - REMEMBRANCE.MID
    After:  12 - Remembrance.mid

NOTES:
    - Only processes .mid files
    - Shows preview before renaming
    - Requires confirmation (y/n) to proceed
    - Uses case-sensitive comparison to detect case-only changes
    - Dynamic numbering: 2-digit (01-99) or 3-digit (001-999) based on folder size
    - Script non-recursive by default (only processes specified folder)

RECOMMENDED WORKFLOW:
    1. Process filenames:
       .\Rename-Titlecase.ps1 -Path "\\RackStation\Music\Piano\MIDI"

    2. Update MIDI metadata to match new filenames:
       ..\embed_tags_metadata.exe --default --add-xf-metadata --recursive "\\RackStation\Music\Piano\MIDI"

TROUBLESHOOTING:
    Q: Files are being skipped
    A: Script only processes .mid files and requires actual changes (name difference)

    Q: Case-only changes not detected
    A: Script uses -cne (case-sensitive) comparison - should work correctly

    Q: Wrong number padding
    A: Script auto-detects: 2-digit for ≤99 files, 3-digit for 100+ files per folder

SEE ALSO:
    - Fix-Numbering.ps1 (convert 2-digit to 3-digit padding in 100+ file folders)
    - Rename-FindReplace.ps1 (flexible find/replace for specific patterns)
    - embed_tags_metadata.exe (update MIDI metadata after renaming)
