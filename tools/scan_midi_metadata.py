#!/usr/bin/env python3
"""
Scan MIDI files for XF metadata and track information.
Reports on each file's format, track count, and XF metadata presence.
Can also add XF Solo metadata to files that don't have it.
"""
import sys
import mido
from pathlib import Path
import argparse
from datetime import datetime


def detect_xf_metadata(mid):
    """
    Detect XF metadata in a MIDI file.
    Returns dict with XF metadata details.
    """
    xf_info = {
        'has_xf_format_marker': False,  # (67, 123, 0, 88, 70, ...) - "XF" signature
        'has_xf_header': False,          # XFhd: text event
        'has_xf_line': False,            # XFln: text event
        'has_xg_marker': False,          # (67, 113, ...) - XG system markers
        'has_copyright': False,
        'has_cue_marker': False,
        'xf_type': None                  # Will be 'Solo', 'Plus', 'Audio', or None
    }
    
    for track in mid.tracks:
        for msg in track:
            if msg.is_meta:
                if msg.type == 'sequencer_specific':
                    data = msg.data
                    # XF format marker: (67, 123, 0, 88, 70, 48, 50, 0, 27)
                    # 0x58 0x46 = "XF"
                    if len(data) >= 5 and data[0] == 67 and data[1] == 123 and data[3] == 88 and data[4] == 70:
                        xf_info['has_xf_format_marker'] = True
                    # XG system markers
                    elif len(data) >= 2 and data[0] == 67 and data[1] == 113:
                        xf_info['has_xg_marker'] = True
                        
                elif msg.type == 'text':
                    if 'XFhd:' in msg.text:
                        xf_info['has_xf_header'] = True
                    elif 'XFln:' in msg.text:
                        xf_info['has_xf_line'] = True
                        
                elif msg.type == 'copyright':
                    xf_info['has_copyright'] = True
                    
                elif msg.type == 'cue_marker' and '$Lyrc:' in msg.text:
                    xf_info['has_cue_marker'] = True
    
    # Determine XF type based on metadata
    if xf_info['has_xf_format_marker'] and xf_info['has_xf_header'] and xf_info['has_xf_line']:
        xf_info['xf_type'] = 'Solo'  # Full PianoSoft Solo metadata
    elif xf_info['has_xg_marker']:
        xf_info['xf_type'] = 'Basic'  # Has some XG markers but not full Solo
    else:
        xf_info['xf_type'] = None  # No XF metadata
    
    return xf_info


def scan_midi_file(filepath):
    """Scan a single MIDI file and return its info."""
    try:
        mid = mido.MidiFile(filepath)
        xf_info = detect_xf_metadata(mid)
        
        return {
            'path': str(filepath),
            'type': mid.type,
            'tracks': len(mid.tracks),
            'ticks_per_beat': mid.ticks_per_beat,
            'xf_type': xf_info['xf_type'],
            'has_xf_format_marker': xf_info['has_xf_format_marker'],
            'has_xf_header': xf_info['has_xf_header'],
            'has_xf_line': xf_info['has_xf_line'],
            'has_xg_marker': xf_info['has_xg_marker'],
            'has_copyright': xf_info['has_copyright'],
            'error': None
        }
    except Exception as e:
        return {
            'path': str(filepath),
            'error': str(e)
        }


def scan_directory(directory, recursive=True):
    """Scan all MIDI files in a directory."""
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Error: Directory not found: {directory}", file=sys.stderr)
        return []
    
    # Find all .mid files
    if recursive:
        midi_files = list(directory.rglob('*.mid'))
    else:
        midi_files = list(directory.glob('*.mid'))
    
    if not midi_files:
        print(f"No MIDI files found in {directory}", file=sys.stderr)
        return []
    
    print(f"Found {len(midi_files)} MIDI file(s)")
    print()
    
    results = []
    for filepath in sorted(midi_files):
        info = scan_midi_file(filepath)
        results.append(info)
    
    return results


def print_results(results):
    """Print scan results in a formatted table."""
    if not results:
        return
    
    # Print header
    print(f"{'File':<50} {'Type':<5} {'Trks':<5} {'XF Type':<10} {'XF Marker':<10} {'XFhd':<6} {'XFln':<6} {'XG':<5}")
    print("=" * 120)
    
    # Print each file
    for info in results:
        if info.get('error'):
            print(f"{Path(info['path']).name:<50} ERROR: {info['error']}")
        else:
            filename = Path(info['path']).name
            xf_type = info['xf_type'] or 'None'
            xf_marker = 'Yes' if info['has_xf_format_marker'] else 'No'
            xf_header = 'Yes' if info['has_xf_header'] else 'No'
            xf_line = 'Yes' if info['has_xf_line'] else 'No'
            xg_marker = 'Yes' if info['has_xg_marker'] else 'No'
            
            print(f"{filename:<50} {info['type']:<5} {info['tracks']:<5} {xf_type:<10} {xf_marker:<10} {xf_header:<6} {xf_line:<6} {xg_marker:<5}")
    
    print()
    
    # Print summary
    total = len(results)
    with_xf_solo = sum(1 for r in results if r.get('xf_type') == 'Solo')
    with_xf_basic = sum(1 for r in results if r.get('xf_type') == 'Basic')
    without_xf = sum(1 for r in results if r.get('xf_type') is None)
    type_0 = sum(1 for r in results if r.get('type') == 0)
    type_1 = sum(1 for r in results if r.get('type') == 1)
    
    print("SUMMARY:")
    print(f"  Total files: {total}")
    print(f"  MIDI Type 0: {type_0}")
    print(f"  MIDI Type 1: {type_1}")
    print(f"  XF Solo (full metadata): {with_xf_solo}")
    print(f"  XF Basic (partial metadata): {with_xf_basic}")
    print(f"  No XF metadata: {without_xf}")


def add_xf_solo_metadata(filepath, artist=None, year=None, output_path=None):
    """
    Add XF Solo metadata to a MIDI file.
    
    Args:
        filepath: Path to input MIDI file
        artist: Artist name (default: extracted from filename or 'Unknown Artist')
        year: Year (default: current year)
        output_path: Path for output file (default: overwrite input)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        mid = mido.MidiFile(filepath)
        
        # Check if already has XF Solo metadata
        xf_info = detect_xf_metadata(mid)
        if xf_info['xf_type'] == 'Solo':
            print(f"  File already has XF Solo metadata: {Path(filepath).name}")
            return False
        
        # Ensure it's Type 0
        if mid.type != 0:
            print(f"  Warning: File is Type {mid.type}, should be Type 0 for Solo format: {Path(filepath).name}")
            return False
        
        # Extract song title from filename
        filename = Path(filepath).stem
        # Try to extract track number and title (e.g., "01 - Song Name")
        parts = filename.split(' - ', 1)
        if len(parts) == 2:
            song_title = parts[1].strip()
        else:
            song_title = filename
        
        # Default values
        if artist is None:
            artist = 'Unknown Artist'
        if year is None:
            year = str(datetime.now().year)
        
        # Get the track
        track = mid.tracks[0]
        
        # Find insertion point (after initial meta messages like tempo, time_sig)
        insert_pos = 0
        for i, msg in enumerate(track):
            if msg.type in ['set_tempo', 'time_signature', 'track_name']:
                insert_pos = i + 1
            else:
                break
        
        # Create XF Solo metadata messages (SMFSOLO format - matching Sting album format)
        # This is the format recognized by DKC-900 as SMFSOLO
        xf_messages = [
            # Copyright (appears before other XF metadata in Sting files)
            mido.MetaMessage('copyright', text=f'(P) {year} Yamaha Corporation', time=0),
            
            # XF format marker (XF02 signature)
            mido.MetaMessage('sequencer_specific', data=(67, 123, 0, 88, 70, 48, 50, 0, 27), time=0),
            
            # XG system marker
            mido.MetaMessage('sequencer_specific', data=(67, 113, 0, 1, 0, 1, 0), time=0),
            
            # XG system on
            mido.MetaMessage('sequencer_specific', data=(67, 113, 0, 0, 0, 65), time=0),
            
            # XF end marker (note: 12, 1, 0 not 12, 2, 1)
            mido.MetaMessage('sequencer_specific', data=(67, 123, 12, 1, 0), time=0),
        ]
        
        # Insert XF metadata at the beginning (after initial meta messages)
        for msg in reversed(xf_messages):
            track.insert(insert_pos, msg)
        
        # Determine output path
        if output_path is None:
            output_path = filepath
        
        # Save the modified file
        mid.save(output_path)
        print(f"  Added XF Solo metadata: {Path(filepath).name}")
        return True
        
    except Exception as e:
        print(f"  Error processing {Path(filepath).name}: {e}")
        return False


def add_metadata_to_files(directory, recursive=True, artist=None, year=None, dry_run=False):
    """Add XF Solo metadata to all MIDI files that don't have it."""
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
        print(f"No MIDI files found in {directory}", file=sys.stderr)
        return
    
    print(f"Found {len(midi_files)} MIDI file(s)")
    print()
    
    if dry_run:
        print("DRY RUN - No files will be modified")
        print()
    
    modified_count = 0
    skipped_count = 0
    
    for filepath in sorted(midi_files):
        if dry_run:
            # Just check if it needs metadata
            mid = mido.MidiFile(filepath)
            xf_info = detect_xf_metadata(mid)
            if xf_info['xf_type'] != 'Solo' and mid.type == 0:
                print(f"  Would add XF metadata: {filepath.name}")
                modified_count += 1
            else:
                skipped_count += 1
        else:
            # Actually add metadata
            if add_xf_solo_metadata(filepath, artist=artist, year=year):
                modified_count += 1
            else:
                skipped_count += 1
    
    print()
    print(f"Modified: {modified_count}")
    print(f"Skipped: {skipped_count}")


def main():
    parser = argparse.ArgumentParser(
        description='Scan MIDI files for XF metadata and track information'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Scan subdirectories'
    )
    parser.add_argument(
        '--add-metadata',
        action='store_true',
        help='Add XF Solo metadata to files that don\'t have it'
    )
    parser.add_argument(
        '--artist',
        help='Artist name for XF metadata (default: Unknown Artist)'
    )
    parser.add_argument(
        '--year',
        help='Year for copyright (default: current year)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be modified without making changes'
    )
    
    args = parser.parse_args()
    
    if args.add_metadata or args.dry_run:
        add_metadata_to_files(
            args.directory,
            recursive=args.recursive,
            artist=args.artist,
            year=args.year,
            dry_run=args.dry_run
        )
    else:
        results = scan_directory(args.directory, recursive=args.recursive)
        print_results(results)


if __name__ == "__main__":
    main()
