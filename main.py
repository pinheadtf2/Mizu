from datetime import datetime
from os import getenv, listdir

import aiohttp
import discord
from dotenv import load_dotenv
from rich.console import Console

from api.openai.handler import generate_response

load_dotenv()
console = Console()

bot = discord.Bot(intents=discord.Intents.all())
bot.openai_thinking = False
bot.openai_message_history = []
bot.session = None

# config
bot.openai_url = "http://100.92.68.7:5000/v1/chat/completions"
bot.openai_character = "Sabine"


@bot.event
async def on_ready():
    # bot.session = aiohttp.ClientSession()
    console.print(f"{bot.user} is ready and online!")


@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")


for filename in listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


if __name__ == '__main__':
    bot.run(getenv("TOKEN"))
