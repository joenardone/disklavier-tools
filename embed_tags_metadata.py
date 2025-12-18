#!/usr/bin/env python3
"""
Embed metadata from PFBU .tags.txt files into MIDI files.

PFBU (Piano Floppy Backup Utility) extracts metadata from Disklavier floppies
and saves it in .tags.txt files. This tool reads those tags and embeds them
into MIDI files as standard MIDI metadata messages.
"""
import sys
import mido
from pathlib import Path
import argparse
import re


def parse_filename_metadata(midi_path, auto_track_number=None, keep_full_filename=False):
    """
    Parse metadata from filename pattern: NN_title.mid or N-NN_title.mid or NNN_title.mid or NNN-title.mid
    
    Args:
        midi_path: Path to MIDI file
        auto_track_number: If provided, use this track number for files without a track prefix
        keep_full_filename: If True, use full filename as title (for DKC-900 display with track number)
    
    Returns:
        dict with parsed metadata including:
        - TIT2: Song title (from filename)
        - TALB: Album name (from parent directory)
        - TRCK: Track number (from filename prefix or auto-assigned)
        - Disc number if present in N-NN format
    """
    path = Path(midi_path)
    filename = path.stem
    
    tags = {}
    
    # If keep_full_filename is True, use entire filename as title but still parse track number
    if keep_full_filename:
        # Still need to extract track number for TRCK tag
        # Parse track number prefix patterns:
        disc_track_pattern = r'^(\d+)-(\d{2,3})[-_]'
        simple_underscore = r'^(\d{2,3})_'
        simple_hyphen = r'^(\d{2,3})-'
        
        disc_match = re.match(disc_track_pattern, filename)
        underscore_match = re.match(simple_underscore, filename)
        hyphen_match = re.match(simple_hyphen, filename)
        
        if disc_match:
            track_num = disc_match.group(2)
            tags['TRCK'] = f"{int(track_num)}"
        elif underscore_match:
            track_num = underscore_match.group(1)
            tags['TRCK'] = f"{int(track_num)}"
        elif hyphen_match:
            track_num = hyphen_match.group(1)
            tags['TRCK'] = f"{int(track_num)}"
        else:
            tags['TRCK'] = str(auto_track_number) if auto_track_number else '1'
        
        # Use full filename as title (replace underscores with spaces)
        title = filename.replace('_', ' ').strip()
        tags['TIT2'] = title
    else:
        # Original behavior: extract title without track prefix
        # Parse track number prefix patterns:
        # NN_ or NNN_ (e.g., "01_Song.mid" or "001_Song.mid")
        # NN- or NNN- (e.g., "036-2004-Song.mid")
        # N-NN_ (disc-track format, e.g., "1-05_Song.mid")
        
        # Try disc-track format first: N-NN_title
        disc_track_pattern = r'^(\d+)-(\d{2,3})[-_](.+)$'
        disc_match = re.match(disc_track_pattern, filename)
        
        # Try simple track with underscore: NN_title or NNN_title
        simple_underscore = r'^(\d{2,3})_(.+)$'
        underscore_match = re.match(simple_underscore, filename)
        
        # Try simple track with hyphen: NN-title or NNN-title
        simple_hyphen = r'^(\d{2,3})-(.+)$'
        hyphen_match = re.match(simple_hyphen, filename)
        
        if disc_match:
            # Format: N-NN_title or N-NN-title
            disc_num = disc_match.group(1)
            track_num = disc_match.group(2)
            title = disc_match.group(3)
            tags['TRCK'] = f"{int(track_num)}"  # Store as track number
            # Could store disc info in TPOS tag if needed
        elif underscore_match:
            # Format: NN_title or NNN_title
            track_num = underscore_match.group(1)
            title = underscore_match.group(2)
            tags['TRCK'] = f"{int(track_num)}"  # Remove leading zeros
        elif hyphen_match:
            # Format: NN-title or NNN-title
            track_num = hyphen_match.group(1)
            title = hyphen_match.group(2)
            tags['TRCK'] = f"{int(track_num)}"  # Remove leading zeros
        else:
            # No track number prefix, use auto-assigned number or 1
            title = filename
            tags['TRCK'] = str(auto_track_number) if auto_track_number else '1'
        
        # Clean up title (replace underscores with spaces)
        title = title.replace('_', ' ').strip()
        tags['TIT2'] = title
    
    # Album name from parent directory
    album_name = path.parent.name
    tags['TALB'] = album_name
    
    # Set empty but present fields
    tags['TPE1'] = ''  # Artist
    tags['TCOM'] = ''  # Composer
    tags['TYER'] = ''  # Year
    tags['COMM'] = ''  # Catalog
    tags['TCON'] = ''  # Genre
    
    return tags


def parse_tags_file(tags_path):
    """
    Parse PFBU .tags.txt file.
    
    Format:
        TIT2=Title
        TPE1=Artist
        TALB=Album
        TYER=Year
        COMM=Catalog
        TRCK=Track
        TCOM=Composer
        TPE2=Album Artist
        TMED=Medium
        TCON=Genre
    
    Returns:
        dict with parsed tags
    """
    tags = {}
    
    try:
        with open(tags_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '=' not in line:
                    continue
                
                key, value = line.split('=', 1)
                tags[key] = value
    except Exception as e:
        print(f"Error reading tags file {tags_path}: {e}")
        return None
    
    return tags


def clean_genre(genre):
    """Remove (Disklavier) suffix from genre."""
    if genre:
        # Remove (Disklavier) or similar suffixes
        genre = re.sub(r'\s*\(Disklavier\)\s*$', '', genre, flags=re.IGNORECASE)
        return genre.strip()
    return genre


def embed_tags_in_midi(midi_path, tags, output_path=None, add_xf_metadata=False, force=False):
    """
    Embed metadata from tags into MIDI file.
    
    Args:
        midi_path: Path to input MIDI file
        tags: Dict of parsed tags
        output_path: Path for output file (default: overwrite input)
        add_xf_metadata: If True, also add XF Solo metadata
        force: If True, always write even if metadata matches existing
    
    Returns:
        dict with status: {'modified': bool, 'reason': str}
    """
    try:
        mid = mido.MidiFile(midi_path)
        
        if len(mid.tracks) == 0:
            print(f"Error: {Path(midi_path).name} has no tracks")
            return {'modified': False, 'reason': 'no tracks'}
        
        track = mid.tracks[0]
        
        # Find ALL track_names in the entire file and remove duplicates
        # We need to: 1) Update the first track_name, 2) Remove ALL subsequent track_names
        insert_pos = 0
        first_track_name_idx = None
        track_names_to_remove = []
        
        # First pass: find all track_names throughout the entire track
        for i, msg in enumerate(track):
            if msg.is_meta and msg.type == 'track_name':
                if first_track_name_idx is None:
                    # This is the first track_name - we'll update it
                    first_track_name_idx = i
                else:
                    # This is a duplicate track_name anywhere in the file - mark for removal
                    track_names_to_remove.append(i)
        
        # Remove ALL duplicate track_names (in reverse order to preserve indices)
        needs_update = False
        for idx in reversed(track_names_to_remove):
            track.pop(idx)
            needs_update = True
        
        # Second pass: find insertion point and update first track_name
        for i, msg in enumerate(track):
            if msg.type in ['set_tempo', 'time_signature', 'key_signature']:
                insert_pos = i + 1
            elif msg.is_meta and msg.type == 'track_name':
                # Update the first (and now only) track_name
                if 'TIT2' in tags and msg.name != tags['TIT2']:
                    msg.name = tags['TIT2']
                    needs_update = True
                insert_pos = i + 1
                break
        
        # Scan existing text messages to check what's already there
        existing_text_messages = {}
        for msg in track:
            if msg.is_meta and msg.type == 'text':
                text = msg.text
                # Parse format like "Artist: Some Artist"
                if ':' in text:
                    key, value = text.split(':', 1)
                    existing_text_messages[key.strip()] = value.strip()
        
        # Build list of new metadata messages and track changes
        new_messages = []
        messages_to_remove = []
        # needs_update already set above if we removed duplicate track_names
        
        # Track name (title)
        if 'TIT2' in tags:
            # Check if track_name already exists
            has_track_name = any(msg.type == 'track_name' for msg in track if msg.is_meta)
            if not has_track_name:
                new_messages.append(mido.MetaMessage('track_name', name=tags['TIT2'], time=0))
                needs_update = True
        
        # Copyright (use year from tags if available)
        year = tags.get('TYER', '2025')
        expected_copyright = f'(P) {year} Yamaha Corporation'
        existing_copyright = None
        for msg in track:
            if msg.is_meta and msg.type == 'copyright':
                existing_copyright = msg.text
                break
        
        if existing_copyright is None:
            new_messages.append(mido.MetaMessage('copyright', text=expected_copyright, time=0))
            needs_update = True
        elif existing_copyright != expected_copyright:
            # Update existing copyright
            for msg in track:
                if msg.is_meta and msg.type == 'copyright':
                    msg.text = expected_copyright
                    needs_update = True
                    break
        
        # Text metadata (artist, album, composer, catalog, genre)
        # Check each field and only add/update if different
        text_fields = [
            ('TPE1', 'Artist'),
            ('TALB', 'Album'),
            ('TCOM', 'Composer'),
            ('COMM', 'Catalog'),
        ]
        
        for tag_key, field_name in text_fields:
            if tag_key in tags:
                expected_value = tags[tag_key]
                existing_value = existing_text_messages.get(field_name)
                
                if existing_value is None:
                    # Doesn't exist, add it
                    new_messages.append(mido.MetaMessage('text', text=f'{field_name}: {expected_value}', time=0))
                    needs_update = True
                elif existing_value != expected_value:
                    # Exists but different, update it
                    for msg in track:
                        if msg.is_meta and msg.type == 'text' and msg.text.startswith(f'{field_name}:'):
                            msg.text = f'{field_name}: {expected_value}'
                            needs_update = True
                            break
        
        # Genre (cleaned)
        if 'TCON' in tags:
            genre = clean_genre(tags['TCON'])
            if genre:
                existing_genre = existing_text_messages.get('Genre')
                
                if existing_genre is None:
                    new_messages.append(mido.MetaMessage('text', text=f'Genre: {genre}', time=0))
                    needs_update = True
                elif existing_genre != genre:
                    # Update existing genre
                    for msg in track:
                        if msg.is_meta and msg.type == 'text' and msg.text.startswith('Genre:'):
                            msg.text = f'Genre: {genre}'
                            needs_update = True
                            break
        
        # Add XF Solo metadata if requested
        if add_xf_metadata and mid.type == 0:
            # Check if already has XF metadata
            has_xf = any(
                msg.is_meta and msg.type == 'sequencer_specific' 
                and len(msg.data) >= 5 
                and msg.data[0] == 67 and msg.data[1] == 123 
                and msg.data[3] == 88 and msg.data[4] == 70
                for msg in track
            )
            
            if not has_xf:
                # XF format marker (XF02 signature)
                new_messages.append(mido.MetaMessage('sequencer_specific', data=(67, 123, 0, 88, 70, 48, 50, 0, 27), time=0))
                
                # XG system marker
                new_messages.append(mido.MetaMessage('sequencer_specific', data=(67, 113, 0, 1, 0, 1, 0), time=0))
                
                # XG system on
                new_messages.append(mido.MetaMessage('sequencer_specific', data=(67, 113, 0, 0, 0, 65), time=0))
                
                # XF end marker
                new_messages.append(mido.MetaMessage('sequencer_specific', data=(67, 123, 12, 1, 0), time=0))
                
                needs_update = True
        
        # If no changes needed, skip (unless force is True)
        if not needs_update and not force:
            return {'modified': False, 'reason': 'already has matching metadata'}
        
        # Insert new messages
        for msg in reversed(new_messages):
            track.insert(insert_pos, msg)
        
        # Determine output path
        if output_path is None:
            output_path = midi_path
        
        # Save the modified file
        mid.save(output_path)
        return {'modified': True, 'reason': 'updated'}
        
    except Exception as e:
        print(f"Error processing {Path(midi_path).name}: {e}")
        return {'modified': False, 'reason': f'error: {e}'}


def process_directory(directory, recursive=True, add_xf_metadata=False, dry_run=False, use_defaults=False):
    """Process all MIDI files with corresponding .tags.txt files in directory."""
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Error: Directory not found: {directory}", file=sys.stderr)
        return
    
    # Find all .tags.txt files
    if recursive:
        tags_files = list(directory.rglob('*.tags.txt'))
        if use_defaults:
            midi_files = list(directory.rglob('*.mid'))
    else:
        tags_files = list(directory.glob('*.tags.txt'))
        if use_defaults:
            midi_files = list(directory.glob('*.mid'))
    
    if not use_defaults and not tags_files:
        print(f"No .tags.txt files found in {directory}")
        return
    
    if use_defaults:
        # Build set of MIDI files that already have tags
        midi_with_tags = set()
        for tags_file in tags_files:
            base_name = tags_file.name.replace('.tags.txt', '')
            midi_file = tags_file.parent / f"{base_name}.mid"
            midi_with_tags.add(midi_file)
        
        # Filter to only MIDI files without tags
        midi_without_tags = [f for f in midi_files if f not in midi_with_tags]
        
        print(f"Found {len(tags_files)} .tags.txt file(s)")
        if midi_without_tags:
            print(f"Found {len(midi_without_tags)} .mid file(s) without .tags.txt (will use defaults)")
        print()
    else:
        if not tags_files:
            print(f"No .tags.txt files found in {directory}")
            return
    
    print(f"Found {len(tags_files)} .tags.txt file(s)\n")
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    error_details = []  # Track error details
    
    for tags_file in sorted(tags_files):
        # Find corresponding MIDI file
        # Tags file is named like "song.tags.txt", MIDI is "song.mid"
        base_name = tags_file.name.replace('.tags.txt', '')
        midi_file = tags_file.parent / f"{base_name}.mid"
        
        if not midi_file.exists():
            print(f"Skipping {tags_file.name}: No corresponding .mid file")
            skipped_count += 1
            continue
        
        # Parse tags
        tags = parse_tags_file(tags_file)
        if not tags:
            error_msg = f"Could not parse {tags_file.name}"
            print(f"Error: {error_msg}")
            error_details.append(f"{midi_file.name}: {error_msg}")
            error_count += 1
            continue
        
        # Display what we're doing
        print(f"Processing: {midi_file.name}")
        print(f"  Tags file: {tags_file.name}")
        
        if 'TIT2' in tags:
            print(f"  Title: {tags['TIT2']}")
        if 'TPE1' in tags:
            print(f"  Artist: {tags['TPE1']}")
        if 'TALB' in tags:
            print(f"  Album: {tags['TALB']}")
        if 'TYER' in tags:
            print(f"  Year: {tags['TYER']}")
        if 'TCOM' in tags:
            print(f"  Composer: {tags['TCOM']}")
        if 'TCON' in tags:
            genre = clean_genre(tags['TCON'])
            print(f"  Genre: {genre}")
        if 'COMM' in tags:
            print(f"  Catalog: {tags['COMM']}")
        
        if add_xf_metadata:
            print(f"  XF Solo metadata: Will add")
        
        if dry_run:
            print(f"  [DRY RUN] Would embed metadata")
            processed_count += 1
        else:
            result = embed_tags_in_midi(midi_file, tags, add_xf_metadata=add_xf_metadata)
            if result['modified']:
                print(f"  ✓ Embedded metadata")
                processed_count += 1
            elif result['reason'] == 'already has matching metadata':
                print(f"  ⊙ Skipped (already has matching metadata)")
                skipped_count += 1
            else:
                error_msg = result['reason']
                print(f"  ✗ Failed: {error_msg}")
                error_details.append(f"{midi_file.name}: {error_msg}")
                error_count += 1
        
        print()
    
    # Process MIDI files without tags if --default is active
    if use_defaults and 'midi_without_tags' in locals():
        # Group files by directory to assign sequential track numbers within each album
        from collections import defaultdict
        files_by_dir = defaultdict(list)
        for midi_file in sorted(midi_without_tags):
            files_by_dir[midi_file.parent].append(midi_file)
        
        for directory, files in sorted(files_by_dir.items()):
            auto_track = 1  # Start track numbering at 1 for each directory
            
            for midi_file in sorted(files):
                print(f"Processing (default): {midi_file.name}")
                
                # Generate default tags from filename, with auto track number
                # Use keep_full_filename=True so DKC-900 displays track number in title
                tags = parse_filename_metadata(midi_file, auto_track_number=auto_track, keep_full_filename=True)
                
                print(f"  Title: {tags['TIT2']}")
                print(f"  Album: {tags['TALB']}")
                print(f"  Track: {tags['TRCK']}")
                
                # Only increment auto track number if file didn't have a track prefix
                # (parse_filename_metadata returns the auto_track_number we passed if no prefix found)
                if tags['TRCK'] == str(auto_track):
                    auto_track += 1
                
                if dry_run:
                    print(f"  [DRY RUN] Would embed default metadata")
                    processed_count += 1
                else:
                    # Only write if metadata doesn't match existing
                    result = embed_tags_in_midi(midi_file, tags, add_xf_metadata=add_xf_metadata)
                    if result['modified']:
                        print(f"  ✓ Embedded default metadata")
                        processed_count += 1
                    elif result['reason'] == 'already has matching metadata':
                        print(f"  ⊙ Skipped (already has matching metadata)")
                        skipped_count += 1
                    else:
                        error_msg = result['reason']
                        print(f"  ✗ Error: {error_msg}")
                        error_details.append(f"{midi_file.name}: {error_msg}")
                        error_count += 1
                print()
    
    print(f"Summary:")
    print(f"  {'Would process' if dry_run else 'Processed'}: {processed_count}")
    print(f"  Skipped (already has metadata): {skipped_count}")
    if error_count > 0:
        print(f"  Errors: {error_count}")
        print(f"\nError Details:")
        for error in error_details:
            print(f"  • {error}")


def main():
    parser = argparse.ArgumentParser(
        description='Embed metadata from PFBU .tags.txt files into MIDI files',
        epilog='Reads metadata extracted by PFBU and embeds it as MIDI meta messages.'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='MIDI file, .tags.txt file, or directory to process (default: current directory)'
    )
    parser.add_argument(
        '--add-xf-metadata',
        action='store_true',
        help='Also add XF Solo metadata for DKC-900 recognition'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Scan subdirectories'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--default',
        action='store_true',
        help='Generate default metadata from filename/directory for MIDI files without .tags.txt'
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        if path.suffix == '.txt' and path.stem.endswith('.tags'):
            # Process single tags file
            tags = parse_tags_file(path)
            if not tags:
                print(f"Error: Could not parse {path}", file=sys.stderr)
                sys.exit(1)
            
            midi_file = path.with_suffix('.mid')
            if not midi_file.exists():
                print(f"Error: No corresponding .mid file found: {midi_file}", file=sys.stderr)
                sys.exit(1)
            
            print(f"Processing: {midi_file.name}")
            for key, value in tags.items():
                if key == 'TCON':
                    value = clean_genre(value)
                print(f"  {key}: {value}")
            
            if args.dry_run:
                print(f"\n[DRY RUN] Would embed metadata into {midi_file.name}")
            else:
                result = embed_tags_in_midi(midi_file, tags, add_xf_metadata=args.add_xf_metadata)
                if result['modified']:
                    print(f"\n✓ Embedded metadata into {midi_file.name}")
                elif result['reason'] == 'already has matching metadata':
                    print(f"\n⊙ Skipped (already has matching metadata)")
                else:
                    print(f"\n✗ Failed: {result['reason']}")
                    sys.exit(1)
        
        elif path.suffix == '.mid':
            # Process single MIDI file
            # Look for corresponding .tags.txt file
            tags_file = path.parent / f"{path.stem}.tags.txt"
            if not tags_file.exists():
                if not args.default:
                    print(f"Error: No corresponding .tags.txt file found: {tags_file}", file=sys.stderr)
                    sys.exit(1)
                else:
                    # Generate default tags from filename
                    print(f"No .tags.txt found, using defaults from filename")
                    tags = parse_filename_metadata(path)
            else:
                tags = parse_tags_file(tags_file)
                if not tags:
                    print(f"Error: Could not parse {tags_file}", file=sys.stderr)
                    sys.exit(1)
            
            print(f"Processing: {path.name}")
            for key, value in tags.items():
                if key == 'TCON':
                    value = clean_genre(value)
                print(f"  {key}: {value}")
            
            if args.dry_run:
                print(f"\n[DRY RUN] Would embed metadata")
            else:
                result = embed_tags_in_midi(path, tags, add_xf_metadata=args.add_xf_metadata)
                if result['modified']:
                    print(f"\n✓ Embedded metadata")
                elif result['reason'] == 'already has matching metadata':
                    print(f"\n⊙ Skipped (already has matching metadata)")
                else:
                    print(f"\n✗ Failed: {result['reason']}")
                    sys.exit(1)
        else:
            print(f"Error: File must be .mid or .tags.txt: {path}", file=sys.stderr)
            sys.exit(1)
    
    elif path.is_dir():
        # Process directory
        process_directory(path, recursive=args.recursive, 
                         add_xf_metadata=args.add_xf_metadata, dry_run=args.dry_run,
                         use_defaults=args.default)
    else:
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
