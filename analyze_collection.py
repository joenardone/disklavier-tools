#!/usr/bin/env python3
"""
Analyze MIDI collection to identify candidates for removal to meet DKC-900's 5000 song limit.
"""
import sys
import mido
from pathlib import Path
from collections import defaultdict, Counter
import hashlib

def get_file_hash(filepath):
    """Get MD5 hash of file content to identify duplicates."""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def analyze_midi_file(filepath):
    """Get basic info about a MIDI file."""
    try:
        mid = mido.MidiFile(filepath)
        
        # Check for XF metadata
        has_xf = False
        for track in mid.tracks:
            for msg in track:
                if msg.is_meta and msg.type == 'sequencer_specific':
                    data = msg.data
                    if len(data) >= 5 and data[0] == 67 and data[1] == 123 and data[3] == 88 and data[4] == 70:
                        has_xf = True
                        break
            if has_xf:
                break
        
        # Count notes and calculate duration
        total_notes = 0
        total_ticks = 0
        
        for track in mid.tracks:
            track_ticks = sum(msg.time for msg in track)
            total_ticks = max(total_ticks, track_ticks)
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    total_notes += 1
        
        # Rough duration estimate (assumes 120 BPM default)
        duration_seconds = (total_ticks / mid.ticks_per_beat) * 0.5
        
        return {
            'type': mid.type,
            'tracks': len(mid.tracks),
            'has_xf': has_xf,
            'notes': total_notes,
            'duration': duration_seconds,
            'ticks_per_beat': mid.ticks_per_beat
        }
    except Exception as e:
        return {'error': str(e)}

def analyze_collection(root_path):
    """Analyze entire MIDI collection."""
    root = Path(root_path)
    
    print("Analyzing MIDI collection...")
    print("This may take several minutes for 5000+ files...")
    print()
    
    files_by_folder = defaultdict(list)
    files_by_name = defaultdict(list)
    files_by_hash = defaultdict(list)
    
    all_files = list(root.rglob('*.mid'))
    total_files = len(all_files)
    
    print(f"Found {total_files} MIDI files")
    print()
    
    # Analyze each file
    type1_files = []
    no_xf_files = []
    short_files = []
    few_notes_files = []
    
    for i, filepath in enumerate(all_files, 1):
        if i % 100 == 0:
            print(f"  Processing: {i}/{total_files}...", end='\r')
        
        rel_path = filepath.relative_to(root)
        folder = filepath.parent.relative_to(root)
        
        # Track by folder
        files_by_folder[str(folder)].append(filepath)
        
        # Track by name (potential duplicates)
        files_by_name[filepath.name.lower()].append(filepath)
        
        # Track by hash (exact duplicates)
        file_hash = get_file_hash(filepath)
        if file_hash:
            files_by_hash[file_hash].append(filepath)
        
        # Analyze content
        info = analyze_midi_file(filepath)
        
        if 'error' not in info:
            if info['type'] == 1:
                type1_files.append((filepath, info))
            if not info['has_xf']:
                no_xf_files.append((filepath, info))
            if info['duration'] < 30:  # Less than 30 seconds
                short_files.append((filepath, info))
            if info['notes'] < 50:  # Very few notes
                few_notes_files.append((filepath, info))
    
    print(f"  Processing: {total_files}/{total_files}... Done!")
    print()
    
    # Generate report
    print("="*70)
    print("ANALYSIS REPORT")
    print("="*70)
    print()
    
    print(f"Total MIDI files: {total_files}")
    print(f"DKC-900 limit: 5000")
    print(f"Files to remove: {max(0, total_files - 5000)}")
    print()
    
    # Duplicates by hash (exact duplicates)
    exact_duplicates = {h: paths for h, paths in files_by_hash.items() if len(paths) > 1}
    duplicate_count = sum(len(paths) - 1 for paths in exact_duplicates.values())
    
    print("="*70)
    print(f"1. EXACT DUPLICATES (same content): {duplicate_count} files")
    print("="*70)
    if exact_duplicates:
        print("These files have identical content. Keep one, delete the rest:")
        print()
        for i, (hash_val, paths) in enumerate(list(exact_duplicates.items())[:10], 1):
            print(f"  Duplicate set {i} ({len(paths)} copies):")
            for p in paths:
                print(f"    {p.relative_to(root)}")
            print()
        if len(exact_duplicates) > 10:
            print(f"  ... and {len(exact_duplicates) - 10} more duplicate sets")
    print()
    
    # Similar names (potential duplicates)
    similar_names = {name: paths for name, paths in files_by_name.items() if len(paths) > 1}
    similar_count = sum(len(paths) - 1 for paths in similar_names.values())
    
    print("="*70)
    print(f"2. SIMILAR FILENAMES: {similar_count} potential duplicates")
    print("="*70)
    if similar_names:
        print("These files have identical names in different folders:")
        print()
        for i, (name, paths) in enumerate(list(similar_names.items())[:10], 1):
            if name not in [p.name.lower() for h, ps in exact_duplicates.items() for p in ps]:
                print(f"  {name} ({len(paths)} copies):")
                for p in paths:
                    print(f"    {p.relative_to(root)}")
                print()
        if len(similar_names) > 10:
            print(f"  ... and {len(similar_names) - 10} more similar name sets")
    print()
    
    # Type 1 files
    print("="*70)
    print(f"3. TYPE 1 FILES (not converted): {len(type1_files)} files")
    print("="*70)
    print("These need convert_midi_type.exe --force to work optimally on DKC-900")
    if type1_files:
        for filepath, info in type1_files[:20]:
            print(f"  {filepath.relative_to(root)} (tracks: {info['tracks']})")
        if len(type1_files) > 20:
            print(f"  ... and {len(type1_files) - 20} more")
    print()
    
    # No XF metadata
    print("="*70)
    print(f"4. NO XF METADATA: {len(no_xf_files)} files")
    print("="*70)
    print("These won't show as 'Solo' or 'Plus' on DKC-900")
    if no_xf_files:
        for filepath, info in no_xf_files[:20]:
            print(f"  {filepath.relative_to(root)}")
        if len(no_xf_files) > 20:
            print(f"  ... and {len(no_xf_files) - 20} more")
    print()
    
    # Short files
    print("="*70)
    print(f"5. VERY SHORT FILES (<30 seconds): {len(short_files)} files")
    print("="*70)
    if short_files:
        short_files.sort(key=lambda x: x[1]['duration'])
        for filepath, info in short_files[:20]:
            print(f"  {filepath.relative_to(root)} ({info['duration']:.1f}s, {info['notes']} notes)")
        if len(short_files) > 20:
            print(f"  ... and {len(short_files) - 20} more")
    print()
    
    # Files by folder
    print("="*70)
    print("6. FILES BY FOLDER:")
    print("="*70)
    folder_counts = [(folder, len(files)) for folder, files in files_by_folder.items()]
    folder_counts.sort(key=lambda x: x[1], reverse=True)
    
    for folder, count in folder_counts[:20]:
        print(f"  {count:4d} files: {folder}")
    if len(folder_counts) > 20:
        print(f"  ... and {len(folder_counts) - 20} more folders")
    print()
    
    # Recommendations
    print("="*70)
    print("RECOMMENDATIONS TO REACH 5000 FILES:")
    print("="*70)
    
    removable = 0
    print(f"\n1. Remove {duplicate_count} exact duplicate files → {removable + duplicate_count} removed")
    removable += duplicate_count
    
    if removable < (total_files - 5000):
        remaining = (total_files - 5000) - removable
        print(f"\n2. Remove {min(remaining, len(short_files))} very short files → {removable + min(remaining, len(short_files))} removed")
        removable += min(remaining, len(short_files))
    
    if removable < (total_files - 5000):
        remaining = (total_files - 5000) - removable
        print(f"\n3. Review folders with most files and remove least favorites → {remaining} more needed")
    
    print(f"\nTotal removable identified: {removable}")
    print(f"Still need to identify: {max(0, (total_files - 5000) - removable)}")
    print()

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_collection.py <directory>")
        print("\nExample:")
        print("  python analyze_collection.py \\\\RackStation\\Music\\Piano\\MIDI")
        sys.exit(1)
    
    root_path = sys.argv[1]
    
    if not Path(root_path).exists():
        print(f"Error: Directory not found: {root_path}", file=sys.stderr)
        sys.exit(1)
    
    analyze_collection(root_path)

if __name__ == "__main__":
    main()
