import sqlite3

conn = sqlite3.connect("orders.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())  # Should include 'orders'
conn.close()
