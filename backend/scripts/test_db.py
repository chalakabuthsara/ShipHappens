"""
Script to test database connection and create all tables.

Usage:
    uv run python -m scripts.test_db

This script will:
1. Test the connection to Supabase
2. Enable pgvector extension
3. Create all tables
4. Insert a test user
5. Verify everything works
"""

from sqlmodel import SQLModel, Session, select, text

from app.database import engine
from app.models import User


def test_db():
    """Test database connection and initialize schema"""
    print("🔍 Testing database connection...\n")

    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")

        # Enable pgvector extension
        print("📦 Enabling pgvector extension...")
        with Session(engine) as session:
            session.exec(text("CREATE EXTENSION IF NOT EXISTS vector"))
            session.commit()
        print("✓ pgvector extension enabled!")

        # Create all tables
        print("\n📝 Creating tables...")
        SQLModel.metadata.create_all(engine)
        print("✓ All tables created successfully!")

        # Test insert
        print("\n🧪 Testing write operations...")
        with Session(engine) as session:
            # Check if test user already exists
            existing = session.exec(
                select(User).where(User.email == "test@example.com")
            ).first()
            if not existing:
                test_user = User(
                    email="test@example.com",
                    name="Test User",
                    organization="Test Org",
                )
                session.add(test_user)
                session.commit()
                session.refresh(test_user)
                print(f"✓ Test user created with ID: {test_user.id}")
            else:
                print(f"✓ Test user already exists with ID: {existing.id}")

        # Verify data persisted
        print("\n✅ Verifying data persistence...")
        with Session(engine) as session:
            user = session.exec(
                select(User).where(User.email == "test@example.com")
            ).first()
            if user:
                print(f"✓ Retrieved user: {user.name} ({user.email})")
            else:
                print("✗ Failed to retrieve user!")
                return False

        print("\n" + "=" * 50)
        print("🎉 Database setup successful!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Fill DATABASE_URL in .env with your Supabase connection string")
        print("2. Set GEMINI_API_KEY in .env")
        print("3. Run: uv run python -m scripts.init_db")
        print("4. Start the API: uv run uvicorn app.main:app --reload")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check DATABASE_URL is set correctly in .env")
        print("2. Verify Supabase project is running")
        print("3. Make sure pgvector extension is available in your Supabase instance")
        return False


if __name__ == "__main__":
    success = test_db()
    exit(0 if success else 1)
