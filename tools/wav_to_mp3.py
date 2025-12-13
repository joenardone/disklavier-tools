#!/usr/bin/env python3
"""
Convert WAV files to MP3 for Yamaha DKC-900.

Provides batch WAV to MP3 conversion with optional metadata and cover art
copying from tagged MP3 files. Uses FFmpeg for high-quality audio conversion.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path


def check_ffmpeg():
    """Check if FFmpeg is available."""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_wav_to_mp3(wav_path, mp3_path, bitrate=192, sample_rate=44100, 
                       metadata_source=None, overwrite=False, verbose=True):
    """
    Convert WAV file to MP3.
    
    Args:
        wav_path: Input WAV file path
        mp3_path: Output MP3 file path
        bitrate: MP3 bitrate in kbps (default: 192)
        sample_rate: Sample rate in Hz (default: 44100)
        metadata_source: Optional MP3 file to copy metadata and cover art from
        overwrite: Overwrite existing files
        verbose: Print conversion progress
    
    Returns:
        True if successful, False otherwise
    """
    if not overwrite and mp3_path.exists():
        if verbose:
            print(f"  Skipping (exists): {mp3_path.name}")
        return False
    
    cmd = ['ffmpeg']
    
    if overwrite:
        cmd.append('-y')
    else:
        cmd.append('-n')
    
    # Input WAV file
    cmd.extend(['-i', str(wav_path)])
    
    # If metadata source provided, add it as second input
    if metadata_source and metadata_source.exists():
        cmd.extend(['-i', str(metadata_source)])
        if verbose:
            print(f"  Copying metadata from: {metadata_source.name}")
    
    # Audio mapping and encoding
    cmd.extend(['-map', '0:a'])
    
    # If metadata source exists, map video stream (cover art) and metadata
    if metadata_source and metadata_source.exists():
        cmd.extend([
            '-map', '1:v?',  # Map cover art if present (? = optional)
            '-c:v', 'copy',   # Copy cover art without re-encoding
            '-map_metadata', '1',  # Copy metadata from source
        ])
    
    # Audio codec settings (DKC-900 compatible)
    cmd.extend([
        '-c:a', 'libmp3lame',
        '-b:a', f'{bitrate}k',
        '-ar', str(sample_rate),
        '-ac', '2',  # Stereo
        '-id3v2_version', '3',
    ])
    
    # Output file
    cmd.append(str(mp3_path))
    
    try:
        if verbose:
            print(f"  Converting: {wav_path.name} → {mp3_path.name}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        if verbose:
            print(f"  ✓ Created: {mp3_path.name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ERROR converting {wav_path.name}: {e.stderr}", file=sys.stderr)
        return False


def batch_convert(directory, output_dir=None, metadata_dir=None, 
                 bitrate=192, sample_rate=44100, suffix=None,
                 overwrite=False, recursive=False, dry_run=False):
    """
    Batch convert WAV files in a directory to MP3.
    
    Args:
        directory: Directory containing WAV files
        output_dir: Output directory (default: same as input)
        metadata_dir: Directory containing tagged MP3 files for metadata copying
        bitrate: MP3 bitrate in kbps
        sample_rate: Sample rate in Hz
        suffix: Add suffix to output filenames (e.g., "_SYNC")
        overwrite: Overwrite existing MP3 files
        recursive: Process subdirectories
        dry_run: Preview without converting
    """
    dir_path = Path(directory)
    
    if not dir_path.is_dir():
        raise SystemExit(f"ERROR: Directory not found: {directory}")
    
    # Find WAV files
    pattern = "**/*.wav" if recursive else "*.wav"
    wav_files = list(dir_path.glob(pattern))
    
    # Case-insensitive search for Windows
    if not wav_files and os.name == 'nt':
        wav_files = [f for f in dir_path.rglob("*") if f.suffix.lower() == ".wav"]
    
    if not wav_files:
        print(f"No WAV files found in: {directory}")
        return
    
    print(f"Found {len(wav_files)} WAV file(s)")
    if dry_run:
        print("[DRY RUN MODE - No files will be converted]\n")
    
    # Setup output directory
    out_dir = Path(output_dir) if output_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup metadata directory
    meta_dir = Path(metadata_dir) if metadata_dir else None
    
    converted = 0
    skipped = 0
    errors = 0
    
    for wav_path in wav_files:
        # Determine output path
        if out_dir:
            mp3_name = wav_path.stem + (suffix or '') + '.mp3'
            mp3_path = out_dir / mp3_name
        else:
            mp3_name = wav_path.stem + (suffix or '') + '.mp3'
            mp3_path = wav_path.parent / mp3_name
        
        # Find metadata source if metadata_dir provided
        metadata_source = None
        if meta_dir:
            meta_file = meta_dir / (wav_path.stem + '.mp3')
            if meta_file.exists():
                metadata_source = meta_file
        
        if dry_run:
            print(f"Would convert: {wav_path.name}")
            if metadata_source:
                print(f"  With metadata from: {metadata_source.name}")
            print(f"  Output: {mp3_path}")
            converted += 1
        else:
            result = convert_wav_to_mp3(
                wav_path, mp3_path,
                bitrate=bitrate,
                sample_rate=sample_rate,
                metadata_source=metadata_source,
                overwrite=overwrite
            )
            
            if result:
                converted += 1
            elif mp3_path.exists():
                skipped += 1
            else:
                errors += 1
        
        print()
    
    print(f"{'[DRY RUN] ' if dry_run else ''}DONE:")
    print(f"  {'Would convert' if dry_run else 'Converted'}: {converted}")
    if skipped:
        print(f"  Skipped (existing): {skipped}")
    if errors:
        print(f"  Errors: {errors}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert WAV files to MP3 for Yamaha DKC-900",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all WAV files in current directory
  wav_to_mp3.exe .
  
  # Convert with metadata from tags/ subdirectory
  wav_to_mp3.exe --metadata-dir tags .
  
  # Add suffix to output files
  wav_to_mp3.exe --suffix _SYNC .
  
  # Output to different directory
  wav_to_mp3.exe --output-dir output_mp3 input_wav
  
  # Custom bitrate and sample rate
  wav_to_mp3.exe --bitrate 320 --sample-rate 48000 .
  
  # Dry run to preview
  wav_to_mp3.exe --dry-run .

Metadata Copying:
  If --metadata-dir is specified, the tool will look for MP3 files
  with matching names and copy their metadata (title, artist, album,
  track number) and embedded cover art to the converted files.

DKC-900 Compatible Settings:
  - Sample rate: 44100 Hz (default)
  - Stereo output
  - ID3v2.3 tags
  - Constant bitrate MP3
        """
    )
    
    parser.add_argument('directory', nargs='?', default='.',
                       help='directory containing WAV files (default: current directory)')
    parser.add_argument('--output-dir', 
                       help='output directory (default: same as input)')
    parser.add_argument('--metadata-dir',
                       help='directory containing tagged MP3 files for metadata copying')
    parser.add_argument('--bitrate', type=int, default=192,
                       help='MP3 bitrate in kbps (default: 192)')
    parser.add_argument('--sample-rate', type=int, default=44100,
                       help='sample rate in Hz (default: 44100)')
    parser.add_argument('--suffix',
                       help='add suffix to output filenames (e.g., "_SYNC")')
    parser.add_argument('--overwrite', action='store_true',
                       help='overwrite existing MP3 files')
    parser.add_argument('--recursive', action='store_true',
                       help='process subdirectories')
    parser.add_argument('--dry-run', action='store_true',
                       help='preview conversions without converting')
    
    args = parser.parse_args(argv)
    
    # Check FFmpeg availability
    if not check_ffmpeg():
        print("ERROR: FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
        print("Download from: https://ffmpeg.org/download.html")
        return 1
    
    try:
        batch_convert(
            args.directory,
            output_dir=args.output_dir,
            metadata_dir=args.metadata_dir,
            bitrate=args.bitrate,
            sample_rate=args.sample_rate,
            suffix=args.suffix,
            overwrite=args.overwrite,
            recursive=args.recursive,
            dry_run=args.dry_run
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
