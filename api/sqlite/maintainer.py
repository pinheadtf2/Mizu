import aiosqlite

async def create_database(db_path: str):
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS webhooks (
                webhook_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL
            )
        ''')
        await db.commit()

# later features: https://chatgpt.com/share/6810422f-7874-800f-9e55-5a698a6848e9
