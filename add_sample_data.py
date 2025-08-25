import sqlite3

# Connect to the database
conn = sqlite3.connect("orders.db")
cursor = conn.cursor()

# Sample orders to insert
orders = [
    ("TRACK001", "Alice Johnson", "Shipped", "Expected delivery: 2025-08-28"),
    ("TRACK002", "Bob Smith", "Processing", "Your order is being prepared"),
    ("TRACK003", "Carol White", "Delivered", "Delivered on 2025-08-20"),
    ("TRACK004", "David Brown", "Cancelled", "Order cancelled by customer"),
    ("TRACK005", "Eva Green", "Shipped", "Expected delivery: 2025-08-26"),
    ("TRACK006", "Frank Black", "Processing", "Payment confirmed, preparing shipment"),
    ("TRACK007", "Grace Blue", "Delivered", "Delivered on 2025-08-22"),
    ("TRACK008", "Hank Grey", "Shipped", "Expected delivery: 2025-08-27"),
    ("TRACK009", "Ivy Red", "Processing", "Order is being packed"),
    ("TRACK010", "Jack Yellow", "Cancelled", "Cancelled due to payment issue"),
]

# Insert records into 'orders' table
cursor.executemany("""
INSERT OR IGNORE INTO orders (tracking_id, customer_name, order_status, details)
VALUES (?, ?, ?, ?)
""", orders)

conn.commit()
conn.close()

print("10 sample orders added successfully!")
