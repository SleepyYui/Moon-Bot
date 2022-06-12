import traceback

import discord
from discord.ext import commands
from handler import InteractionContext
from utils.exceptions import (
    NotSetup, NotStaff, NotAdmin, ModRoleNotFound,
    TicketCategoryNotFound, TranscriptChannelNotFound,
    UserAlreadyInAModmailThread, DMsDisabled, NoBots,
    GuildOnlyPls
)
from typing import Union
from humanfriendly import format_timespan


def e(title: str, desc: str) -> discord.Embed:
    return discord.Embed(title=title, description=desc, color=discord.Color.red())


class EphemeralContext(InteractionContext):
    async def reply(self, *args, **kwargs):
        await super().reply(*args, **kwargs, ephemeral=True)


class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_command_error')
    async def on_command_error(self, ctx: Union[commands.Context, InteractionContext], error):
        if isinstance(ctx, InteractionContext):
            ctx = EphemeralContext(ctx, ctx.bot)
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"Du bist im cooldown für **{format_timespan(round(error.retry_after, 2))}**", delete_after=5)
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            perms = error.missing_permissions
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Neeeee!",
                "Du brauchst **{}** Berechtigungen um diesen Command zu benutzen.".format(' '.join(error.missing_permissions[0].split('_')).title())
            ))
        elif isinstance(error, commands.BotMissingPermissions):
            perms = error.missing_permissions
            if "embed_links" in perms:
                return await ctx.reply("Bitte gib mir embed_links Berechtigungen")
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Ich habe keine berechtigungen :(",
                "Ich brauche **{}** Berechtigungen um diesen Command auszuführen.".format(' '.join(error.missing_permissions[0].split('_')).title())
            ))
        elif isinstance(error, commands.CheckFailure):
            return
        elif isinstance(error, NotSetup):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Der Server ist nicht aufgesetzt!",
            ))
        elif isinstance(error, NotStaff):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Nur Team!",
                "Haha du bist nicht im Team. F"
            ))
        elif isinstance(error, NotAdmin):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Nur Admins!",
                "Haha du bist kein Admin. F"
            ))
        elif isinstance(error, ModRoleNotFound):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Nicht gefunden!",
                "Ääääääh, ich konnte die Mod-Rollen nicht finden. Bitte mach nochmal `/edit-config` und gib mir die Rollen."
            ))
        elif isinstance(error, TicketCategoryNotFound):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Nicht gefunden!",
                "Ääääääh, ich konnte die Kategorie nicht finden. Bitte mach nochmal `/edit-config` und gib mir die Kategorie."
            ))
        elif isinstance(error, TranscriptChannelNotFound):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Nicht gefunden!",
                "Ääääääh, ich konnte den Kanaö nicht finden. Bitte mach nochmal `/edit-config` und gib mir den Kanal."
            ))
        elif isinstance(error, UserAlreadyInAModmailThread):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Wir sind schon in einem Modmail-Thread!",
                f"`{error.user}` hat schon einen Thread"
            ))
        elif isinstance(error, DMsDisabled):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Ich kann keine DM schicken! :c",
                f"Der / Die gemeine {error.user} hat DMs deaktiviert. Ich kann leider keine DM schicken. :c"
            ))
        elif isinstance(error, (commands.MemberNotFound, commands.UserNotFound, commands.ChannelNotFound, commands.RoleNotFound)):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} Nicht gefunden!",
                f"I was unable to find: `{error.argument}`"
            ))
        elif isinstance(error, NoBots):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} KEINE ROBOTER!",
                "Versuchs an einer echten Person."
            ))
        elif isinstance(error, GuildOnlyPls):
            await ctx.reply(embed=e(
                f"{self.bot.config.emojis.no} KEINE DMs!",
                "Ich reagiere nicht auf DMs. Benutz lieber nen Server."
            ))
        else:
            error_text = "".join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))[:4000]
            print(error_text)
            try:
                await ctx.channel.send(embed=e(
                    f"{self.bot.config.emojis.no} Was ist denn hier Passiert?",
                    f"Was heißt das???\n```{error}```"
                ))
            except Exception:
                await ctx.channel.send(f"Error: \n\n```{error}```")
            try:
                await self.bot.get_channel(self.bot.config.logs.cmd_errs).send(embed=e("Unbekannter Error", f"```py\n{error_text}\n```"))
            except Exception:
                traceback.print_exception(etype=type(error), value=error, tb=error.__traceback__)

    @commands.Cog.listener('on_app_command_error')
    async def on_app_command_error(self, ctx: InteractionContext, error):
        await self.on_command_error(ctx, error)


def setup(bot):
    bot.add_cog(ErrorHandling(bot))
