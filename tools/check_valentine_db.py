import sqlite3

conn = sqlite3.connect('samples/.dkvsong.db')
cursor = conn.cursor()

# Find Valentine songs
print("="*120)
print("Searching for Valentine songs in database:")
print("="*120)

cursor.execute("""
    SELECT s.song_id, s.song_title, s.midi_path, s.format, a.album_title, a.album_path
    FROM song s
    JOIN album a ON s.album_id = a.album_id
    WHERE s.song_title LIKE '%Valentine%' OR s.midi_path LIKE '%Valentine%'
    ORDER BY s.song_title
""")

valentine_songs = cursor.fetchall()

if valentine_songs:
    for s in valentine_songs:
        print(f"\nSong ID: {s[0]}")
        print(f"  Title: {s[1]}")
        print(f"  MIDI Path: {s[2]}")
        print(f"  Format: {s[3]}")
        print(f"  Album: {s[4]}")
        print(f"  Album Path: {s[5]}")
else:
    print("No Valentine songs found!")

# Compare with a known SMFSOLO song
print("\n" + "="*120)
print("Comparing with a known SMFSOLO song:")
print("="*120)

cursor.execute("""
    SELECT s.song_id, s.song_title, s.midi_path, s.format, s.performer, s.composer, s.tags
    FROM song s
    WHERE s.format = 'SMFSOLO'
    LIMIT 3
""")

solo_songs = cursor.fetchall()
for s in solo_songs:
    print(f"\nSong ID: {s[0]}")
    print(f"  Title: {s[1]}")
    print(f"  MIDI Path: {s[2]}")
    print(f"  Format: {s[3]}")
    print(f"  Performer: {s[4]}")
    print(f"  Composer: {s[5]}")
    print(f"  Tags: {s[6]}")

# Check all columns for Valentine to see if anything is different
if valentine_songs:
    print("\n" + "="*120)
    print("Full details for first Valentine song:")
    print("="*120)
    
    song_id = valentine_songs[0][0]
    cursor.execute("SELECT * FROM song WHERE song_id = ?", (song_id,))
    full_data = cursor.fetchone()
    
    cursor.execute("PRAGMA table_info(song)")
    columns = cursor.fetchall()
    
    for i, col in enumerate(columns):
        print(f"  {col[1]}: {full_data[i]}")

conn.close()
