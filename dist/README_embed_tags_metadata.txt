EMBED TAGS METADATA - Embed PFBU Metadata into MIDI Files
============================================================

PURPOSE:
--------
Reads metadata from PFBU (Piano Floppy Backup Utility) .tags.txt files 
and embeds it into MIDI files as standard meta messages. Uses accurate 
year information from the tags instead of the current year.

METADATA EMBEDDED:
------------------
- Title (track_name)
- Copyright: (P) YYYY Yamaha Corporation (using year from tags)
- Artist (text message)
- Album (text message)
- Composer (text message)
- Catalog Number (text message)
- Genre (text message, cleaned - removes "(Disklavier)" suffix)

BASIC USAGE:
------------
Process all MIDI files in a directory and its subdirectories:
  embed_tags_metadata.exe C:\path\to\midi\files

Process a single MIDI file:
  embed_tags_metadata.exe "C:\path\to\song.mid"

Process current directory:
  embed_tags_metadata.exe

COMMAND-LINE FLAGS:
-------------------
--default
  Generate metadata from filename and directory when .tags.txt files don't exist.
  
  Filename Patterns Supported:
    036-2004-Song.mid     → Track 36, Title "036-2004-Song"
    01_Song Name.mid      → Track 1, Title "01 Song Name"
    1-05_Song.mid         → Disc 1 Track 5, Title "1-05 Song"
    Song Name.mid         → Track 1 (auto), Title "Song Name"
  
  For files without track numbers, assigns sequential track numbers (1, 2, 3...)
  within each directory to avoid duplicates.
  
  Title includes full filename (with track number) so DKC-900 displays it,
  since DKC-900 doesn't show track numbers separately.
  
  Album name is taken from the parent directory name.
  
  Empty fields (Artist, Composer, Year, Catalog, Genre) are created but left blank.
  
  Only writes files if metadata is different from what's already embedded (fast).
  
  NOTE: If a .tags.txt file exists, it always takes precedence over --default.
  
  Examples:
    embed_tags_metadata.exe --default C:\Music\MyAlbum
    embed_tags_metadata.exe --default --add-xf-metadata C:\Music

--add-xf-metadata
  Also add XF Solo metadata to Type 0 MIDI files for DKC-900 recognition.
  This adds the XF format markers that make songs show as "Solo" on the 
  Disklavier controller.
  
  Example:
    embed_tags_metadata.exe --add-xf-metadata samples\solo

--recursive
  Scan subdirectories in addition to the specified directory.
  
  Example:
    embed_tags_metadata.exe --recursive C:\Music\AllAlbums

--dry-run
  Preview what changes would be made without actually modifying any files.
  Shows all metadata that would be embedded.
  
  Example:
    embed_tags_metadata.exe --dry-run samples\audio

WORKFLOW WITH PFBU:
-------------------
1. Use PFBU (Piano Floppy Backup Utility) to copy Disklavier floppies
   - Make sure PFBU creates .tags.txt files along with .fil and .mid files

2. Run this tool on the output directory:
     embed_tags_metadata.exe --recursive C:\PFBU_Output

3. Upload the processed MIDI files to your DKC-900

TAGS.TXT FORMAT:
----------------
The .tags.txt files use ID3-style tags:
  TIT2 = Title
  TPE1 = Artist (performer)
  TALB = Album
  TYER = Year (e.g., 1990, 2003, 2006)
  TCOM = Composer
  COMM = Catalog Number
  TCON = Genre (cleaned to remove "(Disklavier)")

FILE MATCHING:
--------------
The tool looks for files with matching base names:
  "Song Name.tags.txt" → "Song Name.mid"
  
If a .tags.txt file exists but no corresponding .mid file is found, 
it will be skipped (shown in summary as "Skipped").

GENRE CLEANING:
---------------
The Genre field in PFBU tags often includes "(Disklavier)" suffix:
  Before: "Jazz & Blue (Disklavier)"
  After:  "Jazz & Blue"

This tool automatically removes the suffix for cleaner metadata.

YEAR ACCURACY:
--------------
Unlike other tools that use the current year (2025), this tool uses 
the actual recording/release year from the TYER tag in .tags.txt:
  
  From tags: TYER=2003
  In MIDI:   (P) 2003 Yamaha Corporation

This preserves the accurate historical information from your floppies.

COMBINING WITH OTHER TOOLS:
----------------------------
If you also want to ensure XF Solo metadata:
  embed_tags_metadata.exe --add-xf-metadata --recursive C:\Music

Or use the dedicated tool after embedding tags:
  add_xf_solo_metadata.exe --recursive C:\Music

EXAMPLES:
---------
1. Process PFBU output with XF Solo metadata (recursive):
     embed_tags_metadata.exe --add-xf-metadata --recursive C:\PFBU_Output

2. Preview changes before applying:
     embed_tags_metadata.exe --dry-run samples\audio

3. Process single album (non-recursive is default):
     embed_tags_metadata.exe "C:\Music\Mamma Mia"

4. Process specific file:
     embed_tags_metadata.exe "01 - Waiting For Spring.mid"

5. Generate metadata from filenames (recursive):
     embed_tags_metadata.exe --default --recursive C:\Music

OUTPUT:
-------
The tool shows:
- Each file being processed
- All metadata being embedded (title, artist, album, year, etc.)
- Success (✓) or error (✗) status for each file
- Summary: processed count and skipped count

NOTES:
------
- Files are modified in-place (original MIDI file is overwritten)
- Make backups if you want to preserve originals
- Only processes Type 0 MIDI files when adding XF metadata
- Skips files that don't have a corresponding .tags.txt file
- Safe to run multiple times:
  * Skips files that already have matching metadata (no changes needed)
  * Updates files where tags have changed
  * Never creates duplicate metadata entries

RELATED TOOLS:
--------------
- fil2mid.exe: Convert .fil to .mid
- add_xf_solo_metadata.exe: Add XF Solo markers only
- mid_title_from_filename.exe: Set title from filename
- convert_midi_type.exe: Convert between Type 0/1
