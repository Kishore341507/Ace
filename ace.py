from discord.ext import commands
import asyncio      
from database import *
import time
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

@client.event
async def on_ready():
    print(f'bot logged in named : {client.user}')
    user = client.get_user(591011843552837655)
    client.start_time = datetime.now()
    await user.send(f"{client.user} is Online Now")

def seconds_to_dhms(seconds):
    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def ping(ctx):
    ping = round(client.latency * 1000 , ndigits=2)
    time1 = time.time()
    x = await client.db.execute("SELECT 1")
    time2 = time.time()
    db_ping = round((time2 - time1) * 1000 , ndigits=2)
    embed = bembed("")
    embed.set_author(name=client.user.name, icon_url=client.user.avatar)
    embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.display_avatar)
    embed.timestamp  = datetime.now()
    embed.add_field(name="**Bot Ping**", value= f"`{ping}ms`")
    embed.add_field(name="**Database Ping**",value=f"`{db_ping}ms`")
    if ctx.author.id in [799908382421024808, 591011843552837655] and ctx.guild.id == 995100985494089789:
        elpased_time = (datetime.now() - client.start_time).total_seconds()
        uptime_string = seconds_to_dhms(elpased_time)
        embed.add_field(name="**Uptime** ",value=f"`{uptime_string}`")
    await ctx.reply(embed=embed)
    #await ctx.reply(embed = bembed(f'Bot : `{ping}ms`\nDatabase : `{db_ping}ms`\nUptime: `{uptime_string}`'))


load_dotenv()
client.run(os.environ.get("TOKEN"))
