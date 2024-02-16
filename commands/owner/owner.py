import discord
import os
from discord.ext import commands
import typing
from tabulate import tabulate
from database import *
class Owner(commands.Cog):

    def __init__(self , client):
        self.client = client

    @commands.hybrid_command()
    @commands.is_owner()
    async def setactivity(self , ctx , activity : typing.Optional[typing.Literal['unknown', 'playing' , 'streaming' , 'listening' , 'watching' , 'custom' , 'competing' ]] , status : typing.Optional[typing.Literal['online' , 'offline' , 'dnd' , 'idle']] , emoji : discord.PartialEmoji = None , * ,  input : str ):
        status_set = None
        activity_set = None
        if activity == "unknown" :
            activity_set = discord.ActivityType.unknown
        elif activity == "playing" :
            activity_set = discord.ActivityType.playing
        elif activity == "streaming" :
            activity_set = discord.ActivityType.streaming
        elif activity == "listening" :
            activity_set = discord.ActivityType.listening
        elif activity == "watching" :
            activity_set = discord.ActivityType.watching
        elif activity == "custom" :
            activity_set = discord.ActivityType.custom
        elif activity == "competing" :
            activity_set = discord.ActivityType.competing
        
        if status == 'online' :
            status_set = discord.Status.online
        elif status == 'offline' :
            status_set = discord.Status.offline
        elif status == 'idle' :
            status_set = discord.Status.idle
        elif status == 'dnd' :
            status_set = discord.Status.dnd
        
        await self.client.change_presence(status = status_set , activity = discord.Activity( name = input, emoji=emoji, type = activity_set) )
        embed = discord.Embed(color= 0x2b2c31 , description = "Bot Presence Updated" )
        await ctx.send(embed = embed)

    @commands.hybrid_command()
    @commands.is_owner()
    async def eval(self, ctx, type: typing.Optional[bool] = False, *, input: str):
        if type:
            data = await eval(input)
        else:
            data = eval(input)
        data = str(data)
        if input.find("config") is not -1:
            data = "-1"
        # self.lis[0] = data
            
        max_size = 1000
        if len(str(data)) > max_size:
            data_list = [data[i:i + max_size] for i in range(0, len(data), max_size)]
        else:
            data_list = [data]
        embeds = []
        embeds.append(bembed().add_field(name="**Input**", value=f"```py\n{input}```"))
        i = 1
        edited_first_embed = False

        for data in data_list:
            if not edited_first_embed:
                embeds[0].add_field(name=f"Output {i}", value=f"```py\n{data}```", inline=False)
                edited_first_embed = True
                i += 1
            else:
                print(i)
                embeds.append(bembed().add_field(name=f"**Output {i}**", value=f"```py\n{data}```"))
                i += 1
        await ctx.send(embeds=embeds)

        # embed.add_field(name= "eval list" , value= f"```py\n{self.lis}```" , inline = False )

 
    @eval.error
    async def error123(self , ctx , error):
        await ctx.author.send(error)

    @commands.command()
    @commands.is_owner() 
    async def files(self , ctx):
        files = [ ]
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                files.append(f'{filename[:-3]}')
            elif not filename.endswith('.py'):
                filenametemp =  filename
                for filename in os.listdir(f'./commands/{filenametemp}'):
                    if filename.endswith('.py'):
                        files.append(f'{filenametemp}.{filename[:-3]}')
        await ctx.send(embed = discord.Embed(color= 0x2b2c31, description= "\n".join(files) ))

    @commands.command()
    @commands.is_owner()
    async def disableall(self , ctx , command):
        command = self.client.get_command(command)
        command.update(enabled=False)
        await ctx.send(embed = discord.Embed(color= 0x2b2c31 , description=f'Disabled {command.name}')) 

    @commands.command()
    @commands.is_owner()
    async def enableall(self , ctx , command):
        command = self.client.get_command(command)
        command.update(enabled=False)
        await ctx.send( embed = discord.Embed(color= 0x2b2c31 , description=f'Enabled {command.name}' )) 

    async def load_fun(self , extension):
        await self.client.load_extension(f'commands.{extension}')


    @commands.command()
    @commands.is_owner()
    async def load(self , ctx , extension):
        
        file = None
        
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                if extension.lower() == f'{filename[:-3]}'.lower() :
                    file = f'{filename[:-3]}'
                    break
            elif not filename.endswith('.py'):
                filenametemp =  filename
                for filename in os.listdir(f'./commands/{filenametemp}'):
                    if filename.endswith('.py'):
                        if extension.lower() == f'{filename[:-3]}'.lower() or extension.lower() == f'{filenametemp}.{filename[:-3]}'.lower() :
                            file = f'{filenametemp}.{filename[:-3]}'
                            break
        if file :                       
            await self.load_fun(file)
            await ctx.send( embed = discord.Embed(color= 0x2b2c31 , description=f'**{file}** Loaded' )) 


    async def unload_fun(self , extension):
        await self.client.unload_extension(f'commands.{extension}')

    @load.error
    async def reload_error(self ,ctx , error):
        await ctx.author.send(f"{error}")

    @commands.command()
    @commands.is_owner()
    async def unload(self , ctx , extension):
        
        file = None
        
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                if extension.lower() == f'{filename[:-3]}'.lower() :
                    file = f'{filename[:-3]}'
                    break
            elif not filename.endswith('.py'):
                filenametemp =  filename
                for filename in os.listdir(f'./commands/{filenametemp}'):
                    if filename.endswith('.py'):
                        if extension.lower() == f'{filename[:-3]}'.lower() or extension.lower() == f'{filenametemp}.{filename[:-3]}'.lower() :
                            file = f'{filenametemp}.{filename[:-3]}'
                            break
        if file :                       
            await self.unload_fun(file)
            await ctx.send( embed = discord.Embed(color= 0x2b2c31 , description=f'**{file}** Loaded' )) 

    async def reload_fun(self , extension):
        await self.client.reload_extension(f'commands.{extension}')


    @commands.command()
    @commands.is_owner()
    async def reload(self , ctx , extension):
        file = None
        
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                if extension.lower() == f'{filename[:-3]}'.lower() :
                    file = f'{filename[:-3]}'
                    break
            elif not filename.endswith('.py'):
                filenametemp =  filename
                for filename in os.listdir(f'./commands/{filenametemp}'):
                    if filename.endswith('.py'):
                        if extension.lower() == f'{filename[:-3]}'.lower() or extension.lower() == f'{filenametemp}.{filename[:-3]}'.lower() :
                            file = f'{filenametemp}.{filename[:-3]}'
                            break
        if file :                       
            await self.reload_fun(file)
            await ctx.send( embed = discord.Embed(color= 0x2b2c31 , description=f'**{file}** Loaded' )) 

    @reload.error
    async def reload_error(self ,ctx , error):
        await ctx.author.send(f"{error}")

    @commands.command()
    @commands.is_owner()
    async def getguild(self , ctx , guild : discord.Guild) :
        invite = " "
        if guild.vanity_url :
            invite =  guild.vanity_url   
        else :
            try:
                lis = await guild.invites()
                invite = lis[0]
            except :
                try :
                    invite = str(await guild.channels[0].create_invite())
                except :
                    pass
        embed = discord.Embed(color= 0x2b2c31 , description= f"Name : {guild.name} ({guild.id})\nOwner : {guild.owner} ({guild.owner.id})\nMembers : {guild.member_count}\nInvite : {invite}")

        embed.set_thumbnail(url = guild.icon)
        embed.add_field(name="Permissions" , value= " ,".join([str(perm) for perm , value in guild.me.guild_permissions]))
        await ctx.send(embed = embed)
    
    @getguild.error
    async def status_error(self ,ctx , error):
        await ctx.author.send(f"{error}")

    @commands.command()
    @commands.is_owner()
    async def status(self , ctx , leave : bool = False):

        total_users = 0

        data = [ ]

        for guild in self.client.guilds :
            invite = " "
            if guild.vanity_url :
                invite =  guild.vanity_url   
            else :
                try:
                    lis = await guild.invites()
                    invite = lis[0]
                except :
                    try :
                        invite = str(await guild.channels[0].create_invite())
                    except :
                        pass
            
            data.append([ f"{guild.name[:17]} ({guild.id})" , f"{guild.owner.name[:17]} ({guild.owner_id})" , f"{guild.member_count:,}" , invite , (guild.me.guild_permissions).value ]) #= dis + f"{guild.name} , {guild.id} - {invite} , {guild.owner} {guild.owner_id}\n"
            total_users += guild.member_count

        table_str = tabulate(data, headers=[ 'Name', 'Owner' , "Members" , "Invite" , "Permissions"])
       
        txt = open("test.txt" , "w")
        new_file = txt.write(table_str)
        txt.close()
        file = discord.File( "test.txt" , filename= f"{self.client.user.name}.txt"   )
        await ctx.send( f"Total Number Of Guilds : {len(self.client.guilds):,}\nTotal Number Of Users : {total_users:,}" , file = file)

    @status.error
    async def status_error(self ,ctx , error):
        await ctx.author.send(f"{error}")

    @commands.command()
    @commands.is_owner()
    async def leaveguild(self , ctx , *guilds : discord.Guild) :
        await ctx.send(f'''leaving guild(s) **{' ,'.join([ str(f"**{guild.name} ({guild.id})**") for guild in guilds  ])}** type YES to continue....''')

        def check(m):
            return m.content == 'YES' and m.author == ctx.author

        msg = await self.client.wait_for('message', check=check , timeout= 10)
        
        for guild in guilds :
            await guild.leave()
        
        await ctx.author.send("done")


    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
      self , ctx, guilds: commands.Greedy[discord.Object], spec: typing.Optional[typing.Literal["~", "*", "^"]] = None) -> None:
      if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

      ret = 0
      for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

      await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @sync.error
    async def unload_error(self ,ctx , error):
        await ctx.author.send(f"owner only command , {error}")

    @commands.command(aliases = ['set_thumb', 'setthumb'])
    @commands.is_owner()
    async def set_embed_thumb(self, ctx, url : str = None):
        if not url:
            client.embed_thumbnail = None
            await ctx.reply(embed=bembed("Thumbnail has been reset.", discord.Color.brand_green()))
        elif url.startswith('http://'):
            client.embed_thumbnail = url
        else:
            ctx.author.send("URL must start with `http://`")
            
    @set_embed_thumb.error
    async def embed_error(self, ctx, error):
        await ctx.author.send(error)



async def setup(client):
   await client.add_cog(Owner(client))        