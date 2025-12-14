# Disklavier Tools

Utilities for working with Yamaha Disklavier and DKC-900 systems, including FIL to MIDI conversion, audio processing, and album management.

**Credits:** Special thanks to [Alexander Peppe](https://www.alexanderpeppe.com/) for assistance with DKC-900 tools and workflows.

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

### patch_dkvsong_coverart.exe
Patches Yamaha DKC-900 `.dkvsong.db` to register album cover art for ALL albums with cover.jpg.

**Purpose:**
The DKC-900 only auto-registers artwork for Downloaded Songs. User albums need explicit database entries for `cover.jpg` to display. This tool patches ALL albums in any location.

**Usage:**
```powershell
# Copy exe to USB root and double-click (auto-finds .dkvsong.db)
.\dist\patch_dkvsong_coverart.exe

# Or specify database path
.\dist\patch_dkvsong_coverart.exe D:\.dkvsong.db

# Dry run to preview changes
.\dist\patch_dkvsong_coverart.exe --dry-run
```

**Features:**
- Works on ALL albums, not just Albums/ folder
- No arguments needed - auto-finds .dkvsong.db in current directory
- Creates timestamped backup automatically
- Scans for albums with `cover.jpg` but no registered artwork
- Updates database to reference existing cover.jpg files
- Safe rollback via backup file
- Dry-run mode to preview changes

**Requirements:**
- USB drive with `.dkvsong.db` at root
- Album folders with `cover.jpg` files (any location)

### normalize_coverart.exe
Normalizes album cover art to 265x265 pixels for Yamaha DKC-900.

**Purpose:**
Yamaha Downloaded Songs use 265x265 JPEG artwork. This tool normalizes all album artwork to match that format for consistent display and faster loading.

**Usage:**
```powershell
# Normalize all cover.jpg in Albums folder
.\dist\normalize_coverart.exe Albums

# Dry run to preview changes
.\dist\normalize_coverart.exe --dry-run Albums

# Custom size
.\dist\normalize_coverart.exe --size 300 Albums

# Don't recurse into subdirectories
.\dist\normalize_coverart.exe --no-recursive Albums
```

**Features:**
- Center-crops to square (preserves aspect ratio)
- Resizes to 265x265 pixels (DKC-900 standard)
- Respects EXIF rotation
- Creates backup as `cover.original.jpg`
- Saves as optimized baseline JPEG
- Dry-run mode to preview changes

**Requirements:**
- Python Pillow library: `pip install pillow`
- Album folders containing `cover.jpg` files

**Recommended Workflow:**
1. Prepare albums with `cover.jpg` files
2. Run `normalize_coverart.exe` to resize images
3. Run `patch_dkvsong_coverart.exe` to update database
4. Eject USB and insert into DKC-900

### convert_midi_type.exe
Converts MIDI files from Type 1 (multi-track) to Type 0 (single track).

**Purpose:**
Type 0 is the standard format for Disklavier solo piano files and is required for proper album organization on DKC-900. Use this tool to convert previously-converted files to the correct format.

**Usage:**
```powershell
# Convert all MIDI files in current directory
.\dist\convert_midi_type.exe

# Convert single file
.\dist\convert_midi_type.exe "song.mid"

# Convert directory recursively
.\dist\convert_midi_type.exe --recursive "C:\Music\MIDI"

# Convert without creating backups
.\dist\convert_midi_type.exe --no-backup .

# Verbose output (show skipped files)
.\dist\convert_midi_type.exe --verbose .
```

**Features:**
- Merges all tracks into a single track
- Preserves all MIDI events and exact timing
- Automatically creates `.backup` files
- Skips files already in Type 0 format
- Batch processing with summary statistics
- Recursive directory scanning

**Why Type 0:**
- DKC-900 treats Type 0 and Type 1 differently for album organization
- Yamaha's own .fil conversions create Type 0 files
- Type 0 files appear correctly in the DKC-900 album view

### wav_to_mp3.exe
Converts WAV audio files to MP3 with optional metadata and cover art copying.

**Purpose:**
The DKC-900 requires MP3 format for audio playback with metadata. This tool provides batch WAV to MP3 conversion with DKC-900-compatible settings.

**Usage:**
```powershell
# Convert all WAV files in current directory
.\dist\wav_to_mp3.exe .

# Convert with metadata from tagged MP3 files
.\dist\wav_to_mp3.exe --metadata-dir tags .

# Add suffix to output files
.\dist\wav_to_mp3.exe --suffix _SYNC .

# Output to different directory
.\dist\wav_to_mp3.exe --output-dir output_mp3 input_wav

# Custom bitrate
.\dist\wav_to_mp3.exe --bitrate 320 .

# Dry run to preview
.\dist\wav_to_mp3.exe --dry-run .
```

**Features:**
- Batch WAV to MP3 conversion
- Copies metadata (title, artist, album, track) from tagged MP3 files
- Copies embedded cover art from tagged MP3 files  
- DKC-900 compatible settings (44.1kHz, stereo, ID3v2.3)
- Configurable bitrate and sample rate
- Dry-run mode to preview conversions

**Requirements:**
- FFmpeg installed and in PATH
- Download from: https://ffmpeg.org/download.html

**Metadata Copying Workflow:**
1. Convert WAV files: `wav_to_mp3.exe .`
2. Tag MP3 files with metadata using your preferred tool
3. Place tagged MP3s in `tags/` subdirectory
4. Re-run with metadata: `wav_to_mp3.exe --metadata-dir tags --overwrite .`

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

This builds all executables:
- fil2mid.exe
- mid_title_from_filename.exe  
- clean_filenames.exe
- patch_dkvsong_coverart.exe
- normalize_coverart.exe
- wav_to_mp3.exe

## Requirements

- Python 3.12+
- mido (MIDI file handling)
- pillow (image processing for cover art tools)
- python-rtmidi (optional, for MIDI playback)
- pyinstaller (for building executables)
- FFmpeg (for wav_to_mp3.exe) - https://ffmpeg.org/download.html
