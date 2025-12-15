"""
Remove metadata added by embed_tags_metadata.py
"""
import mido
from pathlib import Path
import sys
import argparse


def remove_tags_from_midi(midi_path):
    """
    Remove metadata tags added by embed_tags_metadata.py
    
    Removes:
    - Text messages starting with: Artist:, Album:, Composer:, Catalog:, Genre:
    - Copyright messages matching pattern: (P) YYYY Yamaha Corporation
    
    Returns:
        bool: True if file was modified, False if no changes needed
    """
    try:
        mid = mido.MidiFile(midi_path)
        
        if len(mid.tracks) == 0:
            return False
        
        track = mid.tracks[0]
        
        # Messages to remove
        indices_to_remove = []
        
        for i, msg in enumerate(track):
            if msg.is_meta:
                # Remove text messages with our prefixes
                if msg.type == 'text':
                    text = msg.text
                    if any(text.startswith(prefix) for prefix in ['Artist:', 'Album:', 'Composer:', 'Catalog:', 'Genre:']):
                        indices_to_remove.append(i)
                
                # Remove copyright messages matching our pattern
                elif msg.type == 'copyright':
                    if msg.text.startswith('(P) ') and 'Yamaha Corporation' in msg.text:
                        indices_to_remove.append(i)
        
        if not indices_to_remove:
            return False
        
        # Remove messages in reverse order to preserve indices
        for i in reversed(indices_to_remove):
            del track[i]
        
        # Save the modified file
        mid.save(midi_path)
        return True
        
    except Exception as e:
        print(f"Error processing {Path(midi_path).name}: {e}")
        return False


def process_directory(directory, recursive=True, dry_run=False):
    """Process all MIDI files in directory."""
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Error: Directory not found: {directory}", file=sys.stderr)
        return
    
    # Find all .mid files
    if recursive:
        midi_files = list(directory.rglob('*.mid'))
    else:
        midi_files = list(directory.glob('*.mid'))
    
    if not midi_files:
        print(f"No .mid files found in {directory}")
        return
    
    print(f"Found {len(midi_files)} .mid file(s)\n")
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for midi_file in sorted(midi_files):
        if dry_run:
            # Just scan without modifying
            try:
                mid = mido.MidiFile(midi_file)
                if len(mid.tracks) > 0:
                    track = mid.tracks[0]
                    has_tags = False
                    for msg in track:
                        if msg.is_meta and msg.type == 'text':
                            if any(msg.text.startswith(prefix) for prefix in ['Artist:', 'Album:', 'Composer:', 'Catalog:', 'Genre:']):
                                has_tags = True
                                break
                    
                    if has_tags:
                        print(f"Would remove metadata from: {midi_file.name}")
                        processed_count += 1
                    else:
                        skipped_count += 1
            except Exception as e:
                error_count += 1
        else:
            result = remove_tags_from_midi(midi_file)
            if result:
                print(f"Removed metadata from: {midi_file.name}")
                processed_count += 1
            else:
                skipped_count += 1
    
    print(f"\nSummary:")
    print(f"  {'Would remove metadata from' if dry_run else 'Removed metadata from'}: {processed_count}")
    print(f"  Skipped (no metadata to remove): {skipped_count}")
    if error_count > 0:
        print(f"  Errors: {error_count}")


def main():
    parser = argparse.ArgumentParser(
        description='Remove metadata added by embed_tags_metadata.py',
        epilog='Removes Artist, Album, Composer, Catalog, Genre text messages and copyright.'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='MIDI file or directory to process (default: current directory)'
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not scan subdirectories'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be removed without modifying files'
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        if path.suffix != '.mid':
            print(f"Error: File must be .mid: {path}", file=sys.stderr)
            sys.exit(1)
        
        if args.dry_run:
            print(f"[DRY RUN] Would process: {path.name}")
        else:
            result = remove_tags_from_midi(path)
            if result:
                print(f"Removed metadata from {path.name}")
            else:
                print(f"No metadata to remove from {path.name}")
    
    elif path.is_dir():
        # Process directory
        process_directory(path, recursive=not args.no_recursive, dry_run=args.dry_run)
    else:
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
