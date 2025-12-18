================================================================================
Fix-Numbering.ps1 - Fix Track Numbering for 100+ File Folders
================================================================================

DESCRIPTION:
    Fixes track numbering inconsistencies in folders with 100+ files by
    converting all files to use 3-digit padding for proper sorting.

THE PROBLEM:
    When folders have files numbered 01-99 (2-digit) and 100+ (3-digit),
    sorting breaks:
    
    Expected Order:       Actual Sort Order:
    01 - Song.mid         01 - Song.mid
    02 - Song.mid         02 - Song.mid
    ...                   ...
    99 - Song.mid         09 - Song.mid
    100 - Song.mid        10 - Song.mid  ← Wrong! Should be after 99
    101 - Song.mid        100 - Song.mid ← This is where 100 actually appears
    
    This causes display order problems on DKC-900 and file browsers.

THE SOLUTION:
    Renumbers ALL files in folders with 100+ files to use 3-digit padding:
    
    Before:               After:
    01 - Song.mid    →    001 - Song.mid
    02 - Song.mid    →    002 - Song.mid
    ...                   ...
    09 - Song.mid    →    009 - Song.mid
    10 - Song.mid    →    010 - Song.mid
    ...                   ...
    99 - Song.mid    →    099 - Song.mid
    100 - Song.mid   →    100 - Song.mid
    101 - Song.mid   →    101 - Song.mid

FEATURES:
    - Automatically detects folders with 100+ files
    - Only modifies affected folders (leaves smaller folders unchanged)
    - Preserves track numbers and titles exactly
    - Shows preview before renaming
    - Tracks success/error counts
    - Supports recursive processing

USAGE:
    # Fix single directory
    .\Fix-Numbering.ps1 -Path "Albums\Composer Name"

    # Fix all subdirectories with 100+ files
    .\Fix-Numbering.ps1 -Path "C:\Music\MIDI" -Recurse

    # Fix network share
    .\Fix-Numbering.ps1 -Path "\\RackStation\Music\Piano\MIDI" -Recurse

PARAMETERS:
    -Path <string>
        Directory to process. Defaults to current directory.

    -Recurse
        Process subdirectories recursively.

BEHAVIOR:
    - Scans each folder for .mid file count
    - Folders with <100 files: SKIPPED (no renumbering needed)
    - Folders with 100+ files: ALL files renumbered to 3-digit padding
    - Only processes files matching pattern: NN - Title or NNN - Title
    - Shows which folders need fixing before execution

EXAMPLES:
    Folder with 150 files (needs fixing):
        Before:                 After:
        01 - Bach.mid      →    001 - Bach.mid
        02 - Beethoven.mid →    002 - Beethoven.mid
        ...
        10 - Mozart.mid    →    010 - Mozart.mid
        ...
        99 - Chopin.mid    →    099 - Chopin.mid
        100 - Liszt.mid    →    100 - Liszt.mid
        150 - Debussy.mid  →    150 - Debussy.mid

    Folder with 50 files (skipped):
        Files remain as: 01 - Song.mid, 02 - Song.mid, ... 50 - Song.mid
        (2-digit padding is correct for <100 files)

RECOMMENDED WORKFLOW:
    1. Fix numbering in folders with 100+ files:
       .\Fix-Numbering.ps1 -Path "\\RackStation\Music\Piano\MIDI" -Recurse

    2. Update MIDI metadata to match new filenames:
       ..\embed_tags_metadata.exe --default --add-xf-metadata --recursive "\\RackStation\Music\Piano\MIDI"

    This ensures both filenames and MIDI track_name metadata are synchronized.

NOTES:
    - Only processes .mid files
    - Only renames files with NN - Title or NNN - Title format
    - Shows preview of all changes before execution
    - Requires confirmation (y/n) to proceed
    - Reports success/error counts after completion
    - Checks for existing files to prevent overwrites

SAFETY FEATURES:
    - Preview all changes before execution
    - Requires user confirmation
    - Checks for naming conflicts
    - Won't overwrite existing files
    - Reports errors without stopping entire batch

WHEN TO USE:
    - After importing large collections (100+ files per folder)
    - Before uploading to DKC-900 (ensures correct display order)
    - When files sort incorrectly (10 appears after 100)
    - When adding files to folder that crosses 100-file threshold

SEE ALSO:
    - Rename-Titlecase.ps1 (comprehensive filename normalization)
    - embed_tags_metadata.exe (update MIDI metadata after renaming)
