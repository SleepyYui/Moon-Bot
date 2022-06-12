import discord
from discord.ext import commands
from typing import Union, Optional, Dict
from handler import slash_command, user_command, InteractionContext
from handler import SlashCommandOption as Option
from handler import SlashCommandChoice as Choice
from cogs.modmail.error_handler import EphemeralContext
from utils.exceptions import GuildOnlyPls, NotAdmin, NotSetup, NoBots, NotStaff, ModRoleNotFound, TicketCategoryNotFound, DMsDisabled
from utils.ui import PaginatorView, ServersDropdown, ServersDropdownView, Confirm
from utils.message import wait_for_msg
from utils.tickets_core import start_modmail_thread, get_webhook, prepare_transcript, send_modmail_message
from utils.converters import SettingConverter


dropdown_concurrency = []


class Mailhook(commands.Cog, name="Moon Angel"):
    def __init__(self, bot):
        self.bot = bot

    #@commands.command(help="Setup modmail for your server.")
    @commands.bot_has_permissions(embed_links=True)
    @slash_command(help="Setze MoonAngel für diesen Server auf.")
    async def setup(self, ctx: Union[InteractionContext, commands.Context]):
        if not ctx.guild:
            raise GuildOnlyPls()
        if not ctx.author.guild_permissions.administrator:
            raise NotAdmin()
        try:
            await self.bot.mongo.get_guild_data(ctx.guild.id)
            return await ctx.reply(embed=discord.Embed(title=f"{self.bot.config.emojis.yes} Schon aufgesetzt!", description=f"Eyo, das hast du schon gemacht.\nBitte wende dich an `Yui#9097` falls du Probleme hast.", color=discord.Color.blurple()))
        except NotSetup:
            pass
        if ctx.guild.id in self.bot.config.bot_lists:
            return await ctx.reply(f"Bitte wende dich an `Yui#9097` falls du Probleme hast.")
        final = {}
        main_msg = await ctx.reply(embed=discord.Embed(
            title=f"{self.bot.config.emojis.loading} Modmail setup!",
            description="Gib eine Mod Rolle ein.\nMit dieser Rolle, kannst du dann die Tickets sehen und antworten.",
            color=discord.Color.blurple()
        ))
        main_msg = main_msg or await ctx.original_message()
        staff_role_msg = await wait_for_msg(ctx, 60, main_msg)
        if staff_role_msg is None:
            return
        try:
            staff_role = await commands.RoleConverter().convert(ctx, staff_role_msg.content)
            if staff_role.position >= ctx.guild.me.top_role.position:
                return await main_msg.edit(content=f"{self.bot.config.emojis.no} Eyooo, die Rolle ist weiter oben als ich.\n> Bitte gib mir einfach die höhere Rolle.", embed=None)
            final.update({"staff_role": staff_role.id})
        except commands.RoleNotFound:
            return await main_msg.edit(content=f"{self.bot.config.emojis.no} Das schaut mir nicht nach einer Rolle aus.\nVersuche es bitte nochmal.", embed=None)
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            staff_role: discord.PermissionOverwrite(read_messages=True)
        }
        await main_msg.edit(embed=discord.Embed(
            title=f"{self.bot.config.emojis.loading} Modmail setup!",
            description="Gib eine Mail Kategorie ein.\nIn dieser Kategorie, kannst du die Tickets sehen und antworten.",
            color=discord.Color.blurple()
        ))
        category_msg = await wait_for_msg(ctx, 60, main_msg)
        if category_msg is None:
            return
        try:
            category = await commands.CategoryChannelConverter().convert(ctx, category_msg.content)
            final.update({"category": category.id})
        except commands.ChannelNotFound:
            return await main_msg.edit(f"{self.bot.config.emojis.no}  Das schaut mir nicht nach einer Rolle aus.\nVersuche es bitte nochmal.")
        try:
            await category.edit(overwrites=overwrites)
            transcripts = await category.create_text_channel('transcripts', topic="Modmail transcripts werden hier gelöst.", overwrites=overwrites)
        except discord.Forbidden:
            return await main_msg.edit(embed=discord.Embed(
                title=f"{self.bot.config.emojis.no} Ich kann keine Kanäle erstellen. smh",
                description="Ich brauche die `Manage Channels` Permission um Kanäle zu machen.\nBitte gib mir die und versuche es erneut..",
                color=discord.Color.red()
            ))
        final.update({"transcripts": transcripts.id})
        await self.bot.mongo.set_guild_data(ctx.guild.id, **final)
        await main_msg.edit(embed=discord.Embed(
            title=f"{self.bot.config.emojis.yes} Setup abgeschlossen.",
            color=discord.Color.blurple()
        ))

    #@commands.command(name='edit-config', help="Edit the current modmail configuration.")
    @slash_command(name='edit-config', help="Bearbeite die Konfiguration", options=[
        Option(name="Einstellung", type=3, description="Wähle aus was du ändern willst.", required=True, choices=[
            Choice(name='Transcript Kanal', value='transcripts_channel'),
            Choice(name="Mod Rolle", value='staff_role'),
            Choice(name='Mail Kategorie', value='category')
        ])
    ])
    async def edit_config(self, ctx: Union[InteractionContext, commands.Context], setting: Optional[SettingConverter] = None):
        if not ctx.guild:
            raise GuildOnlyPls()
        if not ctx.author.guild_permissions.administrator:
            raise NotAdmin()
        if setting is None:
            return await ctx.reply(f"Sag was du bearbeiten willst!\nDeine Optionen: `transcripts_channel`, `staff_role`, `category`")#\nBenutzung: `{ctx.clean_prefix}edit-config <setting>`")
        await self.bot.mongo.get_guild_data(ctx.guild.id)
        main_msg = await ctx.reply(f"Bearbeite {setting.replace('_', '').title()}\n\nGib einen neuen Wert ein...")
        main_msg = main_msg or await ctx.original_message()
        new_msg = await wait_for_msg(ctx, 60, main_msg)
        if not new_msg:
            return
        if setting == 'transcripts_channel':
            try:
                final = await commands.TextChannelConverter().convert(ctx, new_msg.content)
            except Exception:
                return await main_msg.edit(f"Ich kann den Kanal nicht finden. `{new_msg.content}`\nVersuche es bitte erneut.")
        elif setting == 'staff_role':
            try:
                final = await commands.RoleConverter().convert(ctx, new_msg.content)
            except Exception:
                return await main_msg.edit(f"Ich kann diese Rollel nicht finden. `{new_msg.content}`\nVersuche es bitte erneut.")
        else:
            try:
                final = await commands.CategoryChannelConverter().convert(ctx, new_msg.content)
            except Exception:
                return await main_msg.edit(f"Ich kann diese Kategorie nicht finden. `{new_msg.content}`\nVersuche es bitte erneut.")
        wew = {setting.replace("_channel", ""): final.id}
        await self.bot.mongo.set_guild_data(ctx.guild.id, **wew)
        return await main_msg.edit(content="Ge-Updated!\nVerwende `/show-config` um die neue Konfiguration zu sehen.")

    #@commands.command(name='show-config', help="Get the current config.")
    @slash_command(name='show-config', help="Zeige die derzeitige Konfiguration")
    async def show_config(self, ctx: Union[InteractionContext, commands.Context]):
        if not ctx.guild:
            raise GuildOnlyPls()
        guild_data = await self.bot.mongo.get_guild_data(ctx.guild.id)
        staff_role = ctx.guild.get_role(guild_data['staff_role'])
        if staff_role is None:
            raise ModRoleNotFound()
        transcript_channel = ctx.guild.get_channel(guild_data['transcripts'])
        category = ctx.guild.get_channel(guild_data['category'])
        if category is None:
            raise TicketCategoryNotFound()
        if staff_role not in ctx.author.roles:
            raise NotStaff()
        embed = discord.Embed(color=discord.Color.blurple(), title="Modmail Konfiguration!", description=f"Konfiguration für {ctx.guild.name}")
        embed.add_field(name="Mod Rolle:", value=staff_role.mention)
        embed.add_field(name="Transcript Kanal:", value=transcript_channel.mention if transcript_channel is not None else "Kein Transkript Kanal. [Nicht Empfohlen]")
        embed.add_field(name="Kategorie:", value=category.name)
        await ctx.reply(embed=embed)

    #@commands.command(name='start-ticket', help="Start a ticket with a user.")
    @slash_command(
        name="start-ticket", help="Erstelle ein Ticket mit einem User.",
        options=[
            Option(name="user", type=6, description="Der Benutzer mit dem das Ticket geführt wird.", required=True),
            Option(name="reason", type=3, description="Der Grund für das Ticket.", required=False)
        ]
    )
    @user_command(name="Start ticket")
    async def start_ticket(self, ctx: Union[InteractionContext, commands.Context], user: discord.Member = None, *, reason: str = "Kein Grund angegeben."):
        if not ctx.guild:
            raise GuildOnlyPls()
        guild_data = await self.bot.mongo.get_guild_data(ctx.guild.id)
        staff_role = ctx.guild.get_role(guild_data['staff_role'])
        if staff_role is None:
            raise ModRoleNotFound()
        if staff_role not in ctx.author.roles:
            raise NotStaff()
        user = user or ctx.target
        if user is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"Gib einen Benutzer an.")
        if user.bot:
            raise NoBots()
        channel = await start_modmail_thread(self.bot, ctx.guild.id, user.id, guild_data)
        webhook = await get_webhook(self.bot, channel.id)
        try:
            await user.send(f"""
Hallo! Ein Modmail-Ticket wurde von einem Teammitglied erstellt.

**Teammitglied:** {ctx.author.mention}
**Server:** {ctx.guild.name}
**Grund:** {reason}

Du kannst hier antworten und mit dem Team kommunizieren.
Das Ticket wird zwar NUR mit dem Team geteilt, gib jedoch bitte KEINE PERSÖNLICHEN Informationen / Daten so wie Passwörter an.
                            """)
        except discord.Forbidden:
            raise DMsDisabled(user)
        await webhook.send(f"📩 {staff_role.mention} Ein Modmail-Ticket wurde von {ctx.author.mention} geöffnet.")
        await ctx.reply(f"Bitte gehe zu {channel.mention}")

    #@commands.command(name="close-ticket", help="Close this ticket.")
    @slash_command(name="close-ticket", help="Schließe das Ticket.")
    async def close(self, ctx: Union[commands.Context, InteractionContext], channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        if not ctx.guild:
            raise GuildOnlyPls()
        guild_data = await self.bot.mongo.get_guild_data(ctx.guild.id)
        if ctx.guild.get_role(guild_data['staff_role']) not in ctx.author.roles:
            raise NotStaff()
        ticket_data = await self.bot.mongo.get_channel_modmail_thread(channel.id)
        if ticket_data is None:
            return await ctx.reply("Das schaut mir nicht nach einem Ticket aus.\nBenutze `/modmail-tickets` um alle Tickets zu sehen.")
        await self.bot.mongo.delete_channel_modmail_thread(channel.id)
        await prepare_transcript(self.bot, channel.id, ctx.guild.id, guild_data)
        await channel.delete()
        user = self.bot.get_user(ticket_data['_id'])
        if channel != ctx.channel:
            await ctx.reply("Ticket geschlossen.")
        if user is not None:
            await user.send("Dieses Ticket wurde von einem Teammitglied geschlossen.")

    #@commands.command(name='modmail-tickets', help="View all the current modmail tickets.")
    @slash_command(name='modmail-tickets', help="Zeige alle aktiven tickets.")
    async def modmail_tickets(self, ctx: Union[commands.Context, InteractionContext]):
        if not ctx.guild:
            raise GuildOnlyPls()
        guild_data = await self.bot.mongo.get_guild_data(ctx.guild.id)
        if ctx.guild.get_role(guild_data['staff_role']) not in ctx.author.roles:
            raise NotStaff()
        modmail_threads = await self.bot.mongo.get_guild_modmail_threads(ctx.guild.id)
        embed = discord.Embed(
            title="Modmail Threads",
            description="Hier sind alle Tickets:" if len(modmail_threads) != 0 else "Keine offenen Tickets.",
            color=discord.Color.blurple()
        )
        for thread in modmail_threads:
            channel = self.bot.get_channel(thread['channel_id'])
            user = self.bot.get_user(thread['_id'])
            embed.add_field(
                name=f"{user if user is not None else thread['_id']}",
                value=channel.mention if channel is not None else thread['channel_id'],
                inline=True
            )
        return await ctx.reply(embed=embed)

    """#@commands.command(name="transcripts", help="View all the modmail transcripts.")
    @slash_command(name="transcripts", help="Zeige die Modmail Transcripts.")
    async def mailhook_transcripts(self, ctx: Union[commands.Context, InteractionContext]):
        if not ctx.guild:
            raise GuildOnlyPls()
        guild_data = await self.bot.mongo.get_guild_data(ctx.guild.id)
        if ctx.guild.get_role(guild_data['staff_role']) not in ctx.author.roles:
            raise NotStaff()
        transcripts = guild_data.get("ticket_transcripts", {})
        embed = discord.Embed(
            title="Server Transcripts",
            color=discord.Color.blurple(),
            description=f"Dieser Server hat keine Transcripts."
        )
        paginator = commands.Paginator(prefix="", suffix="")
        for num, transcript_id in enumerate(transcripts):
            paginator.add_line(f"`{num}.` [{transcript_id}](https://localhost/viewticket/{ctx.guild.id}/{transcript_id})")
        embeds = []
        for page in paginator.pages:
            embed.description = page
            embeds.append(embed)
        if len(embeds) == 0:
            return await ctx.reply(embed=embed)
        elif len(embeds) == 1:
            return await ctx.reply(embed=embeds[0])
        else:
            view = PaginatorView(ctx, embeds)
            return await ctx.reply(embeds[0], view=view)

    def format_ticket_message(self, message: str) -> str:
        return "" """

    @commands.Cog.listener('on_message')
    async def modmail_dm(self, message: discord.Message):
        if message.author.bot:
            return
        if message.author.id in self.bot.mongo.blacklist_cache:
            return
        if message.guild is not None:
            return
        ctx = await self.bot.get_context(message)
        if ctx.command is not None:
            return
        modmail_thread = await self.bot.mongo.get_user_modmail_thread(message.author.id)
        if modmail_thread is None:
            mutual_guilds = message.author.mutual_guilds
            final_mutual_guilds: Dict[discord.Guild, dict] = {}
            for guild in mutual_guilds:
                try:
                    guild_data = await self.bot.mongo.get_guild_data(guild.id)
                    final_mutual_guilds.update({guild: guild_data})
                except NotSetup:
                    pass
            if len(final_mutual_guilds) == 0:
                return
            if len(final_mutual_guilds) == 1:
                for g in final_mutual_guilds:
                    final_guild = g
            else:
                view = ServersDropdownView()
                select = ServersDropdown(list(final_mutual_guilds))
                view.add_item(select)
                main_msg = await message.channel.send("Hey, du willst also ein Ticket öffnen.\nWenn ja, wähle den Server den du kontaktieren willst aus.", view=view)
                dropdown_concurrency.append(message.author.id)
                await view.wait()
                if not view.yes:
                    return await main_msg.delete()
                final_guild = self.bot.get_guild(int(view.children[2].values[0]))
                await main_msg.edit(view=None)
            confirm = Confirm(ctx, 60)
            m = await message.channel.send(f"Willst du diese Nachricht an die Teammitglieder von {final_guild.name} senden?", view=confirm)
            await confirm.wait()
            if not confirm.value:
                return await m.delete()
            await m.edit(view=None)
            if message.author.id in dropdown_concurrency:
                dropdown_concurrency.remove(message.author.id)
            channel = await start_modmail_thread(self.bot, final_guild.id, message.author.id)
            ping_staff = final_mutual_guilds[final_guild].get('ping_staff', True)
            await channel.send(
                f"<@&{final_mutual_guilds[final_guild]['staff_role']}> {message.author.mention} hat ein Ticket geöffnet.",
                allowed_mentions=discord.AllowedMentions.all() if ping_staff else discord.AllowedMentions.none()
            )
            await channel.send(
                f"""
Alle Nachrichten hier, landen in den DMs des Ticket-Erstellers.
Nachroichten mit `-` am Anfang werden Ignoriert und nicht an den Benutzer gesendet.
                """
            )
        else:
            channel = self.bot.get_channel(modmail_thread['channel_id'])
        if channel is None:
            await message.channel.send("Dieses Ticket existiert nicht mehr.\nBitte sende diese Nachricht erneut um ein neues Ticket zu öffnen.")
            return await self.bot.mongo.delete_user_modmail_thread(message.author.id)
        await send_modmail_message(self.bot, channel, message)
        await message.add_reaction('✔️')

    @commands.Cog.listener('on_message')
    async def modmail_reply(self, message: discord.Message):
        if message.author.bot:
            return
        if message.author.id in self.bot.mongo.blacklist_cache:
            return
        if message.guild is None:
            return
        if message.content.startswith("-"):
            return
        if not message.channel.name.startswith("ticket-"):
            return
        ctx = await self.bot.get_context(message)
        if ctx.command is not None:
            return
        try:
            ticket_user = self.bot.get_user(int(message.channel.name[7:]))
            if ticket_user is None:
                return
            modmail_thread = await self.bot.mongo.get_channel_modmail_thread(message.channel.id)
            if modmail_thread is None:
                return
        except ValueError:
            return
        try:
            data = await self.bot.mongo.get_guild_data(message.guild.id)
        except NotSetup:
            return
        if message.guild.get_role(data['staff_role']) not in message.author.roles:
            return
        embeds = [discord.Embed().set_author(name=message.author, icon_url=message.author.display_avatar.url
                                             ).set_footer(text=f"Server: {message.guild.name}")]
        for sticker in message.stickers:
            embeds.append(discord.Embed(
                title=sticker.name,
                url=sticker.url,
                color=discord.Color.blurple(),
                description=f"Sticker ID: `{sticker.id}`"
            ).set_image(url=sticker.url))
        await ticket_user.send(
            message.content,
            files=[await attachment.to_file() for attachment in message.attachments],
            embeds=embeds
        )
        await message.add_reaction('✔️')

    #@commands.command(name='anon-reply', help="Reply anonymously to a ticket.")
    @slash_command(name="anon-reply", help="Antworte anonym auf ein Ticket.")
    async def areply(self, ctx: InteractionContext, *, message: str):
        if not ctx.guild:
            raise GuildOnlyPls()
        guild_data = await self.bot.mongo.get_guild_data(ctx.guild.id)
        if ctx.guild.get_role(guild_data['staff_role']) not in ctx.author.roles:
            raise NotStaff()
        if isinstance(ctx, InteractionContext):
            ctx = EphemeralContext(ctx, self.bot)
        ticket_data = await self.bot.mongo.get_channel_modmail_thread(ctx.channel.id)
        if ticket_data is None:
            return await ctx.reply("Das schaut mir nicht nach einem Ticket aus.\nBenutze `/modmail-tickets` um alle Tickets zu sehen.")
        user = self.bot.get_user(ticket_data['_id'])
        try:
            await user.send(message, embed=discord.Embed().set_author(name="Anonyme Antwort.").set_footer(text=f"Server: {ctx.guild.name}"))
            await send_modmail_message(self.bot, ctx.channel, message, anon=True)
            if isinstance(ctx, commands.Context):
                await ctx.message.delete()
            else:
                await ctx.reply("Nachricht gesendet!")
        except Exception as e:
            await ctx.reply(f"Nachricht kann nicht gesendet werden weil: `{e}`")

    """@commands.Cog.listener('on_message')
    async def prefix_reply(self, message: discord.Message):
        if message.author.bot:
            return
        if message.content.lower() not in [f"<@{self.bot.user.id}>", f"<@!{self.bot.user.id}>"]:
            return
        prefixes = self.bot.config.prefixes.copy()
        if not message.guild:
            return await message.reply(f"My prefixes are: {', '.join(['`' + p + '`' for p in prefixes])}")
        guild_prefixes = await self.bot.mongo.get_prefixes(message.guild.id)
        if not guild_prefixes:
            return await message.reply(f"My prefixes are: {', '.join(['`' + p + '`' for p in prefixes])}")
        await message.reply(f"My prefixes are: {', '.join(['`' + p + '`' for p in guild_prefixes])}")

    @commands.group(name="prefix", help="Manage the prefixes for the bot.")
    async def prefix(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            prefixes = await self.bot.mongo.get_prefixes(ctx.guild.id)
            if not prefixes:
                prefixes = self.bot.config.prefixes.copy()
            return await ctx.reply(f"Your current prefixes are: {', '.join(['`' + prefix + '`' for prefix in prefixes])}\nYou can use the following commands to manage them:\n\n- `{ctx.clean_prefix}prefix add <prefix>`\n- `{ctx.clean_prefix}prefix remove <prefix>`")

    @prefix.command(name="add", help="Add a prefix to the bot.")
    @commands.has_permissions(manage_guild=True)
    async def prefix_add(self, ctx: commands.Context, *, prefix: str = None):
        if prefix is None:
            return await ctx.reply(f"{self.bot.config.emojis.no} Please specify a prefix to add.")
        prefixes = await self.bot.mongo.get_prefixes(ctx.guild.id)
        if not prefixes:
            prefixes = self.bot.config.prefixes.copy()
        if len(prefixes) >= 10:
            return await ctx.reply(f"{self.bot.config.emojis.no} You can only have 10 prefixes.")
        if prefix in prefixes:
            return await ctx.reply(f"{self.bot.config.emojis.no} This prefix is already added.")
        prefixes.append(prefix)
        await self.bot.mongo.set_guild_data(ctx.guild.id, prefixes=prefixes)
        await ctx.reply(f"{self.bot.config.emojis.yes} Added `{prefix}` to your prefixes.")

    @prefix.command(name="remove", help="Remove a prefix from the bot.")
    @commands.has_permissions(manage_guild=True)
    async def prefix_remove(self, ctx: commands.Context, *, prefix: str = None):
        if prefix is None:
            return await ctx.reply(f"{self.bot.config.emojis.no} Please specify a prefix to remove.")
        prefixes = await self.bot.mongo.get_prefixes(ctx.guild.id)
        if not prefixes:
            prefixes = self.bot.config.prefixes.copy()
        if prefix not in prefixes:
            return await ctx.reply(f"{self.bot.config.emojis.no} This prefix is not added.")
        if len(prefixes) == 1:
            return await ctx.reply(f"{self.bot.config.emojis.no} You cannot remove the last prefix.\nPlease add another one and then remove this one.")
        prefixes.remove(prefix)
        await self.bot.mongo.set_guild_data(ctx.guild.id, prefixes=prefixes)
        await ctx.reply(f"{self.bot.config.emojis.yes} Removed `{prefix}` from your prefixes.")"""


def setup(bot):
    bot.add_cog(Mailhook(bot))
