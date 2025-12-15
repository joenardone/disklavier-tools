#!/usr/bin/env python3
"""
Add Yamaha XF Solo metadata to existing MIDI files.
This makes files appear as "Solo" format on DKC-900/Enspire.
"""
import sys
import mido
from pathlib import Path
import argparse
from datetime import datetime


def add_smfsolo_metadata(filepath, output_path=None, year=None):
    """
    Add XF Solo metadata to a MIDI file.
    
    Args:
        filepath: Path to input MIDI file
        output_path: Path for output file (default: overwrite input)
        year: Year for copyright (default: current year)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        mid = mido.MidiFile(filepath)
        
        # Only add to Type 0 (single track) files
        if mid.type != 0:
            print(f"Skipping {Path(filepath).name}: Not Type 0 (has {len(mid.tracks)} tracks)")
            return False
        
        # Check if already has XF metadata
        track = mid.tracks[0]
        has_xf = False
        for msg in track:
            if msg.is_meta and msg.type == 'sequencer_specific':
                data = msg.data
                # Check for XF format marker
                if len(data) >= 5 and data[0] == 67 and data[1] == 123 and data[3] == 88 and data[4] == 70:
                    has_xf = True
                    break
        
        if has_xf:
            print(f"Skipping {Path(filepath).name}: Already has XF metadata")
            return False
        
        # Default year
        if year is None:
            year = str(datetime.now().year)
        
        # Find insertion point (after initial meta messages like tempo, time_sig, track_name)
        insert_pos = 0
        for i, msg in enumerate(track):
            if msg.type in ['set_tempo', 'time_signature', 'track_name']:
                insert_pos = i + 1
            else:
                break
        
        # Create XF Solo metadata messages (SMFSOLO format)
        xf_messages = [
            # Copyright
            mido.MetaMessage('copyright', text=f'(P) {year} Yamaha Corporation', time=0),
            
            # XF format marker (XF02 signature)
            mido.MetaMessage('sequencer_specific', data=(67, 123, 0, 88, 70, 48, 50, 0, 27), time=0),
            
            # XG system marker
            mido.MetaMessage('sequencer_specific', data=(67, 113, 0, 1, 0, 1, 0), time=0),
            
            # XG system on
            mido.MetaMessage('sequencer_specific', data=(67, 113, 0, 0, 0, 65), time=0),
            
            # XF end marker
            mido.MetaMessage('sequencer_specific', data=(67, 123, 12, 1, 0), time=0),
        ]
        
        # Insert XF metadata
        for msg in reversed(xf_messages):
            track.insert(insert_pos, msg)
        
        # Determine output path
        if output_path is None:
            output_path = filepath
        
        # Save the modified file
        mid.save(output_path)
        print(f"✓ Added XF Solo metadata: {Path(filepath).name}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {Path(filepath).name}: {e}")
        return False


def process_directory(directory, recursive=True, year=None):
    """Process all MIDI files in a directory."""
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
        print(f"No MIDI files found in {directory}")
        return
    
    print(f"Found {len(midi_files)} MIDI file(s)\n")
    
    modified_count = 0
    skipped_count = 0
    error_count = 0
    
    for filepath in sorted(midi_files):
        result = add_smfsolo_metadata(filepath, year=year)
        if result:
            modified_count += 1
        elif result is False:
            skipped_count += 1
        else:
            error_count += 1
    
    print(f"\nSummary:")
    print(f"  Modified: {modified_count}")
    print(f"  Skipped: {skipped_count}")
    if error_count > 0:
        print(f"  Errors: {error_count}")


def main():
    parser = argparse.ArgumentParser(
        description='Add Yamaha XF Solo metadata to MIDI files for DKC-900 recognition',
        epilog='This adds the metadata that makes files show as "Solo" format on DKC-900/Enspire.'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='MIDI file or directory to process (default: current directory)'
    )
    parser.add_argument(
        '--year',
        help='Year for copyright (default: current year)'
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not scan subdirectories'
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        # Process single file
        add_smfsolo_metadata(path, year=args.year)
    elif path.is_dir():
        # Process directory
        process_directory(path, recursive=not args.no_recursive, year=args.year)
    else:
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
