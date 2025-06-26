import aiosqlite

DB_NAME = "channels.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id TEXT PRIMARY KEY,
                username TEXT
            )
        """)
        await db.commit()

async def add_channel(channel_id: str, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR REPLACE INTO channels (id, username) VALUES (?, ?)", (channel_id, username))
        await db.commit()

async def remove_channel(channel_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
        await db.commit()

async def get_channels():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id, username FROM channels") as cursor:
            return await cursor.fetchall()
