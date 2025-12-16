from pathlib import Path
import argparse
import mido
import sys


def sanitize_title(title: str) -> str:
    """Convert title to latin-1 compatible string, replacing common Unicode chars."""
    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        '\u2019': "'",  # Right single quotation mark
        '\u2018': "'",  # Left single quotation mark
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2026': '...',  # Horizontal ellipsis
    }
    
    for unicode_char, ascii_char in replacements.items():
        title = title.replace(unicode_char, ascii_char)
    
    # Remove any remaining characters that can't be encoded in latin-1
    title = title.encode('latin-1', errors='ignore').decode('latin-1')
    
    return title


def update_midi_title(midi_path: Path, dry_run: bool = False):
    """
    Update a MIDI file's title metadata to match its filename (without extension).
    
    Returns:
        (bool, str): (success, error_message if failed)
    """
    try:
        # Validate it's a MIDI file
        mid = mido.MidiFile(midi_path)
    except Exception as e:
        error_msg = f"Cannot load: {e}"
        print(f"ERROR: {midi_path.name} - {error_msg}")
        return False, error_msg
    
    # Check for type 0 with multiple tracks - this is invalid and cannot be saved
    if mid.type == 0 and len(mid.tracks) > 1:
        print(f"SKIP: {midi_path.name} (type 0 with {len(mid.tracks)} tracks - use convert_midi_type.exe to fix)")
        return True, None  # Return True to not count as failure
    
    # Extract title from filename (without extension)
    new_title = midi_path.stem
    
    # Sanitize title to latin-1 compatible characters
    new_title = sanitize_title(new_title)
    
    # Find and update track_name in first track
    track = mid.tracks[0]
    found_track_name = False
    
    for i, msg in enumerate(track):
        if msg.type == 'track_name':
            old_title = msg.name
            if old_title == new_title:
                print(f"SKIP: {midi_path.name} (title already matches)")
                return True, None
            
            if dry_run:
                print(f"DRY RUN: {midi_path.name}: '{old_title}' -> '{new_title}'")
            else:
                track[i] = mido.MetaMessage('track_name', name=new_title, time=msg.time)
                print(f"UPDATE: {midi_path.name}: '{old_title}' -> '{new_title}'")
            found_track_name = True
            break
    
    # If no track_name exists, insert one at the beginning
    if not found_track_name:
        if dry_run:
            print(f"DRY RUN: {midi_path.name}: (no title) -> '{new_title}'")
        else:
            track.insert(0, mido.MetaMessage('track_name', name=new_title, time=0))
            print(f"INSERT: {midi_path.name}: (no title) -> '{new_title}'")
    
    # Save the file (unless dry run)
    if not dry_run:
        try:
            mid.save(midi_path)
        except Exception as e:
            error_msg = f"Cannot save: {e}"
            print(f"ERROR: {midi_path.name} - {error_msg}")
            return False, error_msg
    
    return True, None


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='mid_title_from_filename',
        description='Update MIDI file title metadata to match filename (without extension)'
    )
    parser.add_argument('--version', action='version', version='mid_title_from_filename 0.1')
    parser.add_argument('input', nargs='?', default='.', help='input .mid file path or directory containing .mid files (default: current directory)')
    parser.add_argument('--recursive', action='store_true', help='recurse into subdirectories to find .mid files')
    parser.add_argument('--dry-run', action='store_true', help='show what would be changed without modifying files')
    return parser


def main(argv=None):
    parser = get_parser()
    args = parser.parse_args(argv)
    in_path = Path(args.input)
    
    if not in_path.exists():
        print(f"ERROR: Path does not exist: {in_path}")
        return 1
    
    # Collect files to process
    files = []
    if in_path.is_file():
        if in_path.suffix.lower() == '.mid':
            files = [in_path]
        else:
            print(f"ERROR: File must have .mid extension: {in_path}")
            return 1
    elif in_path.is_dir():
        if args.recursive:
            files = list(in_path.rglob('*.mid'))
        else:
            files = list(in_path.glob('*.mid'))
        
        if not files:
            print(f"No .mid files found in: {in_path}")
            return 0
    else:
        print(f"ERROR: Invalid path: {in_path}")
        return 1
    
    # Process files
    success_count = 0
    failed_files = []  # List of (Path, error_message) tuples
    
    for fp in sorted(files):
        success, error_msg = update_midi_title(fp, dry_run=args.dry_run)
        if success:
            success_count += 1
        else:
            failed_files.append((fp, error_msg))
    
    # Summary
    print(f"\nProcessed {len(files)} file(s): {success_count} successful, {len(failed_files)} failed")
    sys.stdout.flush()
    
    # Show failed files if any
    if failed_files:
        print(f"\nFailed files:")
        sys.stdout.flush()
        for fp, error_msg in failed_files:
            print(f"  • {fp}")
            if error_msg:
                print(f"    {error_msg}")
        sys.stdout.flush()
    
    return 0 if len(failed_files) == 0 else 1


if __name__ == '__main__':
    result = main()
    # Keep window open if not running in interactive terminal
    try:
        if sys.stdin and sys.stdin.isatty():
            pass  # Interactive terminal, let it close normally
        else:
            input("\nPress Enter to close...")
    except:
        input("\nPress Enter to close...")
    sys.exit(result)
