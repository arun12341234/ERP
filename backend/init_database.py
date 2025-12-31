#!/usr/bin/env python3
"""
Initialize database with all tables and create test users.
This uses SQLAlchemy to create the proper schema.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.database import init_db, SessionLocal
    from app.core.security import get_password_hash
    from app.models.user import User

    print("🔧 Initializing database...")

    # Create all tables
    init_db()
    print("✓ All tables created")

    # Create session
    db = SessionLocal()

    try:
        # Create test user
        user = db.query(User).filter(User.email == "user@example.com").first()
        if not user:
            user = User(
                email="user@example.com",
                hashed_password=get_password_hash("user123"),
                full_name="Test User",
                role="user",
                is_active=True
            )
            db.add(user)
            db.commit()
            print("✓ Created test user: user@example.com / user123")
        else:
            print("✓ Test user already exists: user@example.com")

        # Create admin user
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✓ Created admin user: admin@example.com / admin123")
        else:
            print("✓ Admin user already exists: admin@example.com")

        print("\n✅ Database initialization complete!")
        print("\nLogin Credentials:")
        print("  Email: user@example.com")
        print("  Password: user123")
        print("\nAdmin Credentials:")
        print("  Email: admin@example.com")
        print("  Password: admin123")

    finally:
        db.close()

except ImportError as e:
    print(f"❌ Error: {e}")
    print("\n⚠️  Dependencies not installed!")
    print("\nPlease install dependencies first:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
