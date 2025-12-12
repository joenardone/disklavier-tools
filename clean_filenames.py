from pathlib import Path
import argparse
import sys
from collections import defaultdict


def sanitize_filename(name: str) -> str:
    """
    Clean filename by replacing Unicode characters and illegal characters.
    
    Replaces:
    - Curly quotes with straight quotes
    - Em/en dashes with hyphens
    - Other Unicode with ASCII equivalents
    - Illegal Windows characters: < > : " / \ | ? *
    """
    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        '\u2019': "'",  # Right single quotation mark (curly apostrophe)
        '\u2018': "'",  # Left single quotation mark
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2026': '...',  # Horizontal ellipsis
        '\u00a0': ' ',  # Non-breaking space
    }
    
    for unicode_char, ascii_char in replacements.items():
        name = name.replace(unicode_char, ascii_char)
    
    # Replace illegal Windows filename characters
    illegal_chars = {
        '<': '',
        '>': '',
        ':': '-',
        '"': "'",
        '/': '-',
        '\\': '-',
        '|': '-',
        '?': '',
        '*': '',
    }
    
    for illegal_char, replacement in illegal_chars.items():
        name = name.replace(illegal_char, replacement)
    
    # Clean up multiple spaces and trim
    while '  ' in name:
        name = name.replace('  ', ' ')
    name = name.strip()
    
    # Remove leading/trailing dots and spaces (Windows doesn't like them)
    name = name.strip('. ')
    
    return name


def needs_cleaning(name: str) -> bool:
    """Check if a filename needs cleaning."""
    return sanitize_filename(name) != name


def process_files(directory: Path, recursive: bool, dry_run: bool):
    """
    Process files in directory, grouping related files together.
    
    Files with the same stem (name without extension) are renamed together
    to keep .mid and .mp3 files synchronized.
    """
    # Collect all files
    if recursive:
        all_files = [f for f in directory.rglob('*') if f.is_file()]
    else:
        all_files = [f for f in directory.glob('*') if f.is_file()]
    
    # Group files by directory and stem
    file_groups = defaultdict(list)
    for file_path in all_files:
        if needs_cleaning(file_path.name):
            key = (file_path.parent, file_path.stem)
            file_groups[key].append(file_path)
    
    # Process each group
    renamed_count = 0
    skip_count = 0
    error_count = 0
    
    for (parent, old_stem), files in sorted(file_groups.items()):
        new_stem = sanitize_filename(old_stem)
        
        # Check if any target files would conflict
        conflicts = []
        for file_path in files:
            new_name = new_stem + file_path.suffix
            new_path = parent / new_name
            
            if new_path.exists() and new_path not in files:
                conflicts.append(new_path)
        
        if conflicts:
            print(f"SKIP (conflict): {parent / old_stem}* -> {parent / new_stem}* (target exists)")
            skip_count += len(files)
            continue
        
        # Rename all files in the group
        for file_path in files:
            old_name = file_path.name
            new_name = sanitize_filename(file_path.stem) + file_path.suffix
            new_path = parent / new_name
            
            if old_name == new_name:
                continue
            
            try:
                if dry_run:
                    print(f"DRY RUN: {file_path.relative_to(directory.parent if recursive else directory)} -> {new_name}")
                else:
                    file_path.rename(new_path)
                    print(f"RENAME: {file_path.relative_to(directory.parent if recursive else directory)} -> {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"ERROR: {file_path}: {e}")
                error_count += 1
    
    return renamed_count, skip_count, error_count


def process_directories(directory: Path, recursive: bool, dry_run: bool):
    """Process directory names (bottom-up to avoid breaking paths)."""
    if not recursive:
        # Only process immediate subdirectories
        dirs = [d for d in directory.glob('*') if d.is_dir() and needs_cleaning(d.name)]
    else:
        # Get all subdirectories, sorted by depth (deepest first)
        dirs = [d for d in directory.rglob('*') if d.is_dir() and needs_cleaning(d.name)]
        dirs.sort(key=lambda p: len(p.parts), reverse=True)
    
    renamed_count = 0
    skip_count = 0
    error_count = 0
    
    for dir_path in dirs:
        old_name = dir_path.name
        new_name = sanitize_filename(old_name)
        
        if old_name == new_name:
            continue
        
        new_path = dir_path.parent / new_name
        
        if new_path.exists():
            print(f"SKIP (exists): {dir_path.relative_to(directory.parent if recursive else directory)} -> {new_name}")
            skip_count += 1
            continue
        
        try:
            if dry_run:
                print(f"DRY RUN DIR: {dir_path.relative_to(directory.parent if recursive else directory)} -> {new_name}")
            else:
                dir_path.rename(new_path)
                print(f"RENAME DIR: {dir_path.relative_to(directory.parent if recursive else directory)} -> {new_name}")
            renamed_count += 1
        except Exception as e:
            print(f"ERROR: {dir_path}: {e}")
            error_count += 1
    
    return renamed_count, skip_count, error_count


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='clean_filenames',
        description='Clean filenames by replacing Unicode and illegal characters with ASCII equivalents'
    )
    parser.add_argument('--version', action='version', version='clean_filenames 0.1')
    parser.add_argument('path', help='directory to process')
    parser.add_argument('--recursive', action='store_true', help='process subdirectories recursively')
    parser.add_argument('--dry-run', action='store_true', help='show what would be changed without modifying files')
    parser.add_argument('--dirs-only', action='store_true', help='only rename directories, not files')
    parser.add_argument('--files-only', action='store_true', help='only rename files, not directories')
    return parser


def main(argv=None):
    parser = get_parser()
    args = parser.parse_args(argv)
    path = Path(args.path)
    
    if not path.exists():
        print(f"ERROR: Path does not exist: {path}")
        return 1
    
    if not path.is_dir():
        print(f"ERROR: Path must be a directory: {path}")
        return 1
    
    total_files_renamed = 0
    total_files_skipped = 0
    total_files_errors = 0
    total_dirs_renamed = 0
    total_dirs_skipped = 0
    total_dirs_errors = 0
    
    # Process files first (so we don't break paths)
    if not args.dirs_only:
        print("Processing files...")
        total_files_renamed, total_files_skipped, total_files_errors = process_files(
            path, args.recursive, args.dry_run
        )
    
    # Process directories (bottom-up)
    if not args.files_only:
        print("\nProcessing directories...")
        total_dirs_renamed, total_dirs_skipped, total_dirs_errors = process_directories(
            path, args.recursive, args.dry_run
        )
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"  Files renamed: {total_files_renamed}")
    print(f"  Files skipped: {total_files_skipped}")
    print(f"  File errors: {total_files_errors}")
    print(f"  Directories renamed: {total_dirs_renamed}")
    print(f"  Directories skipped: {total_dirs_skipped}")
    print(f"  Directory errors: {total_dirs_errors}")
    print("="*60)
    
    return 0 if (total_files_errors == 0 and total_dirs_errors == 0) else 1


if __name__ == '__main__':
    sys.exit(main())
