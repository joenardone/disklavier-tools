#!/usr/bin/env python3
"""
Find duplicate MIDI files using fuzzy filename matching and content analysis.
"""
import sys
import re
import mido
from pathlib import Path
from collections import defaultdict

def normalize_title(filename):
    """Normalize a filename for comparison by removing track numbers and normalizing formatting."""
    # Remove track numbers at start (NN - or NNN - )
    name = re.sub(r'^\d+ - ', '', filename)
    
    # Convert to lowercase
    name = name.lower()
    
    # Normalize common variations
    name = name.replace('op.', 'op-')
    name = name.replace('op ', 'op-')
    name = name.replace('no.', 'no-')
    name = name.replace('no ', 'no-')
    
    # Remove common middle names and variations
    name = name.replace('frederic francois', '')
    name = name.replace('frederick francois', '')
    name = name.replace(', ', ' ')
    
    # Remove extension
    name = name.replace('.mid', '')
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    return name

def get_midi_stats(filepath):
    """Get basic statistics about a MIDI file."""
    try:
        mid = mido.MidiFile(filepath)
        
        note_count = 0
        total_ticks = 0
        
        for track in mid.tracks:
            track_ticks = sum(msg.time for msg in track)
            total_ticks = max(total_ticks, track_ticks)
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_count += 1
        
        # Rough duration estimate (assumes 120 BPM default)
        duration_seconds = (total_ticks / mid.ticks_per_beat) * 0.5
        
        return {
            'notes': note_count,
            'duration': duration_seconds,
            'ticks': total_ticks,
            'tpb': mid.ticks_per_beat
        }
    except:
        return None

def find_fuzzy_duplicates(root_path):
    """Find duplicates using fuzzy filename matching."""
    root = Path(root_path)
    
    print("Scanning for fuzzy duplicates between Classical and composer folders...")
    print()
    
    # Track files by normalized name
    files_by_normalized = defaultdict(list)
    
    # Classical folders
    classical_folders = []
    
    # Composer folders
    composer_folders = []
    
    # Known composer names
    composer_names = [
        'Bach', 'Beethoven', 'Brahms', 'Chopin', 'Mozart', 'Tchai', 
        'Rachmaninov', 'Alkan', 'Grieg', 'Poulenc', 'Prokofiev', 'Liszt',
        'Schubert', 'Schumann', 'Debussy', 'Ravel', 'Haydn', 'Handel'
    ]
    
    # Scan all folders
    all_folders = [f for f in root.iterdir() if f.is_dir()]
    
    for folder in all_folders:
        folder_name = folder.name
        
        if folder_name.startswith('Classical ') and any(c in folder_name for c in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']):
            classical_folders.append(folder)
        elif any(composer.lower() in folder_name.lower() for composer in composer_names):
            composer_folders.append(folder)
    
    print(f"Classical folders: {len(classical_folders)}")
    print(f"Composer folders: {len(composer_folders)}")
    print()
    
    # Process all files
    print("Analyzing files...")
    total_files = 0
    
    for folder in classical_folders + composer_folders:
        folder_type = 'Classical' if folder in classical_folders else 'Composer'
        
        for filepath in folder.glob('*.mid'):
            total_files += 1
            if total_files % 100 == 0:
                print(f"  Processed {total_files} files...", end='\r')
            
            normalized = normalize_title(filepath.name)
            stats = get_midi_stats(filepath)
            
            files_by_normalized[normalized].append({
                'type': folder_type,
                'folder': folder.name,
                'path': filepath,
                'original': filepath.name,
                'stats': stats
            })
    
    print(f"  Processed {total_files} files... Done!")
    print()
    
    # Find duplicates across Classical and Composer folders
    duplicates = []
    
    for normalized, files in files_by_normalized.items():
        if len(files) > 1:
            has_classical = any(f['type'] == 'Classical' for f in files)
            has_composer = any(f['type'] == 'Composer' for f in files)
            
            if has_classical and has_composer:
                duplicates.append((normalized, files))
    
    # Report results
    print("="*70)
    print("FUZZY DUPLICATES FOUND")
    print("="*70)
    print()
    
    if duplicates:
        # Count files to remove (keep composer, remove classical)
        classical_to_remove = 0
        
        for normalized, files in duplicates:
            for f in files:
                if f['type'] == 'Classical':
                    classical_to_remove += 1
        
        print(f"Duplicate sets found: {len(duplicates)}")
        print(f"Classical files that can be removed: {classical_to_remove}")
        print()
        print("="*70)
        print()
        
        # Show first 50 duplicate sets
        for i, (normalized, files) in enumerate(duplicates[:50], 1):
            print(f"{i}. Normalized: {normalized}")
            
            for f in files:
                stats_str = ""
                if f['stats']:
                    stats_str = f" ({f['stats']['notes']} notes, {f['stats']['duration']:.1f}s)"
                print(f"   [{f['type']:9s}] {f['folder']}/{f['original']}{stats_str}")
            print()
        
        if len(duplicates) > 50:
            print(f"... and {len(duplicates) - 50} more duplicate sets")
            print()
        
        # Summary
        print("="*70)
        print("RECOMMENDATION:")
        print("="*70)
        print()
        print(f"Delete {classical_to_remove} files from Classical folders")
        print(f"Keep organized composer folders")
        print()
        
        current_total = 5371
        after_removal = current_total - classical_to_remove
        
        print(f"Current total: {current_total} files")
        print(f"After removal: {after_removal} files")
        
        if after_removal > 5000:
            print(f"Still need to remove: {after_removal - 5000} more files")
        else:
            print(f"SUCCESS! {5000 - after_removal} files under limit")
        print()
        
    else:
        print("No fuzzy duplicates found!")
    
    print()

def main():
    if len(sys.argv) != 2:
        print("Usage: python find_duplicates_fuzzy.py <directory>")
        print("\nExample:")
        print("  python find_duplicates_fuzzy.py \\\\RackStation\\Music\\Piano\\MIDI")
        sys.exit(1)
    
    root_path = sys.argv[1]
    
    if not Path(root_path).exists():
        print(f"Error: Directory not found: {root_path}", file=sys.stderr)
        sys.exit(1)
    
    find_fuzzy_duplicates(root_path)

if __name__ == "__main__":
    main()
