#!/usr/bin/env python3
"""
Generate secure secrets for production deployment.
Run this script to generate secure SECRET_KEY and passwords.
"""
import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(length)

def generate_password(length=16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def main():
    print("=" * 70)
    print("🔐 SECURE SECRETS GENERATOR")
    print("=" * 70)
    print()
    print("Copy these values to your .env file:")
    print()
    print("-" * 70)
    print(f"SECRET_KEY={generate_secret_key()}")
    print()
    print(f"ADMIN_EMAIL=your-admin@yourdomain.com")
    print(f"ADMIN_PASSWORD={generate_password(20)}")
    print()
    print(f"# Database credentials (PostgreSQL)")
    print(f"DB_USER=erp_user")
    print(f"DB_PASSWORD={generate_password(24)}")
    print("-" * 70)
    print()
    print("⚠️  IMPORTANT:")
    print("1. Store these values securely (password manager)")
    print("2. Never commit .env to git")
    print("3. Use different values for staging and production")
    print("4. Rotate secrets periodically")
    print()

if __name__ == "__main__":
    main()
