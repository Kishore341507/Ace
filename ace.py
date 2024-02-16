from discord.ext import commands
import asyncio      
from database import *
import time
from dotenv import load_dotenv
import os
from datetime import datetime

@client.event
async def on_ready():
    client.start_time = datetime.now()
    client.embed_thumbnail = None
    print("Freezing accounts")
    for guild in client.guilds:
        member_ids = []
        async for member in guild.fetch_members():
            member_ids.append(member.id)
        result = await client.db.fetch("SELECT id FROM users WHERE guild_id = $1 AND frozen = False", guild.id)
        user_ids = [row[0] for row in result]
        left_users = list(set(user_ids) - set(member_ids))
        if len(left_users) > 0:
            for user in left_users:
                await client.db.execute("UPDATE users SET frozen = $1 WHERE id = $2 and guild_id = $3", True, user, guild.id)
    print(f'bot logged in named : {client.user}')
    user = client.get_user(591011843552837655)
    # await user.send(f"{client.user} is Online Now")

@client.event
async def on_member_leave(member):
    try:
        await client.db.execute("UPDATE TABLE users SET frozen = True WHERE id = $1", member.id)
    except:
        pass

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
    def get_connection_emoji(ping):
        if ping <= 199:
            return "<:goodconnection:1207146803582206083>"
        elif ping > 199 and ping <= 499:
            return "<:normalconnection:1207146802411741225>"
        elif ping > 499 and ping <= 999:
            return "<:lowconnection:1207146800998514719>"
        else:
            return "<:badconnection:1207146798674878534>"

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
    embed.add_field(name="**Bot Ping**", value= f"{get_connection_emoji(ping)}**{ping}ms**")
    embed.add_field(name="**Database Ping**",value=f"{get_connection_emoji(ping)}**{db_ping}ms**")
    if ctx.author.id in [799908382421024808, 591011843552837655] and ctx.guild.id == 995100985494089789:
        elpased_time = (datetime.now() - client.start_time).total_seconds()
        uptime_string = seconds_to_dhms(elpased_time)
        embed.add_field(name="**Uptime** ",value=f"<:timer_:1207146799970652221>**{uptime_string}**")
    await ctx.reply(embed=embed)
    #await ctx.reply(embed = bembed(f'Bot : `{ping}ms`\nDatabase : `{db_ping}ms`\nUptime: `{uptime_string}`'))


load_dotenv()
client.run(os.environ.get("TOKEN"))
