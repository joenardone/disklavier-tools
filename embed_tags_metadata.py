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


def embed_tags_in_midi(midi_path, tags, output_path=None, add_xf_metadata=False):
    """
    Embed metadata from tags into MIDI file.
    
    Args:
        midi_path: Path to input MIDI file
        tags: Dict of parsed tags
        output_path: Path for output file (default: overwrite input)
        add_xf_metadata: If True, also add XF Solo metadata
    
    Returns:
        dict with status: {'modified': bool, 'reason': str}
    """
    try:
        mid = mido.MidiFile(midi_path)
        
        if len(mid.tracks) == 0:
            print(f"Error: {Path(midi_path).name} has no tracks")
            return {'modified': False, 'reason': 'no tracks'}
        
        track = mid.tracks[0]
        
        # Find insertion point (after initial meta messages like tempo, time_sig)
        insert_pos = 0
        for i, msg in enumerate(track):
            if msg.type in ['set_tempo', 'time_signature', 'key_signature']:
                insert_pos = i + 1
            elif msg.is_meta and msg.type == 'track_name':
                # Replace existing track_name
                if 'TIT2' in tags:
                    msg.name = tags['TIT2']
                insert_pos = i + 1
            else:
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
        needs_update = False
        
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
        
        # If no changes needed, skip
        if not needs_update:
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


def process_directory(directory, recursive=True, add_xf_metadata=False, dry_run=False):
    """Process all MIDI files with corresponding .tags.txt files in directory."""
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Error: Directory not found: {directory}", file=sys.stderr)
        return
    
    # Find all .tags.txt files
    if recursive:
        tags_files = list(directory.rglob('*.tags.txt'))
    else:
        tags_files = list(directory.glob('*.tags.txt'))
    
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
        '--no-recursive',
        action='store_true',
        help='Do not scan subdirectories'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
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
                print(f"Error: No corresponding .tags.txt file found: {tags_file}", file=sys.stderr)
                sys.exit(1)
            
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
        process_directory(path, recursive=not args.no_recursive, 
                         add_xf_metadata=args.add_xf_metadata, dry_run=args.dry_run)
    else:
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
