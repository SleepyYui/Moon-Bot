
import discord
from discord.ext import commands, tasks
from datetime import datetime
import json
from decouple import config

rolelist = [953778432813187123, 632674518317531137]
statrole = int(config('SROLE'))
guildid = int(config('SGUILD'))

class statusmain(commands.Cog):

    def __init__(self, client):
        self.client = client

    """@commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = self.client.get_guild(guildid)
        member = guild.get_member(before.id)
        cstatus = self.get_status(member)
        rstatus = self.check_status(member, cstatus)
        #print("E")
        if rstatus == "Yes" or rstatus == "True":
            role = guild.get_role(statrole)
            await member.add_roles(role)
        elif rstatus == "False":
            role = guild.get_role(statrole)
            await member.remove_roles(role)
        else:
            return"""

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        guild = self.client.get_guild(guildid)
        member = guild.get_member(before.id)
        cstatus = self.get_status(member)
        rstatus = self.check_status(member, cstatus)
        #print("E")
        if rstatus == "Yes" or rstatus == "True":
            role = guild.get_role(statrole)
            await member.add_roles(role)
        elif rstatus == "False":
            role = guild.get_role(statrole)
            await member.remove_roles(role)
        else:
            return

    @tasks.loop(hours=12)
    async def check_roles(self):
        boosters = self.get_booster()
        guild = self.client.get_guild(int(config('SGUILD')))
        role = guild.get_role(int(config('SROLE')))
        for user in boosters:
            user = guild.get_member(user)
            status = self.get_status(user)
            if status != None:
                #print(status)
                if ".gg/moonfamily" not in status.lower():
                    await user.remove_roles(role)
            else:
                await user.remove_roles(role)
        print(f"Checked status roles at {datetime.now()}")

    """@tasks.loop(seconds=1800)
    async def check_offline_roles(self):
        obooster = self.get_obooster()"""

    @commands.slash_command(name="check_status", description="??berpr??fe, ob ein User \"discord.gg/moonfamily\" im Status hat.")
    async def checksbooster(self, ctx, member : discord.Member = None):
        if member is None:
            member = ctx.author
        member = ctx.guild.get_member(int(member.id))
        cstatus = self.get_status(member)
        guild = self.client.get_guild(ctx.guild.id)
        check = self.check_status(member, cstatus)
        role = guild.get_role(statrole)
        if check == "True":
            await member.add_roles(role)
            await ctx.respond(f"{member.name} ist ein Status-Booster.")
        elif check == "False":
            await member.remove_roles(role)
            await ctx.respond(f"{member.name} ist kein Status-Booster.")
        elif check == "None":
            await ctx.respond(f"{member.name} hat keinen / nicht den richtigen Status.")
        elif check == "Yes":
            await ctx.respond(f"{member.name} ist ein Status-Booster.")

    def get_status(self, user):
        try:
            for status in user.activities:
                if isinstance(status, discord.CustomActivity):
                    return status.state
        except:
            return None

    def check_status(self, user, status):
        if status != None:
            if ".gg/moonfamily" in status.lower():
                if user.id in self.get_booster():
                    return "Yes"
                else:
                    self.add_booster(user.id)
                    return "True"
            else:
                if user.id in self.get_booster():
                    self.remove_booster(user.id)
                    return "False"
                else:
                    return "None"
        elif user.id in self.get_booster():
            self.remove_booster(user.id)
            return "False"
        else:
            return "None"


    def get_booster(self):
        with open('./json_files/status_boosters.json', 'r') as f:
            boosters = json.load(f)
        return boosters

    def add_booster(self, booster):
        with open('./json_files/status_boosters.json', 'r') as f:
            boosters = json.load(f)
        boosters.append(booster)
        with open('./json_files/status_boosters.json', 'w') as f:
            json.dump(boosters, f)

    def remove_booster(self, booster):
        with open('./json_files/status_boosters.json', 'r') as f:
            boosters = json.load(f)
        boosters.remove(booster)
        with open('./json_files/status_boosters.json', 'w') as f:
            json.dump(boosters, f)

    def add_obooster(self, booster):
        with open('./json_files/status_oboosters.json', 'r') as f:
            boosters = json.load(f)
        boosters.append(booster)
        with open('./json_files/status_oboosters.json', 'w') as f:
            json.dump(boosters, f)

    def remove_obooster(self, booster):
        with open('./json_files/status_oboosters.json', 'r') as f:
            boosters = json.load(f)
        boosters.remove(booster)
        with open('./json_files/status_oboosters.json', 'w') as f:
            json.dump(boosters, f)

def setup(client):
    client.add_cog(statusmain(client))