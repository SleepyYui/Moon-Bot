import discord
from discord.ext import commands, tasks
from datetime import datetime
import json
from decouple import config
import calendar
import datetime
from datetime import timedelta
import asyncio


rolelist = [953778432813187123, 632674518317531137]
arole = int(config('AROLE'))
guildid = int(config('SGUILD'))


async def get_user_activity():
        with open("json_files/activity.json", "r") as f:
            user_activity = json.load(f)
        return user_activity

async def check_user_activity(member):
    user = member
    user_activity = await get_user_activity()
    if str(user.id) in user_activity:
        return False
    else:
        return True

async def new_user_activity(member):
        user = member
        user_activity = await get_user_activity()

        if str(user.id) in user_activity:
            return False
        else:
            user_activity[str(user.id)] = {}
            user_activity[str(user.id)]["messages"] = 0
            user_activity[str(user.id)]["timestamp"] = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
        file = open('json_files/activity.json', 'w', encoding='utf-8')
        file.write(json.dumps(user_activity, indent=4))
        file.close()

        return True

async def update_user_activity(member):
    try:
        user = member.id
    except:
        user = member
    users_activity = await get_user_activity()
    try:
        user_activity = users_activity[str(user)]
    except:
        usr = await new_user_activity(member)
        users_activity = await get_user_activity()
        if usr is False:
            user_activity = users_activity[str(user)]
    users_activity[str(user)]["messages"] += 1
    users_activity[str(user)]["timestamp"] = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
    with open('json_files/activity.json', 'w', encoding='utf-8') as f:
        json.dump(users_activity, f)
    return True

class activitymain(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="check_messages", description="Wie viele Nachrichten hat der User heute gesendet?")
    async def checksbooster(self, ctx, member : discord.Member = None):
        if member is None:
            member = ctx.author
        #member = ctx.guild.get_member(int(member.id))
        user = member
        usac = await get_user_activity()
        try:
            messages = usac[str(user.id)]["messages"]
        except:
            messages = 0
        if messages > 1 or messages == 0:
            await ctx.respond(f"{member.name} hat heute {messages} Nachrichten gesendet.")
        else:
            await ctx.respond(f"{member.name} hat heute {messages} Nachricht gesendet.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:# and message.channel.id in [903714957923864588]:
            guild = self.client.get_guild(guildid)
            member = guild.get_member(message.author.id)
            time = calendar.timegm(datetime.datetime.utcnow().utctimetuple()) - 5
            usac = await get_user_activity()
            try:
                timestamp = usac[str(member.id)]["timestamp"]
            except:
                timestamp = 0
            role = guild.get_role(arole)
            if timestamp <= time:
                await update_user_activity(member)
                if not role in member.roles:
                    usac = await get_user_activity()
                    if usac[str(member.id)]["messages"] >= 30:
                        await member.add_roles(role)
            else:
                return

#    @commands.Cog.listener()
#    async def on_ready(self):
#        self.before_set_activity_zero.start(self)

    @tasks.loop(hours=24)
    async def set_activity_zero(self):
        with open('json_files/activity.json' ,'w') as f:
            f.write("{}")
        guild = self.client.get_guild(guildid)
        role = guild.get_role(arole)
        for member in role.members:
            await member.remove_roles(role)
        print(f"Reset activity roles at {datetime.datetime.now()}")

    """@set_activity_zero.before_loop
    async def before_set_activity_zero(self):
        hour = 14
        minute = 56
        #await self.client.wait_until_ready()
        now = datetime.datetime.now()
        future = datetime.datetime.datetime(now.year, now.month, now.day, hour, minute)
        if now.hour >= hour and now.minute > minute:
            future += timedelta(days=1)
        print(f"set_activity_zero loop starting in {(future-now).seconds} seconds")
        await asyncio.sleep((future-now).seconds)"""


def setup(client):
    client.add_cog(activitymain(client))