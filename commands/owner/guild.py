from discord.ext import commands
from database import *

class Guild(commands.Cog):

    def __init__(self , client):
        self.client = client

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
        
    @commands.command()
    @commands.is_owner()
    async def loadguilds(self , ctx):
        for guild in client.guilds :
            if guild.id not in client.data :
                try :
                    await client.db.execute('INSERT INTO guilds(id) VALUES ($1)' , guild.id)
                except Exception as e :
                    pass
                finally :
                    guild_data = await self.client.db.fetchrow('SELECT * FROM guilds WHERE id = $1' , guild.id)
                    client.data[guild.id] = dict(guild_data) 
        await ctx.send("Done")
        

async def setup(client):
   await client.add_cog(Guild(client))         
        