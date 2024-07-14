import discord
from discord.ext import commands
from database import client
from utils import bembed
import time
import datetime
from dotenv import load_dotenv
import os

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    # user = client.get_user(591011843552837655)
    # await user.send(f"{client.user} is Online Now")

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def ping(ctx):
    ping = round(client.latency * 1000 , ndigits=2)
    time1 = time.time()
    x = await client.db.execute("SELECT 1")
    time2 = time.time()
    db_ping = round((time2 - time1) * 1000 , ndigits=2)
    embed = bembed("", discord.Color.blue())
    embed.title = "**__BOT STATS__**"
    embed.url = "https://discord.com/oauth2/authorize?client_id=1165310965710082099&permissions=288706128&scope=bot+applications.commands"
    embed.set_footer(text=f"Use /bug to report a bug.")
    embed.timestamp  = datetime.now()
    embed.add_field(name="**Bot Ping**", value= f"<:goodconnection:1207146803582206083>**{ping}ms**")
    embed.add_field(name="**Database Ping**",value=f"<:goodconnection:1207146803582206083>**{db_ping}ms**")
    await ctx.reply(embed=embed)

load_dotenv()
client.run(os.environ.get("TOKEN"))