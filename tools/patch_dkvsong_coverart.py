#!/usr/bin/env python3
"""
Patch Yamaha DKC-900 .dkvsong.db to register album cover art.

The DKC-900 only auto-registers artwork for Downloaded Songs.
User albums need explicit database entries for cover.jpg to display.
"""
import os
import shutil
import sqlite3
from datetime import datetime
import argparse
from urllib.parse import unquote


def find_table(conn, name):
    """Check if a table exists in the database."""
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


def get_columns(conn, table):
    """Get all column names for a table."""
    cols = []
    for cid, name, coltype, notnull, dflt, pk in conn.execute(f"PRAGMA table_info({table})"):
        cols.append(name)
    return cols


def patch_coverart(db_path, albums_folder="Albums", dry_run=False):
    """
    Patch .dkvsong.db to register cover.jpg for albums.
    
    Args:
        db_path: Path to .dkvsong.db file
        albums_folder: Name of albums folder (default: "Albums")
        dry_run: If True, show what would be changed without modifying database
    """
    if not os.path.isfile(db_path):
        raise SystemExit(f"ERROR: Database not found: {db_path}")

    usb_root = os.path.dirname(os.path.abspath(db_path))

    # Create backup (skip for dry-run)
    if not dry_run:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = db_path + f".bak-{ts}"
        shutil.copy2(db_path, backup_path)
        print(f"Backup created: {backup_path}")
    else:
        print("[DRY RUN] No backup created")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        if not find_table(conn, "album"):
            raise SystemExit("ERROR: table 'album' not found in this database.")

        cols = get_columns(conn, "album")
        if "album_path" not in cols or "coverart_path" not in cols:
            raise SystemExit("ERROR: album table missing expected columns (album_path / coverart_path).")

        # Select albums where coverart_path is blank/null
        rows = conn.execute("""
            SELECT rowid, album_path, coverart_path
            FROM album
            WHERE (coverart_path IS NULL OR TRIM(coverart_path) = '')
        """).fetchall()

        print(f"\nAlbums needing cover art patch: {len(rows)}")

        patched = 0
        skipped_missing_file = 0

        for r in rows:
            album_path = r["album_path"]  # e.g. Albums/Jim Brickman - The Romance...
            # URL-decode path (handles %20, %26, etc.) and convert to OS path
            album_path_decoded = unquote(album_path)
            # cover.jpg is in the album directory (on disk)
            cover_on_disk = os.path.join(usb_root, album_path_decoded.replace("/", os.sep), "cover.jpg")

            if os.path.isfile(cover_on_disk):
                cover_db_path = album_path.rstrip("/") + "/cover.jpg"  # keep DB style with /
                
                if dry_run:
                    print(f"[DRY RUN] Would patch: {album_path}")
                else:
                    conn.execute(
                        "UPDATE album SET coverart_path=? WHERE rowid=?",
                        (cover_db_path, r["rowid"])
                    )
                patched += 1
            else:
                if dry_run:
                    print(f"[DRY RUN] Would skip (no cover.jpg): {album_path}")
                skipped_missing_file += 1

        if not dry_run:
            conn.commit()
            print(f"\n✓ Patched albums: {patched}")
        else:
            print(f"\n[DRY RUN] Would patch: {patched} albums")
        
        print(f"  Skipped (no cover.jpg found): {skipped_missing_file}")
        print("\nDONE.")

    except Exception:
        if not dry_run:
            conn.rollback()
        raise
    finally:
        conn.close()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Patch Yamaha DKC-900 .dkvsong.db to register album cover art for ALL albums with cover.jpg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Patch database in current directory (auto-finds .dkvsong.db)
  patch_dkvsong_coverart.exe
  
  # Patch specific database
  patch_dkvsong_coverart.exe /path/to/usb/.dkvsong.db
  
  # Dry run to preview changes
  patch_dkvsong_coverart.exe --dry-run
  
Note: This patches ALL albums with empty coverart_path, not just Albums/ folder.
      Any album with cover.jpg in its directory will be registered.
        """
    )
    parser.add_argument('database', nargs='?', default='.dkvsong.db',
                       help='path to .dkvsong.db file (default: .dkvsong.db in current directory)')
    parser.add_argument('--albums-folder', default='Albums', 
                       help='name of albums folder (default: Albums - unused, kept for compatibility)')
    parser.add_argument('--dry-run', action='store_true',
                       help='preview changes without modifying database')
    
    args = parser.parse_args(argv)
    
    try:
        patch_coverart(args.database, args.albums_folder, args.dry_run)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
