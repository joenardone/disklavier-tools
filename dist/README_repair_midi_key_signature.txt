repair_midi_key_signature.exe
================================

Repairs corrupted MIDI files with invalid key signature mode bytes.

BACKGROUND
----------
Some MIDI files may have corrupted key signature meta messages where the mode
byte is set to 255 (0xFF) instead of the valid values:
  - 0 = Major key
  - 1 = Minor key

This corruption causes standard MIDI libraries and players to fail with errors like:
  "Could not decode key with 2 flats and mode 255"
  "KeySignatureError: mode 255"

This tool repairs the corruption by working at the byte level, finding and
replacing invalid mode bytes with 0 (major).


FEATURES
--------
- Detects and repairs invalid key signature mode bytes
- Works at byte level (doesn't require MIDI library parsing)
- Creates repaired copies with "_repaired" suffix (original files preserved)
- Supports single file or recursive directory processing
- Reports all repairs made with detailed information
- Shows track number, byte position, and key signature details


USAGE
-----
Repair a single file (creates input_repaired.mid):
  repair_midi_key_signature.exe corrupted.mid

Specify output filename:
  repair_midi_key_signature.exe corrupted.mid fixed.mid

Repair all MIDI files in directory and subdirectories:
  repair_midi_key_signature.exe . --recursive
  repair_midi_key_signature.exe "C:\Music\MIDI" --recursive

Quiet mode (only show errors):
  repair_midi_key_signature.exe input.mid --quiet


WHEN TO USE THIS TOOL
----------------------
Use this tool when you encounter errors like:

1. "Could not decode key with X flats and mode 255"
2. "KeySignatureError: mode 255"
3. MIDI files that won't load in standard players/tools
4. Files that other MIDI tools refuse to process

These errors indicate the MIDI file has a corrupted key signature meta message.


EXAMPLE OUTPUT
--------------
  Repairing: corrupted.mid
    Format: Type 1, Tracks: 11
    Track 2: Found invalid key signature
      Position: 223
      Sharps/Flats: -2
      Invalid mode: 255 (0xFF)
      Repairing to: 0 (major)
    Repaired 1 invalid key signature(s)
    Saved to: corrupted_repaired.mid


TECHNICAL DETAILS
-----------------
Key Signature Meta Message Format:
  FF 59 02 [sf] [mode]
  
  Where:
    sf (sharps/flats): -7 to +7
      Negative values = flats (e.g., -2 = 2 flats = Bb major/G minor)
      Positive values = sharps (e.g., +2 = 2 sharps = D major/B minor)
    
    mode: Should be 0 or 1
      0 = Major key
      1 = Minor key
      255 (0xFF) = INVALID (corruption)

This tool finds mode bytes set to 255 and changes them to 0 (major).


WORKFLOW
--------
1. Run repair_midi_key_signature.exe on your MIDI files
2. Verify the repaired files load correctly in your MIDI player
3. If satisfied, replace the original files with the repaired versions
4. Delete the original corrupted files


OPTIONS
-------
  input               Input MIDI file or directory
  output              Output MIDI file (optional, default: input_repaired.mid)
  --recursive, -r     Process all .mid files in subdirectories
  --quiet, -q         Suppress output except for errors


NOTES
-----
- Original files are never modified - repairs create new files
- Repaired files have "_repaired" suffix unless output filename specified
- The tool assumes major key (mode 0) when repairing
- If you need minor key instead, manually edit the MIDI file after repair


TROUBLESHOOTING
---------------
"ERROR: Not a valid MIDI file"
  The file is not a MIDI file or is severely corrupted beyond repair.

"No repairs needed"
  The file has valid key signatures and doesn't need repair.

Files still won't load after repair:
  The file may have other types of corruption. Try other MIDI repair tools
  or re-acquire the file from the original source.


RELATED TOOLS
-------------
- mid_title_from_filename.exe - Update MIDI title metadata from filename
- convert_midi_type.exe - Convert MIDI Type 1 to Type 0
- clean_filenames.exe - Clean and sanitize filenames


For more information, see README.md in the Disklavier Tools package.
