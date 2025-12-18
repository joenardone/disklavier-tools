============================================================
CLEAN_FILENAMES - Filename Sanitizer
============================================================

DESCRIPTION
-----------
Cleans filenames by replacing Unicode characters and illegal
Windows characters with safe equivalents. Essential for
cross-platform compatibility and Disklavier systems.


FEATURES
--------
- Converts curly quotes to straight quotes
- Converts em/en dashes to hyphens
- Removes/replaces illegal Windows characters
- Preserves Unicode letters (ü, é, ñ, etc.)
- Keeps related files synchronized (.mid and .mp3)
- Processes directories bottom-up to avoid breaking paths
- Dry-run mode to preview changes


BASIC USAGE
-----------
Clean current directory:
  clean_filenames.exe

Clean specific directory:
  clean_filenames.exe directory

Clean with recursion:
  clean_filenames.exe --recursive

Preview changes:
  clean_filenames.exe --dry-run --recursive

Note: If no directory is specified, processes current directory


OPTIONS
-------
--recursive
  Process subdirectories
  Example: clean_filenames.exe --recursive Music

--dry-run
  Preview changes without renaming files
  Example: clean_filenames.exe --dry-run .

--files-only
  Only rename files, skip directories
  Example: clean_filenames.exe --files-only directory

--dirs-only
  Only rename directories, skip files
  Example: clean_filenames.exe --dirs-only directory


CHARACTER REPLACEMENTS
----------------------
Unicode quotes:
  ' (U+2019) → ' (straight apostrophe)
  ' (U+2018) → ' (straight apostrophe)
  " (U+201C) → " (straight quote)
  " (U+201D) → " (straight quote)

Dashes:
  — (em dash) → - (hyphen)
  – (en dash) → - (hyphen)

Illegal Windows characters:
  < > : " / \ | ? * → removed or replaced

Other:
  … (ellipsis) → ... (three dots)


CLEANING EXAMPLES
-----------------
Before: "It's a Beautiful Day.mid"
After:  "It's a Beautiful Day.mid"

Before: "Song: The Title.mp3"
After:  "Song- The Title.mp3"

Before: "Track #1 – Best Song Ever….mid"
After:  "Track #1 - Best Song Ever....mid"

Before: "Für Elise.mid" (Unicode letters preserved)
After:  "Für Elise.mid"


SYNCHRONIZED RENAMING
---------------------
When renaming files, the tool keeps related files in sync:
- If "Song.mid" is renamed to "New Song.mid"
- And "Song.mp3" exists in the same directory
- Then "Song.mp3" is automatically renamed to "New Song.mp3"


QUICK START
-----------
1. Copy clean_filenames.exe to folder with files to clean
2. Run: clean_filenames.exe --dry-run (preview changes)
3. Run: clean_filenames.exe (apply changes)


EXAMPLES
--------
# Clean all files in Albums folder
clean_filenames.exe --recursive Albums

# Preview what would be changed
clean_filenames.exe --dry-run --recursive "My Music"

# Clean only directory names
clean_filenames.exe --dirs-only --recursive Music


TYPICAL WORKFLOW
----------------
1. Run with --dry-run first to preview changes
2. Run without --dry-run to apply changes
3. Use mid_title_from_filename.exe to update MIDI metadata


TROUBLESHOOTING
---------------
- Always use --dry-run first on large libraries
- Files are renamed from deepest directories first
- If a file is in use, it will be skipped
- Multiple consecutive spaces are collapsed to one


MORE INFORMATION
----------------
https://github.com/joenardone/disklavier-tools
