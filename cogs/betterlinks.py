import discord
from discord.ext import commands
from typing import List
from urllib.parse import urlparse
import re

# Assume this mapping exists
netloc_map = {
    "twitter.com": "vxtwitter.com",
    "x.com": "vxtwitter.com",
    "tiktok.com": "vxtiktok.com",
    "instagram.com": "ddinstagram.com"
}

async def get_convertable_media(bot: discord.Bot, url: str) -> List[str]:
    async with bot.aiohttp_session.get(url) as response:
        json_data = await response.json()
        return [media["url"] for media in json_data.get("media_extended", []) if media["type"] != "image"]

class TwitterActionView(discord.ui.View):
    def __init__(self, original_message, vxtwitter_links, media_links, other_links):
        super().__init__(timeout=60)
        self.original_message = original_message
        self.vxtwitter_links = vxtwitter_links
        self.media_links = media_links
        self.other_links = other_links

        # Disable "Send Media" button if there's no media
        self.send_media.disabled = len(self.media_links) == 0

    @discord.ui.button(label="Send Link", style=discord.ButtonStyle.primary)
    async def send_link(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.other_links:
            await self.original_message.reply(f"{chr(10).join(self.vxtwitter_links)}\n{chr(10).join(self.other_links)}")
        else:
            await self.original_message.reply(f"{chr(10).join(self.vxtwitter_links)}")

    @discord.ui.button(label="Send Media", style=discord.ButtonStyle.secondary)
    async def send_media(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.media_links:
            await self.original_message.reply(f"{chr(10).join(self.media_links)}\n{chr(10).join(self.other_links)}")
        else:
            await self.original_message.reply(f"{chr(10).join(self.media_links)}")

    @discord.ui.button(label="Ignore", style=discord.ButtonStyle.danger)
    async def ignore(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.other_links:
            await self.original_message.reply(f"{chr(10).join(self.other_links)}")

class BetterLinks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.console.log("[bold blue](init cog)[/] BetterLinks initializing...")
        self.bot.console.log("[bold blue](init cog)[/] BetterLinks active")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        extracted_links = re.findall(r'https?://\S+', message.content)
        vxtwitter_links = []
        media_links = []
        other_links = []

        for link in extracted_links:
            url = urlparse(link)
            clean_netloc = url.netloc.lower().removeprefix("www.")
            new_netloc = netloc_map.get(clean_netloc)
            if not new_netloc:
                continue

            converted_link = f"{url.scheme}://{new_netloc}{url.path}"

            if new_netloc == "vxtwitter.com":
                vxtwitter_links.append(converted_link)
                twitter_media = await get_convertable_media(self.bot, f"{url.scheme}://api.vxtwitter.com{url.path}")
                media_links.extend(twitter_media)
            else:
                other_links.append(converted_link)

        if vxtwitter_links:
            view = TwitterActionView(message, vxtwitter_links, media_links, other_links)
            await message.channel.send(
                "Choose how to handle Twitter links:\n-# Deletes in 15 seconds",
                view=view,
                delete_after=15,
                silent=True
            )
        elif other_links:
            await message.reply(f"{chr(10).join(other_links)}")

def setup(bot):
    bot.add_cog(BetterLinks(bot))
