import asyncio
import sys

from sqlalchemy import text

from app.core.database import engine


async def check_database() -> int:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as error:  # The driver can expose DNS and connection errors directly.
        print(
            f"Database readiness check failed: {type(error).__name__}: {error}",
            file=sys.stderr,
        )
        return 1
    finally:
        await engine.dispose()

    print("Database connection is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(check_database()))
