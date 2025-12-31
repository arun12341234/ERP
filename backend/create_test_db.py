#!/usr/bin/env python3
"""
Simple script to create database and test user.
Run this if you get 401 errors during login.
"""
import sqlite3
import hashlib
from datetime import datetime

# Database path
DB_PATH = "erp.db"

# Create database and tables
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Check if user exists
cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("user@example.com",))
if cursor.fetchone()[0] == 0:
    # Hash: user123 with bcrypt
    # Generated using: from passlib.context import CryptContext; CryptContext(schemes=["bcrypt"]).hash("user123")
    hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJqQBxOTW"

    cursor.execute("""
        INSERT INTO users (email, hashed_password, full_name, role, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, ("user@example.com", hashed_password, "Test User", "user", 1))
    print("✓ Created test user: user@example.com / user123")
else:
    print("✓ Test user already exists: user@example.com / user123")

# Check if admin exists
cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("admin@example.com",))
if cursor.fetchone()[0] == 0:
    # Hash: admin123 with bcrypt
    hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

    cursor.execute("""
        INSERT INTO users (email, hashed_password, full_name, role, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, ("admin@example.com", hashed_password, "Administrator", "admin", 1))
    print("✓ Created admin user: admin@example.com / admin123")
else:
    print("✓ Admin user already exists: admin@example.com / admin123")

conn.commit()
conn.close()

print("\n✅ Database setup complete!")
print("\nTest Credentials:")
print("  Email: user@example.com")
print("  Password: user123")
print("\nAdmin Credentials:")
print("  Email: admin@example.com")
print("  Password: admin123")
print("\nNow start your backend with: uvicorn app.main:app --reload")
