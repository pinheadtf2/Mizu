import asyncio
from datetime import datetime
from os import getenv, listdir
from os.path import isfile
from time import time

from api.sqlite.maintainer import create_database

import aiosqlite
import discord
import yaml
import aiohttp
from discord import option
from discord.ext import commands
from dotenv import load_dotenv
from rich.console import Console

start_time = time()
load_dotenv()
console = Console(record=True, width=160, log_time_format="[%H:%M:%S.%f]")
console.log("[bold blue](init)[/] Starting...")

settings = None
with open("settings.yaml") as stream:
    try:
        settings = list(yaml.safe_load_all(stream))
    except yaml.YAMLError as error:
        console.log(error)
        exit(1)  # fuck that im not going any further
console.log("[bold blue](init)[/] Settings loaded")

bot = discord.Bot(
    intents=discord.Intents.all(),
    debug_guilds=settings[0]["debug_guilds"],
    owner_ids=settings[0]["owner_ids"],
    status=discord.Status.dnd,
    activity=discord.CustomActivity(name="Initializing...", status=discord.Status.do_not_disturb)
)
bot.aiohttp_session = None
bot.console = console
bot.webhook_cache = {}
bot.core_settings = settings[0]
bot.chatbot_settings = settings[1]
bot.chatbot_thinking = False
bot.chatbot_message_history = []
console.log("[bold blue](init)[/] Bot created")


@bot.event
async def on_ready():
    bot.aiohttp_session = aiohttp.ClientSession()
    bot.database_connection = await aiosqlite.connect(settings[0]['sqlite_database'])
    await bot.change_presence(activity=discord.CustomActivity(name="Hello!", status=discord.Status.online))
    bot.console.log(
        f"[bold green](ready)[/] {bot.user} up and running!\n"
        f"\tTimestamp:  {datetime.now().strftime('%I:%M:%S %p, %m/%d/%Y')}\n"
        f"\tStart Time: {round(time() - start_time, 6)} seconds\n"
        f"\tStatistics: {len(bot.guilds)} servers, {len(bot.emojis)} emoji, {len(bot.stickers)} stickers")


def owner_only(ctx):
    if ctx.author.id in bot.owner_ids:
        return True
    else:
        return False


admin = bot.create_group("admin", "Admin only commands", checks=[owner_only])


@admin.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.respond("o7", ephemeral=True)
    await bot.close()


edit = admin.create_subgroup("edit", "Profile related commands")


@edit.command()
@commands.is_owner()
@option("name", description="New name for the bot to use")
async def username(ctx,
                   name: str):
    old_name = bot.user.name
    try:
        await bot.user.edit(username=name)
    except discord.HTTPException as err:
        await ctx.respond(f"**Error:** Username could not be changed. `({err.code})`\n"
                          f"**HTTP Status:** {err.status}\n"
                          f"**Error Details:** `{err.text}`",
                          ephemeral=True)
    await ctx.respond(f"Successfully changed my username from `{old_name}` to **{bot.user.name}**.", ephemeral=True)


@edit.command()
@commands.is_owner()
@option("picture", description="New avatar for the bot to use")
async def avatar(ctx,
                 picture: discord.Attachment):
    try:
        await bot.user.edit(avatar=await picture.read())
    except discord.HTTPException as err:
        await ctx.respond(f"**Error:** Avatar could not be changed. `({err.code})`\n"
                          f"**HTTP Status:** {err.status}\n"
                          f"**Error Details:** `{err.text}`",
                          ephemeral=True)
    except discord.InvalidArgument:
        await ctx.respond(f"**Error**: The picture supplied isn't in the right format.",
                          ephemeral=True)
    await ctx.respond(f"Successfully changed my avatar!", ephemeral=True)


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, err: discord.DiscordException):
    if isinstance(err, commands.CommandOnCooldown):
        await ctx.respond("This command is currently on cooldown!")
    else:
        try:
            await ctx.respond(
                embed=discord.Embed(
                    title=err.__class__.__name__,
                    description=str(err),
                    color=discord.Color.red(),
                ), ephemeral=True
            )
            raise err
        finally:
            raise err


cogs = admin.create_subgroup("cogs", "Cog-related commands")


async def get_loaded_cogs():
    loaded_cogs = []
    for loaded_cog in list(bot.cogs):
        loaded_cogs.append(f"cogs.{loaded_cog}".lower())
    return loaded_cogs


async def cog_names(ctx: discord.AutocompleteContext):
    load_choice = ctx.options['load_choice']
    loaded_cogs = await get_loaded_cogs()
    if load_choice == 'reload' or load_choice == 'unload':
        return loaded_cogs
    else:
        unloaded_cogs = []

        for filename in listdir('./cogs'):
            if filename.endswith('.py'):
                unloaded_cogs.append(f'cogs.{filename[:-3]}'.lower())

        for loaded_cog in loaded_cogs:
            filter(loaded_cog.__ne__, unloaded_cogs)

        return unloaded_cogs


@cogs.command(name="cog", description="Manages the load state of a cog")
@option("load_choice", description="Choose what you'll do with the cog", choices=['reload', 'load', 'unload'])
@option("cog_name", description="Select the cog you wish to manage",
        autocomplete=discord.utils.basic_autocomplete(cog_names))
@commands.is_owner()
async def cog(ctx,
              load_choice: str,
              cog_name: str
              ):
    interaction = await ctx.respond(f"*Attempting to {load_choice} cog {cog_name}...*", ephemeral=True)
    match load_choice:
        case 'reload':
            bot.reload_extension(cog_name)
        case 'load':
            bot.load_extension(cog_name)
        case 'unload':
            bot.unload_extension(cog_name)
        case _:
            await interaction.edit_original_response(content="Invalid cog choice.", ephemeral=True)
    await interaction.edit_original_response(content=f"**Successfully {load_choice}ed {cog_name}!**")


@cogs.command()
@commands.is_owner()
async def list_cogs(ctx):
    if len(bot.cogs) == 0:
        return await ctx.respond("No cogs loaded!", ephemeral=True)
    await ctx.respond("Loaded cogs: ".join(map(str, bot.cogs)), ephemeral=True)


console.log("[bold blue](init)[/] Performing cog initialization...")
for filename in listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == '__main__':
    console.log(f"[bold blue](init)[/] Validating {settings[0]['sqlite_database']}...")
    if not isfile(settings[0]['sqlite_database']):
        console.log(f"[bold blue](init)[/] Database not found or is corrupted, creating new...")
        asyncio.run(create_database(settings[0]['sqlite_database']))
        console.log(f"[bold blue](init)[/] Database {settings[0]['sqlite_database']} created")
    else:
        console.log(f"[bold blue](init)[/] Database validated")
    bot.run(getenv("TOKEN"))
