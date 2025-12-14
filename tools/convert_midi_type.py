"""
Convert MIDI files from Type 1 (multi-track) to Type 0 (single track).

This tool merges all tracks from a Type 1 MIDI file into a single track,
creating a Type 0 MIDI file. Type 0 is the standard format for Disklavier
solo piano files and is required for proper album organization on DKC-900.

Usage:
    python convert_midi_type.py [file_or_directory] [options]

Examples:
    python convert_midi_type.py song.mid              # Convert single file
    python convert_midi_type.py music/                # Convert directory
    python convert_midi_type.py music/ --recursive    # Convert recursively
"""

import argparse
import mido
from pathlib import Path
import sys


def convert_to_type0(input_path, output_path=None, backup=True, force=False):
    """
    Convert a MIDI file to Type 0 (single track).
    
    Args:
        input_path: Path to input MIDI file
        output_path: Path to output file (if None, overwrites input)
        backup: If True and overwriting, create .backup file
        force: If True, convert even if file has multiple tracks
    
    Returns:
        True if conversion was performed, False if already Type 0, None if skipped due to multi-track
    """
    try:
        mid = mido.MidiFile(input_path)
        
        # Check if already Type 0
        if mid.type == 0:
            return False
        
        # Check for multiple tracks and warn
        if len(mid.tracks) > 1 and not force:
            print(f"⚠ Warning: {input_path} has {len(mid.tracks)} tracks")
            print(f"  Skipping to preserve track structure. Use --force to convert anyway.")
            return None
        
        # Create new Type 0 file with same ticks_per_beat
        new_mid = mido.MidiFile(type=0, ticks_per_beat=mid.ticks_per_beat)
        
        # Create single track
        merged_track = mido.MidiTrack()
        new_mid.tracks.append(merged_track)
        
        # Merge all tracks, converting delta times to absolute times first
        all_events = []
        
        for track_idx, track in enumerate(mid.tracks):
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                # Store message with absolute time and track index
                all_events.append((abs_time, track_idx, msg.copy(time=abs_time)))
        
        # Sort by absolute time, then by track index (to preserve order)
        all_events.sort(key=lambda x: (x[0], x[1]))
        
        # Convert back to delta times and add to merged track
        last_time = 0
        for abs_time, _, msg in all_events:
            delta_time = abs_time - last_time
            msg.time = delta_time
            merged_track.append(msg)
            last_time = abs_time
        
        # Determine output path
        if output_path is None:
            output_path = input_path
            # Create backup if requested
            if backup:
                backup_path = str(input_path) + '.backup'
                Path(input_path).rename(backup_path)
        
        # Save the Type 0 file
        new_mid.save(output_path)
        return True
        
    except Exception as e:
        print(f"Error converting {input_path}: {e}", file=sys.stderr)
        return False


def process_file(file_path, args):
    """Process a single MIDI file."""
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = None
    
    converted = convert_to_type0(file_path, output_path, backup=not args.no_backup, force=args.force)
    
    if converted:
        print(f"✓ Converted: {file_path}")
    elif converted is False:
        if args.verbose:
            print(f"  Skipped (already Type 0): {file_path}")
    # If converted is None, already printed warning about multi-track


def process_directory(dir_path, args):
    """Process all MIDI files in a directory."""
    pattern = '**/*.mid' if args.recursive else '*.mid'
    
    midi_files = list(dir_path.glob(pattern))
    
    if not midi_files:
        print(f"No MIDI files found in {dir_path}")
        return
    
    converted_count = 0
    skipped_count = 0
    multitrack_count = 0
    error_count = 0
    
    for midi_file in midi_files:
        try:
            converted = convert_to_type0(midi_file, backup=not args.no_backup, force=args.force)
            if converted:
                converted_count += 1
                print(f"✓ Converted: {midi_file}")
            elif converted is False:
                skipped_count += 1
                if args.verbose:
                    print(f"  Skipped (already Type 0): {midi_file}")
            else:  # None = multi-track warning
                multitrack_count += 1
        except Exception as e:
            error_count += 1
            print(f"✗ Error: {midi_file}: {e}", file=sys.stderr)
    
    print(f"\nSummary: {converted_count} converted, {skipped_count} skipped, {multitrack_count} multi-track warnings, {error_count} errors")


def main():
    parser = argparse.ArgumentParser(
        description='Convert MIDI files from Type 1 to Type 0 (single track)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s song.mid                 Convert single file (creates backup)
  %(prog)s song.mid --no-backup     Convert without backup
  %(prog)s music/                   Convert all .mid files in directory
  %(prog)s music/ --recursive       Convert recursively
  %(prog)s song.mid -o output.mid   Convert to different file
        """
    )
    
    parser.add_argument('input', nargs='?', default='.', 
                        help='MIDI file or directory (default: current directory)')
    parser.add_argument('-o', '--output', 
                        help='Output file (only for single file input)')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Process directories recursively')
    parser.add_argument('--no-backup', action='store_true',
                        help='Do not create backup files when overwriting')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Convert multi-track files (merges all tracks)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output (show skipped files)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: {input_path} does not exist", file=sys.stderr)
        return 1
    
    # Single file mode
    if input_path.is_file():
        if not input_path.suffix.lower() == '.mid':
            print(f"Error: {input_path} is not a MIDI file (.mid)", file=sys.stderr)
            return 1
        process_file(input_path, args)
    
    # Directory mode
    elif input_path.is_dir():
        if args.output:
            print("Error: --output option is only valid for single file input", file=sys.stderr)
            return 1
        process_directory(input_path, args)
    
    else:
        print(f"Error: {input_path} is not a file or directory", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
