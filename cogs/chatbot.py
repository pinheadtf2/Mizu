from datetime import datetime
import yaml

import discord
from discord.ext import commands
from requests import HTTPError

from api.openai.handler import generate_response


def check_webhook(ctx):
    return


class Chatbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open(
                f"data/characters/{bot.chatbot_settings["default_character"]}/{bot.chatbot_settings["default_character"]}.yaml") as stream:
            try:
                self.bot.chatbot_character = yaml.safe_load(stream)
            except yaml.YAMLError as error:
                self.bot.console.log(error)
                exit(1)

    chatbot = discord.SlashCommandGroup("chatbot", "Chatbot relevant commands")

    @chatbot.command()
    async def change_character(self, ctx):
        await ctx.respond('WIP')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.bot.user.id and message.channel.id == 1353259955733397597 and not self.bot.chatbot_thinking:
            self.bot.chatbot_thinking = True

            async with message.channel.typing():
                try:
                    response = generate_response(self.bot.chatbot_character, self.bot.chatbot_settings, message)
                    self.bot.openai_thinking = False
                    await message.reply(response)
                except HTTPError as error:
                    self.bot.openai_thinking = False
                    raise error


def setup(bot):
    bot.add_cog(Chatbot(bot))
