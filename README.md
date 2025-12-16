# Disklavier Tools

Utilities for working with Yamaha Disklavier and DKC-900 systems, including FIL to MIDI conversion, audio processing, album management, and XF metadata handling.

**Credits:** Special thanks to [Alexander Peppe](https://www.alexanderpeppe.com/) for assistance with DKC-900 tools and workflows.

**Note:** Each executable in the `dist/` folder has its own README.txt file with detailed documentation.

## Tools

### fil2mid.exe
Converts Yamaha .fil (ESEQ format) files to standard MIDI files with **automatic XF Solo metadata** for DKC-900 recognition.

**Features:**
- **Automatically adds XF metadata for "Solo" badge on DKC-900**
- Extracts title from FIL header and embeds as MIDI track_name metadata
- Creates Type 0 (single track) MIDI files
- Automatic tempo/timing conversion
- DKC-900 preset support
- Channel mapping and forcing
- Optional title extraction from filename
- Optional output filename from FIL title

**Usage:**
```powershell
# Basic conversion (auto-adds XF metadata)
fil2mid.exe input.fil output.mid

# Convert directory recursively
fil2mid.exe --recursive input_dir output_dir

# Use filename as title (strips track numbers like "01 -")
fil2mid.exe --title-from-filename "01 - Song.fil"

# Name output file from FIL title
fil2mid.exe --output-from-title "track01.fil"
# Creates: "Waiting For Spring.mid" (from FIL header)

# DKC-900 preset (tempo 117 BPM, program 0)
fil2mid.exe --preset dkc900 input.fil output.mid

# Custom tempo
fil2mid.exe --tempo-bpm 110 input.fil output.mid
```

**Flags:**
- `--recursive` - Process subdirectories
- `--title-from-filename` - Use filename (minus track number) as MIDI title
- `--output-from-title` - Name output file using title from FIL header
- `--tempo-bpm <number>` - Set tempo (default: 120)
- `--preset dkc900` - Apply DKC-900 preset
- `--force-channel <0-15>` - Force all events to channel
- `--channel-map <src:dst,...>` - Map channels (e.g., 2:0,3:0)

### embed_tags_metadata.exe ⭐ NEW
Embeds metadata from PFBU (Piano Floppy Backup Utility) .tags.txt files into MIDI files with **accurate year information**.

**Purpose:**
Reads rich metadata extracted by PFBU (title, artist, album, composer, year, genre, catalog) and embeds it as MIDI meta messages. Uses the **actual recording/release year** from tags instead of current year.

**Features:**
- Embeds title, copyright, artist, album, composer, catalog, and genre metadata
- Uses accurate year from tags (e.g., 1990, 2003) instead of current year (2025)
- Automatically cleans genre (removes "(Disklavier)" suffix)
- Optional XF Solo metadata for DKC-900 recognition
- Batch processing with recursive scanning
- Dry-run mode to preview changes

**Usage:**
```powershell
# Process PFBU output directory
embed_tags_metadata.exe C:\PFBU_Output

# Add XF Solo metadata too
embed_tags_metadata.exe --add-xf-metadata C:\PFBU_Output

# Preview changes without modifying files
embed_tags_metadata.exe --dry-run samples\audio

# Process single file or current directory
embed_tags_metadata.exe "song.mid"
embed_tags_metadata.exe
```

**Workflow with PFBU:**
1. Use PFBU to copy Disklavier floppies (creates .fil, .mid, and .tags.txt files)
2. Run `embed_tags_metadata.exe --add-xf-metadata C:\PFBU_Output`
3. Upload processed MIDI files to DKC-900

**Note:** See `dist/README_embed_tags_metadata.txt` for detailed documentation on tags format and metadata fields.

### add_xf_solo_metadata.exe
Adds Yamaha XF metadata to existing MIDI files to make them appear as "PianoSoft Solo" on DKC-900.

**Purpose:**
Retroactively adds XF metadata to files converted before this feature existed, or to MIDI files from other sources.

**Features:**
- Adds XF Solo metadata to existing Type 0 MIDI files
- Batch processing with recursive scanning
- Skips files already having XF metadata
- Only modifies Type 0 (single track) files

**Usage:**
```powershell
# Process all MIDI files in current directory
add_xf_solo_metadata.exe

# Process specific directory
add_xf_solo_metadata.exe Albums

# Specify copyright year
add_xf_solo_metadata.exe --year "2010" Albums
```

### convert_midi_type.exe
Converts MIDI files from Type 1 (multi-track) to Type 0 (single track) format.

**Purpose:**
Type 0 is required for proper DKC-900 album organization and XF metadata support.

**Features:**
- Merges all tracks into a single track
- Preserves all MIDI events and exact timing
- Automatically creates `.backup` files
- Skips files already in Type 0 format
- Batch processing with summary statistics
- Recursive directory scanning

**Usage:**
```powershell
# Convert current directory
convert_midi_type.exe

# Convert single file
convert_midi_type.exe "song.mid"

# Convert directory recursively
convert_midi_type.exe --recursive "C:\Music\MIDI"

# Convert without creating backups
convert_midi_type.exe --no-backup .

# Verbose output (show skipped files)
convert_midi_type.exe --verbose .
```

### mid_title_from_filename.exe
Updates MIDI file title metadata to match the filename (without extension).

**Features:**
- Updates track_name metadata in MIDI files
- Sanitizes Unicode characters (curly quotes → straight quotes)
- Validates files are valid MIDI before processing
- Shows what changes will be made

**Usage:**
```powershell
# Single file
mid_title_from_filename.exe file.mid

# Directory
mid_title_from_filename.exe directory

# Recursive
mid_title_from_filename.exe --recursive directory

# Dry run (preview changes)
mid_title_from_filename.exe --dry-run directory
```

### repair_midi_key_signature.exe
Repairs corrupted MIDI files with invalid key signature mode bytes.

**Background:** Some MIDI files may have corrupted key signature meta messages where the mode byte is set to 255 (0xFF) instead of 0 (major) or 1 (minor). This causes standard MIDI libraries like mido to fail with errors like "Could not decode key with 2 flats and mode 255". This tool repairs the corruption at the byte level.

**Features:**
- Detects and repairs invalid key signature mode bytes
- Works at byte level (doesn't require MIDI library parsing)
- Creates repaired copies (original files preserved)
- Supports single file or recursive directory processing
- Reports all repairs made

**Usage:**
```powershell
# Repair single file
repair_midi_key_signature.exe corrupted.mid
# Creates: corrupted_repaired.mid

# Specify output filename
repair_midi_key_signature.exe corrupted.mid fixed.mid

# Repair all MIDI files in directory and subdirectories
repair_midi_key_signature.exe . --recursive

# Quiet mode (only show errors)
repair_midi_key_signature.exe input.mid --quiet
```

**Note:** This tool is needed when you see errors like:
- "Could not decode key with X flats and mode 255"
- "KeySignatureError: mode 255"
- MIDI files that won't load in standard players/tools

### clean_filenames.exe
Cleans filenames by replacing Unicode characters and illegal characters with safe equivalents.

**Features:**
- Converts curly quotes (', ', ", ") to straight quotes
- Converts em/en dashes to hyphens
- Removes/replaces illegal Windows characters: `< > : " / \ | ? *`
- Preserves Unicode letters (ü, é, ñ, etc.)
- Keeps related files synchronized (.mid and .mp3 with same name renamed together)
- Processes directories bottom-up to avoid breaking paths

**Usage:**
```powershell
# Clean directory
clean_filenames.exe directory

# Recursive
clean_filenames.exe --recursive directory

# Dry run
clean_filenames.exe --dry-run --recursive directory

# Files only (skip directories)
clean_filenames.exe --files-only directory

# Directories only (skip files)
clean_filenames.exe --dirs-only directory
```

**Cleaning behavior:**
- ✅ Converts: `It's` → `It's` (curly to straight apostrophe)
- ✅ Preserves: `Für Elise` (Unicode letters kept)
- ✅ Cleans: `Song: Title` → `Song- Title` (illegal chars)

### normalize_coverart.exe
Normalizes album cover art to 265x265 pixels for Yamaha DKC-900.

**Purpose:**
Yamaha Downloaded Songs use 265x265 JPEG artwork. This tool normalizes all album artwork to match that format for consistent display and faster loading.

**Features:**
- Center-crops to square (preserves aspect ratio)
- Resizes to 265x265 pixels (DKC-900 standard)
- Respects EXIF rotation
- Creates backup as `cover.original.jpg`
- Saves as optimized baseline JPEG
- Dry-run mode to preview changes
- **Fixed: Works with special character folders** (`Pop & Rock`, `Jazz & Blues`)

**Usage:**
```powershell
# Normalize all cover.jpg in Albums folder
normalize_coverart.exe Albums

# Dry run to preview changes
normalize_coverart.exe --dry-run Albums

# Custom size
normalize_coverart.exe --size 300 Albums

# Don't recurse into subdirectories
normalize_coverart.exe --no-recursive Albums
```

**Recommended Workflow:**
1. Prepare albums with `cover.jpg` files
2. Run `normalize_coverart.exe` to resize images
3. Run `patch_dkvsong_coverart.exe` to update database
4. Eject USB and insert into DKC-900

### patch_dkvsong_coverart.exe
Patches Yamaha DKC-900 `.dkvsong.db` to register album cover art for ALL albums with cover.jpg.

**Purpose:**
The DKC-900 only auto-registers artwork for Downloaded Songs. User albums need explicit database entries for `cover.jpg` to display.

**Features:**
- Works on ALL albums, not just Albums/ folder
- No arguments needed - auto-finds .dkvsong.db in current directory
- Creates timestamped backup automatically
- Scans for albums with `cover.jpg` but no registered artwork
- Updates database to reference existing cover.jpg files
- Safe rollback via backup file
- Dry-run mode to preview changes

⚠️ **IMPORTANT:** DKC-900 does NOT support ampersand `&` in folder names. Use hyphens instead:
- ✅ `Jazz - Blues` NOT ❌ `Jazz & Blues`
- ✅ `Pop - Rock` NOT ❌ `Pop & Rock`

**Usage:**
```powershell
# Copy exe to USB root and double-click (auto-finds .dkvsong.db)
patch_dkvsong_coverart.exe

# Or specify database path
patch_dkvsong_coverart.exe D:\.dkvsong.db

# Dry run to preview changes
patch_dkvsong_coverart.exe --dry-run
```

**Requirements:**
- USB drive with `.dkvsong.db` at root
- Album folders with `cover.jpg` files (any location)

### wav_to_mp3.exe
Converts WAV audio files to MP3 with optional metadata and cover art copying.

**Purpose:**
The DKC-900 requires MP3 format for audio playback with metadata. This tool provides batch WAV to MP3 conversion with DKC-900-compatible settings.

**Features:**
- Batch WAV to MP3 conversion
- Copies metadata (title, artist, album, track) from tagged MP3 files
- Copies embedded cover art from tagged MP3 files  
- DKC-900 compatible settings (44.1kHz, stereo, ID3v2.3)
- Configurable bitrate and sample rate
- Dry-run mode to preview conversions

**Usage:**
```powershell
# Convert all WAV files in current directory
wav_to_mp3.exe .

# Convert with metadata from tagged MP3 files
wav_to_mp3.exe --metadata-dir tags .

# Add suffix to output files
wav_to_mp3.exe --suffix _SYNC .

# Output to different directory
wav_to_mp3.exe --output-dir output_mp3 input_wav

# Custom bitrate
wav_to_mp3.exe --bitrate 320 .

# Dry run to preview
wav_to_mp3.exe --dry-run .
```

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

## Complete DKC-900 Workflow

### Converting FIL Files to MIDI with Solo Recognition
```powershell
# 1. Convert .fil files (auto-adds XF metadata)
fil2mid.exe --recursive input_fil output_midi

# 2. Clean filenames if needed
clean_filenames.exe --recursive output_midi

# 3. Copy to USB Albums folder
# Organize as: Albums/Artist Name/Album Name/*.mid

# 4. Add cover art (265x265 recommended)
# Place cover.jpg in each album folder

# 5. Normalize artwork
normalize_coverart.exe D:\Albums

# 6. Patch database
patch_dkvsong_coverart.exe D:\.dkvsong.db

# 7. Insert USB into DKC-900
# Files will show with "Solo" badge
```

### Fixing Existing MIDI Files
```powershell
# If files don't show "Solo" on DKC-900:

# 1. Convert to Type 0 if needed
convert_midi_type.exe --recursive Albums

# 2. Add XF Solo metadata
add_xf_solo_metadata.exe Albums

# 3. Update titles to match filenames
mid_title_from_filename.exe --recursive Albums

# 4. Re-insert USB in DKC-900
```

### Adding Audio Sync
```powershell
# 1. Convert audio
wav_to_mp3.exe input_wav

# 2. Match filenames to MIDI files
#    Song Title.mid
#    Song Title.mp3

# 3. Tag MP3s (external tool)

# 4. Copy metadata
wav_to_mp3.exe --metadata-dir tags --overwrite .

# 5. Copy both .mid and .mp3 to USB
```

## XF Metadata & Solo Recognition

### What is XF Metadata?
Yamaha's eXtended Format (XF) adds metadata to MIDI files that the DKC-900 uses to:
- Categorize files as Solo/Plus/Audio formats
- Display appropriate badges in browser interface
- Organize files in database (SMFSOLO vs SMF)

### Why Files Need XF Metadata
- Original PianoSoft Solo floppies contain .fil files WITHOUT XF metadata
- XF metadata must be ADDED during conversion
- Without it, files show as generic "SMF" instead of "Solo"
- DKC-900 checks for specific XF markers to set database format field

### Tools for XF Metadata
- **fil2mid.exe** - Automatically adds XF metadata during conversion
- **add_xf_solo_metadata.exe** - Adds XF metadata to existing files
- **convert_midi_type.exe** - Converts to Type 0 (required for XF metadata)

## Building

Executables are built using PyInstaller:
```powershell
.\pack.ps1
```

This builds all executables in `dist/`:
- fil2mid.exe
- add_xf_solo_metadata.exe ⭐ NEW
- mid_title_from_filename.exe  
- clean_filenames.exe
- patch_dkvsong_coverart.exe
- normalize_coverart.exe
- convert_midi_type.exe
- wav_to_mp3.exe

Each executable has a corresponding README.txt in the dist/ folder.

## Requirements

- No Python required - standalone executables
- FFmpeg required for wav_to_mp3.exe: https://ffmpeg.org/download.html

## Development Requirements

- Python 3.12+
- mido (MIDI file handling)
- pillow (image processing for cover art tools)
- python-rtmidi (optional, for MIDI playback)
- pyinstaller (for building executables)
