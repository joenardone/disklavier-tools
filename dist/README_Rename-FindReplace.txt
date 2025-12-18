================================================================================
Rename-FindReplace.ps1 - Flexible Filename Find/Replace
================================================================================

DESCRIPTION:
    Flexible find/replace tool for patterns in MIDI filenames. Useful for
    cleaning up specific text patterns, normalizing punctuation, or removing
    unwanted text.

FEATURES:
    - Case-insensitive pattern matching
    - Handles special characters safely
    - Preview before execution
    - Conflict detection
    - Progress updates for large batches
    - Optional recursive processing
    - Custom file filters

USAGE:
    # Basic find/replace
    .\Rename-FindReplace.ps1 -Find "old text" -Replace "new text"

    # Remove text (empty replacement)
    .\Rename-FindReplace.ps1 -Find "Frederic Francois" -Replace ""

    # Process specific directory
    .\Rename-FindReplace.ps1 -Path "C:\Music" -Find "Op.25" -Replace "Op-25"

    # Process subdirectories
    .\Rename-FindReplace.ps1 -Find "text" -Replace "new" -Recurse

    # Custom file filter
    .\Rename-FindReplace.ps1 -Find "old" -Replace "new" -Filter "*.txt"

PARAMETERS:
    -Path <string>
        Directory to process. Defaults to current directory.

    -Find <string> (REQUIRED)
        Text pattern to find (case-insensitive).

    -Replace <string> (REQUIRED)
        Replacement text. Use empty string "" to remove text.

    -Filter <string>
        File pattern filter. Default: *.mid

    -Recurse
        Process subdirectories recursively.

EXAMPLES:
    # Remove middle names from composer names
    .\Rename-FindReplace.ps1 -Find "Frederic Francois" -Replace ""
    Result: "Chopin Frederic Francois" → "Chopin"

    # Normalize opus notation
    .\Rename-FindReplace.ps1 -Find "Op.25" -Replace "Op-25"
    Result: "Etude Op.25 No-11" → "Etude Op-25 No-11"

    # Clean up punctuation
    .\Rename-FindReplace.ps1 -Find ", " -Replace " "
    Result: "Chopin, Frederic" → "Chopin Frederic"

    # Remove parenthetical text
    .\Rename-FindReplace.ps1 -Find " (Seq Yogore)" -Replace ""
    Result: "Song Title (Seq Yogore).mid" → "Song Title.mid"

    # Fix apostrophes
    .\Rename-FindReplace.ps1 -Find "'" -Replace "'"
    Result: "It's" → "It's"

NOTES:
    - Pattern matching is case-insensitive (finds "Text", "TEXT", "text")
    - Special regex characters are automatically escaped
    - Shows preview of all changes before execution
    - Checks for naming conflicts (won't overwrite existing files)
    - Progress shown every 10 files for large batches
    - Uses -LiteralPath to handle special characters in filenames

SAFETY FEATURES:
    - Preview all changes before execution
    - Requires confirmation (y/n) to proceed
    - Detects and warns about naming conflicts
    - Won't rename if target filename already exists
    - Shows count of files that will be renamed

RECOMMENDED USE CASES:
    - Normalize composer name formats
    - Clean up opus/catalog number notation (Op.25 → Op-25)
    - Remove sequencer names (Seq Yogore)
    - Fix unicode quote characters
    - Remove genre tags from filenames
    - Standardize separator characters

SEE ALSO:
    - Rename-Titlecase.ps1 (comprehensive filename normalization)
    - Fix-Numbering.ps1 (fix track numbering in 100+ file folders)
