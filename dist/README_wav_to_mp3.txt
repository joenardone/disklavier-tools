============================================================
WAV_TO_MP3 - Audio Format Converter for DKC-900
============================================================

DESCRIPTION
-----------
Converts WAV audio files to MP3 with optional metadata and
cover art copying. Required because the DKC-900 does not
support WAV playback with metadata.


PURPOSE
-------
The DKC-900 requires MP3 format for audio playback with
metadata. This tool provides:
- Batch WAV to MP3 conversion
- Metadata copying from tagged MP3 files
- Cover art embedding
- DKC-900 compatible settings


REQUIREMENTS
------------
- FFmpeg installed and in PATH
  Download: https://ffmpeg.org/download.html
- WAV source files
- (Optional) Tagged MP3 files for metadata copying


BASIC USAGE
-----------
Convert all WAV files in current directory:
  wav_to_mp3.exe

Convert specific directory:
  wav_to_mp3.exe wav_input

Convert with output directory:
  wav_to_mp3.exe --output-dir mp3_output wav_input

Preview changes:
  wav_to_mp3.exe --dry-run

Note: If no directory is specified, processes current directory


METADATA COPYING
----------------
To copy metadata from existing MP3 files:

1. Place tagged MP3 files in a subdirectory (e.g., tags/)
2. Run with --metadata-dir option:
   wav_to_mp3.exe --metadata-dir tags .

The tool will:
- Match filenames (without extensions)
- Copy metadata: title, artist, album, track number
- Copy embedded cover art
- Apply to converted MP3


OPTIONS
-------
--metadata-dir <directory>
  Directory containing tagged MP3 files for metadata copying
  Example: wav_to_mp3.exe --metadata-dir tags .

--output-dir <directory>
  Output directory (default: same as input)
  Example: wav_to_mp3.exe --output-dir output input

--suffix <text>
  Add suffix to output filenames
  Example: wav_to_mp3.exe --suffix _SYNC .

--bitrate <kbps>
  MP3 bitrate in kbps (default: 192)
  Example: wav_to_mp3.exe --bitrate 320 .

--sample-rate <Hz>
  Sample rate in Hz (default: 44100)
  Example: wav_to_mp3.exe --sample-rate 48000 .

--overwrite
  Overwrite existing MP3 files
  Example: wav_to_mp3.exe --overwrite .

--recursive
  Process subdirectories
  Example: wav_to_mp3.exe --recursive Albums

--dry-run
  Preview conversions without converting
  Example: wav_to_mp3.exe --dry-run .


AUDIO SETTINGS (DKC-900 COMPATIBLE)
------------------------------------
Codec:        MP3 (LAME)
Sample rate:  44100 Hz (default)
Channels:     Stereo (2)
Bitrate:      192 kbps constant (default)
ID3 tags:     v2.3 (DKC-900 compatible)


QUICK START
-----------
1. Copy wav_to_mp3.exe to folder containing WAV files
2. Double-click wav_to_mp3.exe
3. MP3 files will be created alongside WAV files


EXAMPLES
--------
# Basic conversion
wav_to_mp3.exe .

# Convert with metadata from tags/ folder
wav_to_mp3.exe --metadata-dir tags .

# Add _SYNC suffix to output files
wav_to_mp3.exe --suffix _SYNC .

# Higher quality conversion
wav_to_mp3.exe --bitrate 320 .

# Convert to separate directory
wav_to_mp3.exe --output-dir "E:\MP3" "C:\WAV"

# Preview without converting
wav_to_mp3.exe --dry-run .


TYPICAL WORKFLOWS
-----------------
Workflow 1: Simple conversion
  1. wav_to_mp3.exe .
  2. Tag MP3s with metadata tool
  3. Done

Workflow 2: Metadata copying
  1. Convert initial files: wav_to_mp3.exe .
  2. Tag MP3s with metadata and cover art
  3. Move tagged files to tags/ subdirectory
  4. Re-convert with metadata: 
     wav_to_mp3.exe --metadata-dir tags --overwrite .
  5. All files now have metadata and cover art

Workflow 3: Mark IV to DKC-900 migration
  1. Copy WAV files from Mark IV hard drive
  2. Convert to MP3: wav_to_mp3.exe --suffix _SYNC .
  3. Clean filenames: clean_filenames.exe --recursive .
  4. Update metadata: Tag files or use metadata-dir option
  5. Normalize cover art: normalize_coverart.exe Albums
  6. Patch database: patch_dkvsong_coverart.exe .dkvsong.db


FOLDER STRUCTURE FOR METADATA COPYING
--------------------------------------
Your_Music_Folder\
  song1.wav
  song2.wav
  tags\
    song1.mp3  (tagged with metadata + cover art)
    song2.mp3  (tagged with metadata + cover art)

Command: wav_to_mp3.exe --metadata-dir tags --overwrite .
Result: song1.mp3 and song2.mp3 with metadata and cover art


WHAT IT DOES
------------
- Converts WAV to MP3 using FFmpeg
- Applies constant bitrate encoding
- Ensures DKC-900 compatibility
- Copies metadata from tagged MP3 files (if specified)
- Copies embedded cover art (if present in source)
- Creates ID3v2.3 tags


WHAT IT DOESN'T DO
------------------
- Does NOT delete original WAV files
- Does NOT normalize audio levels
- Does NOT guess missing metadata
- Does NOT auto-tag files (use separate tool)
- Does NOT convert other formats (WAV only)


TROUBLESHOOTING
---------------
FFmpeg not found:
  - Install FFmpeg from https://ffmpeg.org/download.html
  - Add FFmpeg to system PATH
  - Restart terminal/command prompt

Metadata not copying:
  - Ensure MP3 filename matches WAV filename (without extension)
  - Check that source MP3 has metadata (use media player to verify)
  - Try without --metadata-dir first to verify basic conversion

Poor audio quality:
  - Increase bitrate: --bitrate 320
  - Check source WAV quality
  - DKC-900 default (192 kbps) is usually sufficient


MORE INFORMATION
----------------
https://github.com/joenardone/disklavier-tools

Credits:
- Alexander Peppe (alexanderpeppe.com) for DKC-900 assistance
- FFmpeg team for audio conversion library
