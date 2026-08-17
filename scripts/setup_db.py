"""Setup and database initialization script for NEXORA AI."""

import asyncio
import os
import sys

from db import init_db, close_db


async def main():
    """Initialize the database."""
    print("🗄️  Initializing NEXORA database...")
    
    try:
        await init_db()
        print("✅ Database tables created successfully!")
        print("\n📚 Next steps:")
        print("  1. Start the backend: python -m quart run")
        print("  2. Start the frontend: npm run dev")
        print("  3. Visit http://localhost:5173")
    except Exception as e:
        print(f"❌ Error initializing database: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
