import sqlite3

conn = sqlite3.connect('samples/.dkvsong.db')
cursor = conn.cursor()

cursor.execute("SELECT midi_path FROM song WHERE format = 'SMFSOLO' LIMIT 1")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("No SMFSOLO songs found")
conn.close()
