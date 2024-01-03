from discord.ext import commands
import asyncio
from database import *
import time
from dotenv import load_dotenv
import os

@client.event
async def on_ready():
    print(f'bot logged in named : {client.user}')
    user = client.get_user(591011843552837655)
    await user.send(f"{client.user} is Online Now ")


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def ping(ctx):
    ping = round(client.latency * 1000 , ndigits=2)
    time1 = time.time()
    x = await client.db.execute("SELECT 1")
    time2 = time.time()
    db_ping = round( (time2 - time1) * 1000 , ndigits=2)
    await ctx.reply(embed = bembed(f'Bot : `{ping}ms`\nDatabase : `{db_ping}ms`'))

async def load():

    #load Files 
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            await client.load_extension( f'commands.{filename[:-3]}')
        elif not filename.endswith('.py'):
            filenametemp =  filename
            for filename in os.listdir(f'./commands/{filenametemp}'):
                if filename.endswith('.py'):
                   await client.load_extension(f'commands.{filenametemp}.{filename[:-3]}') 

asyncio.run(load())

load_dotenv()
client.run(os.environ.get("TOKEN"))
