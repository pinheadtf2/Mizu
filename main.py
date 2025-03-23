from datetime import datetime
from os import getenv

import aiohttp
import discord
from dotenv import load_dotenv
from rich.console import Console

from api.openai.handler import generate_response

load_dotenv()
console = Console()

bot = discord.Bot(intents=discord.Intents.all())
bot.thinking = False
bot.session = None

message_history = []


@bot.event
async def on_ready():
    bot.session = aiohttp.ClientSession()
    console.print(f"{bot.user} is ready and online!")


@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")


@bot.event
async def on_message(message):
    if (message.author.id != bot.user.id and message.channel.id == 1353259955733397597 and not bot.thinking):
        bot.thinking = True
        generated_response = None

        async with message.channel.typing():
            now = datetime.now()
            formatted_date = now.strftime("%A, %B %d, %Y, at %I:%M %p")
            history = [{
                "role": "system",
                "content": f"You're Sabine in this discussion with a member of the Discord server {message.guild.name}. "
                           f"There may be other members who have chatted with you before. Keep your responses short, appropriate, and in-character. "
                           f"The date is {formatted_date}."
            }, {
                "role": "user",
                "content": f"[{message.author.name}]: {message.content}"
            }]

            generated_response, new_history = generate_response(history, message.author.name,
                                                                message.author.display_name)

        await message.reply(generated_response)
        bot.thinking = False


if __name__ == '__main__':
    bot.run(getenv("TOKEN"))
