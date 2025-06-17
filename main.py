import asyncio
from src.bot import run
from src.cache import create_schema

async def main():
    await create_schema()
    await run()

if __name__ == "__main__":
    asyncio.run(main())
