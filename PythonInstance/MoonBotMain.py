
#pip install -r requirements.txt

import discord
from discord.ext import commands
from datetime import datetime
from discord.ext.commands import CommandNotFound
import os
from discord.ext.commands import MemberNotFound
from discord.ext.commands import MissingPermissions
from decouple import config
import cogs.status_rewards.statusmain as statusmain
import cogs.activity_rewards.activitymain as activitymain
from datetime import timedelta
import asyncio

intents = discord.Intents().all()
client = commands.Bot(intents=intents)
client.remove_command('help')


@client.event
async def on_ready():
    print("Bot is online")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="auf Status & DMs"), status=discord.Status.online)
    client.start_time = datetime.now()
    statussnd = statusmain.statusmain(client)
    statussnd.check_roles.start()

    hour = 23
    minute = 59
    #await self.client.wait_until_ready()
    now = datetime.now()
    future = datetime(now.year, now.month, now.day, hour, minute)
    if now.hour >= hour and now.minute > minute:
        future += timedelta(days=1)
    print(f"set_activity_zero loop starting in {(future-now).seconds} seconds")
    await asyncio.sleep((future-now).seconds)
    activitynd = activitymain.activitymain(client)
    activitynd.set_activity_zero.start()

@client.event
async def on_command_error(ctx, error):

    send_help = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError)

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'Dieser Command ist im Cooldown bis in {round(error.retry_after, 2)} Sekunden')
    elif isinstance(error, CommandNotFound):
        return
    elif isinstance(error, MemberNotFound):
        await ctx.send("Dieses Mitglied existiert nicht")
        return
    elif isinstance(error, send_help):
        await ctx.send(f"Hey! Du hast einen Fehler gemacht.\n{error}", delete_after=10)
        return
    else:
        try:
            channel = client.get_channel(int(config('LOGS')))
        except:
            channel = client.get_channel(int(config('LOGS')))
        await channel.send(f"A command_error occured:\n{error}")
        return


@client.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)
        return
    else:
        try:
            channel = client.get_channel(int(config('LOGS')))
        except:
            channel = client.get_channel(int(config('LOGS')))
        await channel.send(f"A application_command_error occured:\n{error}")
        return

initial_extensions = []
for directory in os.listdir('./cogs'):
    if directory != '__pycache__' and directory != 'testing':
        for filename in os.listdir('./cogs/' + directory):
            #print(filename)
            if filename.endswith(".py"):
                if filename != 'importantfunctions.py':
                    initial_extensions.append("cogs." + directory + '.' + filename[:-3])
                    print(directory + "/" + filename[:-3] + ".py was loaded successfully")


if __name__ == '__main__':
    for extension in initial_extensions:
        client.load_extension(extension)


client.run(config('TOKEN'))