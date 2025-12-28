import discord
from discord.ext import commands
import asyncio
from discord.ext.commands import BucketType, cooldown
from datetime import datetime
import typing
from database import client
from utils import bembed, check_perms, ConfirmView, pvc_coin

class SelectUer(discord.ui.View):
    def __init__(self , user = None , role = None):
        super().__init__()
        self.value = None
        self.user = user
        self.role = role
    
    @discord.ui.select( cls = discord.ui.UserSelect , placeholder = "Select A User" )
    async def selectuser(self, interaction , select) :
        if self.user and self.user != interaction.user :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        if self.role and self.role not in interaction.user.roles :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        await interaction.response.send_message(f'{select.values[0]} Selected', ephemeral=True)
        self.value = select.values[0]
        self.stop()

class PVC_COMMANDS(commands.Cog):

    def __init__(self , client):
        self.client = client
    
    async def cog_load(self) -> None:
        self.client.add_view(PVC_COMMANDS.PanelView())
    
    async def check_channel(ctx) ->bool : 
        
        if client.data[ctx.guild.id]['disabled'] and ctx.command.name in client.data[ctx.guild.id]['disabled'] :
            raise commands.DisabledCommand("Command disable in Server")

        return (client.data[ctx.guild.id]['pvc']) and (client.data[ctx.guild.id]['pvc_channel'] == ctx.channel.id or client.data[ctx.guild.id]['channels'] is None or len(client.data[ctx.guild.id]['channels']) == 0  or ctx.channel.id in client.data[ctx.guild.id]['channels']) 


    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_perms)
    async def pvcs(self , ctx):
        embed = bembed()
        data = await client.db.fetch('SELECT * FROM pvcs WHERE guild_id = $1 ', ctx.guild.id)
        if data is None :
            embed.description = "No Active Pvc In Server"
            await ctx.send(embed = embed)
            return 
        options = []
        i = 1
        for pvc in data :
            if ctx.guild.get_channel(pvc['vcid']) :
                time = f"End <t:{ int(datetime.now().timestamp() + (pvc['duration']))}:R>"
                if pvc['auto'] :
                    time = f"🛺 PAYG Enabled"
                embed.add_field(name = f"{i}. {ctx.guild.get_channel(pvc['vcid']).name}" , value = f"Owner {ctx.guild.get_member(pvc['id']).mention if ctx.guild.get_member(pvc['id']) else pvc['id']}\n{time}")
                i += 1
                options.append( discord.SelectOption(label =  ctx.guild.get_channel(pvc['vcid']).name , value =  ctx.guild.get_channel(pvc['vcid']).id ) )
        
        async def delete_pvc( id , refund = True , reason = None ) :
            info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE vcid = $1 ', id)
            if info == None or ctx.guild.get_channel(id) is None :
                return
            try :
                await ctx.guild.get_channel(id).delete( reason = reason )
                await client.db.execute("DELETE FROM pvcs WHERE vcid = $1" , id)
            except :
                pass
            if refund :
                await client.db.execute("UPDATE users SET pvc = pvc + $1 WHERE id = $2 AND guild_id = $3" , int((info['duration'] - 180 ) * (client.data[ctx.guild.id]['rate']/3600)) , info['id'] , ctx.guild.id )
    

        view = discord.ui.View()
        select = discord.ui.Select(placeholder = "Select VC You Want TO Delete" , options = options )
        async def delete_single( interaction ):
            if interaction.user != ctx.author:
                await interaction.response.send_message( embed = bembed("Not Your Interaction"), ephemeral = True)
                return
            
            id = int(select.values[0])
            view1 = ConfirmView()
            await interaction.response.send_message( embed = bembed(f"Are You Sure ? You want to delete <#{id}> ?") , view = view1 ,ephemeral = True)
            await view1.wait()
            if view1.value :
                view2 = ConfirmView()
                await interaction.followup.send( embed = bembed(f"Do You Want To Refund {pvc_coin(ctx.guild.id)[1]}'s To User ?") , view = view2 ,  ephemeral = True)
                await view2.wait()
                if view2.value :
                    await delete_pvc(id , True , f"PVC Delete By {ctx.author} With Refund")
                elif view2.value is False :
                    await delete_pvc(id , False , f"PVC Delete By {ctx.author} Without Refund")
                await interaction.followup.send(embed = bembed("✅ Done") , ephemeral = True)
        select.callback = delete_single
        
        view.add_item(select)
        delete = discord.ui.Button( style = discord.ButtonStyle.danger , emoji = "🗑️" )
        
        async def delete_multi( interaction ):
            if interaction.user != ctx.author:
                await interaction.response.send_message( embed = bembed("Not Your Interaction"), ephemeral = True)
                return

            view0 = ConfirmView()
            await interaction.response.send_message( embed = bembed("Only Delete the Empty PVC's ? **(1/3)**\nConfirm : delete only empty pvc's\nCencel : All pvc's") , view = view0 ,ephemeral = True)
            await view0.wait()
            if view0.value :
                delete_all = False
            elif view0.value == False :
                delete_all = True
            else :
                return

            view1 = ConfirmView()
            await interaction.response.send_message( embed = bembed("Are You Sure ? **(2/3)**") , view = view1 ,ephemeral = True)
            await view1.wait()
            if view1.value :
                view2 = ConfirmView()
                await interaction.followup.send( embed = bembed(f"Do You Want To Rrfund {pvc_coin(ctx.guild.id)[1]}'s To User ? **(3/3)**") , view = view2 ,  ephemeral = True)
                await view2.wait()
                if view2.value :
                    pvcs = client.db.fetch("SELECT * FROM pvcs WHERE guild_id = $1" , ctx.guild.id)
                    for pvc in pvcs :
                        if delete_all is False :
                            if ctx.guild.get_channel(pvc['vcid']) and ctx.guild.get_channel(pvc['vcid']).members == 0 : 
                                await delete_pvc( pvc['vcid'] , True , f"PVC Delete By {ctx.author} With Refund")
                        elif delete_all :
                            await delete_pvc( pvc['vcid'] , True , f"PVC Delete By {ctx.author} With Refund")

                elif view2.value is False : 
                    pvcs = client.db.fetch("SELECT * FROM pvcs WHERE guild_id = $1" , ctx.guild.id)
                    for pvc in pvcs :
                        if delete_all is False :
                            if ctx.guild.get_channel(pvc['vcid']) and ctx.guild.get_channel(pvc['vcid']).members == 0 : 
                                await delete_pvc( pvc['vcid'] , False , f"PVC Delete By {ctx.author} Without Refund")
                        elif delete_all :
                            await delete_pvc( pvc['vcid'] , False , f"PVC Delete By {ctx.author} Without Refund")
                await interaction.followup.send(embed = bembed("✅ Done") , ephemeral = True)
        delete.callback = delete_multi

        view.add_item(delete)
        await ctx.send(embed =embed , view=view)


    @commands.command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 300, BucketType.member)
    async def rename(self , ctx , * , name : str):
        
        info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        if info == None or ctx.guild.get_channel(info['vcid']) is None :
            return
        await ctx.guild.get_channel(info['vcid']).edit(name=name)
        await ctx.send(embed = bembed(f"PVC name Updated to **{name}**"))
    
    @rename.error
    async def rename_error(self,ctx , error):
        if isinstance(error, commands.CommandOnCooldown):
            sec = int(error.retry_after)
            min , sec = divmod(sec, 60)
            await ctx.send( embed = bembed(f":watch: | You cannot use this command, use after {min}min {sec}seconds."))
            return
        

    @commands.command(aliases =["au" , "addm", 'add' , 'addvc'])
    @commands.guild_only()
    @commands.check(check_channel)
    async def adduser(self , ctx , channel : typing.Optional[discord.VoiceChannel] , *members : typing.Optional[discord.Member]):
        
        info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        if info == None or ctx.guild.get_channel(info['vcid']) is None :
            return
        
        overwrites = ctx.guild.get_channel(info['vcid']).overwrites
        if channel and channel.members != 0 :
            for i , member in enumerate(channel.members , 1) :
                if i > 10 :
                    break
                else :
                    overwrites[member] = discord.PermissionOverwrite(connect=True , view_channel = True)
            await ctx.send(embed = bembed(f"{channel.mention} {10 if len(channel.members) > 10 else len(channel.members)} User(s) Added in your pvc"))
            
        lis = [ "1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣" ]
        for i , member in enumerate(members) :
            if member.bot :
                continue
            overwrites[member] = discord.PermissionOverwrite(connect=True , view_channel = True)
            await ctx.message.add_reaction(lis[i])  
        
        if overwrites != ctx.guild.get_channel(info['vcid']).overwrites :
            await ctx.guild.get_channel(info['vcid']).edit( overwrites = overwrites )

    @commands.command(aliases =["ru" , "removem"])
    @commands.guild_only()
    @commands.check(check_channel)
    async def removeuser(self , ctx , *members : discord.Member):

        info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        if info == None or ctx.guild.get_channel(info['vcid']) is None :
            return
        await ctx.message.add_reaction('⛔')  
        lis = [ "1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣" ]
        overwrites = ctx.guild.get_channel(info['vcid']).overwrites
        for i , member in enumerate(members) :
            try :
                del overwrites[member]
            except :
                pass
            if member in ctx.guild.get_channel(info['vcid']).members :
                pass 
            await ctx.message.add_reaction(lis[i])   
            if member.voice and member.voice.channel ==  ctx.guild.get_channel(info['vcid']) :
                await member.move_to(None)
        
        if overwrites != ctx.guild.get_channel(info['vcid']).overwrites :
            await ctx.guild.get_channel(info['vcid']).edit( overwrites = overwrites )     
  
    @commands.hybrid_command(aliases = ["am" , 'wtj' , "askforinvite"])
    @commands.guild_only()
    @commands.check(check_channel)
    async def addme(self , ctx, channel : discord.VoiceChannel):
        info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE vcid = $1 AND guild_id = $2 ', channel.id , ctx.guild.id)
        if info == None or ctx.guild.get_channel(info['vcid']) is None :
            return
        owner = ctx.guild.get_channel(info['vcid'])
        if owner is None :
            return
        view = ConfirmView(owner)      
        await ctx.reply( embed = bembed(f'{owner.mention} , {ctx.author} want to join your vc !') , view = view)
        await view.wait()
        if view.value :
            await ctx.guild.get_channel(info["vcid"]).set_permissions(ctx.author , connect=True , view_channel = True)
            await ctx.message.add_reaction("🙌")
          
    @commands.hybrid_command(aliases = ['info' , 'ipvc' , 'i'])
    @commands.guild_only()
    @cooldown(1, 10, BucketType.member)
    @commands.check(check_channel)  
    async def pvcinfo(self , ctx ): 
        
        info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        if info == None or ctx.guild.get_channel(info['vcid']) is None :
            return
        
        def check(ctx) ->bool : 
            return (client.data[ctx.guild.id]['pvc']) and (client.data[ctx.guild.id]['pvc_channel'] == ctx.channel.id or client.data[ctx.guild.id]['channels'] is None or len(client.data[ctx.guild.id]['channels']) == 0  or ctx.channel.id in client.data[ctx.guild.id]['channels']) 

        if not check(ctx) and not ctx.channel.id == ctx.guild.get_channel(info['vcid']).id :
            return 
        # async def updateinfo() :
        #     global info 
        #     info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
            

        def pvcinfoembed():
             
            vc = ctx.guild.get_channel(info['vcid'])  
            embed=discord.Embed (title= vc.name , color=0x00ff00) 
            time = f"VC End <t:{ int(datetime.now().timestamp() + (info['duration']))}:R>"
            if info['auto'] and info['duration'] > 600 :
                time = f"🛺 PAYG Enable <t:{ int(datetime.now().timestamp() + (info['duration']))}:R>"
            elif info['auto'] :
                time = f"🛺 PAYG Enabled"

            embed.description = f"VC Owner : {ctx.guild.get_member(info['id']).mention}\n{time} \n\n**Members**" 
            text = " "
            i = 0
            for  j in  vc.overwrites:
                if type(j) == discord.Member and not j.bot :
                    i += 1
                    text  += f"{i}. {j.mention}\n"
                if i != 0 and (i) % 10 == 0 :
                    embed.add_field(name = "\n" , value= text)
                    text = ' '
            embed.add_field(name = "\n" , value= text)          
            return embed
        
        view = discord.ui.View()
        items = [ ]
        
        async def update_adduser(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message( embed = bembed("Not Your Interaction"), ephemeral = True)
                return
            data = adduser.values
            if len(data) == 0 :
               await interaction.response.defer()
               return
            overwrites = ctx.guild.get_channel(info['vcid']).overwrites
            for member in data :
                if member.bot :
                    continue
                overwrites[member] = discord.PermissionOverwrite(connect=True , view_channel = True)
            if overwrites != ctx.guild.get_channel(info['vcid']).overwrites :
                await ctx.guild.get_channel(info['vcid']).edit( overwrites = overwrites )
            await asyncio.sleep(1)
            await interaction.response.edit_message(embed=pvcinfoembed() )

        adduser = discord.ui.UserSelect(placeholder="Select Members You Want To ADD", min_values=0, max_values=25)
        adduser.callback = update_adduser
        items.append(adduser)
        
        async def update_removeuser(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message( embed = bembed("Not Your Interaction"), ephemeral = True)
                return
            data = removeuser.values
            if len(data) == 0:
               await interaction.response.defer()
               return

            vc_channel = ctx.guild.get_channel(info['vcid'])
            overwrites = ctx.guild.get_channel(info['vcid']).overwrites
            for member in data :
                try :
                    del overwrites[member]
                except Exception:
                    pass
                
                # Remove from voice channel if connected
                if member.voice and member.voice.channel == vc_channel:
                    try:
                        await member.move_to(None)
                    except discord.HTTPException:
                        pass

            if overwrites != ctx.guild.get_channel(info['vcid']).overwrites :
                await ctx.guild.get_channel(info['vcid']).edit( overwrites = overwrites )
            await asyncio.sleep(1)
            await interaction.response.edit_message(embed=pvcinfoembed() )

        removeuser = discord.ui.UserSelect(placeholder="Select Members You Want To Remove", min_values=0, max_values=25)
        removeuser.callback = update_removeuser
        items.append(removeuser)
        
        async def update_hide(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(embed = bembed("Not Your Interaction") , ephemeral = True)
                return
            if ctx.guild.get_channel(info['vcid']) and ctx.guild.get_channel(info['vcid']).permissions_for( ctx.guild.default_role).view_channel :
                await ctx.guild.get_channel(info['vcid']).set_permissions(ctx.guild.default_role , view_channel = False , connect = False , stream = True)
                await interaction.response.send_message( embed = bembed("VC is Hidden Now") , ephemeral = True)
            else  :
                await ctx.guild.get_channel(info['vcid']).set_permissions(ctx.guild.default_role , view_channel = None , connect = False , stream = True)
                await interaction.response.send_message( embed = bembed(f"VC is Visible Now") , ephemeral = True )
            
        hide = discord.ui.Button( style=discord.ButtonStyle.gray , emoji='👁️' ) 
        hide.callback = update_hide
        items.append(hide)
        
        
        async def update_to(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(embed = bembed("Not Your Interaction"), ephemeral = True)
                return
            info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
            if info == None or ctx.guild.get_channel(info['vcid']) is None :
                return
            if info['auto'] :
                await interaction.response.send_message(embed = bembed("You Cant Tansfer A PAYG mode PVC to Someone"), ephemeral = True)
                return

            confirm = SelectUer(ctx.author)
            await interaction.response.send_message( embed = bembed(f"Select User You Want To Transfer PVC"), view = confirm , ephemeral = True)
            await confirm.wait()
            if confirm.value :
                info2 = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', (confirm.value).id , ctx.guild.id)
                if info2 != None :
                    await interaction.followup.send( embed = bembed("User Already have a PVC") , ephemeral = True)
                    return
                
                await client.db.execute("UPDATE pvcs SET id = $1 WHERE id = $2 AND guild_id = $3" , (confirm.value).id , ctx.author.id , ctx.guild.id )
                await interaction.followup.send( embed = bembed("✅ Done") , ephemeral = True)
                
                try :
                    await ctx.guild.get_channel(info['vcid']).edit(name = f"{confirm.value.name}'s Pvc")
                except :
                    await interaction.followup.send( embed = bembed("⚠️ Cant Update VC name Due to rate limit") , ephemeral = True)
                await interaction.message.delete()            
        
        to = discord.ui.Button( style=discord.ButtonStyle.gray , emoji='👑' )
        to.callback = update_to
        items.append(to)

        async def update_auto(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(embed = bembed("Not Your Interaction") , ephemeral = True)
                return
            info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
            embed = pvcinfoembed()
            time = f"VC End <t:{ int(datetime.now().timestamp() + (info['duration']))}:R>"
            
            if info['auto'] :
                await client.db.execute('UPDATE pvcs SET auto = $1 WHERE id = $2' , False , ctx.author.id)
                embed.description = f"VC Owner : {ctx.guild.get_member(info['id']).mention}\n{time}\n\n**Members**"
                await interaction.response.edit_message(embed=embed )
            else : 
                await client.db.execute('UPDATE pvcs SET auto = $1 WHERE id = $2' , True , ctx.author.id)
                if info['duration'] > 600 :
                    time = f"🛺 PAYG Enable <t:{ int(datetime.now().timestamp() + (info['duration']))}:R>"
                else :
                    time = f"🛺 PAYG Enabled"
                embed.description = f"VC Owner : {ctx.guild.get_member(info['id']).mention}\n{time}\n\n**Members**"
                
                await interaction.response.edit_message(embed=embed )

        auto = discord.ui.Button( style=discord.ButtonStyle.gray , emoji='🛺' ) 
        auto.callback = update_auto
        items.append(auto)
        
        async def update_friends(interaction):
            info = await client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)

            bal = await client.db.fetchrow('SELECT friends FROM users WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
            view = discord.ui.View()
            friend = discord.ui.UserSelect(placeholder="Add/Remove Friends" ,min_values= 0 , max_values=25 , default_values= [ interaction.guild.get_member(id) for id in bal['friends'] if interaction.guild.get_member(id) is not None] if bal['friends'] else None )
            async def callback(interaction):
                data = [ member.id for member in friend.values if not member.bot ]
                await client.db.execute( "UPDATE users SET friends = $1 WHERE id = $2 AND guild_id = $3" , data , interaction.user.id , interaction.guild.id )
                temp = "\n- "+'\n- '.join( [member.mention for member in friend.values if not member.bot ] )
                embed = bembed(f"✅ FriendList Updated\n{temp}")
                await interaction.response.edit_message(embed=embed , view = view )
                if info and interaction.guild.get_channel(info['vcid']) :
                    overwrites = interaction.guild.get_channel(info['vcid']).overwrites
                    for member in friend.values :
                        if member.bot :
                            continue
                        overwrites[member] = discord.PermissionOverwrite(connect=True , view_channel = True)
                    if overwrites != interaction.guild.get_channel(info['vcid']).overwrites :
                        await interaction.guild.get_channel(info['vcid']).edit( overwrites = overwrites )
                    
            friend.callback = callback
            view.add_item(friend)
            await interaction.response.send_message(view=view , ephemeral=True)
   
        
        # if client.data[ctx.guild.id]['pvc_vc_limit'] != 0 :
        #     async def update_public(interaction):
        #         if interaction.user != ctx.author:
        #             await interaction.response.send_message(embed = bembed("Not Your Interaction") , ephemeral = True)
        #             return
        #         if ctx.guild.get_channel(info['vcid']) and ctx.guild.get_channel(info['vcid']).permissions_for( ctx.guild.default_role).connect :
        #             overwrite = ctx.guild.get_channel(info['vcid']).overwrites_for(ctx.guild.default_role)
        #             overwrite.update(connect = False  , view_channel = None )
        #             overwrites = {**ctx.guild.get_channel(info['vcid']).overwrites , ctx.guild.default_role : overwrite }
        #             await ctx.guild.get_channel(info['vcid']).edit(overwrites = overwrites , user_limit = 0 )
        #             await interaction.response.send_message( embed = bembed("VC is Private Now") , ephemeral = True)
        #         elif ctx.guild.get_channel(info['vcid']) and ctx.guild.get_channel(info['vcid']).permissions_for( ctx.guild.default_role).connect == False:
        #             overwrite = ctx.guild.get_channel(info['vcid']).overwrites_for(ctx.guild.default_role)
        #             overwrite.update(connect = True , view_channel = True)
        #             overwrites = {**ctx.guild.get_channel(info['vcid']).overwrites , ctx.guild.default_role : overwrite }
        #             await ctx.guild.get_channel(info['vcid']).edit(overwrites = overwrites , user_limit = client.data[ctx.guild.id]['pvc_vc_limit']  )
        #             await interaction.response.send_message( embed = bembed(f"VC is Public Now") , ephemeral = True )
             
        #     public = discord.ui.Button( style=discord.ButtonStyle.gray , emoji='👥' , row = 3 ) 
        #     public.callback = update_public
        #     items.append(public)

        friends = discord.ui.Button( style=discord.ButtonStyle.gray , emoji='<:users:1188641484895961228>' , row = 2 )
        friends.callback = update_friends
        items.append(friends)

        async def update_delete_pvc(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(embed = bembed("Not Your Interaction") , ephemeral = True)
                return
            info = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
            if info == None or ctx.guild.get_channel(info['vcid']) is None :
                return

            confirm = ConfirmView(ctx.author)
            await interaction.response.send_message( embed = bembed(f"Want To Delete Your PVC ? will get {pvc_coin(interaction.guild.id)[0]} {int((info['duration'] - 180 ) * (client.data[interaction.guild.id]['rate']/3600)) : ,} back ") , view = confirm , ephemeral = True)
            await confirm.wait()
            if confirm.value :
                try :
                   await ctx.guild.get_channel(info['vcid']).delete()
                   await client.db.execute("DELETE FROM pvcs WHERE vcid = $1" , info['vcid'])
                except :
                    pass
                await client.db.execute("UPDATE users SET pvc = pvc + $1 WHERE id = $2 AND guild_id = $3" , int((info['duration'] - 180 ) * (client.data[interaction.guild.id]['rate']/3600)) , ctx.author.id , ctx.guild.id )
                await ctx.message.delete()
        delete_pvc = discord.ui.Button( style=discord.ButtonStyle.gray , emoji='<:bin:1188639295423139950>' , row = 2 )
        delete_pvc.callback = update_delete_pvc
        items.append(delete_pvc)
        
        async def update_collapse(interaction) :
            if interaction.user != ctx.author:
                await interaction.response.send_message(embed = bembed("Not Your Interaction") , ephemeral = True)
                return
            if len(view.children) == 1 :
                view.clear_items()
                for i in items :
                    view.add_item(i)
                collapse.emoji = '<:up:1193058411928104991>'
                view.add_item(collapse)
            else :
                view.clear_items()
                collapse.emoji = '<:down:1193058406920093706>'
                view.add_item(collapse)
            await interaction.response.edit_message(view = view)
        
        collapse = discord.ui.Button( style=discord.ButtonStyle.gray , emoji= '<:down:1193058406920093706>' ,  row=4 )
        collapse.callback = update_collapse
        view.add_item(collapse)
        
        async def view_timeout():
            await ctx.message.edit(view = None)
        view.on_timeout = view_timeout
         
        await ctx.send(embed = pvcinfoembed() , view = view)
        
    class PanelView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
        

        @discord.ui.button(emoji='<:info:1188641528554455070>', custom_id="pvc:info")
        async def info(self, interaction: discord.Interaction , button: discord.ui.Button,):
            info = await client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
            if info == None or interaction.guild.get_channel(info['vcid']) is None :
                await interaction.response.send_message(embed =bembed(f"Create a PVC first with `pvc <duration>` command") , ephemeral=True)
                return

            vc = interaction.guild.get_channel(info['vcid'])  
            embed=discord.Embed (title= vc.name , color=0x2b2c31) 
            time = f"VC End <t:{ int(datetime.now().timestamp() + (info['duration']))}:R>"
            if info['auto'] and info['duration'] > 600 :
                time = f"🛺 PAYG Enable <t:{ int(datetime.now().timestamp() + (info['duration']))}:R>"
            elif info['auto'] :
                time = f"🛺 PAYG Enabled"

            embed.description = f"VC Owner : {interaction.guild.get_member(info['id']).mention}\n{time}\n\n **Members**" 
            text = " "
            i = 0
            for  j in  vc.overwrites:
                if type(j) == discord.Member and not j.bot :
                    i += 1
                    text  += f"{i}. {j.mention}\n"
                if i != 0 and i % 10 == 0 :
                    embed.add_field(name=" " , value= text)
                    text = " "
            embed.add_field(name = " " , value= text)
            await interaction.response.send_message(embed = embed , ephemeral=True)
        
        @discord.ui.button(emoji="<:add:1188641489392238662>", custom_id="pvc:add-user")
        async def add_user(self,  interaction: discord.Interaction , button: discord.ui.Button,):
            info = await client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
            if info == None or interaction.guild.get_channel(info['vcid']) is None :
                await interaction.response.send_message(embed =bembed(f"Create a PVC first with `pvc <duration>` command") , ephemeral=True)
                return
            
            view = discord.ui.View()
            adduser = discord.ui.UserSelect(placeholder="Select Members You Want To ADD" , max_values=25)
            async def callback(interaction):
                data = adduser.values
                if len(data) == 0 :
                    await interaction.response.defer()
                    return
                overwrites = interaction.guild.get_channel(info['vcid']).overwrites
                for member in data :
                    if member.bot :
                        continue
                    overwrites[member] = discord.PermissionOverwrite(connect=True , view_channel = True)
                if overwrites != interaction.guild.get_channel(info['vcid']).overwrites :
                    await interaction.guild.get_channel(info['vcid']).edit( overwrites = overwrites )
                embed = bembed()
                embed.description = "`✅` " +"  ".join([user.mention for user in data]) + " added in PVC"
                await interaction.response.edit_message(embed=embed )
            adduser.callback = callback
            view.add_item(adduser)
            await interaction.response.send_message(view=view , ephemeral=True)
            
        @discord.ui.button(emoji= '<:remove:1188641493422977085>', custom_id="pvc:remove-user")
        async def remove_user(self, interaction: discord.Interaction , button: discord.ui.Button,):
            info = await client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
            if info == None or interaction.guild.get_channel(info['vcid']) is None :
                await interaction.response.send_message(embed =bembed(f"Create a PVC first with `pvc <duration>` command") , ephemeral=True)
                return
        
            view = discord.ui.View()
            removeuser = discord.ui.UserSelect(placeholder="Select Members You Want To Remove" , max_values=25)
            async def callback(interaction):
                data = removeuser.values
                if len(data) == 0 :
                    await interaction.response.defer()
                    return
                overwrites = interaction.guild.get_channel(info['vcid']).overwrites
                for member in data :
                    try :
                        del overwrites[member]
                        if member.voice and member.voice.channel ==  interaction.guild.get_channel(info['vcid']) :
                            await member.move_to(None)
                    except : pass
                if overwrites != interaction.guild.get_channel(info['vcid']).overwrites :
                    await interaction.guild.get_channel(info['vcid']).edit( overwrites = overwrites )
                embed = bembed()
                embed.description = "`✅` " +"  ".join([user.mention for user in data]) + " Removed From PVC"
                await interaction.response.edit_message(embed=embed )
            removeuser.callback = callback
            view.add_item(removeuser)
            await interaction.response.send_message(view=view , ephemeral=True)
        
        @discord.ui.button(emoji= '👁️', custom_id="pvc:hide-unhide")
        async def hide(self, interaction: discord.Interaction , button: discord.ui.Button,):
            info = await client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
            if info == None or interaction.guild.get_channel(info['vcid']) is None :
                await interaction.response.send_message(embed =bembed(f"Create a PVC first with `pvc <duration>` command") , ephemeral=True)
                return
            
            if interaction.guild.get_channel(info['vcid']) and interaction.guild.get_channel(info['vcid']).permissions_for( interaction.guild.default_role).view_channel :
                await interaction.guild.get_channel(info['vcid']).set_permissions(interaction.guild.default_role , view_channel = False , connect = False , stream = True)
                await interaction.response.send_message( embed = bembed("VC is Hidden Now") , ephemeral = True)
            else  :
                await interaction.guild.get_channel(info['vcid']).set_permissions(interaction.guild.default_role , view_channel = None , connect = False , stream = True)
                await interaction.response.send_message( embed = bembed(f"VC is Visible Now") , ephemeral = True )


        @discord.ui.button(emoji= '<:users:1188641484895961228>', custom_id="pvc:friends" , row=1)
        async def friends(self, interaction: discord.Interaction , button: discord.ui.Button,):
            info = await client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)

            bal = await client.db.fetchrow('SELECT friends FROM users WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
            view = discord.ui.View()
            friend = discord.ui.UserSelect(placeholder="Add/Remove Friends" ,min_values= 0 , max_values=25 , default_values= [ interaction.guild.get_member(id) for id in bal['friends'] if interaction.guild.get_member(id) is not None ] if bal['friends'] else None )
            async def callback(interaction):
                data = [ member.id for member in friend.values if not member.bot ]
                await client.db.execute( "UPDATE users SET friends = $1 WHERE id = $2 AND guild_id = $3" , data , interaction.user.id , interaction.guild.id )
                temp = "\n- "+'\n- '.join( [member.mention for member in friend.values if not member.bot ] )
                embed = bembed(f"✅ FriendList Updated\n{temp}")
                await interaction.response.edit_message(embed=embed , view = view )
                if info and interaction.guild.get_channel(info['vcid']) :
                    overwrites = interaction.guild.get_channel(info['vcid']).overwrites
                    for member in friend.values :
                        if member.bot :
                            continue
                        overwrites[member] = discord.PermissionOverwrite(connect=True , view_channel = True)
                    if overwrites != interaction.guild.get_channel(info['vcid']).overwrites :
                        await interaction.guild.get_channel(info['vcid']).edit( overwrites = overwrites )
                    
            friend.callback = callback
            view.add_item(friend)
            await interaction.response.send_message(view=view , ephemeral=True)

        @discord.ui.button(emoji= '🛺', custom_id="pvc:auto" , row=1)
        async def auto(self, interaction: discord.Interaction , button: discord.ui.Button,):
            info = await client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
            if info == None or interaction.guild.get_channel(info['vcid']) is None :
                await interaction.response.send_message(embed =bembed(f"Create a PVC first with `pvc <duration>` command") , ephemeral=True)
                return
            embed = bembed()
            time = f"VC End <t:{ int(datetime.now().timestamp() + (info['duration']))}:R>"
            
            if info['auto'] :
                await client.db.execute('UPDATE pvcs SET auto = $1 WHERE id = $2' , False , interaction.user.id)
                embed.description = f"🛺 PAYG Disabled \n\n{time}"
                await interaction.response.send_message(embed=embed , ephemeral=True)
            else : 
                await client.db.execute('UPDATE pvcs SET auto = $1 WHERE id = $2' , True , interaction.user.id)
                if info['duration'] > 600 :
                    time = f"🛺 PAYG Enable <t:{ int(datetime.now().timestamp() + (info['duration']))}:R>"
                else :
                    time = f"🛺 PAYG Enabled"
                embed.description = f"{time}"
                await interaction.response.send_message(embed=embed , ephemeral=True )

        @discord.ui.button(emoji= '👑', custom_id="pvc:transfer-ownership", row=1)
        async def transfer_ownership(self, interaction: discord.Interaction , button: discord.ui.Button,):
            info = await client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
            if info == None or interaction.guild.get_channel(info['vcid']) is None :
                await interaction.response.send_message(embed =bembed(f"Create a PVC first with `pvc <duration>` command") , ephemeral=True)
                return
            if info['auto'] :
                await interaction.response.send_message(embed = bembed("You Cant Tansfer A PAYG mode PVC to Someone"), ephemeral = True)
                return
            view = discord.ui.View()
            newowner = discord.ui.UserSelect(placeholder="Select User You Want To Transfer PVC" )
            async def callback(interaction):
                data = newowner.values[0]
                if len(data) == 0 or data.bot or data.id == info['id'] :
                    await interaction.response.defer()
                    return
                info2 = await self.client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ',data.id , interaction.guild.id)
                if info2 != None :
                    await interaction.response.send_message( embed = bembed("User Already have a PVC") , ephemeral = True)
                    return
                
                await client.db.execute("UPDATE pvcs SET id = $1 WHERE id = $2 AND guild_id = $3" , data.id , interaction.author.id , interaction.guild.id )
                await interaction.response.send_message( embed = bembed(f"✅ Pvc Ownership tranferd to {data.mention}") , view = None , ephemeral = True)
            newowner.callback = callback
            view.add_item(newowner)
            await interaction.response.send_message(view=view , ephemeral=True)
        
        @discord.ui.button(emoji= '<:bin:1188639295423139950>', custom_id="pvc:delete", row=1)
        async def delete(self, interaction: discord.Interaction , button: discord.ui.Button,):
            info = await client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
            if info == None or interaction.guild.get_channel(info['vcid']) is None :
                await interaction.response.send_message(embed =bembed(f"Create a PVC first with `pvc <duration>` command") , ephemeral=True)
                return
            
            confirm = ConfirmView(interaction.user)
            await interaction.response.send_message( embed = bembed(f"Want To Delete Your PVC ? will get {pvc_coin(interaction.guild.id)[0]} {int((info['duration'] - 180 ) * (client.data[interaction.guild.id]['rate']/3600)) : ,} back ") , view = confirm , ephemeral = True)
            await confirm.wait()
            if confirm.value :
                try                :
                   await client.db.execute("DELETE FROM pvcs WHERE vcid = $1" , info['vcid'])
                   await interaction.guild.get_channel(info['vcid']).delete()
                except :
                    pass
                await client.db.execute("UPDATE users SET pvc = pvc + $1 WHERE id = $2 AND guild_id = $3" , int((info['duration'] - 180 ) * (client.data[interaction.guild.id]['rate']/3600)) , interaction.user.id , interaction.guild.id )

        @discord.ui.button(emoji= '📢' , custom_id="pvc:public", row=2)
        async def public(self, interaction: discord.Interaction , button: discord.ui.Button,):
            info = await client.db.fetchrow('SELECT * FROM pvcs WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
            if not client.data[interaction.guild.id]['pvc_public'] :
                await interaction.response.send_message(embed =bembed(f"Public PVC is Disabled in server") , ephemeral=True)
                return
            
            if info == None or interaction.guild.get_channel(info['vcid']) is None :
                await interaction.response.send_message(embed =bembed(f"Create a PVC first with `pvc <duration>` command") , ephemeral=True)
                return
            if interaction.guild.get_channel(info['vcid']) and interaction.guild.get_channel(info['vcid']).permissions_for( interaction.guild.default_role).connect :
                overwrite = interaction.guild.get_channel(info['vcid']).overwrites_for(interaction.guild.default_role)
                overwrite.update(connect = False)
                overwrites = {**interaction.guild.get_channel(info['vcid']).overwrites , interaction.guild.default_role : overwrite }
                await interaction.guild.get_channel(info['vcid']).edit(overwrites = overwrites , user_limit = 0 )
                await interaction.response.send_message( embed = bembed("VC is Private Now") , ephemeral = True)
            elif interaction.guild.get_channel(info['vcid']) and interaction.guild.get_channel(info['vcid']).permissions_for( interaction.guild.default_role).connect == False:
                overwrite = interaction.guild.get_channel(info['vcid']).overwrites_for(interaction.guild.default_role)
                overwrite.update(connect = True)
                overwrites = {**interaction.guild.get_channel(info['vcid']).overwrites , interaction.guild.default_role : overwrite }
                await interaction.guild.get_channel(info['vcid']).edit(overwrites = overwrites , user_limit = client.data[interaction.guild.id]['pvc_public'] if client.data[interaction.guild.id]['pvc_public'] != 100 else 0 )
                await interaction.response.send_message( embed = bembed(f"VC is Public Now") , ephemeral = True )


    @commands.hybrid_command(aliases = ['panel'])
    @commands.guild_only()
    @cooldown(1, 10, BucketType.guild)
    @commands.check(check_perms)
    async def pvcpanel(self , ctx ):
        embed = bembed()

        embed.set_author(name='PVC Panel', icon_url=ctx.guild.icon)
        embed.title = "Click on the buttons to perform actions\n"
        embed.add_field(name=" " , value="<:info:1188641528554455070> : Pvc Information\n\n<:add:1188641489392238662> : Add User\n\n<:remove:1188641493422977085> : Remove User\n\n👁️ : Hide/Unhide\n\n📢 : Public/Private")
        embed.add_field(name=" " , value="<:users:1188641484895961228> : Add/Remove Friends\n\n🛺 : Auto Mode\n\n👑 : Transfer Ownership\n\n<:bin:1188639295423139950> : Delete PVC" )
        view = PVC_COMMANDS.PanelView()
            
        await ctx.send(embed = embed , view = view)
    
    
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # async def hide(self , ctx):
    #     pvcdata = db[f"{ctx.guild.id}"]        
    #     info = await pvcdata.find_one({"info_id" : ctx.author.id})
    #     guild = ctx.guild
    #     if info == None :
    #         return 
    #     else:
    #        await guild.get_channel(info["vcid"]).set_permissions( ctx.guild.default_role , view_channel = False , connect = False )
    #        await ctx.message.add_reaction("🙌")  

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # async def unhide(self , ctx):
    #     pvcdata = db[f"{ctx.guild.id}"]        
    #     info = await pvcdata.find_one({"info_id" : ctx.author.id})
    #     guild = ctx.guild
    #     if info == None :
    #         return 
    #     else:
    #        await guild.get_channel(info["vcid"]).set_permissions( ctx.guild.default_role , view_channel = True , connect = False )
    #        await ctx.message.add_reaction("🙌")                           

    # @commands.hybrid_command(aliases = ["to"])
    # @commands.guild_only()
    # @cooldown(1, 600, BucketType.user)
    # @commands.check(check_channel)
    # async def tansferownership(self , ctx , member : discord.Member):
    #     pvcdata = db[f"{ctx.guild.id}"]        
    #     info = await pvcdata.find_one({"info_id" : ctx.author.id})
    #     info2 = await pvcdata.find_one({"info_id" : member.id})
    #     guild = ctx.guild
    #     if info == None :
    #         ctx.command.reset_cooldown(ctx)
    #         return
    #     elif info2 == None:
    #         await guild.get_channel(info["vcid"]).edit(name= f"{member.name}'Pvc")
    #         await pvcdata.update_one({"info_id" : ctx.author.id} , {"$set" : {"info_id" : member.id } }) 
    #         await ctx.reply(f"PVC ownership transfered to {member.name}") 
    #     else : 
    #         ctx.command.reset_cooldown(ctx)
    #         await ctx.send(f"{member.name} already have a PVC")

    # @tansferownership.error
    # async def tranferownership_error(self,ctx , error):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         sec = int(error.retry_after)
    #         min , sec = divmod(sec, 60)
    #         await ctx.send(f":watch: | You cannot use this command use after {min}min {sec}seconds.")
    #         return
    #     if isinstance(error, commands.MemberNotFound): 
    #         ctx.command.reset_cooldown(ctx)
    #         await ctx.send("cant find user !!!")
    #         return      
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send("Not enough arguments passed !!!")
    #         ctx.command.reset_cooldown(ctx)
    #         return                   

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @cooldown(1, 600, BucketType.user)
    # @commands.check(check_channel)
    # async def rename(self , ctx , * , name):
    #     def check(reaction, user):
    #         return user.guild_permissions.manage_messages and str(reaction.emoji) == '✅'
    #     pvcdata = db[f"{ctx.guild.id}"]        
    #     info = await pvcdata.find_one({"info_id" : ctx.author.id})
    #     guild = ctx.guild
    #     if info == None :
    #         ctx.command.reset_cooldown(ctx)
    #         return 
    #     else : 
    #         msg = await ctx.reply(f'**Tag any of the online staff (manage_message perms) to rename your vc ! ||Expire in 5 min||**')
    #         await msg.add_reaction("✅")
    #         try : 
    #             reaction , user = await client.wait_for('reaction_add', check=check , timeout = 300)
    #             await guild.get_channel(info["vcid"]).edit(name= f"☁ {name}")
    #             await ctx.reply(f"PVC renamed to {name}") 
    #         except asyncio.TimeoutError:
    #             ctx.command.reset_cooldown(ctx)
    #             return

    # @rename.error
    # async def rename_error(self,ctx , error):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         sec = int(error.retry_after)
    #         min , sec = divmod(sec, 60)
    #         await ctx.send(f":watch: | You cannot use this command use after {min}min {sec}seconds.")
    #         return
    #     if isinstance(error, commands.MemberNotFound): 
    #         ctx.command.reset_cooldown(ctx)
    #         await ctx.send("cant find user !!!")
    #         return      
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send("Not enough arguments passed !!!")
    #         ctx.command.reset_cooldown(ctx)
    #         return  
    
    
            
    # @commands.hybrid_command(aliases = ["e"])
    # @commands.guild_only()
    # @cooldown(1, 10, BucketType.user)
    # @commands.check(check_channel)
    # async def extend(self , ctx , duration : DurationConverter):
    #     multiplier = { 'h' : 3600}
    #     amount , unit = duration
    #     guild = ctx.guild
    #     user = ctx.author 
    #     economy = db[f"{ctx.guild.id}"]
    #     bal = await economy.find_one({'id' : ctx.author.id})
    #     info = await economy.find_one({"info_id" : ctx.author.id})
    #     rate = (await economy.find_one({"category": "pvc"}))["rate"]  
    #     if info == None:
    #         await ctx.send("You dont have PVC , create with command ,pvc <time>h")
    #         return
    #     elif bal['pvc'] >= int((amount*multiplier[unit])* rate): 
    #         def check( m):
    #             return (m.content =='yes' or m.content =='Yes' or m.content =='T' or m.content =='t' or m.content =='Y' or m.content =='y') and m.channel == ctx.channel and m.author.id == ctx.author.id
    #         await ctx.send(f'This will charge you **{int((amount*multiplier[unit])* rate)}** PAODs ! \nif you want to cont. type `yes`')
    #         try:
    #             await client.wait_for('message', check=check , timeout = 10) 
    #             await economy.update_one({"info_id" : ctx.author.id } , {"$inc": {"info_time" : + (amount*60) }}) 
    #             await economy.update_one({"id" : ctx.author.id } , {"$inc": {"pvc" : -(int((amount*multiplier[unit])* rate))}})
    #             time = (await economy.find_one({"id" : ctx.author.id }))["info_time"] 
    #             await ctx.reply(f"Time inc. now you have more then {time}min")
    #         except asyncio.TimeoutError:
    #             await ctx.reply("transetion cenceled")      
    #     else:
    #             await ctx.send(f"not enough pvc coins you need {int((amount*multiplier[unit])* rate)} pvc coins")    

async def setup(client):
    await client.add_cog(PVC_COMMANDS(client))                     