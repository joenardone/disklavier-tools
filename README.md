# Disklavear - Yamaha FIL to MIDI Converter

Tools for converting Yamaha Disklavier FIL files to standard MIDI format.

## Tools

### fil2mid.exe
Converts Yamaha .fil (ESEQ format) files to standard MIDI files.

**Features:**
- Extracts title from FIL header and embeds as MIDI track_name metadata
- Automatic tempo/timing conversion
- DKC-900 preset support
- Channel mapping and forcing
- Optional title extraction from filename
- Optional output filename from FIL title

**Usage:**
```powershell
# Basic conversion
.\dist\fil2mid.exe input.fil output.mid

# Convert directory
.\dist\fil2mid.exe --recursive input_dir output_dir

# Use filename as title (strips track numbers like "01 -")
.\dist\fil2mid.exe --title-from-filename "01 - Song.fil"

# Name output file from FIL title
.\dist\fil2mid.exe --output-from-title "track01.fil"
# Creates: "Waiting For Spring.mid" (from FIL header)

# DKC-900 preset (tempo 117 BPM, program 0)
.\dist\fil2mid.exe --preset dkc900 input.fil output.mid

# Custom tempo
.\dist\fil2mid.exe --tempo-bpm 110 input.fil output.mid
```

**Flags:**
- `--recursive` - Process subdirectories
- `--title-from-filename` - Use filename (minus track number) as MIDI title
- `--output-from-title` - Name output file using title from FIL header
- `--tempo-bpm <number>` - Set tempo (default: 120)
- `--preset dkc900` - Apply DKC-900 preset
- `--force-channel <0-15>` - Force all events to channel
- `--channel-map <src:dst,...>` - Map channels (e.g., 2:0,3:0)

### mid_title_from_filename.exe
Updates MIDI file title metadata to match the filename (without extension).

**Usage:**
```powershell
# Single file
.\dist\mid_title_from_filename.exe file.mid

# Directory
.\dist\mid_title_from_filename.exe directory

# Recursive
.\dist\mid_title_from_filename.exe --recursive directory

# Dry run (preview changes)
.\dist\mid_title_from_filename.exe --dry-run directory
```

**Features:**
- Updates track_name metadata in MIDI files
- Sanitizes Unicode characters (curly quotes → straight quotes)
- Validates files are valid MIDI before processing
- Shows what changes will be made

### clean_filenames.exe
Cleans filenames by replacing Unicode characters and illegal characters with safe equivalents.

**Usage:**
```powershell
# Clean directory
.\dist\clean_filenames.exe directory

# Recursive
.\dist\clean_filenames.exe --recursive directory

# Dry run
.\dist\clean_filenames.exe --dry-run --recursive directory

# Files only (skip directories)
.\dist\clean_filenames.exe --files-only directory

# Directories only (skip files)
.\dist\clean_filenames.exe --dirs-only directory
```

**Features:**
- Converts curly quotes (', ', ", ") to straight quotes
- Converts em/en dashes to hyphens
- Removes/replaces illegal Windows characters: `< > : " / \ | ? *`
- Preserves Unicode letters (ü, é, ñ, etc.)
- Keeps related files synchronized (.mid and .mp3 with same name renamed together)
- Processes directories bottom-up to avoid breaking paths

**Cleaning behavior:**
- ✅ Converts: `It's` → `It's` (curly to straight apostrophe)
- ✅ Preserves: `Für Elise` (Unicode letters kept)
- ✅ Cleans: `Song: Title` → `Song- Title` (illegal chars)

## File Format

### Yamaha ESEQ (.fil)
- Header: 124 bytes (0x00-0x7B)
- Title field: Offset 0x57 to first 0xF0+ byte
- Timebase: Offset 0x1A-0x1B (typically 20480)
- Target resolution: Offset 0x18-0x19 (typically 16384)
- MIDI data: Fixed offset 0x7C

## Building

Executables are built using PyInstaller:
```powershell
.\pack.ps1
```

This builds all three executables:
- fil2mid.exe
- mid_title_from_filename.exe  
- clean_filenames.exe

## Requirements

- Python 3.12+
- mido
- python-rtmidi (optional, for MIDI playback)
- pyinstaller (for building executables)
