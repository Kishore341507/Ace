from discord.ext import commands, tasks
from database import client

class Guild(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.load_guilds.start()

    @tasks.loop( seconds=10 , count=1)
    async def load_guilds(self):
        for guild in self.client.guilds :
            if guild.id not in self.client.data :
                try :
                    await self.client.db.execute('INSERT INTO guilds(id) VALUES ($1)' , guild.id)
                except Exception as e :
                    pass
                finally :
                    guild_data = await self.client.db.fetchrow('SELECT * FROM guilds WHERE id = $1' , guild.id)
                    client.data[guild.id] = dict(guild_data)
    
    @load_guilds.before_loop
    async def before_load_guilds(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_guild_join(self ,  guild):  
        try :
            await self.client.db.execute('INSERT INTO guilds(id) VALUES ($1)' , guild.id)
            guild_data = await self.client.db.fetchrow('SELECT * FROM guilds WHERE id = $1' , guild.id)
            print(1)
        except Exception as e:
            print(e)
            pass
        finally :
            guild_data = await self.client.db.fetchrow('SELECT * FROM guilds WHERE id = $1' , guild.id)
            client.data[guild.id] = dict(guild_data)         

async def setup(client):
    await client.add_cog(Guild(client))
        