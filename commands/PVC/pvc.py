import discord
from discord.ext import commands , tasks
from discord.ext.commands import BucketType, cooldown
import re
import typing
import math
from database import client
from utils import bembed, open_account, pvc_coin, ConfirmView

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
                        if not bal or bal['pvc'] < math.ceil(int(client.data[pvc['guild_id']]["rate"] * (1/3600) * (120 - pvc['duration'] ))):
                            pass
                        else :
                            await client.db.execute('UPDATE pvcs SET duration = 120 WHERE id = $1' , pvc['id'])
                            await client.db.execute('UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3 ' , ( math.ceil(client.data[pvc['guild_id']]["rate"] * (1/3600) * (120 - pvc['duration'] )) ), pvc['id'] , pvc['guild_id'] )
                            continue
                    try :
                        await client.get_guild(pvc['guild_id']).get_channel(pvc['vcid']).delete()
                        await client.db.execute('DELETE FROM pvcs WHERE  vcid = $1' , pvc['vcid'])
                    except :
                        pass  
                else:
                    await client.db.execute('DELETE FROM pvcs WHERE  vcid = $1' , pvc['vcid'])

        if client.user.id == 1329511720284196915 :
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

                view = ConfirmView(member) 
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
            
            view = ConfirmView(member)
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

                if client.data[member.guild.id]['pvc_perms'] :
                    for role in client.data[member.guild.id]['pvc_perms'] :
                        if member.guild.get_role(int(role)) :
                            overwrites[member.guild.get_role(int(role))] = discord.PermissionOverwrite.from_pair( discord.Permissions( client.data[member.guild.id]['pvc_perms'][role]['allow']) , discord.Permissions( client.data[member.guild.id]['pvc_perms'][role]['deny']) )

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

                PVC = await member.guild.create_voice_channel(f"{member.name}'s Pvc" ,  category = discord.Object(pvc_category) if pvc_category else None , overwrites=overwrites)
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


async def setup(client):
    await client.add_cog(PVC(client))
