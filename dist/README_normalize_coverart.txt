============================================================
NORMALIZE_COVERART - Album Artwork Resizer
============================================================

DESCRIPTION
-----------
Normalizes album cover art to 265x265 pixels for Yamaha
DKC-900. Yamaha Downloaded Songs use this size; matching it
ensures consistent display and faster loading.

** FIXED: Glob pattern corrected to properly find cover.jpg
   files in subdirectories with special characters like 
   "Pop & Rock" and "Jazz & Blues" **


PURPOSE
-------
Resize album artwork to the DKC-900's native format:
- 265 x 265 pixels (square)
- JPEG format
- Baseline (non-progressive)
- Optimized for embedded display


REQUIREMENTS
------------
- Album folders containing cover.jpg files
- Images can be any size/format (will be converted)
- Python Pillow library (included in executable)


BASIC USAGE
-----------
Normalize all cover.jpg in current directory:
  normalize_coverart.exe

Normalize specific folder:
  normalize_coverart.exe Albums

Preview changes first:
  normalize_coverart.exe --dry-run

Note: If no directory is specified, processes current directory


OPTIONS
-------
--dry-run
  Preview changes without modifying files
  Example: normalize_coverart.exe --dry-run Albums

--size <pixels>
  Custom size (default: 265 for DKC-900)
  Example: normalize_coverart.exe --size 300 Albums

--quality <1-100>
  JPEG quality (default: 88)
  Example: normalize_coverart.exe --quality 95 Albums

--recursive
  Process subdirectories
  Example: normalize_coverart.exe --recursive Albums


WHAT IT DOES
------------
For each cover.jpg found:
1. Creates backup as cover.original.jpg (first run only)
2. Center-crops to square (if needed)
3. Resizes to 265 x 265 pixels
4. Respects EXIF rotation
5. Saves as optimized baseline JPEG
6. Overwrites cover.jpg with normalized version


WHAT IT DOESN'T DO
------------------
- Does NOT modify the database (use patch_dkvsong_coverart.exe)
- Does NOT modify MIDI or MP3 files
- Does NOT rename files
- Does NOT affect Downloaded Songs


IMAGE PROCESSING
----------------
Center cropping:
  - If image is not square, it's center-cropped
  - Maintains aspect ratio of cropped region
  - Uses Lanczos resampling (high quality)

EXIF handling:
  - Respects rotation metadata
  - Auto-rotates based on camera orientation
  - Ensures correct display orientation

Format:
  - Converts all formats to JPEG
  - RGB color space
  - Baseline JPEG (not progressive)
  - Optimized for file size


QUICK START
-----------
1. Copy normalize_coverart.exe to Albums folder
2. Run: normalize_coverart.exe --dry-run (preview)
3. Run: normalize_coverart.exe (normalize all cover.jpg)


EXAMPLES
--------
# Normalize all albums
normalize_coverart.exe Albums

# Preview what would be changed
normalize_coverart.exe --dry-run Albums

# Custom size for different device
normalize_coverart.exe --size 300 Albums

# Higher quality for large screens
normalize_coverart.exe --quality 95 Albums

# Only current directory (not subdirs)
normalize_coverart.exe --no-recursive .


RECOMMENDED WORKFLOW
--------------------
1. Prepare Albums/ with cover.jpg files (any size/format)
2. Run normalize_coverart.exe Albums
3. Run patch_dkvsong_coverart.exe to update database
4. Eject USB and insert into DKC-900


BACKUP AND RECOVERY
-------------------
Original images saved as:
  cover.original.jpg

To restore originals:
  1. Delete cover.jpg
  2. Rename cover.original.jpg to cover.jpg
  3. Re-run tool if needed


WHY 265 x 265?
--------------
- Verified from Yamaha Downloaded Songs
- Efficient for embedded display hardware
- Avoids unnecessary scaling on playback
- Matches ENSPIRE UI behavior
- Reduces USB storage requirements

Yamaha does not publish official specs, but this size is
proven to work reliably across all DKC-900 systems.


TROUBLESHOOTING
---------------
- Use --dry-run first to preview changes
- Backups are created automatically (cover.original.jpg)
- Tool skips files it can't read or process
- Progressive JPEG is avoided (compatibility)
- All images converted to RGB color space


MORE INFORMATION
----------------
https://github.com/joenardone/disklavier-tools
Credit: Alexander Peppe (alexanderpeppe.com) for DKC-900 assistance
