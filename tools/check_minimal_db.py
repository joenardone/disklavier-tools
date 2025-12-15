import sqlite3

conn = sqlite3.connect('samples/.dkvsong.db')
cursor = conn.cursor()

# Find minimal Valentine songs
print("="*120)
print("Searching for minimal Valentine songs:")
print("="*120)

cursor.execute("""
    SELECT s.song_id, s.song_title, s.midi_path, s.format, s.album_id, a.album_title, a.album_path
    FROM song s
    LEFT JOIN album a ON s.album_id = a.album_id
    WHERE s.song_title LIKE '%minimal%' OR s.midi_path LIKE '%minimal%'
    ORDER BY s.song_id DESC
""")

minimal_songs = cursor.fetchall()

if minimal_songs:
    for s in minimal_songs:
        print(f"\nSong ID: {s[0]}")
        print(f"  Title: {s[1]}")
        print(f"  MIDI Path: {s[2]}")
        print(f"  Format: {s[3]} <--- THIS IS THE KEY")
        print(f"  Album ID: {s[4]}")
        print(f"  Album Title: {s[5]}")
        print(f"  Album Path: {s[6]}")
else:
    print("No minimal songs found!")

# Check if there's a new standalone album
print("\n" + "="*120)
print("Checking most recently added albums:")
print("="*120)

cursor.execute("""
    SELECT album_id, album_title, album_path 
    FROM album 
    ORDER BY album_id DESC 
    LIMIT 5
""")

recent_albums = cursor.fetchall()
for a in recent_albums:
    print(f"\nAlbum ID: {a[0]}")
    print(f"  Title: {a[1]}")
    print(f"  Path: {a[2]}")
    
    # Show songs in this album
    cursor.execute("SELECT song_title, format FROM song WHERE album_id = ?", (a[0],))
    songs = cursor.fetchall()
    if songs:
        print(f"  Songs ({len(songs)}):")
        for song in songs:
            print(f"    - {song[0]} (format: {song[1]})")

# Show format breakdown
print("\n" + "="*120)
print("Format distribution in database:")
print("="*120)

cursor.execute("SELECT format, COUNT(*) FROM song WHERE format IS NOT NULL GROUP BY format ORDER BY COUNT(*) DESC")
formats = cursor.fetchall()
for f in formats:
    print(f"  {f[0]}: {f[1]} songs")

conn.close()
