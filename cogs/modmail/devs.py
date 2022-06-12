import discord
from handler import InteractionContext
from typing import Union
from discord.ext import commands


class Devs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.is_owner()
    async def blacklist(self, ctx: commands.Context):
        p = ctx.clean_prefix
        if ctx.invoked_subcommand is None:
            return await ctx.reply(f"Nutzung: `{p}blacklist add/remove @user [grund]`")

    @blacklist.command()
    @commands.is_owner()
    async def add(self, ctx: commands.Context, user: discord.Member = None, *, reason: str = None):
        if user is None:
            return await ctx.invoke(self.bot.get_command('blacklist'))
        await self.bot.mongo.blacklist(user.id, reason)
        await ctx.message.add_reaction('👌')
        await self.bot.mongo.get_blacklist_cache()

    @blacklist.command()
    @commands.is_owner()
    async def remove(self, ctx: commands.Context, user: discord.Member = None):
        if user is None:
            return await ctx.invoke(self.bot.get_command('blacklist'))
        await self.bot.mongo.unblacklist(user.id)
        await ctx.message.add_reaction('👌')
        await self.bot.mongo.get_blacklist_cache()

    @commands.Cog.listener('on_command')
    async def cmd_logs(self, ctx: Union[commands.Context, InteractionContext]):
        if not ctx.guild:
            return
        channel = self.bot.get_channel(self.bot.config.logs.cmds)
        await channel.send(embed=discord.Embed(
            title="Command benutzt:",
            description=f"Command: `{ctx.message.content if isinstance(ctx, commands.Context) else ctx.command.name}`\nSlash?: {'True' if isinstance(ctx, InteractionContext) else 'False'}",
            color=discord.Color.blurple()
        ).set_author(name=f"{ctx.author} | {ctx.author.id}", icon_url=ctx.author.display_avatar.url
        ).add_field(name="Kanal:", value=f"{ctx.channel.mention}\n#{ctx.channel.name} ({ctx.channel.id})"
        ).add_field(name="Server:", value=f"{ctx.guild.name}\n{ctx.guild.id}"))

    @commands.Cog.listener('on_app_command')
    async def slash_cmd_logs(self, ctx):
        await self.cmd_logs(ctx)


def setup(bot):
    bot.add_cog(Devs(bot))
