import sqlite3

conn = sqlite3.connect('samples/.dkvsong.db')
cursor = conn.cursor()

# Find all songs in Test directory/album
print("="*120)
print("Songs in Test Albums:")
print("="*120)

cursor.execute("""
    SELECT s.song_id, s.song_title, s.midi_path, s.format, s.performer, a.album_title, a.album_path
    FROM song s
    JOIN album a ON s.album_id = a.album_id
    WHERE a.album_path LIKE '%Test%' OR a.album_title LIKE '%Test%'
    ORDER BY s.song_id DESC
""")

test_songs = cursor.fetchall()

if test_songs:
    for s in test_songs:
        print(f"\nSong ID: {s[0]}")
        print(f"  Title: {s[1]}")
        print(f"  MIDI Path: {s[2]}")
        print(f"  Format: {s[3]} <--- KEY")
        print(f"  Performer: {s[4]}")
        print(f"  Album: {s[5]}")
        print(f"  Album Path: {s[6]}")
else:
    print("No songs in Test albums found!")

# Show all unique album paths to find the test folder
print("\n" + "="*120)
print("Recent albums (last 10):")
print("="*120)

cursor.execute("""
    SELECT album_id, album_title, album_path 
    FROM album 
    ORDER BY album_id DESC 
    LIMIT 10
""")

recent_albums = cursor.fetchall()
for a in recent_albums:
    print(f"\nAlbum ID: {a[0]}")
    print(f"  Title: {a[1]}")
    print(f"  Path: {a[2]}")
    
    # Count songs and show formats
    cursor.execute("""
        SELECT format, COUNT(*) 
        FROM song 
        WHERE album_id = ? 
        GROUP BY format
    """, (a[0],))
    format_counts = cursor.fetchall()
    if format_counts:
        print(f"  Formats:")
        for fmt, cnt in format_counts:
            print(f"    {fmt}: {cnt} songs")

conn.close()
