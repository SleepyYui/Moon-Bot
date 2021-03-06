import discord
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
from datetime import date

class uptime(commands.Cog):

    def __init__(self, client):
        self.client = client



    """@commands.command()
    async def uptime(self, ctx):
        delta_uptime =  datetime.now() - self.client.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"The bot has been online for **{days} days**, **{hours} hours** and **{minutes} minutes**")"""

    @commands.slash_command(name="uptime", description="Wie lange ist der Bot schon Online?")
    async def uptime_slash(self, ctx):
        delta_uptime =  datetime.now() - self.client.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.respond(f"Der Bot ist online seit **{days} Tagen**, **{hours} Stunden** und **{minutes} Minuten** und **{seconds} Sekunden**", ephemeral=True)



def setup(client):
    client.add_cog(uptime(client))