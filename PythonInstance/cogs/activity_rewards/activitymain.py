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
achannel = int(config('ACHANNEL'))


async def get_user_activity():
        with open(f'json_files/activities/activity.json', 'r', encoding='utf-8') as f:
            user_activity = json.load(f)
        return user_activity

async def check_user_activity(member):
    user = member
    user_activity = await get_user_activity()
    timestamp = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
    njsonname = timestamp / 864#00
    njsonname = str(round(njsonname))
    if str(user.id) in user_activity[njsonname]:
        return False
    else:
        return True

async def new_user_activity(member):
        user = member
        user_activity = await get_user_activity()
        timestamp = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
        njsonname = timestamp / 864#00
        njsonname = str(round(njsonname))

        #try:
        if True:
            if str(user.id) in user_activity[njsonname]:
                return False
            else:
                user_activity[njsonname][str(user.id)] = {}
                user_activity[njsonname][str(user.id)]["messages"] = 0
                user_activity[njsonname][str(user.id)]["timestamp"] = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
        """except:
            user_activity[njsonname][str(user.id)] = {}
            user_activity[njsonname][str(user.id)]["messages"] = 0
            user_activity[njsonname][str(user.id)]["timestamp"] = calendar.timegm(datetime.datetime.utcnow().utctimetuple())"""
        file = open(f'json_files/activities/activity.json', 'w', encoding='utf-8')
        file.write(json.dumps(user_activity, indent=4))
        file.close()

        return True

async def update_user_activity(member):
    timestamp = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
    njsonname = timestamp / 864#00
    njsonname = str(round(njsonname))
    try:
        user = member.id
    except:
        user = member
    users_activity = await get_user_activity()
    try:
        user_activity = users_activity[njsonname][str(user)]
    except:
        usr = await new_user_activity(member)
        users_activity = await get_user_activity()
        if usr is False:
            user_activity = users_activity[njsonname][str(user)]
    users_activity[njsonname][str(user)]["messages"] += 1
    users_activity[njsonname][str(user)]["timestamp"] = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
    with open(f'json_files/activities/activity.json', 'w', encoding='utf-8') as f:
        json.dump(users_activity, f)
    return True

class activitymain(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="daily", description="Wie viele Nachrichten hat der User heute gesendet?")
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
        if member == ctx.author:
            if messages >= 30:
                await ctx.respond(f"<:DailyReward:990693035543265290> __**Tägliche Belohnung**__ <:DailyReward:990693035543265290>\n\n> Du hast heute **{messages}`/`30** *gezählte* Nachrichten in <#{achannel}> geschrieben!\n> \n> Du hast dein tägliches mindestziel ***erreicht***! <:minecraft_cake:989670170928762921>")
            else:
                await ctx.respond(f"<:DailyReward:990693035543265290> __**Tägliche Belohnung**__ <:DailyReward:990693035543265290>\n\n> Du hast heute **{messages}`/`30** *gezählte* Nachrichten in <#{achannel}> geschrieben!\n> \n> Du hast dein tägliches mindestziel __noch nicht__ erreicht! <a:rainbowbunny:985294876105130025>")
        else:
            if messages >= 30:
                await ctx.respond(f"<:DailyReward:990693035543265290> __**Tägliche Belohnung**__ <:DailyReward:990693035543265290>\n\n> {member.display_name} hat heute **{messages}`/`30** *gezählte* Nachrichten in <#{achannel}> geschrieben!\n> \n> {member.display_name} hat das tägliche mindestziel ***erreicht***! <:minecraft_cake:989670170928762921>")
            else:
                await ctx.respond(f"<:DailyReward:990693035543265290> __**Tägliche Belohnung**__ <:DailyReward:990693035543265290>\n\n> {member.display_name} hat heute **{messages}`/`30** *gezählte* Nachrichten in <#{achannel}> geschrieben!\n> \n> {member.display_name} hat das tägliche mindestziel __noch nicht__ erreicht! <a:rainbowbunny:985294876105130025>")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and int(message.channel.id) == int(achannel):
            if not "<@443769343138856961>" in message.content and not "<@!443769343138856961>" in message.content:
                timestamp = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
                njsonname = timestamp / 864#00
                njsonname = str(round(njsonname))
                guild = self.client.get_guild(guildid)
                member = guild.get_member(message.author.id)
                time = calendar.timegm(datetime.datetime.utcnow().utctimetuple()) - 5
                usac = await get_user_activity()
                try:
                    timestamp = usac[njsonname][str(member.id)]["timestamp"]
                except:
                    timestamp = 0
                role = guild.get_role(arole)
                if timestamp <= time:
                    await update_user_activity(member)
                    if not role in member.roles:
                        usac = await get_user_activity()
                        if usac[njsonname][str(member.id)]["messages"] >= 30:
                            await member.add_roles(role)
                else:
                    return
            else:
                await message.channel.send("Ping den doch nicht <:sip:985295434635415622>", reference=message)

#    @commands.Cog.listener()
#    async def on_ready(self):
#        self.before_set_activity_zero.start(self)

    @tasks.loop(seconds=24)
    async def set_activity_zero(self):
        njsonname = {datetime.datetime.now().strftime("%m%d")}
        print(njsonname[0])
        with open(f"json_files/activities/activity.json",'w') as f:
            content = json.load(f)
        content[njsonname] = {}
        with open(f'json_files/activities/activity.json', 'w', encoding='utf-8') as f:
            json.dump(content, f)
        json_name = njsonname
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