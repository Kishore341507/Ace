import discord
from discord.ext import commands , tasks
from database import *
import asyncio
# from discord.ext.commands import BucketType, cooldown
# import random
# import math
# import typing
# from discord.ui import Button , View , Select , TextInput
from datetime import datetime
# from easy_pil import Editor, Canvas, load_image_async, Font
# from numerize import numerize

class event(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.emoji = ["\U0001f1e6", "\U0001f1e7" ,"\U0001f1e8" ,"\U0001f1e9", "\U0001f1ea" ,"\U0001f1eb", "\U0001f1ec", "\U0001f1ed", "\U0001f1ee" ,"\U0001f1ef", "\U0001f1f0", "\U0001f1f1" ,"\U0001f1f2" ,"\U0001f1f3" ,"\U0001f1f4" ,"\U0001f1f5" ,"\U0001f1f6" ,"\U0001f1f7", "\U0001f1f8", "\U0001f1f9" ]
        # self.voice_users = []
        # self.voice_rumble.start()
        # self.clear_list.start()
        # self.role = 525979283328335892 #con
        # self.role2 = 1100127448064081973 #mentor 
        # self.auto = {'rumble' : 0 , 'rumble++' : 0}
        # self.sw = "https://cdn.discordapp.com/attachments/1012101436869447840/1100136665319747625/logo_server_war.png"


    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.has_permissions(moderate_members = True)
    # async def guess(self,ctx, question : str,word:str , hint : str = None):
 
    #     word = word.lower()
    #     # embed = discord.Embed( color= discord.Color.blue()  , title= question )
    #     embed = discord.Embed(color = 0x2b2c31 )
    #     embed.title = question
    #     embed.set_author( name= ctx.guild.name , icon_url = ctx.guild.icon.url )
    #     if hint :
    #         embed.set_footer( text= f"Hint : {hint}" )
    #     await ctx.interaction.response.send_message( "done" , ephemeral = True)
    #     await ctx.channel.send(embed = embed)
    #     def check(m):
    #         return (m.content).lower() == str(word) and m.channel == ctx.channel
    #     msg = await client.wait_for("message",check = check)
    #     await ctx.send (f"{msg.author.mention} Guessed the right answer, The answer is **{word}**")

    # async def cog_unload(self):
    #     self.voice_rumble.cancel()
    #     self.clear_list.cancel()

    # @tasks.loop(hours= 1)
    # async def clear_list(self):
    #     self.voice_users = []    

    # @tasks.loop(seconds =60)
    # async def voice_rumble(self):
    #     for i in self.voice_users :
    #         coll = db[f"966022734398246963"]
    #         await coll.update_one({"eid": i}, {"$inc": {"rumble++": +(random.randint(0, 25))}})
            

    # async def check_channel(ctx) ->bool : 
    #     return ctx.channel.id == 1010624613442670662 or ctx.channel.category.id == 1100342224497156096  or ctx.author.id == 591011843552837655

    # async def open_account(self , guild_id : int , id : int):
    #         newuser = {"eid": id, "rumble": 0 , "rumble++" : 100 , "item" : []}
    #         coll = db[f"{guild_id}"]
    #         await coll.insert_one(newuser)

    # async def check_perms(ctx) ->bool : 
    #     role = ctx.guild.get_role(manager)
    #     return role in ctx.author.roles or ctx.author.guild_permissions.manage_guild        

# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                            AUTOCOINS     

    # @commands.Cog.listener()
    # async def on_voice_state_update(self , member, before, after):

    #     role = member.guild.get_role(self.role)

    #     if (after.self_mute is False) and (member.id not in self.voice_users) and not member.bot and role in member.roles :
    #         self.voice_users.append(member.id)  
    #         #await client.application.owner.send(f"{member.name} added in list  {len(self.voice_users)}")  
    #     if (after.channel is None or after.self_mute is True) and (member.id in self.voice_users):
    #         self.voice_users.remove(member.id)



    # message_cooldown = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.user)    
    # @commands.Cog.listener()
    # async def on_message(self , message):
    #   try :  
    #     coll = db[f"{message.guild.id}"]
    #     channel = (await coll.find_one({"category" : "economy"}))["auto_money_channel"]  
    #     if (message.channel.id in channel) or len(channel) is 0 :
    #         if message.author.bot:
    #             return

    #         bucket = self.message_cooldown.get_bucket(message)
    #         retry_after = bucket.update_rate_limit()

    #         if not retry_after:
    #             bal = await coll.find_one({"eid": message.author.id})
    #             if bal is None:
    #                 pass

    #             await coll.update_one({"eid": message.author.id}, {"$inc": {"rumble++": +(random.randint(0, self.auto['rumble++']))}}) #+(random.randint(0, x)
    #             role = message.guild.get_role(self.role2)
    #             if role in message.author.roles :
    #                 await coll.update_one({"eid": message.author.id}, {"$inc": {"rumble": +(random.randint(0, self.auto['rumble']))}})
                
    #   except :
    #         pass


# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                             BALANCE

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.is_owner()
    # async def setrumbleauto(self , ctx , rumble : int = None , rumble2 :int = None ):
    #     if rumble is not None :
    #         self.auto['rumble'] = rumble
    #     if rumble2 is not None :
    #         self.auto['rumble++'] = rumble2
    #     await ctx.send(self.auto)    
            

    # @commands.hybrid_command()
    # @commands.guild_only()
    # # @commands.check(check_channel)
    # # @cooldown(1, 5, BucketType.user)
    # async def iqooitem(self, ctx, user: discord.Member = None):
    #     user = user or ctx.author

    #     coll = db[f"{ctx.guild.id}"]

    #     bal = await coll.find_one({"eid": user.id})

    #     role = ctx.guild.get_role(self.role)
    #     if bal is None and (role in user.roles):
    #             await self.open_account(ctx.guild.id , user.id)
    #             bal = await coll.find_one({"eid": user.id})
    #     elif role not in user.roles :
    #         await ctx.send(f"{user} is not in Virtual Playground , join next time 💙")   
    #         return
    #     embed = discord.Embed(
    #             timestamp=ctx.message.created_at,
    #             title=f"{user}'s Balance",
    #             color= 0xF7C906 )
    #     lis = ' '
    #     y = 0
    #     for i in bal['item']:
    #         y = y+1
    #         lis = lis + f"{y}. {i}\n"
    #     if lis == ' ':
    #         lis = "empty"
    #     embed.add_field(
    #             name="items",
    #             value= lis , 
    #             inline= False  ,) 

    #     embed.set_footer(
    #             text=f"Requested By: {ctx.author.name}", icon_url=f"{ctx.author.display_avatar.url}")
    #     embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1055175132085223484/1076941636845707435/iqoo_11_neo7_iqoo_iqoo_smartphones_1.png")        
    #     await ctx.send(embed=embed) 
        
        
    # @commands.hybrid_command(aliases=["sr" , "s"])
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(3, 5, BucketType.user)
    # async def showcoins(self, ctx, user: discord.Member = None):
    #     user = user or ctx.author

    #     coll = db[f"{ctx.guild.id}"]

    #     bal = await coll.find_one({"eid": user.id})
        
    #     rumble_rank = coll.find({"rumble" :{ "$gt" : -1 }}).sort("rumble" , -1)
    #     rumble_docs = await rumble_rank.to_list(length = 100)
        
    #     rumble2_rank = coll.find({"rumble" :{ "$gt" : -1 }}).sort("rumble++" , -1)
    #     rumble2_docs = await rumble2_rank.to_list(length = 100)

    #     role = ctx.guild.get_role(self.role)
    #     role2 = ctx.guild.get_role(self.role2)
    #     if bal is None and (role in user.roles or role2 in user.roles):
    #             await self.open_account(ctx.guild.id , user.id)
    #             bal = await coll.find_one({"eid": user.id})
    #     elif (role not in user.roles) and (role2 not in user.roles) :
    #         await ctx.send(f"{user} is not in event , join next time 💙")   
    #         return
    #     embed = discord.Embed(
    #             title=f"{user.name}",
    #             color= 0xF7C906 )
    #     embed.add_field(
    #             name=f"coin (#{rumble_docs.index(bal) + 1})",
    #             value=f"{coin1}{bal['rumble']:,}", )
    #     embed.add_field(
    #             name=f"coin++ (#{rumble2_docs.index(bal) + 1})",
    #             value=f"{coin2}{bal['rumble++']:,}", ) 
    #     lis = ' '
    #     y = 0
    #     for i in bal['item']:
    #         y = y+1
    #         lis = lis + f"{y}. {i}\n"
    #     if lis == ' ':
    #         lis = "empty"
    #     embed.add_field(
    #             name="🛒 items",
    #             value= lis , 
    #             inline= False  ,) 
    #     if user != ctx.author :
    #         embed.set_footer(
    #                 text=f"Requested By: {ctx.author.name}", icon_url=f"{ctx.author.display_avatar.url}")
    #     # embed.set_thumbnail(url = self.sw)        
    #     await ctx.send(embed=embed) 

    # @showcoins.error
    # async def rr_error(self ,ctx ,error):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         await self.msg.reply(f"{ctx.author.mention} cooldown")
    #     else : 
    #         await client.application.owner.send(f'{error}')
    #         ctx.command.reset_cooldown(ctx)
    #         return 


    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.has_permissions( administrator =True)
    # async def rumbleitems(self , ctx):
    #     economy = db[f"{ctx.guild.id}"]
    #     lb_data = economy.find({"eid" :{ "$gt" : 0 }})
    #     docs = await lb_data.to_list(length = 1000)
    #     dis =  "items\n\n"   
    #     i = 0
    #     for x in docs:
    #         i = 1+i
    #         if len(x['item']) == 0 :
    #             continue
    #         # if i == page*10 + 1:
    #         #     break
    #         # if i <= (page-1)*10:
    #         #     continue
    #         items = (x['item'])
    #         user = ctx.guild.get_member(x['eid'])
    #         if user == None :
    #             i = i - 1 
    #             pass
    #         else:
    #             v = f"**{i}**. {user} **:** {items}\n"
    #             dis = dis + v
    #     embed = discord.Embed(description=dis, color=discord.Colour.blue())
    #     embed.set_author(name=f"{ctx.guild.name} Leaderboard" , icon_url="https://cdn.discordapp.com/attachments/999186452757872701/1007695073988853902/unknown.png")                       
    #     await ctx.send(embed=embed) 
 
    # @rumbleitems.error
    # async def rr_error(self ,ctx ,error):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         await self.msg.reply(f"{ctx.author.mention} cooldown")
    #     else : 
    #         await client.application.owner.send(f'{error}')
    #         ctx.command.reset_cooldown(ctx)
    #         return 



# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                                LB

    # @commands.hybrid_command()
    # @commands.has_permissions( administrator =True)
    # @commands.guild_only()
    # async def datax(self , ctx , code : str , user : typing.Optional[discord.Member] = None ):
    #     #await ctx.send(self.voice_users)
    #     background = Editor("CODE.png")
    #     poppins = Font.montserrat(size=80 , variant = "bold")
    #     background.text(
    #         (40, 20),
    #         f"{code}",
    #         font=poppins,
    #         color="black",
    #         )

    #     file = discord.File(fp=background.image_bytes, filename="code.png" , spoiler=True )  
    #     embed =  discord.Embed() 
    #     embed.set_image(url = "attachment://code.png")
    #     if user is None:
    #         await ctx.send(file = file )
    #     else:
    #         await user.send(file=file)    

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # async def top(self , ctx ,page: typing.Optional[int] = 1, type1 : typing.Literal["rumble" , "rumble++" ] = "rumble++" ):

    #   background = Editor("pg.png")
      
    #   poppins = Font.montserrat(size=45 , variant = "bold")
      
    #   i=0
    #   economy = db[f"{ctx.guild.id}"]
    #   if type1 == "rumble":
    #     lb_data = economy.find({"rumble" :{ "$gt" : -1 }}).sort("rumble" , -1)
    #     docs = await lb_data.to_list(length = 100)
    #     lis = []         
    #     for x in docs:
    #         i = 1+i
    #         if i == page*10 + 1:
    #             break
    #         if i <= (page-1)*10:
    #             continue
    #         bank = int(x['rumble'])
    #         user = ctx.guild.get_member(x['eid'])

    #         lis.append({ "rank" : i, "user" : user , "rumble" : bank})
    #   elif  type1 == "rumble++":
    #     lb_data = economy.find({"rumble" :{ "$gt" : -1 }}).sort("rumble++" , -1)
    #     docs = await lb_data.to_list(length = 100)
    #     lis = []         
    #     for x in docs:
    #         i = 1+i
    #         if i == page*10 + 1:
    #             break
    #         if i <= (page-1)*10:
    #             continue
    #         bank = int(x['rumble++'])
    #         user = ctx.guild.get_member(x['eid'])
    #         if user is None :
    #             continue
    #         lis.append({ "rank" : i, "user" : user , "rumble" : bank})
    #   j = 215
    #   k=  208
    #   for i in range(len(lis)):
    #         try :
    #             if lis[i]['user'].avatar is not None and lis[i]['user'] is not None :
    #                 url = str(lis[i]['user'].avatar.url)
    #             else : 
    #                 url = self.sw 
    #         except :
    #             pass       

    #         profile = await load_image_async(url)
    #         profile = Editor(profile).resize((46, 46))
    #         background.paste(profile.image, (106, k))
    #         background.text(
    #         (50, j),
    #         f"{lis[i]['rank']}",
    #         font=poppins,
    #         color="white",
    #         )
    #         background.text(
    #         (180, j),
    #         f"{lis[i]['user'].name}",
    #         font=poppins,
    #         color="white",
    #         )
    #         background.text(
    #         ( 720, j),
    #         f"{numerize.numerize(lis[i]['rumble'])}",
    #         font=poppins,
    #         color="white",
    #         )
    #         j = j+87
    #         k = k+87


    #   file = discord.File(fp=background.image_bytes, filename="lb.png")
    #   await ctx.send(file=file)

    # @top.error
    # async def rr_error(self ,ctx ,error):
    #         await ctx.author.send(f'{error}')
    #         ctx.command.reset_cooldown(ctx)
    #         return 
        

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def addrumblerole(self , ctx , role : discord.Role  ,  amount : amountconverter ,  location : typing.Literal[ 'rumble', 'rumble++' ] = "rumble"): 
    #     try:
    #            amount = int(amount)
    #     except ValueError:
    #         await ctx.send("Not a valid amount input!")
    #         return   
    #     economy = db[f"{ctx.guild.id}"] 
    #     await ctx.channel.typing()
    #     for member in role.members :
    #         bal = await economy.find_one({"eid": member.id})
    #         if bal is None:
    #             await self.open_account( ctx.guild.id ,member.id)
    #             bal = await economy.find_one({"eid": member.id}) 
    #         if location == "rumble++" :   
    #             await economy.update_one({"eid" : member.id } , {"$inc": {"rumble++" : +amount}})
    #             # await ctx.send(f"**{amount}** **Cash** coins added in {member.name}'s account")
    #         else:
    #             await economy.update_one({"eid" : member.id } , {"$inc": {"rumble" : +amount}})
    #             # await ctx.send(f"**{amount}** **pvc** coins added in {member.name}'s account")  
    #     await ctx.send(f"**{amount}** **{location}** coins added in {len(role.members)} accounts")


    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def addrumble(self , ctx , member : commands.MemberConverter  ,  amount : amountconverter ,  location : typing.Literal[ 'rumble', 'rumble++' ] = "rumble"): 
    #     try:
    #            amount = int(amount)
    #     except ValueError:
    #         await ctx.send("Not a valid amount input!")
    #         return   
    #     economy = db[f"{ctx.guild.id}"] 
    #     bal = await economy.find_one({"eid": member.id})
    #     if bal is None:
    #         await self.open_account( ctx.guild.id ,member.id)
    #         bal = await economy.find_one({"eid": member.id}) 
    #     if location == "rumble++" :   
    #         await economy.update_one({"eid" : member.id } , {"$inc": {"rumble++" : +amount}})
    #         await ctx.send(f"**{amount}** **rumble++** coins added in {member.name}'s account")
    #     else:
    #         await economy.update_one({"eid" : member.id } , {"$inc": {"rumble" : +amount}})
    #         await ctx.send(f"**{amount}** **rumble** coins added in {member.name}'s account") 

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def setrumble(self , ctx , member : commands.MemberConverter  ,  amount : amountconverter ,  location : typing.Literal[ 'rumble', 'rumble++' ] = "rumble++"): 
    #     try:
    #            amount = int(amount)
    #     except ValueError:
    #         await ctx.send("Not a valid amount input!")
    #         return   
    #     economy = db[f"{ctx.guild.id}"] 
    #     bal = await economy.find_one({"eid": member.id})
    #     if bal is None:
    #         await self.open_account( ctx.guild.id ,member.id)
    #         bal = await economy.find_one({"eid": member.id}) 
    #     if location == "rumble++" :
    #         await economy.update_one({"eid" : member.id } , {"$set": {"rumble++" : amount}})
    #         await ctx.send(f"**{amount}** **rumble++** coins seted in {member.name}'s account")
    #     else:
    #         await economy.update_one({"eid" : member.id } , {"$set": {"rumble" : amount}})
    #         await ctx.send(f"**{amount}** **rumble** coins seted in {member.name}'s account")         
    
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def removerumble(self , ctx , member : commands.MemberConverter  ,  amount : amountconverter ,  location : typing.Literal[ 'rumble', 'rumble++' ] = "rumble"): 
    #     try:
    #            amount = int(amount)
    #     except ValueError:
    #         await ctx.send("Not a valid amount input!")
    #         return   
    #     economy = db[f"{ctx.guild.id}"] 
    #     bal = await economy.find_one({"eid": member.id})
    #     if bal is None:
    #         await self.open_account( ctx.guild.id ,member.id)
    #         bal = await economy.find_one({"eid": member.id}) 
    #     if location == "rumble++" :   
    #         await economy.update_one({"eid" : member.id } , {"$inc": {"rumble++" : -amount}})
    #         await ctx.send(f"**{amount}** **rumble++** coins removed from {member.name}'s account")
    #     else:
    #         await economy.update_one({"eid" : member.id } , {"$inc": {"rumble" : -amount}})
    #         await ctx.send(f"**{amount}** **rumble** coins removed from {member.name}'s account") 


    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 5, BucketType.user)
    # async def rumblestore(self , ctx):
    #     i = 0
    #     storedata = db[f"{ctx.guild.id}"]
    #     store_data = storedata.find({"category" : "estore"}).sort("price" , -1)
    #     doc = await store_data.to_list(length = 50)
    #     ecoembed = discord.Embed(color= 0x08FC08)
    #     ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
    #     ecoembed.description = "Buy an item with the ***buyrumbleitem name*** command." 
    #     ecoembed.set_author(name=f"{ctx.guild.name} STORE" , icon_url=ctx.guild.icon)
    #     for x in doc:
    #         ecoembed.add_field(name= f'{x["name"]}' , value= f"{coin2} {x['price']} , limit = {x['limit']}", inline=False)
    #     await ctx.send(embed = ecoembed)

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 5, BucketType.user)
    # async def buyrumbleitem(self , ctx ,* ,name : str):
    #     ecoembed = discord.Embed(color= 0x08FC08)
    #     ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
    #     storedata = economy = db[f"{ctx.guild.id}"]
    #     item = await storedata.find_one({"name" : name.lower()})
    #     bal = await economy.find_one({"eid" : ctx.author.id})
    #     if bal is None:
    #         await ctx.send("open account with /showrumble command") 
    #     if item is None:
    #         ecoembed.description = ":negative_squared_cross_mark: I could not find any items in the store with that name."
    #         await ctx.send(embed = ecoembed)
    #     elif item["price"] > bal["rumble++"] :
    #         ecoembed.description = f'You do not have enough money to buy this item. You currently have {coin2} {bal["rumble++"]} on hand.'
    #         await ctx.send(embed = ecoembed)
    #     elif item['name'] in bal['item']:
    #          ecoembed.description = f"you already have this item in your items"    
    #          await ctx.send(embed = ecoembed)    
    #     elif item['limit'] <= 0 :
    #         ecoembed.description = f"item out of stock"    
    #         await ctx.send(embed = ecoembed)        
    #     else :
    #         await economy.update_one({"category" : "estore" ,"name" : item['name']} , { "$inc" : { "limit" : -1 }})
    #         await economy.update_one({"eid": ctx.author.id} , { "$push" : { "item" : name.lower() }})
    #         await economy.update_one({"eid": ctx.author.id} , {"$inc" : {"rumble++" : -item["price"] }})
    #         ecoembed.description = f'✅ You have bought {item["name"]} item for {coin2} {item["price"]}!'
    #         await ctx.send(embed = ecoembed)
    
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def addrumbleitem(self , ctx, price : int , sell : int , name:str , limit : int):
    #     storedata = db[f"{ctx.guild.id}"]
    #     await storedata.insert_one({ "category" : "estore" ,"name" : name.lower() , "price" : price , "sell" : sell , "limit" : limit})
    #     await ctx.send("done")

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def removerumbleitem(self , ctx, user : discord.Member , number:int):
    #     coll = db[f"{ctx.guild.id}"]
    #     bal = await coll.find_one({"eid": user.id})
    #     if bal is None :
    #         await ctx.send("user dont have account")
    #         return
    #     await coll.update_one({"eid": user.id} , { "$pull" : { "item" : bal['item'][number-1] }}) 
    #     bal = await coll.find_one({"eid": user.id})
    #     await ctx.send(f"item left - {bal['item']}")  

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @cooldown(1, 5 , BucketType.user)
    # async def useitem(self , ctx , number:int):
    #     coll = db[f"{ctx.guild.id}"]
    #     bal = await coll.find_one({"eid": ctx.author.id})
    #     if bal is None :
    #         await ctx.send("user dont have account")
    #         return
    #     item = bal['item'][number-1]  

    #     def check(reaction, user):
    #         return reaction.message.id == msg.id and str(reaction.emoji) == '<:Paod_tic:998964591172272210>' and user.id == 483594098377359360
        
    #     msg = await ctx.reply(f'hi managers {ctx.author} want to use {bal["item"].count(item)}x `{item}` , react to aprove (30s)')
    #     await msg.add_reaction("<:Paod_tic:998964591172272210>")
    #     try : 
    #         reaction , user = await client.wait_for('reaction_add', check=check , timeout = 30)
    #         await coll.update_one({"eid": ctx.author.id} , { "$pull" : { "item" : bal['item'][number-1] }}) 
    #         bal = await coll.find_one({"eid": ctx.author.id})
    #         await ctx.send(f"{ctx.author} item left - {bal['item']}")
    #     except asyncio.TimeoutError:
    #             await msg.reply("times up!") 

    # @useitem.error
    # async def hmm(self , ctx , error):
    #     await ctx.send(error)                       

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_perms)
    # async def drop(self , ctx, name:str , code : typing.Optional[str] = "claim"):
    #   embed = discord.Embed(color= discord.Color.blue() , title = name )
    #   embed.set_author(name = "Server Wars" , icon_url= ctx.guild.icon)
    #   embed.set_thumbnail(url= self.sw)
    #   channel = ctx.guild.get_channel(966022735333572640)
    #   role = ctx.guild.get_role(self.role)

    #   background = Editor("CODE.png")
    #   poppins = Font.montserrat(size=80 , variant = "bold")
    #   background.text(
    #         (40, 20),
    #         f"{code}",
    #         font=poppins,
    #         color="white",
    #         )
    #   file = discord.File(fp=background.image_bytes, filename="code.png")  
    #   embed.set_image(url = "attachment://code.png")

    #   await channel.send(file = file , embed = embed)
    #   await ctx.send("done")
    #   def check(m):
    #     return (m.content == code ) and (role in m.author.roles )
  
    #   msg1 = await client.wait_for('message', check=check , timeout = 120)
    #   storedata = economy = db[f"{ctx.guild.id}"]
    #   bal = await economy.find_one({"eid" : msg1.author.id})
    #   if bal is None:
    #     await self.open_account(ctx.guild.id, msg1.author.id)
    #   await economy.update_one({"eid": msg1.author.id} , { "$push" : { "item" : name.lower() }})
    #   await msg1.reply("congoooo")
    #   await ctx.send(f"{msg1.author} winner")
 
    # @app_commands.command()
    # @app_commands.guild_only()
    # @app_commands.default_permissions(manage_guild=True)
    # async def ad(self , interaction , attachment : discord.Attachment , link : typing.Optional[str]= "https://www.ajio.com/shop/sneaker-store" ,  text : typing.Optional[str] = "Hey! I just finished The AJIO SneakerQuest Game and unlocked cool AJIO vouchers to get the world's finest Sneakers. You can play this too!" , button_label : typing.Optional[str] = "CLICK ME TO WIN SNEAKERS" ,  title : typing.Optional[str] = None):
    #     embed = discord.Embed(color= discord.Color.blue() , title= title , description= f"[{text}]({link})" , url= link) 
    #     embed.set_author(name= "AJIO.COM" , url = link , icon_url= "https://cdn.discordapp.com/attachments/1059511042604015696/1069137540227018852/Ajio-Logo_1.webp" )
    #     view = discord.ui.View(timeout= None)
    #     view.add_item(discord.ui.Button( style= discord.ButtonStyle.link , url= link , label= button_label ))
    #     embed.set_image(url = attachment.url)
    #     await interaction.response.send_message("done" , ephemeral = True)
    #     await interaction.followup.send(embed = embed , view = view)

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.has_permissions(moderate_members = True)
    # async def iqoodrop(self , ctx, attachment : discord.Attachment ,  name:str , code : typing.Optional[str] = "claim" , link : typing.Optional[str]= "https://discord.com/channels/966022734398246963/966022735333572640" ):
      
    #   embed = discord.Embed(color= discord.Color.blue() , title = name )
    #   embed.set_author(name= "iQOO Neo 7 5G" , url = link , icon_url= ctx.guild.icon.url )
      
    #   view = discord.ui.View(timeout= None)
    #   view.add_item(discord.ui.Button( style= discord.ButtonStyle.blurple  , label= code ))
    #   embed.set_image(url = attachment.url)
    #   embed.set_thumbnail( url = "https://cdn.discordapp.com/attachments/1055175132085223484/1076941636845707435/iqoo_11_neo7_iqoo_iqoo_smartphones_1.png" )
    # #   channel = ctx.guild.get_channel(966022735333572640)
    #   role = ctx.guild.get_role(self.role2)

    # #   background = Editor("CODE.png")
    # #   poppins = Font.montserrat(size=80 , variant = "bold")
    # #   background.text(
    # #         (40, 20),
    # #         f"{code}",
    # #         font=poppins,
    # #         color="black",
    # #         )

    # #   file = discord.File(fp=background.image_bytes, filename="code.png")  
    # #   embed.set_image(url = "attachment://code.png")

    #   await ctx.interaction.response.send_message("done" , ephemeral = True)
    #   await ctx.channel.send( embed = embed , view = view)
    #   def check(m):
    #     return (m.content == code ) and (role in m.author.roles )

    #   msg1 = await client.wait_for('message', check=check , timeout = 120)
    #   storedata = economy = db[f"{ctx.guild.id}"]
    #   bal = await economy.find_one({"eid" : msg1.author.id})
    #   if bal is None:
    #     await self.open_account(ctx.guild.id, msg1.author.id)
    #     bal = await economy.find_one({"eid" : msg1.author.id})
    #   if name.lower() in bal['item'] :
    #         pass
    #   else :  
    #         await economy.update_one({"eid": msg1.author.id} , { "$push" : { "item" : name.lower() }})

    #   await msg1.reply("congoooo")
    #   await ctx.author.send(f"{msg1.author} winner")

    # @drop.error
    # async def rr_error(self ,ctx ,error):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         await self.msg.reply(f"{ctx.author.mention} cooldown")
    #     else : 
    #         await client.application.owner.send(f'{error}')
    #         ctx.command.reset_cooldown(ctx)
    #         return          



#----------------------------------

    @commands.command(aliases=["ep"])
    @commands.check(check_perms)
    @commands.guild_only()
    async def eventpoll(self , ctx , * , pollinfo :str):
        options = pollinfo.splitlines()
        description = " "
        for i in range(len(options)):
            if i == 0 :
                pass
            else:
                description = description + f"{self.emoji[i-1]} : {options[i]}\n"

        embed = discord.Embed(
                title=f"{options[0]}",
                color= 0x0847F7,
                description= description
            )
        # embed.set_thumbnail(url= self.sw)  
        embed.set_author(
                    name=f"{ctx.guild.name} VOTING", icon_url= ctx.guild.icon )   #"https://cdn.discordapp.com/attachments/966022737367814156/966412820898000936/PAOD_logo-03.jpg")  
        view = NormalView(timeout=432000 , count = (len(options)-1))
        await ctx.send(embed = embed , view = view)
        
    @eventpoll.error
    async def hi(self , ctx , error) :
        await ctx.send(error)    

    @commands.hybrid_command(aliases=["epr"])
    @commands.check(check_perms)
    @commands.guild_only()
    async def eventpollresult(self , ctx , pollid :str , option : str , multiplay : int):
        try :
            pollid = int(pollid)
        except ValueError:
            await ctx.send("invalid pollid")
            return    
        
        voters = await self.client.db.fetch('SELECT * FROM poll WHERE poll_id = $1 AND vote = $2' , int(pollid) , option)
       
        dis = "winner list \n\n"
        for voter in voters :
            try : 
                await self.client.db.execute('UPDATE users SET pvc = pvc + $1 WHERE id =$2 AND guild_id = $3', (multiplay * voter['amount']) , voter['user_id'] , ctx.guild.id )
                user = ctx.guild.get_member(voter['user_id'])
                dis = dis + f"{user} : +{( multiplay * voter['amount'])}\n"
            except :
                pass
        embed = discord.Embed(description= dis) 
        await ctx.send(  embed = embed) 
    
    
    @commands.hybrid_command()
    @commands.check(check_perms)
    @commands.guild_only()
    async def endpoll(self , ctx):
        r_message = ctx.message.reference 
        if r_message :
            message = ctx.message.reference.cached_message
            await message.edit(view = None)
        await ctx.message.delete()

    # @commands.hybrid_command()
    # @commands.has_permissions( administrator =True)
    # async def reseteventeconomy(self , ctx):
    #     economy = db[f"{ctx.guild.id}"] 

    #     def check(m):
    #         return m.author == ctx.author and m.content == "YES"
    #     await ctx.send("ARE YOU SURE ? , type YES to conti...")
    #     await client.wait_for('message' , check = check , timeout = 120 )    
    #     await economy.delete_many({"eid" : { "$gte": 0}})
    #     await ctx.send('**done**')
        
class NormalView(discord.ui.View):
    def __init__(self , timeout , count):
        super().__init__(timeout= timeout)
        self.count = count
        self.emoji = ["\U0001f1e6", "\U0001f1e7" ,"\U0001f1e8" ,"\U0001f1e9", "\U0001f1ea" ,"\U0001f1eb", "\U0001f1ec", "\U0001f1ed", "\U0001f1ee" ,"\U0001f1ef", "\U0001f1f0", "\U0001f1f1" ,"\U0001f1f2" ,"\U0001f1f3" ,"\U0001f1f4" ,"\U0001f1f5" ,"\U0001f1f6" ,"\U0001f1f7", "\U0001f1f8", "\U0001f1f9" ]
        self.alpha = ["A","B", "C" , "D" , "E","F", "G","H" , "I" , "J" , "K" , "L" , "M" , "N" , "O" , "P" , "Q" , "R" , "S" , "T" ]

        if (self.count )%5 == 0 :
            z = 5
        elif (self.count)%4 == 0:
            z = 4
        elif  (self.count) == 9 or (self.count) == 6 :
            z = 3
        else :
            z = 5         

        for x in range(self.count):
            y = int(x/z)
            self.add_item(PollButton(x, y , self.emoji[x] , self.alpha[x])) 

class PollButton(discord.ui.Button['NormalView']):
    def __init__(self, x: int, y: int , emoji : str , custom_id : str):
        super().__init__(style=discord.ButtonStyle.blurple , emoji= emoji,custom_id= custom_id,  row=y)
        self.x = x
        self.y = y


    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: NormalView = self.view
        x = self.custom_id
        y = self.emoji   
        data = await client.db.fetchrow('SELECT * FROM poll WHERE poll_id = $1 AND user_id = $2' , interaction.message.id , interaction.user.id)
        if data is None:
            await interaction.response.send_modal(Feedback(vote = x , time = datetime.now().timestamp()))
        else :
            await interaction.response.send_message(f"Already Voted !" , ephemeral = True)

class Feedback(discord.ui.Modal, title='TickAp.com'):

    def __init__(self , vote , time ):
        self.vote = vote
        self.time = time
        super().__init__()

    data = discord.ui.TextInput(
        label="type amount",
        style=discord.TextStyle.short,
        placeholder='...',
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.data.value)
        except ValueError:
            await interaction.response.send_message("invalid input , try again" , ephemeral= True)
            return

        bal = await client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , interaction.user.id , interaction.guild.id)

        if datetime.now().timestamp() - self.time > 20 :
            await interaction.response.send_message(f"Input expired" , ephemeral= True)
            return
        
        if bal == None :
            return

        if 0 < amount <= bal['pvc'] :

            await client.db.execute('UPDATE users SET pvc = pvc - $1 WHERE id =$2 AND guild_id = $3', amount , interaction.user.id , interaction.guild.id )
            await client.db.execute('INSERT INTO poll(poll_id , user_id , vote , amount ) VALUES ($1 , $2 ,$3,$4)', interaction.message.id , interaction.user.id, self.vote , amount)
            await interaction.response.send_message(f"your bet registered on {self.vote} of amount {amount}" , ephemeral= True)
        else :
            await interaction.response.send_message(f"error with the amount , check your balance , current bal is {bal['pvc']}" , ephemeral= True)  

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong.{error}', ephemeral=True)        


async def setup(client):
   await client.add_cog(event(client))                       