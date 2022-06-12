import discord
from discord.ext import commands
from datetime import datetime
from decouple import config
from discord import Embed, slash_command
import json

rolelist = [953778432813187123, 632674518317531137]

class statusmain(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        member = self.client.get_guild(before.guild.id).get_member(before.id)
        for status in member.activities:
            if isinstance(status, discord.CustomActivity):
                print(status)

    @commands.slash_command(name="check_status_booster", description="Überprüfe ob ein user \"discord.gg/moonfamily\" im Status hat.")
    async def checksbooster(self, ctx, member : discord.Member = None):
        if any(role.id in rolelist for role in ctx.author.roles):
            if member is None:
                member = ctx.author
            boosters = self.get_booster(member.id)
            if member.id in boosters:
                await ctx.respond(f"{member.mention} ist ein Status-Booster")
            else:
                await ctx.respond(f"{member.mention} ist kein Status-Booster")
            for status in member.activities:
                if isinstance(status, discord.CustomActivity):
                    print(status)
        else:
            await ctx.respond("Du hast keine Berechtigung dazu", ephemeral=True)

    def get_booster(self, booster):
        with open('booster.json', 'r') as f:
            boosters = json.load(f)
        return boosters

    def add_booster(self, booster):
        with open('booster.json', 'r') as f:
            boosters = json.load(f)
        boosters.append(booster)
        with open('booster.json', 'w') as f:
            json.dump(boosters, f)

    def remove_booster(self, booster):
        with open('booster.json', 'r') as f:
            boosters = json.load(f)
        boosters.remove(booster)
        with open('booster.json', 'w') as f:
            json.dump(boosters, f)

def setup(client):
    client.add_cog(statusmain(client))