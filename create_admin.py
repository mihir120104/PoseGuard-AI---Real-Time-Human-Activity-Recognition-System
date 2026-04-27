"""
create_admin.py
Run ONCE after first deploy to create the admin account.

Usage:
    python create_admin.py
    python create_admin.py --username admin --password mypassword
"""

import argparse
from auth import init_db, register, list_users

def main():
    parser = argparse.ArgumentParser(description="Create HAR admin user")
    parser.add_argument("--username", default="admin",    help="Admin username (default: admin)")
    parser.add_argument("--password", default="admin123", help="Admin password (default: admin123)")
    args = parser.parse_args()

    init_db()

    existing = list_users()
    if args.username in existing:
        print(f"⚠  User '{args.username}' already exists.")
        print("   If you forgot the password, delete users.db and run again.")
        return

    success = register(args.username, args.password)
    if success:
        print(f"✅  Admin user created successfully.")
        print(f"    Username : {args.username}")
        print(f"    Password : {args.password}")
        print()
        print("   ⚠  IMPORTANT: Change this password after first login via Admin Panel.")
    else:
        print(f"❌  Failed to create user '{args.username}'.")

if __name__ == "__main__":
    main()