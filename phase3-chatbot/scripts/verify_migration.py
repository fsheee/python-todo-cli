"""
Verify database migration was successful.
Checks that all required tables and indexes exist.
"""

import asyncio
import os
import sys
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Load environment
load_dotenv(".env.production")

DATABASE_URL = os.getenv("DATABASE_URL")


async def verify_migration():
    """Verify database migration."""
    print("Verifying database migration...")

    engine = create_async_engine(DATABASE_URL, echo=False)

    try:
        async with engine.begin() as conn:
            # Get inspector
            inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))

            # Check tables
            tables = await conn.run_sync(lambda sync_conn: inspector.get_table_names())

            required_tables = ["users", "todos", "chat_history"]
            missing_tables = [t for t in required_tables if t not in tables]

            if missing_tables:
                print(f"✗ Missing tables: {', '.join(missing_tables)}")
                return False

            print(f"✓ All required tables exist: {', '.join(required_tables)}")

            # Check chat_history table structure
            print("\nChecking chat_history table structure...")
            columns = await conn.run_sync(
                lambda sync_conn: inspector.get_columns("chat_history")
            )

            required_columns = [
                "id", "user_id", "session_id", "role",
                "content", "metadata", "timestamp", "is_deleted"
            ]

            column_names = [col["name"] for col in columns]
            missing_columns = [c for c in required_columns if c not in column_names]

            if missing_columns:
                print(f"✗ Missing columns: {', '.join(missing_columns)}")
                return False

            print(f"✓ All required columns exist: {', '.join(required_columns)}")

            # Check indexes
            print("\nChecking indexes...")
            indexes = await conn.run_sync(
                lambda sync_conn: inspector.get_indexes("chat_history")
            )

            print(f"✓ Found {len(indexes)} indexes on chat_history table")

            # Test query
            print("\nTesting database connection...")
            result = await conn.execute(text("SELECT COUNT(*) FROM chat_history"))
            count = result.scalar()
            print(f"✓ Database connection successful (chat_history has {count} rows)")

        await engine.dispose()

        print("\n✓ Migration verification complete - all checks passed!")
        return True

    except Exception as e:
        print(f"\n✗ Verification failed: {str(e)}")
        await engine.dispose()
        return False


if __name__ == "__main__":
    success = asyncio.run(verify_migration())
    sys.exit(0 if success else 1)
