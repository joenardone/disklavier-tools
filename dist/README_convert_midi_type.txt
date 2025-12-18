MIDI TYPE CONVERTER
==================

Converts MIDI files from Type 1 (multi-track) to Type 0 (single track).

DESCRIPTION
-----------
This tool merges all tracks from Type 1 MIDI files into a single track,
creating Type 0 MIDI files. Type 0 is the standard format for Disklavier
solo piano files and is required for proper album organization on DKC-900.

FEATURES
--------
* Convert single MIDI files or entire directories
* Recursive directory scanning
* Automatic backup creation (optional)
* Skips files already in Type 0 format
* Safety check: warns about multi-track files before converting
* Preserves all MIDI events and timing
* Batch processing with summary statistics

QUICK START
-----------
1. Copy convert_midi_type.exe to your MIDI directory
2. Double-click convert_midi_type.exe
3. All .mid files in that directory will be converted to Type 0

BASIC USAGE
-----------
  convert_midi_type.exe [file_or_directory] [options]

  If no path is specified, processes all .mid files in the current directory.

OPTIONS
-------
  -r, --recursive       Process directories recursively
  --no-backup          Do not create .backup files
  -f, --force          Convert multi-track files (merges all tracks)
  -v, --verbose        Show files that are already Type 0
  -o, --output FILE    Save to different file (single file mode only)

EXAMPLES
--------
1. Convert a single file (creates backup):
   convert_midi_type.exe "my_song.mid"

2. Convert without backup:
   convert_midi_type.exe "my_song.mid" --no-backup

3. Convert to a different file:
   convert_midi_type.exe "input.mid" -o "output.mid"

4. Convert all files in current directory:
   convert_midi_type.exe

5. Convert all files in a specific directory:
   convert_midi_type.exe "C:\Music\MIDI"

6. Convert recursively (all subdirectories):
   convert_midi_type.exe "C:\Music\MIDI" --recursive

7. Force conversion of multi-track files:
   convert_midi_type.exe --force "C:\Music\MIDI"

WHAT IT DOES
------------
* Reads Type 1 MIDI files (multi-track)
* Checks if file has multiple tracks (warns if found)
* Merges all tracks into a single track (if --force or single track)
* Preserves exact timing and all events
* Creates Type 0 MIDI file (single track)
* Skips files already in Type 0 format

SAFETY FEATURES
---------------
By default, files with multiple tracks are NOT converted. You'll see:
  ⚠ Warning: filename.mid has 3 tracks
  Skipping to preserve track structure. Use --force to convert anyway.

This protects against accidentally merging multi-instrument arrangements
where track separation is important. Use --force only when you're certain
you want all tracks merged into one.

WHY TYPE 0?
-----------
* Type 0 is the standard for Disklavier solo piano files
* DKC-900 treats Type 0 and Type 1 differently for album organization
* Yamaha's own .fil conversions create Type 0 files
* Type 0 files appear correctly in the DKC-900 album view

BACKUP FILES
------------
By default, when overwriting a file, the original is saved with a .backup
extension. To disable backups, use --no-backup flag.

Example:
  Original: song.mid
  Backup:   song.mid.backup
  New file: song.mid (Type 0)

TROUBLESHOOTING
---------------
Q: Nothing happens when I run the tool
A: Make sure there are .mid files in the directory. Use --verbose to see 
   which files are being processed.

Q: "Already Type 0" messages
A: The file is already in the correct format. Use --verbose to see these 
   messages, or they're hidden by default.

Q: Error reading MIDI file
A: The file may be corrupted or not a valid MIDI file. Check the file with
   a MIDI editor or player.

Q: Lost my original file
A: Check for .backup files in the same directory. Backups are created by
   default unless you used --no-backup flag.

TECHNICAL DETAILS
-----------------
* Type 0 = Single track MIDI file
* Type 1 = Multi-track MIDI file
* Type 2 = Multiple independent sequences (rare)

The tool converts Type 1 to Type 0 by merging all tracks while preserving:
* All MIDI events (notes, controllers, program changes, etc.)
* Exact timing (delta times converted to absolute, sorted, then back to delta)
* Tempo maps and time signatures
* Track metadata

For more information, visit:
https://github.com/joenardone/disklavier-tools
