from datetime import datetime

from discord.ext import commands

from api.openai.handler import generate_response


class Chatbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.bot.user.id and message.channel.id == 1353259955733397597 and not self.bot.openai_thinking:
            self.bot.openai_thinking = True

            async with message.channel.typing():
                now = datetime.now()
                formatted_date = now.strftime("%A, %B %d, %Y, at %I:%M %p")
                history = [{
                    "role": "system",
                    "content": f"You're Sabine in this discussion with a member of the Discord server {message.guild.name}. "
                               f"There may be other members who have chatted with you before. "
                               f"Keep your responses short, appropriate, and in-character. "
                               f"Do not include [{self.bot.openai_character}]: in your response. "
                               f"The date is {formatted_date}."
                }, {
                    "role": "user",
                    "content": f"[{message.author.name}]: {message.content}"
                }]

                generated_response, new_history = generate_response(self.bot.openai_url, history, self.bot.openai_character,
                                                                    message.author.name, message.author.display_name)
                await message.reply(generated_response)

            self.bot.openai_thinking = False


def setup(bot):
    bot.add_cog(Chatbot(bot))
