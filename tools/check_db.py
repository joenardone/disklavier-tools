import sqlite3

conn = sqlite3.connect('samples/.dkvsong.db')
cursor = conn.cursor()

# Check for empty cover art
cursor.execute("""
    SELECT album_id, album_title, album_path, coverart_path 
    FROM album 
    WHERE coverart_path IS NULL OR TRIM(coverart_path) = ''
    ORDER BY album_title
""")

empty_rows = cursor.fetchall()
print("Albums with empty coverart_path:")
print(f"{'ID':<5} | {'Title':<50} | {'Path':<60}")
print("-" * 120)
for r in empty_rows:
    print(f"{r[0]:<5} | {r[1]:<50} | {r[2]:<60}")
print(f"\nTotal with empty cover art: {len(empty_rows)}")

# Now check tracks to see if any are marked as Solo
print("\n" + "="*120)
print("Checking track metadata for Solo designation:")
print("="*120)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("\nAll tables in database:")
for t in tables:
    print(f"  {t[0]}")

# Check song table
print("\n" + "="*120)
print("Checking song table:")
cursor.execute("PRAGMA table_info(song)")
song_cols = cursor.fetchall()
print("\nSong table columns:")
for c in song_cols:
    print(f"  {c[1]} ({c[2]})")

# Sample songs from Jazz & Blues and Pop & Rock albums
print("\n" + "="*120)
print("Sample songs from 'Jazz & Blues' albums:")
cursor.execute("""
    SELECT s.song_id, s.song_title, s.midi_path, s.format, a.album_title
    FROM song s
    JOIN album a ON s.album_id = a.album_id
    WHERE a.album_title LIKE 'Jazz & Blues%'
    LIMIT 5
""")
jazz_songs = cursor.fetchall()
for s in jazz_songs:
    print(f"  {s[0]}: {s[1]}")
    print(f"    Path: {s[2]}")
    print(f"    Format: {s[3]}")

print("\nSample songs from 'Pop & Rock' albums:")
cursor.execute("""
    SELECT s.song_id, s.song_title, s.midi_path, s.format, a.album_title
    FROM song s
    JOIN album a ON s.album_id = a.album_id
    WHERE a.album_title LIKE 'Pop & Rock%'
    LIMIT 5
""")
pop_songs = cursor.fetchall()
for s in pop_songs:
    print(f"  {s[0]}: {s[1]}")
    print(f"    Path: {s[2]}")
    print(f"    Format: {s[3]}")

# Check format values
print("\n" + "="*120)
print("All unique format values:")
cursor.execute("SELECT DISTINCT format FROM song WHERE format IS NOT NULL")
formats = cursor.fetchall()
for f in formats:
    cursor.execute("SELECT COUNT(*) FROM song WHERE format = ?", (f[0],))
    count = cursor.fetchone()[0]
    print(f"  '{f[0]}': {count} songs")

conn.close()
