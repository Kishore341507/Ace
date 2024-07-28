import discord
from discord.ext import commands
import asyncpg
from dotenv import load_dotenv
import os
import json
from datetime import datetime


load_dotenv()

"""
# I need this for myself don't remove :PP: (Note from Ashborn)
async def run_queries(filename, connection):
    with open(filename, 'r') as file:
        queries = file.read()
    queries = queries.split(';')
    for query in queries:
        if query.strip():  # Skip empty queries
            await connection.execute(query)
"""

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        
        async def _setup_connection(con):
                    await con.set_type_codec('jsonb', schema='pg_catalog',
                                            encoder= json.dumps , decoder=json.loads)
        
        self.db = await asyncpg.create_pool(dsn= os.environ.get(f"DB") , init=_setup_connection )
        print("Successfully connected to Database!")
        # await run_queries('./migrations/V0_initial.sql', self.db)
        # await run_queries('./migrations/V1_alter_guild.sql', self.db)
        # await run_queries('./migrations/V3_alter_users.sql', self.db)
 
        guilds = await self.db.fetch("SELECT * FROM guilds")
        self.data = { guild['id'] : dict(guild) for guild in guilds }
        print("Loaded guild data!")
        #Load Cogs
        
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                await self.load_extension( f'commands.{filename[:-3]}')
            elif not filename.endswith('.py'):
                filenametemp =  filename
                for filename in os.listdir(f'./commands/{filenametemp}'):
                    if filename.endswith('.py'):
                        await self.load_extension(f'commands.{filenametemp}.{filename[:-3]}')
        print(f"Finished loading all the Cogs.")
        self.start_time = datetime.now()
        try:
            self.error_logging_ch = await self.fetch_channel(1209630548746706944)
        except discord.errors.Forbidden:
            await self.unload_extension('commands.owner.logging')

async def get_prefix(client , message):
    try :
        prefix = client.data[message.guild.id]['prefix']
        if not prefix :
            raise Exception
    except Exception:
        prefix = ","
    finally :
        return commands.when_mentioned_or(prefix)(client , message)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = MyBot(command_prefix= get_prefix , strip_after_prefix =True, case_insensitive=True, intents=intents , help_command= None)