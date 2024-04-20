import discord
from discord.ext import commands
from database import *
from discord.ext.commands import BucketType, cooldown
import typing

class store(commands.Cog):

    def __init__(self , client):
        self.client = client 

    @commands.hybrid_command( aliases = ["item-info"] )
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 5, BucketType.user)
    async def iteminfo(self , ctx , id : typing.Optional[int] , * , name : typing.Optional[str] ):
        ecoembed = bembed()
        ecoembed.set_author(name = ctx.author , url = None , icon_url= ctx.author.display_avatar)
        
        item = None
        if id :
            item = await client.db.fetchrow('SELECT * FROM store WHERE id = $1 AND guild_id = $2', id , ctx.guild.id)
        elif name :
            item = await client.db.fetchrow("SELECT * FROM store WHERE LOWER(name) LIKE '%' || $1 || '%' AND guild_id = $2", name , ctx.guild.id )
        
        if item is None:
            ecoembed.description = "❎ Cant Find Item In Store."
            await ctx.send(embed =ecoembed)
            return
        i = item
        ecoembed.title = f"{item['name']} ({item['id']})"
        # ecoembed.add_field(name="Name" , value= f'{item["name"]}' ) 
        # ecoembed.add_field(name="id" , value= f'`{item["id"]}`')
        ecoembed.add_field(name = 'Price' , value = f"{pvc_coin(ctx.guild.id)[0] if item['currency'] == 2 else coin(ctx.guild.id)} {item['price']}")

        reward = (" ,".join([ (ctx.guild.get_role(role_id)).mention for role_id in i['roles'] if (ctx.guild.get_role(role_id)) ]) if i['roles'] else "") + "\n" + (f"- {pvc_coin(ctx.guild.id)[0]} {i['pvc']}" if i['pvc'] != 0 else "") + "\n" + (f"- {coin(ctx.guild.id)} {i['cash']} cash" if i['cash'] != 0 else "") + "\n" + (f"- {coin(ctx.guild.id)} {i['bank']} bank" if i['bank'] != 0 else ""  ) 
        
        ecoembed.add_field(name = 'Reward(s)' , value = reward)

        if i['rroles'] :
            ecoembed.add_field(name = 'Requirement(s)' , value = " ,".join([ (ctx.guild.get_role(role_id)).mention for role_id in i['rroles'] if (ctx.guild.get_role(role_id)) ]) if i['rroles'] else "None" )
        ecoembed.add_field( name = 'Description' , value = str(i['info']))
        if i['limit'] :
            ecoembed.add_field( name = 'Remaining' , value = f"{i['limit']}") 
        await ctx.send(embed = ecoembed)


    @commands.hybrid_command(aliases=["shop"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 5, BucketType.user)
    async def store(self , ctx):
        i = 0
        doc = await client.db.fetch("SELECT * FROM store WHERE guild_id = $1 ORDER BY currency DESC , price DESC " , ctx.guild.id)
        ecoembed = discord.Embed(color= 0x08FC08)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar)
        ecoembed.description = "Buy an item with the ***buyitem <id>*** command.\nFor more information on an item use the `item-info <id>` command \n\n" 
        ecoembed.set_author(name=f"{ctx.guild.name} STORE" , icon_url=ctx.guild.icon)
 
        for x in doc:
            limit = ''
            if x['limit'] is not None:
                limit = f', (**{x["limit"]} Remaining**)'
            ecoembed.add_field(name= f'{coin(ctx.guild.id) if x["currency"] == 1 else pvc_coin(ctx.guild.id)[0]} {x["price"]:,} - {x["name"]} , `id-{x["id"]}`' , value = f'{x["info"]}{limit}\n<:inv:1148131171885142086>', inline=False)
        await ctx.send(embed = ecoembed) 

 
    @commands.hybrid_command(aliases=["buy"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 5, BucketType.user)
    async def buyitem(self , ctx , id: typing.Optional[int] , * , name : typing.Optional[str] ):
        ecoembed = discord.Embed(color= 0x08FC08)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar)      
        item = None

        if id :
            item = await client.db.fetchrow('SELECT * FROM store WHERE id = $1 AND guild_id = $2', id , ctx.guild.id)
        elif name :
            item = await client.db.fetchrow("SELECT * FROM store WHERE LOWER(name) LIKE '%' || $1 || '%' AND guild_id = $2", name.lower() , ctx.guild.id )
        
        if item is None:
            ecoembed.description = "❎ Cant Find Item In Store."
            await ctx.send(embed =ecoembed)
            return

        itemid = item['id']

        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        if bal is None:
            await open_account(ctx.guild.id, ctx.author.id)
            bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        
        if item['currency'] == 1 :
            t = 'cash'
        elif item['currency'] == 2 :
            t = 'pvc'
        else :
            return

        # print(item['limit'] , item['limit'] and item['limit'] <= 0)
        if item['rroles']:
            for rrole in item['rroles'] :
                if ctx.guild.get_role(rrole) and ctx.guild.get_role(rrole) not in ctx.author.roles :
                    await ctx.send( embed = bembed(f'You Dont Have the Req. Role i.e {ctx.guild.get_role(rrole).mention}'))
                    return 
        
        if item['limit'] != None and item['limit'] <= 0 :
            ecoembed.description = "⚠️ Out Of Limit"
            await ctx.send(embed = ecoembed)
            return    

        elif item['price'] > bal[t]:
            ecoembed.description = f"You do not have enough Currency to buy this item. You currently have {coin(ctx.guild.id) if item['currency'] == 1 else pvc_coin(ctx.guild.id)[0]} {bal[t]} on hand."
            # ecoembed.description = f"You do not have enough Currency to buy this item."
           
            await ctx.send(embed = ecoembed)   
                 
            return 
        
        elif item['price'] <= bal[t] : 
            if t == 'cash' :
                await client.db.execute("UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3", item["price"] , ctx.author.id , ctx.guild.id) 
            elif t == 'pvc' :  
                await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3", item["price"] , ctx.author.id , ctx.guild.id) 
            
            ecoembed.description = f"✅ You have bought **{item['name']}** item for {coin(ctx.guild.id) if item['currency'] == 1 else pvc_coin(ctx.guild.id)[0]} {item['price']}!"
            await ctx.send(embed = ecoembed)
            if item['roles'] : 
                try :
                    await ctx.author.add_roles(*[ ctx.guild.get_role(r_role) for r_role in item['roles'] if ctx.guild.get_role(r_role) ] )
                except :
                    await ctx.send("There is some issue in giving the roles , please inform admins to put the bot role above reward role and bot have manage role perms !")
            
            await client.db.execute("UPDATE users SET cash = cash + $1 , bank = bank + $2 , pvc = pvc + $3 WHERE id = $4 AND guild_id = $5", item["cash"] , item['bank'] , item['pvc'] , ctx.author.id , ctx.guild.id) 
            if item['limit'] is not None :
                await client.db.execute('UPDATE store SET "limit" = "limit" - 1 WHERE id = $1 AND guild_id = $2', itemid , ctx.guild.id)
          
    @buyitem.error
    async def buy_erro(self , ctx , error):
        await ctx.send(error)


        # elif item['rrole'] is None or ctx.guild.get_role( item['rrole']) is None or ctx.guild.get_role( item['rrole']) in ctx.author.roles:
        #     await  ctx.author.add_roles(ctx.guild.get_role(item["role"]))
        #     await ctx.send(embed = ecoembed)
        # else:
            # ecoembed.description = f'❎ you dont have the required role!'
            # await ctx.send(embed = ecoembed)      

    # @commands.hybrid_command(aliases= ["sell"])
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 5, BucketType.user)
    # async def sellitem(self , ctx , id: typing.Optional[int] , * , name : typing.Optional[str]):
    #     ecoembed = discord.Embed(color= 0x08FC08)
    #     ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar)
        
    #     item = None
    #     if id :
    #         item = await client.db.fetchrow('SELECT * FROM store WHERE id = $1', id)
    #     elif name :
    #         item = await client.db.fetchrow("SELECT * FROM store WHERE LOWER(name) LIKE '%' || $1 || '%'", name)
        
    #     if item is None:
        #     ecoembed.description = "❎ Cant Find Item In Store."
        #     await ctx.send(embed =ecoembed)
        #     return
        
        # item_id = item['id']
        
        # bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        # if bal is None:
        #     await open_account(ctx.guild.id, ctx.author.id)
        #     bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)

        # if item is None:
        #     ecoembed.description = ":negative_squared_cross_mark: I could not find any items in the store which give this role."
        #     await ctx.send(embed = ecoembed)
        
        # elif ctx.guild.get_role(item["role"]) in ctx.author.roles:
        #     await ctx.author.remove_roles(ctx.guild.get_role(item["role"]))
        #     await client.db.execute("UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3", item["sell"] , ctx.author.id , ctx.guild.id)
        #     if item['limit'] is not None :
        #         await client.db.execute('UPDATE store SET "limit" = "limit" + 1 WHERE id = $1 AND guild_id = $2', item_id , ctx.guild.id)
        #     ecoembed.description = f'✅ You have sell {item["name"]}({ctx.guild.get_role(item["role"]).mention}) item for {coin(ctx.guild.id)} {item["sell"]}!'
        #     await ctx.send(embed = ecoembed)
        # else:
        #     ecoembed.description = f'you DONT have the item!!?'
        #     await ctx.send(embed = ecoembed)

async def setup(client):
   await client.add_cog(store(client))