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
    njsonname = {datetime.datetime.now().strftime("%y%m%d")}
    for i in njsonname:
        njsonname = i
        break
    if str(user.id) in user_activity[njsonname]:
        return False
    else:
        return True

async def new_user_activity(member):
        user = member
        user_activity = await get_user_activity()
        njsonname = {datetime.datetime.now().strftime("%y%m%d")}
        for i in njsonname:
            njsonname = i
            break
        #print(type(user_activity))
        #print(user_activity)

        try:
            tmp = user_activity[njsonname]
        except:
            user_activity[njsonname] = {}
            user_activity[njsonname][str(user.id)] = {}
            user_activity[njsonname][str(user.id)]["messages"] = 0
            user_activity[njsonname][str(user.id)]["timestamp"] = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
            file = open(f'json_files/activities/activity.json', 'w', encoding='utf-8')
            file.write(json.dumps(user_activity, indent=4, sort_keys=True))
            file.close()

            return False

        #try:
        if True:
            useract = user_activity[njsonname]
            if str(user.id) in useract:
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
        file.write(json.dumps(user_activity, indent=4, sort_keys=True))
        file.close()

        return True

async def update_user_activity(member):
    njsonname = {datetime.datetime.now().strftime("%y%m%d")}
    for i in njsonname:
        njsonname = i
        break
    try:
        user = member.id
    except:
        user = member
    users_activity = await get_user_activity()
    try:
        #print(users_activity[njsonname][str(user)])
        tmp = users_activity[njsonname][str(user)]
    except:
        usr = await new_user_activity(member)
        users_activity = await get_user_activity()

    users_activity[njsonname][str(user)]["messages"] += 1
    users_activity[njsonname][str(user)]["timestamp"] = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
    file = open(f'json_files/activities/activity.json', 'w', encoding='utf-8')
    file.write(json.dumps(users_activity, indent=4, sort_keys=True))
    file.close()
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
        njsonname = {datetime.datetime.now().strftime("%y%m%d")}
        for i in njsonname:
            njsonname = i
            break
        try:
            messages = usac[njsonname][str(user.id)]["messages"]
        except:
            messages = 0

        streak = 0
        for day in reversed(sorted(usac.keys())):
            try:
                if usac[day][str(member.id)]["messages"] >= 30:
                    streak += 1
                else:
                    break
            except:
                break

        if streak > 0:
            addition = f"\nDu hast seit **{streak} Tagen** jeden Tag über 30 Nachrichten geschrieben. <:stonks:913416125201670154>"
            additionf = f"\n**{member.display_name}** hat seit **{streak} Tagen** jeden Tag über 30 Nachrichten geschrieben. <:stonks:913416125201670154>"
        else:
            addition = ""
            additionf = ""

        if member == ctx.author:
            if messages >= 30:
                await ctx.respond(f"<:DailyReward:990693035543265290> __**Tägliche Belohnung**__ <:DailyReward:990693035543265290>\n\n> Du hast heute **{messages}`/`30** *gezählte* Nachrichten in <#{achannel}> geschrieben!\n> \n> Du hast dein tägliches mindestziel ***erreicht***! <:minecraft_cake:989670170928762921>{addition}")
            else:
                await ctx.respond(f"<:DailyReward:990693035543265290> __**Tägliche Belohnung**__ <:DailyReward:990693035543265290>\n\n> Du hast heute **{messages}`/`30** *gezählte* Nachrichten in <#{achannel}> geschrieben!\n> \n> Du hast dein tägliches mindestziel __noch nicht__ erreicht! <a:rainbowbunny:985294876105130025>")
        else:
            if messages >= 30:
                await ctx.respond(f"<:DailyReward:990693035543265290> __**Tägliche Belohnung**__ <:DailyReward:990693035543265290>\n\n> {member.display_name} hat heute **{messages}`/`30** *gezählte* Nachrichten in <#{achannel}> geschrieben!\n> \n> {member.display_name} hat das tägliche mindestziel ***erreicht***! <:minecraft_cake:989670170928762921>{additionf}")
            else:
                await ctx.respond(f"<:DailyReward:990693035543265290> __**Tägliche Belohnung**__ <:DailyReward:990693035543265290>\n\n> {member.display_name} hat heute **{messages}`/`30** *gezählte* Nachrichten in <#{achannel}> geschrieben!\n> \n> {member.display_name} hat das tägliche mindestziel __noch nicht__ erreicht! <a:rainbowbunny:985294876105130025>")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and int(message.channel.id) == int(achannel):
            if not "<@443769343138856961>" in message.content and not "<@!443769343138856961>" in message.content:
                njsonname = {datetime.datetime.now().strftime("%y%m%d")}
                for i in njsonname:
                    njsonname = i
                    break
                guild = self.client.get_guild(guildid)
                member = guild.get_member(message.author.id)
                time = calendar.timegm(datetime.datetime.utcnow().utctimetuple()) - 5
                ousac = await get_user_activity()
                await update_user_activity(member)
                usac = await get_user_activity()
                

                #print("gmsg")
                try:
                    timestamp = ousac[njsonname][str(member.id)]["timestamp"]
                    #print("gmsg1 T")
                except:
                    timestamp = 0
                    #print("gmsg1 F")
                #print("gmsg2")
                #print(str(time))
                #print(timestamp)
                if int(timestamp) <= int(time):

                    #print("gmsg3 T")
                    #try:
                    if True:

                        if usac[njsonname][str(member.id)]["messages"] >= 30:
                            #print("check1")

                            streak = 0
                            for day in reversed(sorted(usac.keys())):
                                try:
                                    if usac[day][str(member.id)]["messages"] >= 30:
                                        streak += 1
                                    else:
                                        break
                                except:
                                    break

                            #print(streak)

                            if streak > 98:
                                role = guild.get_role(992023763736596510)
                                await member.add_roles(role) #  15. Rolle
                            elif streak >= 91:
                                role = guild.get_role(992023763736596510)
                                await member.add_roles(role) #  14. Rolle
                            elif streak >= 84:
                                role = guild.get_role(992023768220311564)
                                await member.add_roles(role) #  13. Rolle
                            elif streak >= 77:
                                role = guild.get_role(992023759722651718)
                                await member.add_roles(role) #  12. Rolle
                            elif streak >= 70:
                                role = guild.get_role(992023735706079332)
                                await member.add_roles(role) #  11. Rolle
                            elif streak >= 63:
                                role = guild.get_role(992023730723246231)
                                await member.add_roles(role) #  10. Rolle
                            elif streak >= 56:
                                role = guild.get_role(992023747622076486)
                                await member.add_roles(role) #  9. Rolle
                            elif streak >= 49:
                                role = guild.get_role(992023743738155038)
                                await member.add_roles(role) #  8. Rolle
                            elif streak >= 42:
                                role = guild.get_role(992023739946512424)
                                await member.add_roles(role) #  7. Rolle
                            elif streak >= 35:
                                role = guild.get_role(992023755444465685)
                                await member.add_roles(role) #  6. Rolle
                            elif streak >= 28:
                                role = guild.get_role(992023751615074334)
                                await member.add_roles(role) #  5. Rolle
                            elif streak >= 21:
                                role = guild.get_role(992023772058095677)
                                await member.add_roles(role) #  4. Rolle
                            elif streak >= 14:
                                role = guild.get_role(992023776323710988)
                                await member.add_roles(role) #  3. Rolle
                            elif streak >= 7:
                                role = guild.get_role(992023780694183967)
                                await member.add_roles(role) #  2. Rolle
                            elif streak >= 3:
                                role = guild.get_role(992023711479775332)
                                await member.add_roles(role) #  1. Rolle
                            else:
                                #print("arole0")
                                role = guild.get_role(990650138273923113)
                                await member.add_roles(role) #  0. Rolle
                    #except:
                    #    pass


                    """if not role1 in member.roles:
                        usac = await get_user_activity()
                        if usac[njsonname][str(member.id)]["messages"] >= 30:
                            #if usac[str(int(njsonname) - 1 )][str(member.id)]["messages"] >= 30 and usac[str(int(njsonname) - 2 )][str(member.id)]["messages"] >= 30:"""

                else:
                    return
            else:
                await message.channel.send("Ping den doch nicht <:sip:985295434635415622>", reference=message)

#    @commands.Cog.listener()
#    async def on_ready(self):
#        self.before_set_activity_zero.start(self)

    @tasks.loop(hours=24)
    async def set_activity_zero(self):
        njsonname = {datetime.datetime.now().strftime("%y%m%d")}
        for i in njsonname:
            njsonname = i
            break
        #print(str(njsonname))
        njsonname = int(njsonname) #+ 1
        njsonname = str(njsonname)
        with open(f"json_files/activities/activity.json",'r') as f:
            content = json.load(f)
        #try:
        if True:
            #print(content)
            #print(type(content))
            try:
                tmp = content[njsonname]
            except:
                content[njsonname] = {}

        #except:
        #    print("Brok?")#content[njsonname] = {"0": {"messages": 0, "timestamp": 0}}
        #print(content)
        #print("EEEEEE")
        with open(f'json_files/activities/activity.json', 'w', encoding='utf-8') as f:
            json.dump(content, f)
        guild = self.client.get_guild(guildid)
        for roleid in [990650138273923113, 992023711479775332, 992023780694183967, 992023776323710988, 992023772058095677, 992023751615074334, 992023755444465685, 992023739946512424, 992023743738155038, 992023747622076486, 992023730723246231, 992023735706079332, 992023759722651718, 992023768220311564, 992023763736596510]:
            role = guild.get_role(roleid)
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