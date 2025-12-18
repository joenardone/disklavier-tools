============================================================
ADD_XF_SOLO_METADATA - Add XF Solo Metadata to MIDI Files
============================================================

DESCRIPTION
-----------
Adds Yamaha XF (eXtended Format) metadata to existing MIDI 
files to make them appear as "PianoSoft Solo" on the 
DKC-900/Enspire.


PURPOSE
-------
The DKC-900 uses XF metadata to categorize MIDI files. 
Without this metadata, files show as generic "SMF" (Standard 
MIDI File) instead of "Solo" format, even if they only contain 
piano tracks.

This tool adds the required metadata structure to make files 
recognized as SMFSOLO in the DKC-900 database.


FEATURES
--------
- Adds XF Solo metadata to existing MIDI files
- Only modifies Type 0 (single track) files
- Skips files that already have XF metadata
- Batch processing with recursive directory scanning
- Overwrites files in place (safe - only adds metadata markers)
- Clear status reporting for each file


XF METADATA ADDED
-----------------
The tool adds the following metadata at the beginning of the 
MIDI file:
1. Copyright: (P) YYYY Yamaha Corporation
2. XF format marker: XF02 signature
3. XG system marker
4. XG system on
5. XF end marker

This is the exact format used by commercial Yamaha PianoSoft 
Solo releases.


USAGE
-----
Process Current Directory:
  add_xf_solo_metadata.exe

Process Single File:
  add_xf_solo_metadata.exe "path/to/file.mid"

Process Directory (Non-Recursive):
  add_xf_solo_metadata.exe "Albums/Artist Name"

Process Directory (Recursive):
  add_xf_solo_metadata.exe --recursive "Albums"

Specify Copyright Year:
  add_xf_solo_metadata.exe --year "2010" "Albums"


OPTIONS
-------
path               MIDI file or directory to process (default: current directory)
--year             Year for copyright (default: current year)
--recursive        Scan subdirectories


OUTPUT
------
The tool shows status for each file:
  √ Added XF Solo metadata: filename.mid (Successfully added)
  Skipping filename.mid: Not Type 0 (has N tracks) (Multi-track file)
  Skipping filename.mid: Already has XF metadata (Already processed)
  X Error processing filename.mid: error details (Error occurred)

At the end, displays summary:
  Summary:
    Modified: 15
    Skipped: 3


WHEN TO USE THIS TOOL
---------------------
Use this tool when:
* You have existing MIDI files that don't show as "Solo" on DKC-900
* You've already deleted the original .fil files
* You have Type 0 (single track) piano MIDI files from other sources
* Files show as "SMF" instead of "SMFSOLO" in database

NOTE: For new conversions from .fil files, use fil2mid.exe 
instead - it automatically adds the metadata.


DKC-900 INTEGRATION
-------------------
After adding metadata:
1. Have DKC-900 rescan the USB drive (remove and reinsert)
2. Check database - files should now show format: SMFSOLO
3. Files will display with "Solo" badge in browser interface


FILE REQUIREMENTS
-----------------
- Files must be Type 0 (single track) MIDI format
- Files must be valid MIDI files
- For Type 1 (multi-track) files, use convert_midi_type.exe first


TROUBLESHOOTING
---------------
Files still don't show as "Solo":
* Verify files are Type 0: Check for "Not Type 0" skip messages
* Convert multi-track files first: Use convert_midi_type.exe
* Force DKC-900 to rescan: Remove USB, wait 10 seconds, reinsert
* Check database directly: Look for format: SMFSOLO in .dkvsong.db

All files skipped:
* If "Already has XF metadata": Files are already correct
* If "Not Type 0": Use convert_midi_type.exe to convert first
* Check that you're pointing to the correct directory with .mid files

Permission errors:
* Ensure files are not read-only
* Close any programs that might have files open
* Run from local drive, not network share


RELATED TOOLS
-------------
- fil2mid.exe - Converts .fil to MIDI with automatic XF metadata
- convert_midi_type.exe - Converts Type 1 to Type 0 format
- mid_title_from_filename.exe - Updates MIDI title metadata


Credits: Special thanks to Alexander Peppe (www.alexanderpeppe.com)
