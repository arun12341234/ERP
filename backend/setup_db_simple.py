#!/usr/bin/env python3
"""
Simple database setup that works without dependencies.
Creates database with proper schema matching SQLAlchemy models.
"""
import sqlite3
from datetime import datetime

DB_PATH = "erp.db"

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create users table with exact schema
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create items table (required for User relationship)
cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
)
""")

# Insert test user
cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("user@example.com",))
if cursor.fetchone()[0] == 0:
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO users (email, hashed_password, full_name, role, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "user@example.com",
        "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJqQBxOTW",  # user123
        "Test User",
        "user",
        1,
        now,
        now
    ))
    print("✓ Created test user: user@example.com / user123")
else:
    print("✓ Test user exists")

# Insert admin user
cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("admin@example.com",))
if cursor.fetchone()[0] == 0:
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO users (email, hashed_password, full_name, role, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "admin@example.com",
        "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # admin123
        "Administrator",
        "admin",
        1,
        now,
        now
    ))
    print("✓ Created admin user: admin@example.com / admin123")
else:
    print("✓ Admin user exists")

conn.commit()
conn.close()

print("\n✅ Database ready!")
print("\nCredentials:")
print("  user@example.com / user123")
print("  admin@example.com / admin123")
