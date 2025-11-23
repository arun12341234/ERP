#!/usr/bin/env python3
"""
Seed database with initial data.
Creates admin user and sample items.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User
from app.models.item import Item


def seed():
    """Seed database with initial data."""
    print("🌱 Seeding database...")

    # Initialize database
    init_db()

    db = SessionLocal()

    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()

        if not admin:
            # Create admin user
            admin = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name="Administrator",
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"✓ Created admin user: {settings.ADMIN_EMAIL}")
        else:
            print(f"✓ Admin user already exists: {settings.ADMIN_EMAIL}")

        # Create sample regular user
        sample_user = db.query(User).filter(User.email == "user@example.com").first()
        if not sample_user:
            sample_user = User(
                email="user@example.com",
                hashed_password=get_password_hash("user123"),
                full_name="Sample User",
                role="user",
                is_active=True,
            )
            db.add(sample_user)
            db.commit()
            db.refresh(sample_user)
            print("✓ Created sample user: user@example.com")

        # Create sample items
        existing_items = db.query(Item).count()
        if existing_items == 0:
            sample_items = [
                Item(
                    title="Sample Item 1",
                    description="This is a sample item for testing",
                    owner_id=admin.id
                ),
                Item(
                    title="Sample Item 2",
                    description="Another sample item",
                    owner_id=admin.id
                ),
                Item(
                    title="User Item 1",
                    description="Item owned by regular user",
                    owner_id=sample_user.id
                ),
            ]

            # Add tenant_id if multi-tenancy is enabled
            if settings.ENABLE_TENANCY:
                for item in sample_items:
                    item.tenant_id = 1  # Default tenant

            db.add_all(sample_items)
            db.commit()
            print(f"✓ Created {len(sample_items)} sample items")

        print("\n✅ Database seeding completed!")
        print(f"\nAdmin credentials:")
        print(f"  Email: {settings.ADMIN_EMAIL}")
        print(f"  Password: {settings.ADMIN_PASSWORD}")
        print(f"\nSample user credentials:")
        print(f"  Email: user@example.com")
        print(f"  Password: user123")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
