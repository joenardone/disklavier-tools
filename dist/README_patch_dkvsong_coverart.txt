============================================================
PATCH_DKVSONG_COVERART - DKC-900 Database Patcher
============================================================

DESCRIPTION
-----------
Patches Yamaha DKC-900 .dkvsong.db to register album cover
art for ALL albums. The DKC-900 only auto-registers artwork
for Downloaded Songs; this tool fixes that limitation.

** IMPORTANT: DKC-900 does NOT support ampersand (&) in folder names!
   Use hyphens instead: "Pop - Rock" NOT "Pop & Rock"
   Use hyphens instead: "Jazz - Blues" NOT "Jazz & Blues" **


PURPOSE
-------
The DKC-900 does NOT automatically display album artwork for
user albums even when cover.jpg exists in the album folder.

This tool updates the database so ALL albums with cover.jpg
display their artwork correctly.


REQUIREMENTS
------------
- USB drive with .dkvsong.db at root
- Album folders with cover.jpg files (any location)
- USB must be mounted on PC (not in piano)


QUICK START
-----------
1. Copy patch_dkvsong_coverart.exe to USB root (where .dkvsong.db is)
2. Double-click patch_dkvsong_coverart.exe
3. All albums with cover.jpg will be registered


BASIC USAGE
-----------
Patch database in current directory:
  patch_dkvsong_coverart.exe

Patch specific database:
  patch_dkvsong_coverart.exe D:\.dkvsong.db

Preview changes first:
  patch_dkvsong_coverart.exe --dry-run


OPTIONS
-------
--dry-run
  Preview changes without modifying database
  Example: patch_dkvsong_coverart.exe --dry-run


WHAT IT DOES
------------
1. Creates timestamped backup of .dkvsong.db
2. Scans for albums with cover.jpg but no registered artwork
3. Updates database to reference existing cover.jpg files
4. Reports what was patched


WHAT IT DOESN'T DO
------------------
- Does NOT resize images (use normalize_coverart.exe first)
- Does NOT scan folders dynamically
- Does NOT modify MIDI or MP3 files
- Does NOT change Downloaded Songs albums
- Does NOT prevent piano from rebuilding database


EXPECTED USB STRUCTURE
----------------------
USB_ROOT\
  .dkvsong.db
  Albums\
    Artist - Album Name\
      cover.jpg
      01 - Track.mid
      01 - Track.mp3


EXAMPLES
--------
# Typical usage at USB root
E:
cd \
patch_dkvsong_coverart.exe .dkvsong.db

# Preview changes first
patch_dkvsong_coverart.exe --dry-run .dkvsong.db

# Custom albums folder
patch_dkvsong_coverart.exe --albums-folder Music .dkvsong.db


RECOMMENDED WORKFLOW
--------------------
1. Prepare Albums/ with cover.jpg files
2. Run normalize_coverart.exe to resize images to 265x265
3. Run patch_dkvsong_coverart.exe to update database
4. Safely eject USB
5. Insert USB into DKC-900
6. Album cover art should now display


SAFETY / RECOVERY
-----------------
Automatic backup:
  .dkvsong.db.bak-YYYYMMDD-HHMMSS

To undo:
  1. Delete .dkvsong.db
  2. Rename backup to .dkvsong.db
  OR
  3. Let piano rebuild database (delete .dkvsong.db)


WHY THIS IS NECESSARY
---------------------
The DKC-900 firmware only auto-registers artwork for Yamaha
Downloaded Songs. User Albums are indexed WITHOUT artwork
unless the database is explicitly patched.


TROUBLESHOOTING
---------------
- Ensure cover.jpg exists (exact name, lowercase .jpg)
- Run normalize_coverart.exe first if images are large
- Backup files are created automatically
- Use --dry-run to preview before applying

⚠️ COVER ART NOT SHOWING?
- Check if folder names contain & (ampersand) character
- DKC-900 DOES NOT support & in folder names
- Rename "Jazz & Blues" to "Jazz - Blues"
- Rename "Pop & Rock" to "Pop - Rock"
- Then run patch_dkvsong_coverart.exe again


MORE INFORMATION
----------------
https://github.com/joenardone/disklavier-tools
Credit: Alexander Peppe (alexanderpeppe.com) for DKC-900 assistance
