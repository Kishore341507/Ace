import discord
from discord.ext import commands
from database import *
import asyncio
from discord.ext.commands import BucketType, cooldown
import random
import math
import typing

class Pets(commands.Cog):

    def __init__(self , client):
        self.client = client 

    async def check_channel(ctx) ->bool : 
        return ctx.channel.id in channel

    async def open_account(self , guild_id : int , id : int):
            newuser = {"id": id, "cash": 0 , "bank" : 1000 , "pvc" : 0 , "pet" : None}
            coll = db[f"{guild_id}"]
            await coll.insert_one(newuser)    


# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                               buypet COMMAND 

    @commands.hybrid_command(aliases=["petshop"])
    @commands.guild_only()
    @commands.check(check_channel)
    # @cooldown(2,0, BucketType.user)
    async def buypet(self , ctx , no:int = None):  
        ecoembed = discord.Embed(title="Pet Shop" ,color=discord.Colour.blue() , description="To buy pet use command `,buypet <number>`")
        ecoembed.set_author(name = ctx.author , url = None , icon_url= ctx.author.display_avatar.url) 
        economy = db[f"{ctx.guild.id}"]
        lb_data = economy.find({"category" : "pet_store" }).sort("price" , -1)
        docs = await lb_data.to_list(length = 20)
        i = 0 
        buy_pet = None
        for x in docs:
            i = 1+i
            if no == i :
               buy_pet = x['pet']
               buy_price = x['price']
            ecoembed.add_field(name=f"**{i}**. {coin1} {x['price']} - {x['pet']}" , value= f"{x['info']}" , inline= False)  
        ecoembed.set_author(name=f"{ctx.guild.name} Pet shop")
        bal = await economy.find_one({"id" : ctx.author.id})
        if no is not None and buy_pet is None :
            await ctx.send("Invalid input (pet number)")
        elif no is not None and bal['pet'] is not None:
            await ctx.send("you already have a pet , first sell with sellpet command")
        elif no is not None and bal['cash'] >= buy_price :
            await economy.update_one({"id" : ctx.author.id} , {"$set": {"pet": f"{buy_pet}" , "pet_name" : f"{ctx.author.name}'s_pet", "win" : 1 , "loss" : 1}})
            await economy.update_one({"id" : ctx.author.id} ,{"$inc": {"cash": - buy_price}})
            ecoembed.add_field(name= "Pet you buy" , value= f"{buy_pet}" , inline = False)
            await ctx.send(embed=ecoembed) 
        elif no is not None and bal['cash'] < buy_price:
            await ctx.send("Not enough balance in cash")
        else : 
            await ctx.send(embed=ecoembed)     
        
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(3, 60, BucketType.user)
    async def sellpet(self , ctx):
        ecoembed = discord.Embed(color= discord.Colour.red())
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        economy = db[f"{ctx.guild.id}"]
        def check( m):
                return (m.content =='yes' or m.content =='Yes' or m.content =='T' or m.content =='t' or m.content =='Y' or m.content =='y') and m.channel == ctx.channel and m.author.id == ctx.author.id
        bal = await economy.find_one({"id": ctx.author.id})
        if bal["pet"] is None:
            ecoembed.description =  'buy pet first from petshop'
            await ctx.send(embed=ecoembed)      
        else :
            await ctx.reply(f'you really want sell **{bal["pet_name"]}**{bal["pet"]} , **{bal["pet_name"]}** fought {bal["win"] + bal["loss"]} times for you :smiling_face_with_tear: ||Expire in 15 sec||')
            try :
                await client.wait_for('message', check=check , timeout = 15)
                await economy.update_one({"id" : ctx.author.id} , {"$set": {"pet": None , "pet_name" : None , "win" : 1 , "loss" : 1}})
                ecoembed.description =  'Done'
                await ctx.send(embed=ecoembed)
            except asyncio.TimeoutError:
                await ctx.reply(f"times up!")    

# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                             pf COMMAND  

    @commands.hybrid_command(aliases=["pf"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 5, BucketType.user)
    async def petfight(self , ctx , amount:amountconverter):
        ecoembed = discord.Embed(color= discord.Color.green())
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        economy = db[f"{ctx.guild.id}"]
        bal = await economy.find_one({"id": ctx.author.id})
        try:
            amount = int(amount)
        except ValueError:
            if amount == "all":
                amount = bal["cash"]
                if amount > 50000:
                    amount=50000   
            elif amount == "half":
                amount =int (0.5 * bal["cash"])
                if amount > 50000:
                    amount=50000
        if bal is None:
                await self.open_account( ctx.guild.id  ,ctx.author.id)
                bal = await economy.find_one({"id": ctx.author.id})
        if bal["pet"] is None:
            ecoembed.description = 'buy pet first from petshop'
            await ctx.send(embed=ecoembed)      
        elif amount > bal['cash']:
                ecoembed.description = 'You do not have enough money to pf that much'
                await ctx.send(embed=ecoembed)
        elif amount <= 0 or amount > 50000:
            ecoembed.description = 'You cannot fight with 0 , less or more then 50000'
            await ctx.send(embed=ecoembed)
        else : 
            w = bal["win"]/(bal["win"]+bal["loss"])
            l = 1-w
            x = random.choices([1,2] , weights = [ l, w])[0]
            if x == 1:
                await economy.update_one({"id": ctx.author.id} , {"$inc": {"cash": +amount  , "win": +1}})
                ecoembed.description = f"your pet **{bal['pet_name']} {bal['pet']}** __won__ the fight and get **{2*amount:,}**"
                ecoembed.set_footer(text= f"pet anger : {round(l*100 , ndigits=2)}%")
                await ctx.send(embed = ecoembed)
            else: 
                y = random.randint(1, 50)
                if y==25:
                    ecoembed.description = f"🪦| sedly you pet **{bal['pet_name']} {bal['pet']} die** during fight"
                    ecoembed.color = discord.Color.red()
                    await economy.update_one({"id" : ctx.author.id} , {"$set": {"pet": None , "pet_name" : None , "win" : 1 , "loss" : 1}})
                    await economy.update_one({"id": ctx.author.id} , {"$inc": {"cash": -amount }})
                    await ctx.send(embed = ecoembed)
                else:
                    await economy.update_one({"id": ctx.author.id} , {"$inc": {"cash": -amount , "loss": +1}})
                    ecoembed.description = f"your pet **{bal['pet_name']} {bal['pet']}** __lose__ the fight and you __lost__ **{amount:,}**"
                    ecoembed.color = discord.Color.red()
                    ecoembed.set_footer(text= f"pet anger : {round(l*100 , ndigits=2)}%")
                    await ctx.send(embed = ecoembed)

# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                               rf COMMAND 



    # @commands.hybrid_command(aliases=["rf"])
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(3, 60, BucketType.user)
    # async def realfight(self , ctx , user : discord.Member , amount: amountconverter):
    #     ecoembed = discord.Embed(color= discord.Color.blue())
    #     ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar)
 
    #     def check( m):
    #             return (m.content =='yes' or m.content =='Yes' or m.content =='T' or m.content =='t' or m.content =='Y' or m.content =='y') and m.channel == ctx.channel and m.author.id == user.id 
        
    #     economy = db[f"{ctx.guild.id}"]
    #     user_bal = await economy.find_one({"id": user.id})
    #     member_bal = await economy.find_one({"id": ctx.author.id})
    #     try:
    #         amount = int(amount)
    #     except ValueError:
    #         if amount == "all":
    #             amount = member_bal["bank"]
    #             if amount > 50000:
    #                 amount=50000  
    #         elif amount == "half":
    #             amount = int(0.5 * member_bal["bank"])
    #             if amount > 50000:
    #                 amount=50000

    #     if user_bal is None:
    #         await self.open_account(ctx.guild.id ,user.id)
    #         user_bal = await economy.find_one({"id": user.id})
    #     if member_bal is None:
    #         await self.open_account(ctx.guild.id ,ctx.author.id)
    #         member_bal = await economy.find_one({"id": ctx.author.id})
    #     if user_bal["pet"] is None or member_bal["pet"] is None :
    #         ecoembed.description =  'you or **user** dont have pet , first buy it from petshop'
    #         await ctx.send(embed=ecoembed)
    #     elif user == ctx.author:
    #         await ctx.send("hmmm cant !!!!!!")
    #     elif amount > member_bal['bank']:
    #         await ctx.send('You do not have enough money to fight')
    #     elif amount <= 0:
    #         await ctx.send('You cannot fight with 0 or less')
    #     elif amount > user_bal["bank"]:
    #         await ctx.send(f'{user.name} do not have enough money to fight in `bank`')    
    #     else:   
    #         x = random.randint(1, 2)
    #         await ctx.reply(f'{user} if you want to accept this type (amount = **{amount}**) `yes` ||Expire in 15 sec||')
    #         try:
    #             await client.wait_for('message', check=check , timeout = 15)
    #             msg = await ctx.send(f"⚔️⚔️ fight between **{ctx.author.name}'s {member_bal['pet_name']} {member_bal['pet']}** and **{user.name}'s {user_bal['pet_name']} {user_bal['pet']}** Started!!!")
    #             await asyncio.sleep(10)
    #             if x==1:
    #                 await economy.update_one({"id": ctx.author.id} , {"$inc": {"bank": + (int(0.8*amount))  , "win": +1}})
    #                 await economy.update_one({"id": user.id} , {"$inc": {"bank": -amount  , "loss": +1}})
    #                 ecoembed.description = f"**{ctx.author.name}'s {member_bal['pet_name']} {member_bal['pet']}** won the fight and get {int(1.8*amount):,} , better luck next time **{user.name}**"
    #                 await msg.reply(embed = ecoembed)
    #             else:                   
    #                 await economy.update_one({"id": user.id} , {"$inc": {"bank": + (int(0.8*amount))  , "win": +1}})
    #                 await economy.update_one({"id": ctx.author.id} , {"$inc": {"bank": -amount  , "loss": +1}})
    #                 ecoembed.description = f"**{user.name}'s {user_bal['pet_name']} {user_bal['pet']}** won the fight and get {int(1.8*amount):,} , better luck next time **{ctx.author.name}**"
    #                 await msg.reply(embed = ecoembed)
    #         except asyncio.TimeoutError:
    #             await ctx.reply(f"{user.name} times up!")

    # @realfight.error
    # async def additem_error(self,ctx , error):
    #     await client.application.owner.send(f'{error}')    

# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                                set pet name

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(2, 300, BucketType.user)
    # async def setpetname(self , ctx ,name: str):
    #     ecoembed = discord.Embed(color= discord.Color.red())
    #     ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
    #     economy = db[f"{ctx.guild.id}"]
    #     bal = await economy.find_one({"id": ctx.author.id})
    #     if bal is None:
    #             await self.open_account(ctx.guild.id ,ctx.author.id)
    #             bal = await economy.find_one({"id": ctx.author.id})
    #     if bal["pet"] is None:
    #         ecoembed.description =  'buy pet first from petshop'
    #         await ctx.send(embed=ecoembed)      
    #     else:
    #         await economy.update_one({"id": ctx.author.id} ,{"$set" :{"pet_name": name}})
    #         ecoembed.description = f"your pet name is now {name}"
    #         ecoembed.color = discord.Color.green()
    #         await ctx.send(embed = ecoembed)        

# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                              profile COMMAND 

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 5, BucketType.user)
    # async def profile(self, ctx):
    #     user = ctx.author
    #     economy = db[f"{ctx.guild.id}"]
    #     bal = await economy.find_one({"id": user.id})
    #     if bal is None:
    #             await self.open_account( ctx.guild.id ,user.id)
    #             bal = await economy.find_one({"id": user.id})
    #     embed = discord.Embed(
    #             timestamp=ctx.message.created_at,
    #             title=f"{user.name}'s Profile",
    #             color= discord.Color.brand_green(),)
    #     embed.add_field(
    #             name="PAOD's Cash",
    #             value=f"<:oiionk:1006619821183602748>{bal['cash']:,}",)
    #     embed.add_field(
    #             name="PAOD's Bank",
    #             value=f"<:oiionk:1006619821183602748>{bal['bank']:,}", )
    #     status = (await economy.find_one({"category" : "pvc"}))["status"]
    #     if status is not None :
    #         embed.add_field(
    #             name="PAOD's ++",
    #             value=f"{coin1}{bal['pvc']:,}",)
    #     else : 
    #         embed.add_field(
    #             name="Total",
    #             value=f"{coin1}{(bal['bank'] + bal['cash'] ):,}",)

    #     if bal["pet"] is not None:        
    #         embed.add_field(
    #             name="PET",
    #             value=f"**{bal['pet_name']}**  \n{bal['pet']}", )
    #         embed.add_field(
    #             name="TOTAL WINS",
    #             value=f"{bal['win']}", )
    #         embed.add_field(
    #             name="TOTAL LOSE",
    #             value=f"{bal['loss']}", )

    #     embed.set_footer(icon_url=f"{ctx.author.display_avatar.url}")
    #     embed.set_thumbnail(url=user.avatar.url)
    #     embed.set_author(name= ctx.guild.name , icon_url= ctx.guild.icon.url)
    #     await ctx.send(embed=embed)



async def setup(client):
   await client.add_cog(Pets(client))           