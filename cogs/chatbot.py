from datetime import datetime

from discord.ext import commands
from requests import HTTPError

from api.openai.handler import generate_response


class Chatbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.bot.user.id and message.channel.id == 1353259955733397597 and not self.bot.chatbot_thinking:
            self.bot.chatbot_thinking = True

            async with message.channel.typing():
                now = datetime.now()
                formatted_date = now.strftime("%A, %B %d, %Y, at %I:%M %p")
                try:
                    response = generate_response(self.bot.chatbot_settings, message.author.display_name)
                    await message.reply(response)
                except HTTPError as error:
                    await message.reply(f"*Unable to generate response.*\n"
                                        f"**Error Code:**{response.status_code}"
                                        f"**Response:**{error}")
                    raise error

            self.bot.openai_thinking = False

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.author.id != self.bot.user.id and message.channel.id == 1353259955733397597 and not self.bot.openai_thinking:
    #         self.bot.openai_thinking = True
    #
    #         async with message.channel.typing():
    #             now = datetime.now()
    #             formatted_date = now.strftime("%A, %B %d, %Y, at %I:%M %p")
    #             history = [{
    #                 "role": "system",
    #                 "content": f"You're {self.bot.openai_settings.character} in this discussion with a member of the Discord server {message.guild.name}. "
    #                            f"There may be other members who have chatted with you before. "
    #                            f"Keep your responses short, appropriate, and in-character. "
    #                            f"Do not include [{self.bot.openai_character}]: in your response. "
    #                            f"The date is {formatted_date}."
    #             }, {
    #                 "role": "user",
    #                 "content": f"[{message.author.name}]: {message.content}"
    #             }]
    #
    #             response, new_history = generate_response(self.bot.openai_settings, history,
    #                                                                 message.author.name, message.author.display_name)
    #             await message.reply(response)
    #
    #         self.bot.openai_thinking = False


def setup(bot):
    bot.add_cog(Chatbot(bot))
