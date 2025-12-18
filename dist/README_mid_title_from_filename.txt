============================================================
MID_TITLE_FROM_FILENAME - MIDI Metadata Updater
============================================================

DESCRIPTION
-----------
Updates MIDI file title metadata to match the filename.
Useful for ensuring MIDI files display correctly on
Disklavier systems and media players.


FEATURES
--------
- Updates track_name metadata in MIDI files
- Sanitizes Unicode characters (curly quotes → straight quotes)
- Validates files are valid MIDI before processing
- Dry-run mode to preview changes
- Batch processing with recursion support


BASIC USAGE
-----------
Update all MIDI files in current directory:
  mid_title_from_filename.exe

Update single file:
  mid_title_from_filename.exe file.mid

Update directory:
  mid_title_from_filename.exe directory

Update with recursion:
  mid_title_from_filename.exe --recursive directory

Note: If no input is specified, processes current directory


OPTIONS
-------
--recursive
  Process subdirectories
  Example: mid_title_from_filename.exe --recursive Music

--dry-run
  Preview changes without modifying files
  Example: mid_title_from_filename.exe --dry-run directory


CHARACTER SANITIZATION
----------------------
The tool automatically cleans filenames:
- Curly quotes (', ', ", ") → straight quotes
- Em/en dashes (—, –) → hyphens (-)
- Ellipsis (…) → three dots (...)
- Preserves Unicode letters (ü, é, ñ, etc.)


QUICK START
-----------
1. Copy mid_title_from_filename.exe to folder with MIDI files
2. Double-click mid_title_from_filename.exe
3. All .mid files will have titles updated from filenames


EXAMPLES
--------
# Update all MIDI files in current directory
mid_title_from_filename.exe .

# Preview changes before applying
mid_title_from_filename.exe --dry-run --recursive Music

# Update specific album folder
mid_title_from_filename.exe "Albums\Jim Brickman"


WHAT IT DOES
------------
1. Reads filename (without .mid extension)
2. Sanitizes Unicode characters
3. Updates MIDI track_name metadata
4. Preserves all other MIDI data and events


WHAT IT DOESN'T DO
------------------
- Does NOT rename files (use clean_filenames.exe)
- Does NOT modify audio quality
- Does NOT change tempo or other MIDI events
- Does NOT process non-MIDI files


TYPICAL WORKFLOW
----------------
1. Rename files with clean_filenames.exe (optional)
2. Run mid_title_from_filename.exe to update metadata
3. Files now display correct titles in players


TROUBLESHOOTING
---------------
- If file is not valid MIDI, it will be skipped
- Backup files before batch processing large libraries
- Use --dry-run first to preview changes


MORE INFORMATION
----------------
https://github.com/joenardone/disklavier-tools
