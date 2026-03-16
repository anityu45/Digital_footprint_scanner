from backend.database import init_db, create_user

if __name__ == "__main__":
    print("Setting up MySQL database...")
    init_db()
    try:
        create_user("admin", "password123")
        print("Admin user created successfully!")
    except Exception as e:
        print(f"Admin user already exists or error: {e}")
    print("Done!")