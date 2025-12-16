#!/usr/bin/env python3
"""
Repair MIDI files with invalid key signature mode bytes.

This tool fixes corrupted MIDI files that have key signature meta messages
with invalid mode values (should be 0=major or 1=minor, but sometimes corrupted to 255).

It works at the byte level, finding and replacing invalid mode bytes with 0 (major).

Usage:
    python repair_midi_key_signature.py <input_file> [output_file]
    python repair_midi_key_signature.py <input_file> --recursive
    
If output_file is not specified, creates filename_repaired.mid
With --recursive flag, processes all .mid files in subdirectories
"""

import sys
import argparse
from pathlib import Path

def read_varlen(data, pos):
    """Read a variable-length quantity from data starting at pos."""
    value = 0
    start_pos = pos
    while True:
        if pos >= len(data):
            return value, pos
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            break
    return value, pos

def repair_midi_file(input_path, output_path=None, verbose=True):
    """
    Repair a MIDI file by fixing invalid key signature mode bytes.
    
    Returns:
        True if file was repaired successfully
        False if file could not be repaired or had no issues
    """
    input_path = Path(input_path)
    
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_repaired{input_path.suffix}"
    else:
        output_path = Path(output_path)
    
    if verbose:
        print(f"Repairing: {input_path}")
    
    try:
        with open(input_path, 'rb') as f:
            data = bytearray(f.read())
    except Exception as e:
        print(f"ERROR: Could not read file: {e}")
        return False
    
    # Check MIDI header
    if data[:4] != b'MThd':
        if verbose:
            print("ERROR: Not a valid MIDI file (missing MThd header)")
        return False
    
    header_length = int.from_bytes(data[4:8], 'big')
    format_type = int.from_bytes(data[8:10], 'big')
    num_tracks = int.from_bytes(data[10:12], 'big')
    
    if verbose:
        print(f"  Format: Type {format_type}, Tracks: {num_tracks}")
    
    # Find and repair corrupted key signatures
    pos = 14
    track_num = 0
    repairs_made = 0
    
    while pos < len(data):
        # Look for MTrk chunk
        if data[pos:pos+4] != b'MTrk':
            break
        
        track_num += 1
        track_length = int.from_bytes(data[pos+4:pos+8], 'big')
        
        track_start = pos + 8
        track_end = track_start + track_length
        track_pos = track_start
        
        # Parse track events
        while track_pos < track_end:
            # Read delta time
            delta, track_pos = read_varlen(data, track_pos)
            
            # Read event type
            if track_pos >= len(data):
                break
                
            event_byte = data[track_pos]
            
            # Check if it's a meta event (0xFF)
            if event_byte == 0xFF:
                track_pos += 1
                if track_pos >= len(data):
                    break
                meta_type = data[track_pos]
                track_pos += 1
                meta_length, track_pos = read_varlen(data, track_pos)
                
                # Check for key signature (meta type 0x59)
                if meta_type == 0x59 and meta_length >= 2:
                    mode_pos = track_pos + 1  # Mode is second byte
                    if mode_pos < len(data):
                        mode = data[mode_pos]
                        
                        if mode not in [0, 1]:
                            # Invalid mode - repair it
                            sf = int.from_bytes([data[track_pos]], 'big', signed=True)
                            if verbose:
                                print(f"  Track {track_num}: Found invalid key signature")
                                print(f"    Position: {mode_pos}")
                                print(f"    Sharps/Flats: {sf}")
                                print(f"    Invalid mode: {mode} (0x{mode:02X})")
                                print(f"    Repairing to: 0 (major)")
                            
                            data[mode_pos] = 0  # Set to major
                            repairs_made += 1
                
                track_pos += meta_length
                
            elif event_byte >= 0x80:
                # MIDI channel message
                track_pos += 1
                if track_pos >= len(data):
                    break
                # Determine message length
                if event_byte < 0xC0 or (event_byte >= 0xE0 and event_byte < 0xF0):
                    track_pos += 2  # Two data bytes
                elif event_byte < 0xE0:
                    track_pos += 1  # One data byte
            else:
                # Running status - reuse previous status
                track_pos += 1
        
        pos = track_end
    
    if repairs_made > 0:
        # Rename original to .original and save repaired file with original name
        try:
            # Create backup of original file
            backup_path = input_path.parent / f"{input_path.stem}.original{input_path.suffix}"
            
            # If output_path was explicitly specified (not auto-generated), use it
            # Otherwise, use the original filename (and backup the original)
            if output_path == input_path.parent / f"{input_path.stem}_repaired{input_path.suffix}":
                # Auto-generated output path - use original filename instead
                import shutil
                shutil.move(str(input_path), str(backup_path))
                output_path = input_path
                if verbose:
                    print(f"  Repaired {repairs_made} invalid key signature(s)")
                    print(f"  Original backed up to: {backup_path.name}")
            else:
                # User specified output path - keep as is
                if verbose:
                    print(f"  Repaired {repairs_made} invalid key signature(s)")
            
            with open(output_path, 'wb') as f:
                f.write(data)
            if verbose:
                print(f"  Saved to: {output_path}")
            return True
        except Exception as e:
            print(f"ERROR: Could not write repaired file: {e}")
            return False
    else:
        if verbose:
            print("  No repairs needed")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Repair MIDI files with invalid key signature mode bytes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Repair a single file
  python repair_midi_key_signature.py corrupted.mid
  python repair_midi_key_signature.py corrupted.mid fixed.mid
  
  # Repair all MIDI files in current directory and subdirectories
  python repair_midi_key_signature.py . --recursive
        """
    )
    
    parser.add_argument('input', nargs='?', default='.', help='Input MIDI file or directory (default: current directory)')
    parser.add_argument('output', nargs='?', help='Output MIDI file (default: input_repaired.mid)')
    parser.add_argument('--recursive', '-r', action='store_true',
                        help='Process all .mid files in subdirectories')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress output except for errors')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    verbose = not args.quiet
    
    if args.recursive:
        if not input_path.is_dir():
            print(f"ERROR: With --recursive, input must be a directory")
            return 1
        
        # Find all MIDI files
        midi_files = list(input_path.rglob('*.mid'))
        
        if not midi_files:
            print(f"No MIDI files found in {input_path}")
            return 0
        
        print(f"Found {len(midi_files)} MIDI file(s) to check")
        print()
        
        repaired_count = 0
        failed_count = 0
        
        for midi_file in midi_files:
            output_file = midi_file.parent / f"{midi_file.stem}_repaired{midi_file.suffix}"
            try:
                if repair_midi_file(midi_file, output_file, verbose=verbose):
                    repaired_count += 1
            except Exception as e:
                print(f"ERROR processing {midi_file}: {e}")
                failed_count += 1
            if verbose:
                print()
        
        print(f"\nSummary:")
        print(f"  Total files: {len(midi_files)}")
        print(f"  Repaired: {repaired_count}")
        print(f"  No repairs needed: {len(midi_files) - repaired_count - failed_count}")
        print(f"  Failed: {failed_count}")
        
    else:
        # Single file mode
        if not input_path.exists():
            print(f"ERROR: File not found: {input_path}")
            return 1
        
        if input_path.is_dir():
            print(f"ERROR: {input_path} is a directory. Use --recursive to process all files.")
            return 1
        
        output_path = Path(args.output) if args.output else None
        repair_midi_file(input_path, output_path, verbose=verbose)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
