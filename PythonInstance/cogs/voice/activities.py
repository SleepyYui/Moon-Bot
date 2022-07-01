import discord
from discord.ext import commands, tasks
from discord import Option
from datetime import datetime
import json
from decouple import config
import calendar
import datetime
from datetime import timedelta
import asyncio
import discord
from discord_together import DiscordTogether

class vcactivity(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="activity", description="Starte eine Aktivität mit deinen Freunden.")
    async def activities(self, ctx, mode: Option(str, 'Aktivität', choices=["Watch Together", "Poker Night", "Chess in the Park", "Betrayal.io", "Fishington.io (Broken)", "Letter League", "Word Snack", "Sketch Heads", "SpellCast", "Awkword", "Checkers in the Park", "Blazing 8s", "Land-io", "Putt Party", "Bobble League"], required=True)):

        if mode == "Watch Together":
            smode = "youtube"
        elif mode == "Poker Night":
            smode = "poker"
        elif mode == "Chess in the Park":
            smode = "chess"
        elif mode == "Betrayal.io":
            smode = "betrayal"
        elif mode == "Fishington.io (Broken)":
            smode = "fishing"
        elif mode == "Letter League":
            smode = "letter-league"
        elif mode == "Word Snack":
            smode = "word-snack"
        elif mode == "Sketch Heads":
            smode = "sketch-heads"
        elif mode == "SpellCast":
            smode = "spellcast"
        elif mode == "Awkword":
            smode = "awkword"
        elif mode == "Checkers in the Park":
            smode = "checkers"
        elif mode == "Blazing 8s":
            smode = "blazing-8s"
        elif mode == "Land-io":
            smode = "land-io"
        elif mode == "Putt Party":
            smode = "putt-party"
        elif mode == "Bobble League":
            smode = "bobble-league"
        else:
            await ctx.respond("Ungültige Auswahl", delete_after=5)

        link = await self.client.togetherControl.create_link(ctx.author.voice.channel.id, smode)

        view = discord.ui.View()
        style = discord.ButtonStyle.blurple
        item = discord.ui.Button(style=style, label="Tritt der Aktivität bei", url=link)
        view.add_item(item=item)

        await ctx.respond(f"Tritt {ctx.author.mention} bei {mode} bei.", view=view)

def setup(client):
    client.add_cog(vcactivity(client))