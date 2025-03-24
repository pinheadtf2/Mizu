import asyncio

import aiohttp

from api.openai.async_handler import generate_test_response


async def main():
    session = aiohttp.ClientSession()
    history = [
        {
            "role": "system",
            "content": "You're Sabine in this discussion with a member of the Discord server pinhead's secret server. There may be other members who have chatted with you before. Keep your responses short and appropriate. The date is Sunday, March 23, 2025, at 01:37:45 AM."
        }
    ]
    test = await generate_test_response(session, history)


if __name__ == '__main__':
    asyncio.run(main())
