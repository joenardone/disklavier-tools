============================================================
FIL2MID - Yamaha FIL to MIDI Converter
============================================================

DESCRIPTION
-----------
Converts Yamaha Disklavier .fil (ESEQ format) files to 
standard MIDI format with automatic XF Solo metadata injection
for DKC-900 recognition.


FEATURES
--------
- **Automatically adds XF metadata for "Solo" badge on DKC-900**
- Extracts title from FIL header and embeds as MIDI metadata
- Creates Type 0 (single track) MIDI files
- Automatic tempo/timing conversion
- DKC-900 preset support (117 BPM, program 0)
- Channel mapping and forcing
- Title extraction from filename
- Output filename from FIL title


XF SOLO METADATA
----------------
The tool automatically adds Yamaha XF (eXtended Format) 
metadata to make files appear as "PianoSoft Solo" on DKC-900:
- Copyright message: (P) YYYY Yamaha Corporation
- XF format marker (XF02 signature)
- XG system markers
- XF end marker

This ensures converted files are properly categorized in the
DKC-900 database with format: SMFSOLO.


BASIC USAGE
-----------
Convert all .fil files in current directory:
  fil2mid.exe

Convert single file:
  fil2mid.exe input.fil output.mid

Convert directory:
  fil2mid.exe input_dir output_dir

Convert with recursion:
  fil2mid.exe --recursive input_dir output_dir

Note: If no input is specified, processes current directory


COMMON OPTIONS
--------------
--preset dkc900
  Apply DKC-900 preset (tempo 117 BPM, program 0)
  Example: fil2mid.exe --preset dkc900 song.fil song.mid

--title-from-filename
  Use filename as MIDI title (removes track numbers like "01 -")
  Example: fil2mid.exe --title-from-filename "01 - Song.fil" output.mid

--output-from-title
  Name output file using title from FIL header
  Example: fil2mid.exe --output-from-title track01.fil
  Creates: "Song Title.mid" (from FIL header)

--tempo-bpm <number>
  Set custom tempo in BPM (default: 120)
  Example: fil2mid.exe --tempo-bpm 110 input.fil output.mid

--recursive
  Process subdirectories
  Example: fil2mid.exe --recursive input_dir output_dir


ADVANCED OPTIONS
----------------
--force-channel <0-15>
  Force all MIDI events to specified channel
  Example: fil2mid.exe --force-channel 0 input.fil output.mid

--channel-map <src:dst,...>
  Map source channels to destination channels
  Example: fil2mid.exe --channel-map 2:0,3:0 input.fil output.mid


FILE FORMAT NOTES
-----------------
Yamaha ESEQ (.fil) format:
- Header: 124 bytes (0x00-0x7B)
- Title field: Offset 0x57
- Timebase: Offset 0x1A-0x1B (typically 20480)
- Target resolution: Offset 0x18-0x19 (typically 16384)
- MIDI data: Fixed offset 0x7C


QUICK START
-----------
1. Copy fil2mid.exe to folder containing .fil files
2. Double-click fil2mid.exe (or run without arguments)
3. All .fil files in that folder will be converted to .mid


EXAMPLES
--------
# Convert with DKC-900 preset
fil2mid.exe --preset dkc900 "Angel Eyes.fil" "Angel Eyes.mid"

# Convert directory with filename titles
fil2mid.exe --title-from-filename --recursive Songs Output

# Auto-name from FIL title
fil2mid.exe --output-from-title --recursive FilFiles .


TROUBLESHOOTING
---------------
- If tempo seems wrong, try --preset dkc900 for Mark IV files
- For base64 encoded files (.fil.b64), tool auto-decodes
- Title extraction stops at first MIDI marker (0xF0+)


MORE INFORMATION
----------------
https://github.com/joenardone/disklavier-tools
