import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect("orders.db")
cursor = conn.cursor()

# Create 'orders' table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    tracking_id TEXT PRIMARY KEY,
    customer_name TEXT,
    order_status TEXT,
    details TEXT
)
""")

conn.commit()
conn.close()
print("Orders table created successfully!")
