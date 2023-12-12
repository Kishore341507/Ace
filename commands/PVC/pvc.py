import discord
from discord.ext import commands , tasks
import asyncio
from database import *
from discord.ext.commands import BucketType, cooldown
from discord.ui import Button , View
from datetime import datetime
import re
import typing

class PvcButton(discord.ui.Button['pvcview']):
    def __init__(self, y: int , label : str , custom_id : str):
        if y == 0 :
            st = discord.ButtonStyle.green
        elif y == 1 :
                st = discord.ButtonStyle.gray    
        elif y == 2 :            
                st = discord.ButtonStyle.blurple   
        super().__init__(style=st , label=label,custom_id= custom_id,  row=y)
 

    async def callback(self, interaction: discord.Interaction):
       assert self.view is not None
       view: pvcview = self.view
       x = int(self.custom_id)
       y = self.row
       economy = db[f"{interaction.guild.id}"]
       rate = ( await economy.find_one({"category": "pvc"}))["rate"] 
       status = (await economy.find_one({"category": "pvc"}))["status"] 

       if status is None :
            await interaction.response.send_message("pvc is disable is this server" , ephemeral = True)
            return

       if y == 0 :
        guild = interaction.guild
        user = interaction.user 
        overwrites = {
        guild.me : discord.PermissionOverwrite(view_channel= True , connect = True , manage_channels = True  , manage_permissions = True  ) ,   
        guild.default_role: discord.PermissionOverwrite(connect=False) ,
        discord.Object(user.id): discord.PermissionOverwrite(connect=True , manage_channels = True , view_channel = True)
        }
        bal = await economy.find_one({'id' : user.id})
        info = await economy.find_one( {"info_id" : user.id})

        if info != None:
            if interaction.guild.get_channel(info["vcid"]) is not None:
               await interaction.response.send_message("you already have a pvc !!" , ephemeral = True)
               return
            else :
               await economy.delete_many({"info_id" : interaction.user.id })
               pass

        if bal['pvc'] >= int((x*3600)* rate):
            #create vc 
                pvc_category = (await economy.find_one({"category": "pvc"}))["pvc_category"]
                await interaction.response.edit_message(content=f"Click to create PVC , Last PVC Created by {user.mention}")
                PVC = await guild.create_voice_channel(f"｜{user.name}'s Pvc" , position = 0 ,  category = discord.Object(pvc_category) , overwrites=overwrites)
                await economy.update_one({"id" : user.id } , {"$inc": {"pvc" : -(int((x*3600)* rate))}})
                await economy.insert_one({"info_id" : user.id , "info_time" : x*60 , "vcid" : PVC.id})
                await interaction.followup.send(f"{user} your vc created named {PVC.mention} for `{x}Hr` , enjoy!" , ephemeral= True) 

        else:
            await interaction.response.send_message(f"not enough pvc coins you need {int(({x}*3600)* rate)} pvc coins" , ephemeral=True)
       elif y == 1 :
        x = int(self.custom_id) - 3
        guild = interaction.guild
        user = interaction.user 
        bal = await economy.find_one({'id' : user.id})
        info = await economy.find_one( {"info_id" : user.id})
        if info == None:
            await interaction.response.send_message("You dont have PVC , create with command green buttons" , ephemeral=True)
            return
        elif bal['pvc'] >= int((x*3600)*rate): 
            await interaction.response.edit_message(content=f"Click to create PVC , Last PVC Extended by {user.mention}") 
            await economy.update_one({"info_id" : user.id } , {"$inc": {"info_time" : + (x*60) }}) 
            await economy.update_one({"id" : user.id } , {"$inc": {"pvc" : -(int((x*3600)*rate))}})
            time = (await economy.find_one({"info_id" : user.id }))["info_time"] 
            await interaction.followup.send(f"Time inc. now you have more then {time}min" , ephemeral=True)
        else:
            await interaction.response.send_message(f"not enough pvc you need {int((x*3600)*rate)} pvc's" , ephemeral=True) 
    #    elif y == 2 :
    #     guild = interaction.guild
    #     user = interaction.user 
    #     bal = await economy.find_one({'id' : user.id})
    #     info = await economy.find_one( {"info_id" : user.id})
    #     if info == None:
    #         await interaction.response.send_message("You dont have PVC , create with command green buttons" , ephemeral=True)
    #         return
    #     vc =  guild.get_channel(info["vcid"])
    #     if vc.permissions_for( guild.default_role).view_channel == True  :
    #         await vc.set_permissions( guild.default_role , view_channel = False , connect = False )
    #         await interaction.response.send_message("Vc is hidden from everyone now !" , ephemeral=True)
    #     else :
    #         await vc.set_permissions( guild.default_role , view_channel = True , connect = False )
    #         await interaction.response.send_message(f"Vc is back to normal !" , ephemeral=True)

class pvcview(discord.ui.View):
    def __init__(self , timeout):
        super().__init__(timeout= timeout)
        self.add_item(PvcButton(0 , "Create 1Hr" , "1"))
        self.add_item(PvcButton(0 , "Create 2Hr" , "2"))
        self.add_item(PvcButton(0 , "Create 3Hr" , "3"))
        self.add_item(PvcButton(1 , "Extend 1Hr" , "4"))
        self.add_item(PvcButton(1 , "Extend 2Hr" , "5"))
        self.add_item(PvcButton(1 , "Extend 3Hr" , "6"))
        # self.add_item(PvcButton(2 , "Hide/Unhide" , "7"))

class DurationConverter(commands.Converter):
    async def convert(self ,  ctx , argument = '1h'):
        
        amount = argument[:-1]
        unit = argument[-1]

        if amount.isdigit() and unit in [ 'h']:
            return (int(amount),unit)

time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        matches = time_regex.findall(argument.lower())
        time = 0
        for v, k in matches:
            try:
                time = time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))       
        return time , argument


class PVC(commands.Cog):

    def __init__(self , client):
        self.client = client
        # self.pvc_loop.start()

    async def check_channel(ctx) ->bool : 
        return client.data[ctx.guild.id]['pvc_channel'] == ctx.channel.id or client.data[ctx.guild.id]['channels'] is None or len(client.data[ctx.guild.id]['channels']) == 0  or ctx.channel.id in client.data[ctx.guild.id]['channels'] 
    
    async def cog_load(self):
        self.pvc_loop.start()
    async def cog_unload(self):
        self.pvc_loop.cancel() 

    @tasks.loop( minutes= 2)
    async def pvc_loop(self):
        pvcs = await client.db.fetch('SELECT * FROM pvcs WHERE duration <= 0')
        for pvc in pvcs :
            if client.get_guild(pvc['guild_id']) :
                if client.get_guild(pvc['guild_id']).get_channel(pvc['vcid']) :
                    if pvc['auto'] and len(client.get_guild(pvc['guild_id']).get_channel(pvc['vcid']).members ) != 0 :
                        bal = await client.db.fetchrow('SELECT pvc FROM users WHERE id = $1 AND guild_id = $2' , pvc['id'] , pvc['guild_id'] )
                        if not bal or bal['pvc'] < (int(client.data[pvc['guild_id']]["rate"] * (1/3600) * (120 - pvc['duration'] )) + 1 ):
                            pass
                        else :
                            await client.db.execute('UPDATE pvcs SET duration = 120 WHERE id = $1' , pvc['id'])
                            await client.db.execute('UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3 ' , (int(client.data[pvc['guild_id']]["rate"] * (1/3600) * (120 - pvc['duration'] )) + 1 ), pvc['id'] , pvc['guild_id'] )
                            continue
                    try :
                        await client.get_guild(pvc['guild_id']).get_channel(pvc['vcid']).delete()
                        await client.db.execute('DELETE FROM pvcs WHERE  vcid = $1' , pvc['vcid'])
                    except :
                        pass  
                else:
                    await client.db.execute('DELETE FROM pvcs WHERE  vcid = $1' , pvc['vcid'])

        if client.user.id == 1010751603365650442 :
            await client.db.execute('UPDATE pvcs SET duration = duration - 120')

    async def create_pvc(self , member , channel , duration = None , auto =False , copy_channel = None ) :
        
        if duration and client.data[member.guild.id]['pvc_min'] > 0 and  duration[0] < (client.data[member.guild.id]['pvc_min'] * 3600) :
            await channel.send( embed = bembed(f"The time must be at least {client.data[member.guild.id]['pvc_min']} Hrs"))
            return None 
        
        if duration and client.data[member.guild.id]['pvc_max'] > 0 and  duration[0] > (client.data[member.guild.id]['pvc_max'] * 3600) :
            await channel.send( embed = bembed(f"The Maximum time of PVC you can create is {client.data[member.guild.id]['pvc_max']} Hrs"))
            return None 

        if duration and duration[0] < 120 :
            await channel.send( embed = bembed("The time must be at least 2min"))
            return None 


        if duration is None :
            duration = [120 , "2min"]
            payg = True

        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', member.id, member.guild.id)
        if bal is None:
            await open_account(member.guild.id, member.id)
            bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', member.id, member.guild.id)
        
        info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', member.id, member.guild.id)
        status = client.data[member.guild.id]["pvc"] 
        rate = client.data[member.guild.id]["rate"]

        if status is None :
            await channel.send( embed = bembed("PVC disable in this server"))
            return None

        if info != None and duration[0] > 120:
            if member.guild.get_channel(info["vcid"]) is not None and bal['pvc'] >= int( int(duration[0]/3600) * rate):

                if duration and client.data[member.guild.id]['pvc_max'] > 0 and  (duration[0] + info['duration']) > (client.data[member.guild.id]['pvc_max'] * 3600) :
                    await channel.send( embed = bembed(f"The Maximum time of PVC you can create is {client.data[member.guild.id]['pvc_max']} Hrs"))
                    return None 

                view = Confirm(member) 
                await channel.send( embed = bembed(f'Want To Extend Your PVC ? , This will charge you {pvc_coin(member.guild.id)[0]} **{ int( (duration[0]/3600) * rate) }** {pvc_coin(member.guild.id)[1]} !') , view = view)
                await view.wait()
                if view.value : 
                    await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3" , int((duration[0]/3600) * rate) , member.id , member.guild.id )
                    await client.db.execute("UPDATE pvcs SET duration = duration + $1 WHERE id = $2 AND guild_id = $3" , duration[0] , member.id , member.guild.id )
                    await channel.send( embed = bembed(f"{member} your vc Extened for `{duration[1]}` , See Info With pvcinfo Command!"))
                    return None
 
            elif member.guild.get_channel(info["vcid"]) is not None :
                await channel.send(embed = bembed(f"Not enough {pvc_coin(member.guild.id)[1]}'s you need {pvc_coin(member.guild.id)[0]}  {int( (duration[0]/3600) * rate)} {pvc_coin(member.guild.id)[1]}'s to extand")) 
                return None

            elif member.guild.get_channel(info["vcid"]) is None :
               await client.db.execute('DELETE FROM pvcs WHERE id = $1 AND guild_id = $2' , member.id, member.guild.id)
               await channel.send(embed = bembed("Opps! , your vc was deleted before time , you can create again with same procces after 10sec"))
               return None
        
        elif info != None :
            return member.guild.get_channel(info['vcid'])

        elif info is None and bal['pvc'] >= int( (duration[0]/3600) * rate):
            
            view = Confirm(member)
            if duration[0] != 120 :
                await channel.send( embed= bembed(f"This will charge you {pvc_coin(member.guild.id)[0]} **{ int( (duration[0]/3600) * rate) }** {pvc_coin(member.guild.id)[1]}'s !"), view = view)
                await view.wait()
            if view.value or duration[0] == 120 :
            #create vc 
                pvc_category = client.data[member.guild.id]["pvc_category"]

                overwrites = {
                member.guild.me : discord.PermissionOverwrite(view_channel= True , connect = True ) ,   
                member.guild.default_role: discord.PermissionOverwrite(connect=False , stream = True) ,
                member : discord.PermissionOverwrite(connect=True ,  view_channel = True)
                }

                if copy_channel and copy_channel.members != 0 :
                    for i , vc_member in enumerate(copy_channel.members , 1) :
                        if i > 10 :
                            break
                        else :
                            overwrites[vc_member] = discord.PermissionOverwrite(connect=True , view_channel = True)

                # bal = await self.client.db.fetchrow('SELECT friends FROM users WHERE id = $1 AND guild_id = $2 ', member.id, member.guild.id)
                if bal and bal['friends'] :
                    for friend in bal['friends'] :
                        if (member.guild.get_member(friend) and not member.guild.get_member(friend).bot ) and  member.guild.get_member(friend) not in overwrites :
                            overwrites[member.guild.get_member(friend)] = discord.PermissionOverwrite(connect=True ,  view_channel = True)

                PVC = await member.guild.create_voice_channel(f"{member.name}'s Pvc" ,  category = discord.Object(pvc_category) , overwrites=overwrites)
                try :  
                    await self.client.db.execute('INSERT INTO pvcs(id , guild_id ,vcid , duration , auto) VALUES ($1 , $2 ,$3 , $4 , $5)' , member.id , member.guild.id , PVC.id , duration[0] , auto )
                except :
                    await PVC.delete()
                    return
                await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3" , int((duration[0]/3600) * rate) , member.id , member.guild.id )
                if auto :
                    await channel.send( embed = bembed(f"{member} your vc created named {PVC.mention} on 🛺 PayAsPerYouGO mode, Manage With pvcinfo Command!"))   
                else :
                    await channel.send( embed = bembed(f"{member} your vc created named {PVC.mention} for `{duration[1]}` , Manage With pvcinfo Command!"))   
                return PVC
            else :
                await channel.send(embed = bembed("transetion cenceled"))   
                return None 
        elif duration[0] <= 120 :
            return None
        else:
            await channel.send( embed = bembed(f"Not Enough {pvc_coin(member.guild.id)[1]}'s you need {pvc_coin(member.guild.id)[0]} {int( int(duration[0]/3600) * rate)} {pvc_coin(member.guild.id)[1]}'s")) 
            return None



    @commands.Cog.listener()
    async def on_voice_state_update(self ,member, before, after):
        if after.channel and (client.data[member.guild.id]['pvc_vc'] and client.data[member.guild.id]['pvc_vc'] == after.channel.id) :
            PVC = await self.create_pvc( member , after.channel , auto = True )
            if PVC :
                await after.channel.send(member.mention)
                await member.move_to(PVC)
            else :
                # await after.channel.send(member.mention)
                await member.move_to(None)


        
    @commands.hybrid_command(aliases = ['create' , 'create-pvc' , 'pvc-create' , 'pvccreate' , 'createpvc' , 'epvc' , 'extend' , 'extendpvc' , 'pvcextend','extend-pvc' , 'pvc-extend'])
    @commands.guild_only()
    @cooldown(1, 10, BucketType.user)
    @commands.check(check_channel)
    async def pvc(self , ctx , duration : TimeConverter , copy_channel : typing.Optional[discord.VoiceChannel]  = None ):

        await self.create_pvc( member=  ctx.author , channel =  ctx.channel , duration = duration , copy_channel = copy_channel )

        # guild = ctx.guild
        # user = ctx.author 
        
        # if duration[0] < 3600 :
        #     return await ctx.send( embed = bembed("The time must be at least an hour"))
        
        # overwrites = {
        # guild.me : discord.PermissionOverwrite(view_channel= True , connect = True ) ,   
        # guild.default_role: discord.PermissionOverwrite(connect=False , stream = True) ,
        # discord.Object(ctx.author.id): discord.PermissionOverwrite(connect=True ,  view_channel = True)
        # }
        # bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        # if bal is None:
        #     await open_account(ctx.guild.id, ctx.author.id)
        #     bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        
        # info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        # status = client.data[guild.id]["pvc"] 
        # rate = client.data[guild.id]["rate"]
        
        # if status is None :
        #     await ctx.send( embed = bembed("PVC disable in this server"))
        #     return

        # if info != None:
        #     if ctx.guild.get_channel(info["vcid"]) is not None and bal['pvc'] >= int( int(duration[0]/3600) * rate):
        #         view = Confirm(ctx.author) 
        #         await ctx.send( embed = bembed(f'Want To Extand Your PVC ? , This will charge you **{ int( int(duration[0]/3600) * rate) }** pvc !') , view = view)
        #         await view.wait()
        #         if view.value : 
        #             await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3" , int( int(duration[0]/3600) * rate) , ctx.author.id , ctx.guild.id )
        #             await client.db.execute("UPDATE pvcs SET duration = duration + $1 WHERE id = $2 AND guild_id = $3" , duration[0] , ctx.author.id , ctx.guild.id )
        #             await ctx.reply( embed = bembed(f"{ctx.author} your vc Extaned for `{duration[1]}` , See Info With pvcinfo Command!"))

        #     elif ctx.guild.get_channel(info["vcid"]) is not None :
        #         await ctx.send(embed = bembed(f"Not enough pvc coins you need {int( int(duration[0]/3600) * rate)} pvc's to extand")) 

        #     elif ctx.guild.get_channel(info["vcid"]) is None :
        #        await client.db.execute('DELETE FROM pvcs WHERE id = $1 AND guild_id = $2' , ctx.author.id, ctx.guild.id)
        #        await ctx.send(embed = bembed("Opps! , your vc was deleted before time , you can create again with same command after 10sec"))
        #        return 
           
        # elif bal['pvc'] >= int( int(duration[0]/3600) * rate):

        #     view = Confirm(ctx.author)
        #     await ctx.send( embed= bembed(f'This will charge you **{ int( int(duration[0]/3600) * rate) }** pvc !'), view = view)
        #     await view.wait()
        #     if view.value :
        #     #create vc 
        #         pvc_category = client.data[ctx.guild.id]["pvc_category"]
        #         PVC = await guild.create_voice_channel(f"{ctx.author.name}'s Pvc" ,  category = discord.Object(pvc_category) , overwrites=overwrites)
        #         await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3" , int( int(duration[0]/3600) * rate) , ctx.author.id , ctx.guild.id )
        #         await self.client.db.execute('INSERT INTO pvcs(id , guild_id ,vcid , duration) VALUES ($1 , $2 ,$3 , $4)' , ctx.author.id , ctx.guild.id , PVC.id , duration[0] )
        #         await ctx.reply( embed = bembed(f"{ctx.author} your vc created named {PVC.mention} for `{duration[1]}` , Manage With pvcinfo Command!"))   
        #     else :
        #         await ctx.reply(embed = bembed("transetion cenceled"))    
        # else:
        #     await ctx.send( embed = bembed(f"not enough pvc coins you need {int( int(duration[0]/3600) * rate)} pvc's")) 

  
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.has_permissions(administrator =True)
    # async def pvcbuttons(self , ctx):
    #     view = pvcview(timeout=2592000)
    #     await ctx.send( "Click to create PVC" , view = view)
     
    # @pvcbuttons.error
    # async def pvc_error(self,ctx , error):
    #     if isinstance(error, commands.CheckFailure):
    #         return   
    #     else: 
    #         await ctx.send(f'use correctly {error}' )
    #         return

async def setup(client):
    await client.add_cog(PVC(client))