import re
from urllib.parse import urlparse

from discord.ext import commands


netloc_map = {
    "x.com": "vxtwitter.com",
    "tiktok.com": "tnktok.com",
    "instagram.com": "ddinstagram.com",
}


class BetterLinks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.console.log("[bold blue](init cog)[/] BetterLinks initializing...")
        # balls
        self.bot.console.log("[bold blue](init cog)[/] BetterLinks active")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.bot.user.id:
            extracted_links = re.compile(r'https?://\S+').findall(message.content)

            corrected_links = []
            for link in extracted_links:
                url = urlparse(link)
                if url.netloc in netloc_map:
                    corrected_links.append(f"{url.scheme}://{netloc_map[url.netloc]}{url.path}")

            if len(corrected_links) >= 1:
                await message.reply(f"Here you go!\n{'\n'.join(map(str, corrected_links))}")


def setup(bot):
    bot.add_cog(BetterLinks(bot))
