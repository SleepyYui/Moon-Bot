
from datetime import datetime, timedelta
from platform import architecture, python_version
from time import time
import cpuinfo
from discord import Embed, client
from discord.ext import commands
from psutil import Process, virtual_memory, cpu_percent
from discord import __version__ as discord_version


class botinfo(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="botinfo",  description="Zeigt Infos über den Bot.")
    async def show_bot_stats(self, ctx):
        embed = Embed(title="Bot Info", colour=ctx.author.colour, timestamp=datetime.now())
        embed.set_thumbnail(url=self.client.user.avatar)

        proc = Process()
        with proc.oneshot():
            uptime = timedelta(seconds=time()-proc.create_time())
            cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
            mem_total = virtual_memory().total / (1024**2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)
            #mem_usage = int(str(mem_usage).split(".")[0]) same Value???
            processor = cpuinfo.get_cpu_info()['brand_raw']
            cpuusage = cpu_percent()
            #cputype = cpuinfo.arch

        memusage = f"{mem_usage:,.3f}"
        memusage = int(memusage.split(".")[0])
        memtotal = str(f"{mem_total:,.0f}")
        memotoal = int(memtotal.replace(",",""))

        cputime = str(cpu_time)
        lencputime = len(cputime)
        cputime = cputime[:lencputime - 4] + "s"
        cputime = cputime.split(":")[2]

        uptime = str(uptime)
        lenuptime = len(uptime)
        uptime = uptime.split(".")[0]# + " HH/MM/SS"

        delta_uptime =  datetime.now() - self.client.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        fields = [
            ("Bot Version:", "0.2.0", True),
            ("Discord-API Version:", python_version(), True),
            ("Py-Cord Version:", discord_version, False),
            ("Uptime:", f"Der Bot ist online seit **{days} Tagen**, **{hours} Stunden**, **{minutes} Minuten** und **{seconds} Sekunden**", False),
            ("Ping:", f'Pong\nLatenz: **{self.client.latency*1000:,.0f}ms**', False),
            ("CPU Modell:", processor, False),
            ("CPU Benuzung:", f"{cpuusage}%", True),
            ("CPU Timedelta:", cputime, True),
            ("Ram Benutzung", f"{memusage} MiB von {memotoal} MiB ({mem_of_total:.0f}%):", False),
            #("Release-Github-Repo:", "https://github.com/YES-German/PC_Creator_2", False),
            #("Testing-Github-Repo:", "https://github.com/SleepyYui/PCC3", False),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(botinfo(bot))