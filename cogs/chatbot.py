import discord
import yaml
from discord.ext import commands
from requests import HTTPError

from api.openai.handler import generate_response


class Chatbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.console.log("[bold blue](init cog)[/] Chatbot initializing...")

        with open(
                f"data/characters/{bot.chatbot_settings["default_character"]}/{bot.chatbot_settings["default_character"]}.yaml") as stream:
            try:
                self.bot.chatbot_character = yaml.safe_load(stream)
            except yaml.YAMLError as error:
                self.bot.console.log(error)
                exit(1)

        # put a test ping here, disable cog if ping fails

        self.bot.console.log("[bold blue](init cog)[/] Chatbot active")

    chatbot = discord.SlashCommandGroup("chatbot", "Chatbot relevant commands")

    @chatbot.command()
    async def initialize(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        webhook = await self.get_or_create_webhook(channel)
        await ctx.respond(f"Webhook {webhook.id} set up for {channel.mention}", ephemeral=True)

    @chatbot.command()
    async def change_character(self, ctx):
        await ctx.respond('WIP')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.bot.user.id and message.channel.id == 1353259955733397597 and not self.bot.chatbot_thinking and not message.guild.id == 1126958363012505640:
            self.bot.chatbot_thinking = True

            async with message.channel.typing():
                try:
                    webhook = await self.get_or_create_webhook(message.channel)
                    response = generate_response(self.bot.console, self.bot.chatbot_character,
                                                 self.bot.chatbot_settings, message)
                    await webhook.send(content=response, username="Sabine",
                                       avatar_url="https://cdn.discordapp.com/attachments/1353259955733397597/1366649445822763119/sabine.png")
                except HTTPError as error:
                    self.bot.chatbot_thinking = False
                    raise error
                except AssertionError as error:
                    await message.respond("It seems I can't generate a response right now, sorry!")
                finally:
                    self.bot.chatbot_thinking = False

    async def get_or_create_webhook(self, channel: discord.TextChannel) -> discord.Webhook:
        if channel.id in self.bot.webhook_cache:
            return self.bot.webhook_cache[channel.id]

        webhook = None
        cursor = await self.bot.database_connection.execute(f"SELECT * from webhooks WHERE channel_id={channel.id}")
        row = await cursor.fetchone()

        if row:
            webhook_id, channel_id, guild_id = row
            try:
                webhook = await self.bot.fetch_webhook(webhook_id)
            except discord.NotFound:
                self.bot.console.log(
                    f"[#d75f00 italic](warning) Webhook {webhook_id} for channel {channel_id} of guild {guild_id} was not found")
            except discord.Forbidden:
                self.bot.console.log(
                    f"[#d75f00 italic](warning) Webhook {webhook_id} for channel {channel_id} of guild {guild_id} is forbidden")
        else:
            webhook = await channel.create_webhook(name="pinbot Integrations",
                                                   reason="[Chatbot] Setting up new webhook for persona messages")
            await self.bot.database_connection.execute(
                f"INSERT INTO webhooks (webhook_id, channel_id, guild_id) VALUES ({webhook.id}, {webhook.channel_id}, {webhook.guild_id})", )
            await self.bot.database_connection.commit()

        self.bot.webhook_cache[channel.id] = webhook
        return webhook


def setup(bot):
    bot.add_cog(Chatbot(bot))
