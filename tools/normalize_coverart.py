#!/usr/bin/env python3
"""
Normalize album cover art to 265x265 pixels for Yamaha DKC-900.

Yamaha Downloaded Songs use 265x265 JPEG artwork. This tool normalizes
all album artwork to match that format for consistent display and faster loading.
"""
import os
import argparse
from pathlib import Path
import sys
try:
    from PIL import Image, ImageOps
except ImportError:
    print("ERROR: Pillow library is required. Install with: pip install pillow")
    sys.exit(1)


def normalize_cover(source_path, target_path, size=265, quality=88, backup=True):
    """
    Normalize an image to square size with center crop.
    
    Args:
        source_path: Input image path
        target_path: Output image path
        size: Target size (will be square: size x size)
        quality: JPEG quality (1-100)
        backup: Create backup of original as .original.jpg
    """
    img = Image.open(source_path)
    img = ImageOps.exif_transpose(img)  # respect EXIF rotation
    img = img.convert("RGB")

    # Center-crop to square, then resize
    img = ImageOps.fit(img, (size, size), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

    # Save as baseline JPEG (avoid progressive for compatibility)
    img.save(target_path, "JPEG", quality=quality, optimize=True, progressive=False)


def normalize_folder(root_dir, size=265, quality=88, dry_run=False, recursive=True):
    """
    Normalize all cover.jpg files in albums folder.
    
    Args:
        root_dir: Root directory containing album folders
        size: Target size (default: 265 for DKC-900)
        quality: JPEG quality (default: 88)
        dry_run: Preview changes without modifying files
        recursive: Process subdirectories
    """
    root_path = Path(root_dir)
    
    if not root_path.is_dir():
        raise SystemExit(f"ERROR: Directory not found: {root_dir}")

    print(f"Scanning for cover.jpg files in: {root_path}")
    if dry_run:
        print("[DRY RUN MODE - No files will be modified]\n")

    changed = 0
    skipped = 0
    errors = 0

    # Find all cover.jpg files
    pattern = "**/cover.jpg" if recursive else "cover.jpg"
    cover_files = list(root_path.glob(pattern))
    
    # Case-insensitive search for Windows
    if not cover_files and os.name == 'nt':
        all_jpgs = list(root_path.glob("**/*.jpg" if recursive else "*.jpg"))
        cover_files = [f for f in all_jpgs if f.name.lower() == "cover.jpg"]

    print(f"Found {len(cover_files)} cover.jpg files\n")

    for cover_path in cover_files:
        backup_path = cover_path.parent / "cover.original.jpg"
        
        try:
            # Check if backup already exists
            if backup_path.exists():
                source = backup_path
                print(f"Using existing backup: {cover_path.parent.name}/")
            else:
                source = cover_path
                print(f"Processing: {cover_path.parent.name}/")

            if dry_run:
                try:
                    img = Image.open(source)
                    w, h = img.size
                    print(f"  Current: {w}x{h} → Would normalize to {size}x{size}")
                except Exception as e:
                    print(f"  ERROR: {e}")
                    errors += 1
                    continue
                changed += 1
            else:
                # Create backup on first run
                if not backup_path.exists() and source == cover_path:
                    cover_path.rename(backup_path)
                    source = backup_path
                    print(f"  Created backup: cover.original.jpg")
                
                # Normalize from backup (or original if no backup yet)
                normalize_cover(source, cover_path, size=size, quality=quality)
                
                img = Image.open(cover_path)
                w, h = img.size
                print(f"  ✓ Normalized to {w}x{h}")
                changed += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1
            skipped += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}DONE:")
    print(f"  {'Would normalize' if dry_run else 'Normalized'}: {changed}")
    if skipped:
        print(f"  Skipped (errors): {skipped}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Normalize album cover art to 265x265 for Yamaha DKC-900",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Normalize all cover.jpg in Albums folder
  normalize_coverart.exe /path/to/usb/Albums
  
  # Normalize in current directory
  normalize_coverart.exe .
  
  # Dry run to preview changes
  normalize_coverart.exe --dry-run Albums
  
  # Custom size (e.g., for other devices)
  normalize_coverart.exe --size 300 Albums
  
  # Recurse into subdirectories
  normalize_coverart.exe --recursive Albums

Note: Original images are backed up as cover.original.jpg
        """
    )
    parser.add_argument('directory', nargs='?', default='.', help='directory containing album folders with cover.jpg files (default: current directory)')
    parser.add_argument('--size', type=int, default=265,
                       help='target size in pixels (square: SIZExSIZE, default: 265)')
    parser.add_argument('--quality', type=int, default=88,
                       help='JPEG quality 1-100 (default: 88)')
    parser.add_argument('--recursive', action='store_true',
                       help='process subdirectories')
    parser.add_argument('--dry-run', action='store_true',
                       help='preview changes without modifying files')
    
    args = parser.parse_args(argv)
    
    if args.quality < 1 or args.quality > 100:
        print("ERROR: quality must be between 1 and 100")
        return 1
    
    if args.size < 1:
        print("ERROR: size must be positive")
        return 1
    
    try:
        normalize_folder(
            args.directory,
            size=args.size,
            quality=args.quality,
            dry_run=args.dry_run,
            recursive=args.recursive
        )
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
