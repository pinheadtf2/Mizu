import math

import discord
from discord.ext import commands


class Color(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.console.log("[bold blue](init cog)[/] Color initializing...")
        self.bot.console.log("[bold blue](init cog)[/] Color active")

    def owner_only(self, ctx) -> bool:
        if ctx.author.id in self.bot.owner_ids:
            return True
        else:
            return False

    def create_color(self, user_id, color: str) -> discord.Color:
        if color[0] == "#":
            color = color[1:]

        if len(color) == 6:
            r, g, b = tuple(int(color[x:x + 2], 16) for x in (0, 2, 4))

            # no dark or white colors for non-admins
            if user_id not in self.bot.owner_ids:
                hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
                assert 50 < hsp < 235

            return discord.Color.from_rgb(r, g, b)
        raise ValueError("Invalid color")

    color = discord.SlashCommandGroup("color", "Create, edit, and delete your color role")

    @color.command(name="create", description="Create your color role. Cannot be black or white")
    async def create_role(self,
                          ctx,
                          color: discord.Option(discord.SlashCommandOptionType.string,
                                                "Use hexadecimal format, no black or white!! Example: #2196f3"),
                          user: discord.Option(discord.Member, required=False)):
        if user is None:
            user = ctx.user
        elif ctx.user.id not in self.bot.owner_ids:
            return await ctx.respond(f"You're not allowed to use this command!", ephemeral=True)

        # ensure it's a member, not a user
        if type(user) is discord.User:
            user = await ctx.guild.get_member(user.id)

        # check if the user has a role already
        for role in user.roles:
            if "[PR]" in role.name:
                return await ctx.respond(f"You already have a color role!\n"
                                         f"**Role:** {role.mention} ({role.id} | {role.color})", ephemeral=True)

        # check for existing role, assigning position to avoid a second guild color search
        designated_position = 1
        for role in await ctx.guild.fetch_roles():
            if role.name == f"[PR] {user.name}":
                await user.add_roles(role, reason=f"Re-applied personal role for {user.name}")
                return await ctx.respond(f"A role for {user.mention} already exists. Reapplied role {role.mention}!",
                                         ephemeral=True)
            elif role.id == 1294456191711313921:
                designated_position = role.position - 3

        # create and assign the role, in a try because create_color may fail
        try:
            converted_color = self.create_color(ctx.user.id, color)
        except AssertionError:
            return await ctx.respond(f"Your color is too light/dark! Please pick a different color.", ephemeral=True)
        except ValueError:
            return await ctx.respond(f"Incorrect format! Please use a hexadecimal format (#2196f3). "
                                     f"You can use this site to pick a color: https://htmlcolorcodes.com/",
                                     ephemeral=True)
        else:
            role = await ctx.guild.create_role(name=f"[PR] {user.name}",
                                               color=converted_color,
                                               reason=f"Created a color role for {user.name}")
            await role.edit(position=designated_position,
                            reason=f"Adjusted the position of {user.name}'s color role")
            await user.add_roles(role, reason=f"Applied personal role for {user.name}")
            return await ctx.respond(f"Created role {role.mention} and assigned it to {user.mention}!", ephemeral=True)

    @color.command(name="edit", description="Edit your color role. Cannot be black or white")
    async def edit_role(self,
                        ctx,
                        color: discord.Option(discord.SlashCommandOptionType.string,
                                              "Use hexadecimal format, no black or white!! Example: #2196f3"),
                        user: discord.Option(discord.Member, required=False)):
        if user is None:
            user = ctx.user
        elif ctx.user.id not in self.bot.owner_ids:
            return await ctx.respond(f"You're not allowed to use this command!", ephemeral=True)

        # ensure it's a member, not a user
        if type(user) is discord.User:
            user = await ctx.guild.get_member(user.id)

        # check if the user has a role already
        for role in user.roles:
            if "[PR]" in role.name:
                try:
                    converted_color = self.create_color(ctx.user.id, color)
                except AssertionError:
                    return await ctx.respond(f"Your color is too light/dark! Please pick a different color.",
                                             ephemeral=True)
                except ValueError:
                    return await ctx.respond(f"Incorrect format! Please use a hexadecimal format (#2196f3). "
                                             f"You can use this site to pick a color: https://htmlcolorcodes.com/",
                                             ephemeral=True)
                else:
                    await role.edit(color=converted_color,
                                    reason=f"Adjusted the color of {user.name}'s color role")
                    return await ctx.respond(f"Created role {role.mention} and assigned it to {user.mention}!",
                                             ephemeral=True)

        return await ctx.respond(f"You don't have a color role! Create one with /color create!", ephemeral=True)

    @color.command(name="delete", description="Delete your color role.")
    async def delete_role(self, ctx, user: discord.Option(discord.Member, required=False)):
        if user is None:
            user = ctx.user
        elif ctx.user.id not in self.bot.owner_ids:
            return await ctx.respond(f"You're not allowed to use this command!", ephemeral=True)

        for role in user.roles:
            if role.name == f"[PR] {user.name}":
                await role.delete(reason=f"{ctx.user.name} requested deletion of {user.name}'s role")
                return await ctx.respond(f"Deleted {user.mention}'s color role!", ephemeral=True)

    # async def get_allowed_roles(self, ctx: discord.AutocompleteContext):
    #     for role in await ctx.guild.fetch_roles():
    #
    # @color.command(description="Assign other colors to yourself.")
    # async def assign(self, ctx, user: discord.Member, roles: discord.Role):
    #     return

    @color.command(description="Debug command")
    async def positions(self, ctx):
        if ctx.user.id in self.bot.owner_ids:
            for role in ctx.guild.roles:
                self.bot.console.log(role.name, "at position", role.position)
        else:
            await ctx.respond(f"You are not allowed to use this command!", ephemeral=True)


def setup(bot):
    bot.add_cog(Color(bot))
