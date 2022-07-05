import discord
from discord.ext import commands, tasks
from datetime import datetime
import json
from decouple import config
import calendar
import datetime
from datetime import timedelta
import asyncio


class hexconsole(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="sdmsg")
    async def setdailymsg(self, ctx, day, userid, messages):
        if str(ctx.author.id) == "443769343138856961":
            try:
                await ctx.message.delete()
            except:
                pass
            try:
                with open(f'json_files/activities/activity.json', 'r', encoding='utf-8') as f:
                    user_activity = json.load(f)
                user_activity[str(day)][str(userid)]["messages"] = int(messages)
                file = open(f'json_files/activities/activity.json', 'w', encoding='utf-8')
                file.write(json.dumps(user_activity, indent=4))
                file.close()
                await ctx.send("Fertig", delete_after=5)
            except:
                await ctx.send("Nope, da hat etwas nicht funktioniert.", delete_after=5)
        else:
            return False


def setup(client):
    client.add_cog(hexconsole(client))

